import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_takeover as ct  # noqa: E402

TEMPLATES = HERE.parent.parent / "templates"
O = ct.OUT_NAME
SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
F = "prompt-diff"
CHANGE = f"{O}/4-change-{F}.md"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(out + ["| " + " | ".join(r) + " |" for r in rows])


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "proj"
        self.out = self.root / O
        self.out.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, rel, text=""):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def tpl(self, name, rel, **subs):
        text = (TEMPLATES / name).read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        return self.write(rel, text)

    def phase(self, p, mode="只读"):
        self.tpl("output-README.md", f"{O}/README.md",
                 **{"当前阶段：A": f"当前阶段：{p}", "运行方式：只读\n技术栈": f"运行方式：{mode}\n技术栈"})

    def phase_a_done(self, human=True):
        self.tpl("project-map.md", f"{O}/{ct.PROJECT_MAP}")
        for n in ("app-architecture", "architecture", "module-deps", "data-model-er", "sequence-login"):
            self.write(f"{O}/diagrams/{n}.svg", SVG)
        self.write(f"{O}/apply/.claude/skills/docs-auto-sync/SKILL.md", "---\nname: docs-auto-sync\n---\n")
        self.write(f"{O}/apply/apply.sh", "#!/bin/bash\n")
        p = self.tpl("CLAUDE.template.md", f"{O}/apply/CLAUDE.md")
        if human:
            t = p.read_text(encoding="utf-8")
            t = t.replace("## 禁区\n", "## 禁区\n\n- 订单表 ext 字段被对账系统读取，不能改格式\n")
            t = t.replace("## 历史包袱\n", "## 历史包袱\n\n- legacy 目录是旧客户端兼容层，勿重构\n")
            p.write_text(t, encoding="utf-8")

    def phase_b_done(self):
        self.tpl("dev-setup.md", f"{O}/{ct.DEV_SETUP}")
        self.tpl("test-guard.md", f"{O}/{ct.TEST_GUARD}")
        self.tpl("dev-env.sh", f"{O}/scripts/dev-env.sh")
        self.write(f"{O}/apply/.claude/skills/env-bootstrap/SKILL.md", "---\nname: env-bootstrap\n---\n")
        self.write(f"{O}/apply/.github/workflows/test.yml", "on: push\n")

    def guard(self, paths=None, gaps=None, plan=None):
        cp = table(["#", "链路", "起点（接口）", "关键节点", "终点（成功状态）", "核心风险"], paths or [])
        detail = table(["编号", "优先级", "链路", "场景", "为什么必须", "建议测试类型", "判断要点"], gaps or [])
        pl = table(["批次", "缺口", "测试类型", "核心链路", "预期工作量", "状态"], plan or [])
        self.write(f"{O}/{ct.TEST_GUARD}",
                   f"# 测试护栏\n\n## 1. 核心链路\n\n{cp}\n\n## 2. 测试现状\n\n### 实际运行结果\n\n通过 10\n\n"
                   f"## 3. 测试缺口\n\n### 明细\n\n{detail}\n\n## 4. 补测试计划\n\n{pl}\n\n## 5. CI\n\n有\n")

    def run_check(self):
        return ct.run(self.root)

    def has(self, items, needle):
        return any(needle in m for m in items)


class TestStart(Base):
    def test_not_started(self):
        self.assertTrue(self.has(self.run_check().errors, "README.md"))

    def test_foreign_readme_not_ours(self):
        self.write(f"{O}/README.md", "# 别人的目录\n")
        self.assertTrue(self.has(self.run_check().errors, "流程还没开始"))

    def test_fallback_dir(self):
        shutil.rmtree(self.out)
        self.tpl("output-README.md", f"{O}-2/README.md")
        self.assertTrue(self.has(self.run_check().passed, f"{O}-2"))

    def test_fresh_phase_a_only_warnings(self):
        self.phase("A")
        r = self.run_check()
        self.assertEqual(r.errors, [])
        self.assertTrue(self.has(r.warnings, f"缺少 {ct.PROJECT_MAP}"))
        self.assertTrue(self.has(r.passed, "运行方式 只读"))

    def test_phase_a_missing_is_error_in_phase_b(self):
        self.phase("B")
        self.assertTrue(self.has(self.run_check().errors, f"缺少 {ct.PROJECT_MAP}"))

    def test_phase_a_complete(self):
        self.phase("A")
        self.phase_a_done()
        r = self.run_check()
        self.assertEqual(r.errors, [])
        self.assertTrue(self.has(r.passed, "阶段 A：项目地图和四张主图齐全"))

    def test_app_architecture_and_module_deps_required(self):
        self.phase("A")
        self.phase_a_done()
        (self.out / "diagrams" / "app-architecture.svg").unlink()
        (self.out / "diagrams" / "module-deps.svg").unlink()
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "diagrams/app-architecture.svg"))
        self.assertTrue(self.has(r.warnings, "diagrams/module-deps.svg"))
        self.phase("B")
        self.assertTrue(self.has(self.run_check().errors, "diagrams/app-architecture.svg"))

    def test_module_description_section_required(self):
        self.phase("A")
        self.phase_a_done()
        p = self.out / ct.PROJECT_MAP
        p.write_text(p.read_text(encoding="utf-8").replace("## 3. 模块说明", "## 3. 其他"), encoding="utf-8")
        self.assertTrue(self.has(self.run_check().warnings, "模块说明"))

    def test_sequence_diagram_expected(self):
        self.phase("A")
        self.phase_a_done()
        (self.out / "diagrams" / "sequence-login.svg").unlink()
        self.assertTrue(self.has(self.run_check().warnings, "时序图"))

    def test_api_section_without_source(self):
        self.phase("A")
        self.phase_a_done()
        self.write(f"{O}/{ct.PROJECT_MAP}", "# 项目地图\n\n## 4. 接口清单\n\n| 方法 | 路径 |\n")
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "扫描来源"))
        self.assertTrue(self.has(r.warnings, "缺少这些小节"))

    def test_mode_line_missing_defaults_to_readonly(self):
        self.phase("A")
        p = self.out / "README.md"
        p.write_text(p.read_text(encoding="utf-8").replace("运行方式：只读\n技术栈", "技术栈"), encoding="utf-8")
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "运行方式"))
        self.assertTrue(self.has(r.passed, "运行方式 只读"))


class TestLayout(Base):
    def setUp(self):
        super().setUp()
        self.phase("A")
        self.phase_a_done()

    def test_only_agreed_files(self):
        self.assertTrue(self.has(self.run_check().passed, "只有约定的文件"))

    def test_extra_top_level_file(self):
        self.write(f"{O}/summary.md", "# s\n")
        msg = next(m for m in self.run_check().errors if "约定以外" in m)
        self.assertIn("summary.md", msg)

    def test_extra_diagram(self):
        self.write(f"{O}/diagrams/external-deps.svg", SVG)
        self.assertTrue(self.has(self.run_check().errors, "diagrams/external-deps.svg"))

    def test_extra_script(self):
        self.write(f"{O}/scripts/install-deps.sh", "#\n")
        self.assertTrue(self.has(self.run_check().errors, "scripts/install-deps.sh"))

    def test_allowed_extras(self):
        self.write(f"{O}/diagrams/change-{F}.svg", SVG)
        self.write(f"{O}/scripts/docker-compose.dev.yml", "services: {}\n")
        self.write(f"{O}/screenshots/{F}/before-list.png", "x")
        self.write(f"{O}/apply/.github/workflows/test.yml", "on: push\n")
        self.assertFalse(self.has(self.run_check().errors, "约定以外"))


class TestSvg(Base):
    def setUp(self):
        super().setUp()
        self.phase("A")
        self.phase_a_done()

    def test_invalid_svg(self):
        self.write(f"{O}/diagrams/architecture.svg", "<svg><g></svg>")
        self.assertTrue(self.has(self.run_check().errors, "不是合法的 SVG"))

    def test_non_svg_root(self):
        self.write(f"{O}/diagrams/architecture.svg", "<html></html>")
        self.assertTrue(self.has(self.run_check().errors, "不是合法的 SVG"))

    def test_png_in_diagrams(self):
        self.write(f"{O}/diagrams/extra.png", "x")
        self.assertTrue(self.has(self.run_check().errors, "图必须是 SVG"))

    def test_mermaid_in_markdown(self):
        self.write(f"{O}/{ct.PROJECT_MAP}", "# 项目地图\n\n```mermaid\ngraph TD\n```\n")
        self.assertTrue(self.has(self.run_check().errors, "Mermaid"))

    def test_png_screenshots_allowed(self):
        self.write(f"{O}/screenshots/{F}/before-page.png", "x")
        self.assertFalse(self.has(self.run_check().errors, "图必须是 SVG"))


class TestContext(Base):
    def test_placeholders_are_warnings(self):
        self.phase("C")
        self.phase_a_done(human=False)
        self.phase_b_done()
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "「禁区」等人填写"))
        self.assertFalse(self.has(r.errors, "禁区"))

    def test_too_long(self):
        self.phase("A")
        self.write(f"{O}/apply/CLAUDE.md", "## 禁区\n- a\n## 历史包袱\n- b\n" + "x\n" * 300)
        self.assertTrue(self.has(self.run_check().errors, "超过 300 行"))

    def test_missing_section(self):
        self.phase("A")
        self.write(f"{O}/apply/CLAUDE.md", "## 历史包袱\n- b\n")
        self.assertTrue(self.has(self.run_check().errors, "缺少「禁区」"))

    def test_heading_inside_code_block_ignored(self):
        self.phase("A")
        self.write(f"{O}/apply/CLAUDE.md", "```\n## 禁区\n- a\n```\n## 历史包袱\n- b\n")
        self.assertTrue(self.has(self.run_check().errors, "缺少「禁区」"))


class TestGuardrails(Base):
    def setUp(self):
        super().setUp()
        self.phase("B")
        self.phase_a_done()

    def test_phase_b_complete_readonly(self):
        self.phase_b_done()
        r = self.run_check()
        self.assertEqual(r.errors, [])
        self.assertTrue(self.has(r.passed, "阶段 B"))
        self.assertFalse(self.has(r.warnings, "未实测"))

    def test_phase_b_missing_is_warning_while_in_b(self):
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "阶段 B 产出缺少"))
        self.assertFalse(self.has(r.errors, "阶段 B 产出缺少"))

    def test_phase_b_missing_is_error_in_c(self):
        self.phase("C")
        r = self.run_check()
        self.assertTrue(self.has(r.errors, "阶段 B 产出缺少"))
        self.assertTrue(self.has(r.errors, "CI 配置"))

    def test_readonly_must_say_untested(self):
        self.phase_b_done()
        self.write(f"{O}/{ct.DEV_SETUP}", "# 环境\n## 依赖清单\n## 新人上手\n## 安装记录\n## 启动记录\n## 冒烟结果\n")
        self.assertTrue(self.has(self.run_check().warnings, "未实测"))

    def test_run_mode_needs_actual_results(self):
        self.phase("B", mode="运行")
        self.phase_b_done()
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "实际运行结果"))
        self.phase("C", mode="运行")
        r = self.run_check()
        self.assertTrue(self.has(r.errors, "实际运行结果"))
        self.assertTrue(self.has(r.errors, "冒烟结果"))

    def test_readonly_does_not_need_actual_results(self):
        self.phase("C")
        self.phase_b_done()
        r = self.run_check()
        self.assertFalse(self.has(r.errors, "实际运行结果"))
        self.assertFalse(self.has(r.errors, "冒烟结果"))

    def test_guard_missing_section(self):
        self.phase_b_done()
        self.write(f"{O}/{ct.TEST_GUARD}", "# 测试护栏\n## 1. 核心链路\n")
        self.assertTrue(self.has(self.run_check().warnings, "缺少这些小节：测试现状"))

    def test_critical_paths_limit(self):
        self.guard(paths=[[str(i), f"链路{i}", "a", "b", "c", "d"] for i in range(1, 10)])
        self.assertTrue(self.has(self.run_check().errors, "核心链路有 9 条"))

    def test_template_rows_not_counted(self):
        self.tpl("test-guard.md", f"{O}/{ct.TEST_GUARD}")
        self.assertTrue(self.has(self.run_check().passed, "核心链路 0 条"))

    def gaps(self, p0, p1):
        rows = [[f"G{i:02d}", "P0", "l", "s", "w", "t", "k"] for i in range(p0)]
        rows += [[f"G{i + 50:02d}", "P1", "l", "s", "w", "t", "k"] for i in range(p1)]
        self.guard(gaps=rows)

    def test_gaps_too_many_p0(self):
        self.gaps(14, 6)
        self.assertTrue(self.has(self.run_check().errors, "14 个 P0"))

    def test_gaps_total_limit(self):
        self.gaps(10, 11)
        r = self.run_check()
        self.assertTrue(self.has(r.errors, "共 21 项"))
        self.assertTrue(self.has(r.errors, "11 个 P1"))

    def test_gaps_ok(self):
        self.gaps(6, 4)
        r = self.run_check()
        self.assertTrue(self.has(r.passed, "P0 6，P1 4，共 10"))
        self.assertFalse(self.has(r.errors, "测试缺口"))

    def test_gaps_few_p0(self):
        self.gaps(2, 0)
        self.assertTrue(self.has(self.run_check().warnings, "只有 2 个 P0"))

    def test_batch_limit(self):
        self.guard(plan=[["1", "G01", "a", "b", "c", "d"], ["2", "G02、G03、G04、G05", "a", "b", "c", "d"]])
        r = self.run_check()
        self.assertTrue(self.has(r.errors, "批次 2 含 4 个缺口"))
        self.assertFalse(self.has(r.errors, "批次 1"))


class TestChanges(Base):
    def setUp(self):
        super().setUp()
        self.phase("C")
        self.phase_a_done()
        self.phase_b_done()

    def change(self, edges=8, basis="基于代码推断", leftover=False, final="", commit="", svg=True):
        p = self.tpl("change.md", CHANGE)
        t = p.read_text(encoding="utf-8")
        rows = "\n".join(
            f"| E{i:02d} | 场景{i} | {'待产品决策' if leftover and i == 1 else '返回 400'} | {basis} |"
            for i in range(1, edges + 1))
        t = t.replace("| E01 | | | |", rows)
        if final:
            t = t.replace("| D1 | | | | |", f"| D1 | 缓存 | 不加 | 加 | {final} |")
        t = t.replace("| 有 / 无（先锁行为） | |", f"| 有 | {commit} |")
        p.write_text(t, encoding="utf-8")
        if svg:
            self.write(f"{O}/diagrams/change-{F}.svg", SVG)
        return p

    def edit(self, old, new):
        p = self.root / CHANGE
        p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_untouched_template(self):
        self.tpl("change.md", CHANGE)
        r = self.run_check()
        self.assertTrue(self.has(r.errors, "边界场景只有 0 条"))
        self.assertFalse(self.has(r.warnings, "待产品决策"))
        self.assertFalse(self.has(r.errors, "缺少「"))

    def test_ai_recommendations_counted(self):
        self.change()
        r = self.run_check()
        self.assertEqual([e for e in r.errors if e.startswith("4-change")], [])
        self.assertTrue(self.has(r.warnings, "AI 推荐等人确认"))

    def test_missing_basis(self):
        self.change(basis="")
        self.assertTrue(self.has(self.run_check().errors, "没写依据"))

    def test_missing_requirement_section(self):
        self.change()
        self.edit("### 5. 老项目约束", "### 5. 其他")
        self.assertTrue(self.has(self.run_check().errors, "缺少「老项目约束」"))

    def test_missing_part(self):
        self.change()
        self.edit("## 二、方案", "## 二、其他")
        self.assertTrue(self.has(self.run_check().errors, "缺少「二、方案」部分"))

    def test_product_pending_leftover(self):
        self.change(leftover=True)
        self.assertTrue(self.has(self.run_check().warnings, "待产品决策"))
        self.change(leftover=True, final="不加缓存（AI 推荐，待确认）")
        self.assertTrue(self.has(self.run_check().errors, "待产品决策"))

    def test_ai_recommended_decision_is_warning(self):
        self.phase("C", mode="运行")
        self.change(final="不加缓存（AI 推荐，待确认）", commit="abc123")
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "决策点等人确认：D1"))
        self.assertFalse(self.has(r.errors, "决策点"))

    def test_empty_decision_before_implementation(self):
        self.change()
        r = self.run_check()
        self.assertTrue(self.has(r.warnings, "决策点没有落定：D1"))
        self.assertFalse(self.has(r.errors, "决策点"))

    def test_unresolved_decision_after_commit(self):
        self.phase("C", mode="运行")
        self.change(final="待审核", commit="abc123")
        self.assertTrue(self.has(self.run_check().errors, "决策点没有落定：D1"))

    def test_readonly_must_not_commit(self):
        self.change(final="同意", commit="abc123")
        self.assertTrue(self.has(self.run_check().errors, "只读方式不改代码"))

    def test_decisions_confirmed(self):
        self.change(final="同意，不加缓存")
        self.assertTrue(self.has(self.run_check().passed, "决策点已全部确认"))

    def test_missing_solution_section(self):
        self.change(final="同意")
        self.edit("### 5. 影响范围与风险", "### 5. 其他")
        self.assertTrue(self.has(self.run_check().errors, "缺少「影响范围」"))

    def test_change_svg_expected(self):
        self.change(final="同意", svg=False)
        self.assertTrue(self.has(self.run_check().warnings, f"change-{F}.svg"))

    def test_template_has_no_mermaid(self):
        self.change(final="同意")
        self.assertFalse(self.has(self.run_check().errors, "Mermaid"))


class TestRisksReviewStatus(Base):
    def setUp(self):
        super().setUp()
        self.phase("C")
        self.phase_a_done()
        self.phase_b_done()

    def risks(self, n, cover="有"):
        rows = [[f"R{i:02d}", "a.java", "改动热点", "x", "a.java:1", "无", cover, "先补测试"] for i in range(1, n + 1)]
        body = table(["编号", "位置", "类型", "为什么危险", "证据", "接缝", "测试兜底", "改之前要做什么"], rows)
        p = self.out / ct.PROJECT_MAP
        t = p.read_text(encoding="utf-8")
        start = t.index("### 风险清单")
        end = t.index("## 5. 模块依赖")
        p.write_text(t[:start] + "### 风险清单\n\n" + body + "\n\n" + t[end:], encoding="utf-8")

    def test_risk_section_required(self):
        p = self.out / ct.PROJECT_MAP
        p.write_text(p.read_text(encoding="utf-8").replace("## 4. 风险地带", "## 4. 其他"), encoding="utf-8")
        self.assertTrue(self.has(self.run_check().errors, "风险地带"))

    def test_risk_limit(self):
        self.risks(16)
        self.assertTrue(self.has(self.run_check().errors, "有 16 条，超过 15 条"))
        self.risks(15)
        self.assertFalse(self.has(self.run_check().errors, "超过 15 条"))

    def test_risk_cover_backfilled_after_b(self):
        self.risks(3, cover="待阶段 B")
        self.assertTrue(self.has(self.run_check().warnings, "测试兜底还没回填"))
        self.phase("B")
        self.assertFalse(self.has(self.run_check().warnings, "测试兜底还没回填"))

    def change(self, review_rows="", commit=""):
        p = self.tpl("change.md", CHANGE)
        t = p.read_text(encoding="utf-8")
        t = t.replace("| D1 | | | | |", "| D1 | 缓存 | 不加 | 加 | 同意 |")
        t = t.replace("| 有 / 无（先锁行为） | |", f"| 有 | {commit} |")
        t = t.replace("| 方案 | 兼容性 / 安全 / 性能 | | | 高 / 中 / 低 | 已改：… / 不改：理由 |", review_rows)
        p.write_text(t, encoding="utf-8")
        self.write(f"{O}/diagrams/change-{F}.svg", SVG)

    def test_plan_review_expected(self):
        self.change()
        self.assertTrue(self.has(self.run_check().warnings, "方案还没做独立 review"))
        self.change("| 方案 | 安全 | Ctl:10 | 越权 | 中 | 已改：加鉴权 |")
        self.assertFalse(self.has(self.run_check().warnings, "方案还没做独立 review"))

    def test_code_review_expected_after_commit(self):
        self.phase("C", mode="运行")
        self.change("| 方案 | 性能 | 方案 5 | 未发现 | 低 | 无 |", commit="abc123")
        self.assertTrue(self.has(self.run_check().warnings, "代码还没做独立 review"))
        self.change("| 方案 | 性能 | 方案 5 | 未发现 | 低 | 无 |\n| 代码 | 兼容性 | A.java:3 | 改了返回 | 高 | |", commit="abc123")
        r = self.run_check()
        self.assertFalse(self.has(r.warnings, "代码还没做独立 review"))
        self.assertTrue(self.has(r.warnings, "高风险问题还没处理：代码·兼容性"))

    def test_readonly_guardrail_status_cannot_claim_built(self):
        self.assertFalse(self.has(self.run_check().errors, "护栏状态"))
        p = self.out / "README.md"
        t = p.read_text(encoding="utf-8")
        line = next(l for l in t.splitlines() if "护栏状态" in l)
        p.write_text(t.replace(line, "> **护栏状态：已建立**，P0 测试 6 个全部通过"), encoding="utf-8")
        self.assertTrue(self.has(self.run_check().errors, "护栏状态写成了「已建立」"))

    def test_guardrail_status_missing(self):
        p = self.out / "README.md"
        t = p.read_text(encoding="utf-8")
        line = next(l for l in t.splitlines() if "护栏状态" in l)
        p.write_text(t.replace(line + "\n", ""), encoding="utf-8")
        self.assertTrue(self.has(self.run_check().warnings, "没有「护栏状态」"))


class TestOtherModes(Base):
    def test_phase_d_docs(self):
        self.phase("D")
        self.assertTrue(self.has(self.run_check().warnings, "1-framework-map.md"))
        self.tpl("plan-oss.md", f"{O}/2-plan.md")
        self.write(f"{O}/1-framework-map.md", "# 框架地图\n")
        r = self.run_check()
        self.assertTrue(self.has(r.passed, "阶段 D 的文档齐全"))
        self.assertFalse(self.has(r.errors, "约定以外"))

    def test_phase_e_docs(self):
        self.phase("E")
        self.write(f"{O}/1-oss-map.md", "# 项目地图\n")
        self.tpl("contributions.md", f"{O}/2-contributions.md")
        self.assertTrue(self.has(self.run_check().passed, "阶段 E 的文档齐全"))


class TestApplyAndReadme(Base):
    HEAD = "# x\n由 legacy-takeover 生成\n当前阶段：A\n运行方式：只读\n## 一、做了什么\n## 二、需要你做的事\n## 四、产出物一览\n"

    def setUp(self):
        super().setUp()
        self.phase("A")
        self.phase_a_done()

    def test_apply_sh_required(self):
        (self.out / "apply" / "apply.sh").unlink()
        self.assertTrue(self.has(self.run_check().errors, "没有 apply.sh"))

    def test_readme_must_cover_every_file(self):
        self.write(f"{O}/README.md", self.HEAD + "- 1-project-map.md\n")
        msg = next(m for m in self.run_check().errors if "没有说明这些产出物" in m)
        self.assertIn("diagrams/architecture.svg", msg)
        self.assertNotIn("1-project-map.md", msg)

    def test_directory_mention_covers_files(self):
        self.write(f"{O}/README.md", self.HEAD + "- 1-project-map.md\n- diagrams/\n- apply/\n")
        self.assertTrue(self.has(self.run_check().passed, "覆盖了产出目录里的全部文件"))

    def test_screenshots_need_directory_mention(self):
        self.write(f"{O}/screenshots/{F}/before-a.png", "x")
        self.write(f"{O}/README.md", self.HEAD + "- 1-project-map.md\n- diagrams/\n- apply/\n")
        self.assertTrue(self.has(self.run_check().errors, "screenshots"))
        self.write(f"{O}/README.md", self.HEAD + "- 1-project-map.md\n- diagrams/\n- apply/\n- screenshots/\n")
        self.assertFalse(self.has(self.run_check().errors, "没有说明"))

    def test_readme_missing_section(self):
        self.write(f"{O}/README.md", "# x\n由 legacy-takeover 生成\n## 一、做了什么\n")
        self.assertTrue(self.has(self.run_check().errors, "缺少「需要你做的事」"))

    def test_template_readme_sections(self):
        self.assertFalse(self.has(self.run_check().errors, "README.md 缺少"))


class TestApplyScript(Base):
    def test_copies_and_skips_existing(self):
        script = self.root / O / "apply" / "apply.sh"
        script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(TEMPLATES / "apply.sh", script)
        self.write(f"{O}/apply/CLAUDE.md", "new\n")
        self.write(f"{O}/apply/.claude/skills/x/SKILL.md", "skill\n")
        self.write("CLAUDE.md", "old\n")

        dry = subprocess.run(["bash", str(script), "--dry-run"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse((self.root / ".claude/skills/x/SKILL.md").exists())

        res = subprocess.run(["bash", str(script)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual((self.root / ".claude/skills/x/SKILL.md").read_text(), "skill\n")
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "old\n")
        self.assertIn("= CLAUDE.md", res.stdout)


class TestDevEnvTemplate(Base):
    def test_syntax_and_usage(self):
        script = TEMPLATES / "dev-env.sh"
        self.assertEqual(subprocess.run(["bash", "-n", str(script)]).returncode, 0)
        res = subprocess.run(["bash", str(script)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 2)
        self.assertIn("install|start|stop|status", res.stderr)


class TestSecrets(Base):
    def test_token_detected_without_echo(self):
        self.phase("A")
        fake = "ghp_" + "A" * 36
        self.write(f"{O}/{ct.DEV_SETUP}", f"# 环境\n\ntoken {fake}\n")
        hits = [m for m in self.run_check().errors if "疑似密钥" in m]
        self.assertEqual(len(hits), 1)
        self.assertIn(f"{ct.DEV_SETUP}:3", hits[0])
        self.assertNotIn(fake, hits[0])

    def test_placeholders_not_flagged(self):
        self.phase("A")
        self.write(f"{O}/{ct.DEV_SETUP}", "password: ${DB_PASSWORD}\napi_key=<需用户提供>\npassword=123456\n")
        self.assertFalse(self.has(self.run_check().errors, "疑似密钥"))


class TestCli(Base):
    def test_exit_codes(self):
        self.assertEqual(ct.main(["--root", str(self.root)]), 1)
        self.phase("A")
        self.assertEqual(ct.main(["--root", str(self.root)]), 0)


if __name__ == "__main__":
    unittest.main()
