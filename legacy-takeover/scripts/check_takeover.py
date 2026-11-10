#!/usr/bin/env python3
"""legacy-takeover 自检：只读，核对产出目录里的交付物是否齐全、是否守住约束。

用法：
    python3 check_takeover.py --root <项目根目录>

所有产出都在 <项目根>/make-skill-legacy-takeover-output/ 下（目录冲突时为 -2 后缀）。
总说明 README.md 兼做进度文件：「当前阶段：A-E」「运行方式：只读 / 运行」两行从这里读取。
有「错误」时退出码为 1；只有「提醒」或全部通过时为 0。
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

OUT_NAME = "make-skill-legacy-takeover-output"
MARKER = "legacy-takeover"

CONTEXT_MAX_LINES = 300
CRITICAL_PATHS_MAX = 8
GAPS_TOTAL_MAX = 20
GAPS_P0_MIN, GAPS_P0_MAX, GAPS_P1_MAX = 5, 10, 10
BATCH_MAX = 3
EDGE_CASES_MIN = 8
RISKS_MAX = 15
REVIEW_VIEWS = ("兼容性", "安全", "性能")

PLACEHOLDER = "待人工填写"
PENDING_HUMAN = "待确认"
UNRESOLVED = ("待审核", "待定", "TBD")
PRODUCT_PENDING = "待产品决策"
PHASES = "ABCDE"
READONLY, RUN = "只读", "运行"

PROJECT_MAP = "1-project-map.md"
DEV_SETUP = "2-dev-setup.md"
TEST_GUARD = "3-test-guard.md"
CHANGE_GLOB = "4-change-*.md"
OTHER_MODE_DOCS = {"D": ("1-framework-map.md", "2-plan.md"), "E": ("1-oss-map.md", "2-contributions.md")}

# 只允许这些文件：产出要少而精，内容写进对应文档的小节，不另建文件
ALLOWED_TOP = ("README.md", PROJECT_MAP, DEV_SETUP, TEST_GUARD, CHANGE_GLOB,
               *OTHER_MODE_DOCS["D"], *OTHER_MODE_DOCS["E"])
PHASE_A_DIAGRAMS = ("app-architecture.svg", "architecture.svg", "module-deps.svg", "data-model-er.svg")
ALLOWED_DIAGRAMS = (*PHASE_A_DIAGRAMS, "sequence-*.svg", "change-*.svg",
                    "boundary.svg", "run-chain.svg")
ALLOWED_SCRIPTS = ("dev-env.sh", "docker-compose.dev.yml")
FREE_DIRS = ("apply", "screenshots")

README_SECTIONS = ("做了什么", "需要你做的事", "产出物")
PROJECT_MAP_SECTIONS = ("应用架构", "技术架构", "模块说明", "风险地带", "模块依赖", "外部依赖", "接口清单", "数据模型", "时序", "互校")
DEV_SETUP_SECTIONS = ("依赖清单", "新人上手", "安装记录", "启动记录", "冒烟结果")
TEST_GUARD_SECTIONS = ("核心链路", "测试现状", "测试缺口", "补测试计划", "CI")
REQUIREMENT_SECTIONS = ("业务目标", "用户场景", "接口契约", "边界场景", "老项目约束", "不在本期范围")
SOLUTION_SECTIONS = ("概要", "涉及链路", "改造点", "流程图", "影响范围", "步骤", "决策点")
PART_REQ, PART_SOL, PART_VERIFY = "一、需求", "二、方案", "三、验证"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[^\s'\"<>{}$]{12,}"),
]


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    passed: list = field(default_factory=list)

    def error(self, m): self.errors.append(m)
    def warn(self, m): self.warnings.append(m)
    def ok(self, m): self.passed.append(m)


@dataclass
class Ctx:
    root: Path
    out: Path
    phase: str
    mode: str
    r: Report

    def sev(self, owner: str):
        """某阶段的产出缺失：还在这个阶段只算提醒，已经进入后面的阶段算错误。"""
        if PHASES.index(self.phase) > PHASES.index(owner):
            return self.r.error
        return self.r.warn


# ---------- Markdown 解析 ----------

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def read_lines(path: Path):
    return path.read_text(encoding="utf-8").splitlines()


def strip_code_blocks(lines):
    out, in_code = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
            out.append("")
            continue
        out.append("" if in_code else line)
    return out


def find_section(lines, keyword):
    lines = strip_code_blocks(lines)
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and keyword in m.group(2):
            level, body = len(m.group(1)), []
            for nxt in lines[i + 1:]:
                n = HEADING.match(nxt)
                if n and len(n.group(1)) <= level:
                    break
                body.append(nxt)
            return body
    return None


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(line):
    return bool(re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", line.strip()))


def tables(lines):
    result, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            header, rows, j = split_row(lines[i]), [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                row = split_row(lines[j])
                if any(row):
                    rows.append(row)
                j += 1
            result.append((header, rows))
            i = j
        else:
            i += 1
    return result


def table_with(lines, column):
    for header, rows in tables(lines or []):
        for k, h in enumerate(header):
            if column in h:
                return header, rows, k
    return None


def filled(rows):
    return [r for r in rows if any(c for c in r[1:])]


def cell(row, idx):
    return row[idx] if idx < len(row) else ""


def prose(lines):
    return "\n".join(l for l in strip_code_blocks(lines)
                     if not HEADING.match(l) and not l.lstrip().startswith(">"))


def section_has_content(body):
    return any(s.strip() and not s.strip().startswith("<!--") and PLACEHOLDER not in s for s in body)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


# ---------- 定位 ----------

def output_dir(root: Path):
    for name in (OUT_NAME, OUT_NAME + "-2"):
        readme = root / name / "README.md"
        if readme.exists() and MARKER in readme.read_text(encoding="utf-8"):
            return root / name
    return None


def read_progress(out: Path):
    text = (out / "README.md").read_text(encoding="utf-8")
    phase = re.search(r"当前阶段[:：]\s*([A-Ea-e])", text)
    mode = re.search(r"运行方式[:：]\s*(只读|运行)\s*$", text, re.M)
    return (phase.group(1).upper() if phase else ""), (mode.group(1) if mode else "")


# ---------- 文件清单：只允许约定的文件 ----------

def check_layout(c: Ctx):
    extra = []
    for f in sorted(c.out.rglob("*")):
        if not f.is_file() or f.name == ".DS_Store":
            continue
        parts = f.relative_to(c.out).parts
        if len(parts) == 1:
            ok = matches(parts[0], ALLOWED_TOP)
        elif parts[0] == "diagrams":
            ok = len(parts) == 2 and matches(parts[1], ALLOWED_DIAGRAMS)
        elif parts[0] == "scripts":
            ok = len(parts) == 2 and matches(parts[1], ALLOWED_SCRIPTS)
        else:
            ok = parts[0] in FREE_DIRS
        if not ok:
            extra.append(rel(f, c.out))
    if extra:
        c.r.error("产出目录里有约定以外的文件（内容应写进对应文档的小节，不另建文件）："
                  + ", ".join(extra[:10]) + (" 等" if len(extra) > 10 else ""))
    else:
        c.r.ok("产出目录只有约定的文件")


# ---------- 图：全部 SVG ----------

def check_svgs(c: Ctx):
    bad = 0
    for svg in sorted(c.out.rglob("*.svg")):
        try:
            tag = ET.parse(svg).getroot().tag
            if not tag.endswith("svg"):
                raise ValueError(tag)
        except (ET.ParseError, ValueError):
            c.r.error(f"{rel(svg, c.root)} 不是合法的 SVG（XML 解析失败或根元素不是 svg）")
            bad += 1
    diagrams = c.out / "diagrams"
    if diagrams.is_dir():
        for f in diagrams.rglob("*"):
            if f.suffix.lower() in IMAGE_EXT:
                c.r.error(f"{rel(f, c.root)}：图必须是 SVG 文件")
    for md in c.out.rglob("*.md"):
        if any(l.strip().lower().startswith("```mermaid") for l in read_lines(md)):
            c.r.error(f"{rel(md, c.root)} 内嵌了 Mermaid 代码：图必须画成 SVG 文件，用图片链接引用")
    if not bad:
        c.r.ok("SVG 全部可解析")


def check_sections(path: Path, sections, report):
    lines = read_lines(path)
    missing = [s for s in sections if find_section(lines, s) is None]
    if missing:
        report(f"{path.name} 缺少这些小节：{'、'.join(missing)}")
    return lines


# ---------- 阶段 A ----------

def check_phase_a(c: Ctx):
    sev = c.sev("A")
    pm = c.out / PROJECT_MAP
    if not pm.exists():
        sev(f"缺少 {PROJECT_MAP}（项目地图）")
    else:
        lines = check_sections(pm, PROJECT_MAP_SECTIONS, sev)
        check_risks(c, lines)
        api = find_section(lines, "接口清单")
        if api is not None and not re.search(r"来源|扫描", "\n".join(api[:6])):
            c.r.warn(f"{PROJECT_MAP}「接口清单」开头没有写扫描来源和数量，无法核对是否漏扫")
    diagrams = c.out / "diagrams"
    missing = [n for n in PHASE_A_DIAGRAMS if not (diagrams / n).exists()]
    if missing:
        sev(f"阶段 A 缺少图：{', '.join('diagrams/' + n for n in missing)}")
    elif pm.exists():
        c.r.ok("阶段 A：项目地图和四张主图齐全")
    if not (diagrams.is_dir() and list(diagrams.glob("sequence-*.svg"))):
        c.r.warn("没有核心接口时序图 diagrams/sequence-<名>.svg")

    apply = c.out / "apply"
    ctx = apply / "CLAUDE.md"
    if not ctx.exists():
        sev("缺少 apply/CLAUDE.md")
    else:
        check_context(ctx, c)
    if not (apply / ".claude" / "skills" / "docs-auto-sync" / "SKILL.md").exists():
        sev("缺少 apply/.claude/skills/docs-auto-sync/SKILL.md")


def check_risks(c: Ctx, lines):
    risks = find_section(lines, "风险地带")
    found = table_with(find_section(risks or [], "风险清单") or risks, "类型")
    if not found:
        return
    header, rows, _ = found
    rows = filled(rows)
    if len(rows) > RISKS_MAX:
        c.r.error(f"{PROJECT_MAP}「风险地带」有 {len(rows)} 条，超过 {RISKS_MAX} 条")
    cover = next((k for k, h in enumerate(header) if "测试兜底" in h), None)
    if cover is not None and PHASES.index(c.phase) > PHASES.index("B"):
        stale = [row[0] for row in rows if "待阶段 B" in cell(row, cover)]
        if stale:
            c.r.warn(f"{PROJECT_MAP}「风险地带」的测试兜底还没回填（B9 之后要补）：{', '.join(stale)}")


def check_context(ctx: Path, c: Ctx):
    name = rel(ctx, c.root)
    lines = read_lines(ctx)
    if len(lines) > CONTEXT_MAX_LINES:
        c.r.error(f"{name} 有 {len(lines)} 行，超过 {CONTEXT_MAX_LINES} 行上限（索引 + 常识，不是规则仓库）")
    for sec in ("禁区", "历史包袱"):
        body = find_section(lines, sec)
        if body is None:
            c.r.error(f"{name} 缺少「{sec}」一节")
        elif not section_has_content(body):
            c.r.warn(f"{name}「{sec}」等人填写（AI 不填；线索见总说明「疑点」）")
        else:
            c.r.ok(f"{name}「{sec}」已有内容")
    for sec in ("项目定位", "核心架构", "关键模块", "关键约定", "怎么跑"):
        if find_section(lines, sec) is None:
            c.r.warn(f"{name} 缺少「{sec}」一节")


# ---------- 阶段 B ----------

def check_phase_b(c: Ctx):
    if PHASES.index(c.phase) < PHASES.index("B"):
        return
    sev = c.sev("B")
    apply = c.out / "apply"
    missing = [n for n in (DEV_SETUP, TEST_GUARD) if not (c.out / n).exists()]
    if not (c.out / "scripts" / "dev-env.sh").exists():
        missing.append("scripts/dev-env.sh")
    if not (apply / ".claude" / "skills" / "env-bootstrap" / "SKILL.md").exists():
        missing.append("apply/.claude/skills/env-bootstrap/SKILL.md")
    wf = apply / ".github" / "workflows"
    if not (list(wf.glob("*.y*ml")) if wf.is_dir() else []) and \
            not any((apply / f).exists() for f in (".gitlab-ci.yml", "Jenkinsfile")):
        missing.append("apply/ 下的 CI 配置")
    if missing:
        sev(f"阶段 B 产出缺少：{', '.join(missing)}")
    else:
        c.r.ok("阶段 B：环境手册、测试护栏、环境脚本、env-bootstrap、CI 配置齐全")

    ds = c.out / DEV_SETUP
    if ds.exists():
        lines = check_sections(ds, DEV_SETUP_SECTIONS, sev)
        if c.mode == READONLY and "未实测" not in "\n".join(lines):
            c.r.warn(f"只读方式下 {DEV_SETUP} 没有标「未实测」：步骤没在本机跑过，要让读者知道")
        smoke = find_section(lines, "冒烟结果")
        if c.mode == RUN and smoke is not None and "未执行" in "\n".join(smoke):
            sev(f"运行方式下 {DEV_SETUP}「冒烟结果」还是「未执行」（B4）")
    tg = c.out / TEST_GUARD
    if tg.exists():
        lines = check_sections(tg, TEST_GUARD_SECTIONS, sev)
        actual = find_section(lines, "实际运行结果")
        if c.mode == RUN and (actual is None or "未运行" in "\n".join(actual)):
            sev(f"运行方式下 {TEST_GUARD} 没有「实际运行结果」（B8 没跑测试）")
        check_guardrail_limits(lines, c.r)


def check_guardrail_limits(lines, r: Report):
    found = table_with(find_section(lines, "核心链路"), "链路")
    if found:
        n = len(filled(found[1]))
        if n > CRITICAL_PATHS_MAX:
            r.error(f"核心链路有 {n} 条，超过 {CRITICAL_PATHS_MAX} 条")
        else:
            r.ok(f"核心链路 {n} 条")
    gaps = find_section(lines, "测试缺口")
    if gaps is not None:
        found = table_with(find_section(gaps, "明细") or gaps, "优先级")
        if found:
            _, rows, idx = found
            rows = filled(rows)
            prios = [cell(row, idx).upper() for row in rows]
            p0, p1, total = prios.count("P0"), prios.count("P1"), len(rows)
            if total > GAPS_TOTAL_MAX:
                r.error(f"测试缺口共 {total} 项，超过 {GAPS_TOTAL_MAX} 项")
            if p0 > GAPS_P0_MAX:
                r.error(f"测试缺口有 {p0} 个 P0，超过 {GAPS_P0_MAX} 个，需要再砍一刀")
            elif total and p0 < GAPS_P0_MIN:
                r.warn(f"测试缺口只有 {p0} 个 P0，确认核心链路都考虑到了")
            if p1 > GAPS_P1_MAX:
                r.error(f"测试缺口有 {p1} 个 P1，超过 {GAPS_P1_MAX} 个")
            if total - p0 - p1:
                r.warn(f"测试缺口有 {total - p0 - p1} 项优先级不是 P0 / P1")
            r.ok(f"测试缺口：P0 {p0}，P1 {p1}，共 {total}")
    found = table_with(find_section(lines, "补测试计划"), "缺口")
    if found:
        _, rows, idx = found
        for row in filled(rows):
            n = len(re.findall(r"G\d+", cell(row, idx)))
            if n > BATCH_MAX:
                r.error(f"补测试计划批次 {row[0]} 含 {n} 个缺口，超过每批 {BATCH_MAX} 个")


# ---------- 阶段 C ----------

def check_changes(c: Ctx):
    for doc in sorted(c.out.glob(CHANGE_GLOB)):
        check_change(c, doc)


def check_change(c: Ctx, doc: Path):
    r, tag = c.r, doc.name
    feature = doc.stem[len("4-change-"):]
    lines = read_lines(doc)
    req = find_section(lines, PART_REQ)
    sol = find_section(lines, PART_SOL)
    for part, body in ((PART_REQ, req), (PART_SOL, sol)):
        if body is None:
            r.error(f"{tag} 缺少「{part}」部分")

    found = table_with(find_section(sol or [], "改造点"), "提交")
    started = bool(found and any(cell(row, found[2]) for row in filled(found[1])))
    if started and c.mode == READONLY:
        r.error(f"{tag} 改造点已经填了提交号，但当前是只读方式：只读方式不改代码")
    decisions = table_with(find_section(sol or [], "决策点"), "最终决策")
    sol_written = bool(decisions and filled(decisions[1]))

    if req is not None:
        for s in REQUIREMENT_SECTIONS:
            if find_section(req, s) is None:
                r.error(f"{tag} 需求部分缺少「{s}」一节")
        found = table_with(find_section(req, "边界场景"), "场景")
        if found is not None:
            rows = filled(found[1])
            if len(rows) < EDGE_CASES_MIN:
                r.error(f"{tag} 边界场景只有 {len(rows)} 条，至少 {EDGE_CASES_MIN} 条")
            basis = next((k for k, h in enumerate(found[0]) if "依据" in h), None)
            if basis is not None and any(not cell(row, basis) for row in rows):
                r.error(f"{tag} 有边界场景没写依据")
        if PRODUCT_PENDING in prose(req):
            (r.error if sol_written else r.warn)(f"{tag} 还有「{PRODUCT_PENDING}」没落定（C2 未完成）")
    pending = prose(lines).count(PENDING_HUMAN)
    if pending:
        r.warn(f"{tag} 有 {pending} 处 AI 推荐等人确认")

    if sol is None:
        return
    for s in SOLUTION_SECTIONS:
        if find_section(sol, s) is None:
            r.error(f"{tag} 方案部分缺少「{s}」一节")
    if not (c.out / "diagrams" / f"change-{feature}.svg").exists():
        r.warn(f"{tag} 缺少改造链路与流程图 diagrams/change-{feature}.svg")
    if find_section(lines, PART_VERIFY) is None:
        r.warn(f"{tag} 缺少「{PART_VERIFY}」部分（只读方式写待验证清单，运行方式写执行记录）")
    check_review(c, tag, lines, sol_written, started)
    if decisions is None:
        if find_section(sol, "决策点") is not None:
            r.error(f"{tag} 决策点缺少「最终决策」列")
        return
    _, rows, idx = decisions
    rows = filled(rows) or rows
    open_rows = [row[0] for row in rows
                 if not cell(row, idx) or any(u in cell(row, idx) for u in UNRESOLVED)]
    human = [row[0] for row in rows if PENDING_HUMAN in cell(row, idx)]
    if open_rows:
        (r.error if started else r.warn)(f"{tag} 决策点没有落定：{', '.join(open_rows)}")
    if human:
        r.warn(f"{tag} 决策点等人确认：{', '.join(human)}")
    if rows and not open_rows and not human:
        r.ok(f"{tag} 决策点已全部确认")


def check_review(c: Ctx, tag, lines, sol_written, started):
    found = table_with(find_section(lines, "独立 review"), "视角")
    done = {"方案": False, "代码": False}
    if found:
        header, rows, view = found
        obj = next((k for k, h in enumerate(header) if "对象" in h), 0)
        level = next((k for k, h in enumerate(header) if "严重" in h), None)
        handle = next((k for k, h in enumerate(header) if "处理" in h), None)
        for row in filled(rows):
            if cell(row, view) not in REVIEW_VIEWS:
                continue
            for k in done:
                if k in cell(row, obj):
                    done[k] = True
            if level is not None and handle is not None and cell(row, level) == "高" and not cell(row, handle):
                c.r.warn(f"{tag} 独立 review 的高风险问题还没处理：{cell(row, obj)}·{cell(row, view)}")
    if sol_written and not done["方案"]:
        c.r.warn(f"{tag} 方案还没做独立 review（C9c）")
    if started and not done["代码"]:
        c.r.warn(f"{tag} 代码还没做独立 review（C18b）")


def check_other_modes(c: Ctx):
    missing = [d for d in OTHER_MODE_DOCS[c.phase] if not (c.out / d).exists()]
    if missing:
        c.r.warn(f"阶段 {c.phase} 还没有：{', '.join(missing)}")
    else:
        c.r.ok(f"阶段 {c.phase} 的文档齐全")


# ---------- apply/ 与总说明 ----------

def check_apply(c: Ctx):
    apply = c.out / "apply"
    if not apply.is_dir():
        return
    files = [f for f in apply.rglob("*") if f.is_file() and f.name != "apply.sh"]
    if files and not (apply / "apply.sh").exists():
        c.r.error("apply/ 里有文件，但没有 apply.sh（从 templates/apply.sh 复制）")


def check_readme(c: Ctx):
    readme = c.out / "README.md"
    text = readme.read_text(encoding="utf-8")
    lines = text.splitlines()
    for sec in README_SECTIONS:
        if find_section(lines, sec) is None:
            c.r.error(f"README.md 缺少「{sec}」一节")
    status = re.search(r"护栏状态[^\n]*", text)
    if status is None:
        if PHASES.index(c.phase) >= PHASES.index("B"):
            c.r.warn("README.md 开头没有「护栏状态」：要写清护栏是只有计划，还是已经建立")
    elif c.mode == READONLY and "已建立" in status.group(0) and "只有计划" not in status.group(0):
        c.r.error("只读方式下 README.md 的护栏状态写成了「已建立」：只读方式没有跑过测试，护栏只是计划")
    missing = set()
    for f in sorted(c.out.rglob("*")):
        if not f.is_file() or f == readme or f.name == ".DS_Store":
            continue
        parts = f.relative_to(c.out).parts
        if parts[0] == "screenshots":  # 截图只要求提到目录
            parts = parts[:1]
        rp = "/".join(parts)
        candidates = {rp} | {"/".join(parts[:i]) + "/" for i in range(1, len(parts) + 1)}
        if not any(x in text for x in candidates):
            missing.add(rp)
    if missing:
        missing = sorted(missing)
        c.r.error(f"README.md 没有说明这些产出物：{', '.join(missing[:10])}" + (" 等" if len(missing) > 10 else ""))
    else:
        c.r.ok("README.md 覆盖了产出目录里的全部文件")


def check_secrets(c: Ctx):
    hits = 0
    for path in c.out.rglob("*"):
        if path.suffix.lower() not in (".md", ".yml", ".yaml", ".sh") or not path.is_file():
            continue
        try:
            lines = read_lines(path)
        except (UnicodeDecodeError, OSError):
            continue
        for no, line in enumerate(lines, 1):
            if any(p.search(line) for p in SECRET_PATTERNS):
                c.r.error(f"疑似密钥：{rel(path, c.root)}:{no}（不回显内容）")
                hits += 1
    if not hits:
        c.r.ok("未发现疑似密钥")


def run(root: Path) -> Report:
    r = Report()
    out = output_dir(root)
    if out is None:
        r.error(f"没有 {OUT_NAME}/README.md（由 {MARKER} 生成的总说明）：流程还没开始，或总说明丢失")
        return r
    phase, mode = read_progress(out)
    if not phase:
        r.warn("README.md 的进度里没有「当前阶段：A-E」这一行，按阶段 A 检查")
        phase = "A"
    if not mode:
        r.warn("README.md 的进度里没有「运行方式：只读 / 运行」这一行，按只读方式检查")
        mode = READONLY
    r.ok(f"产出目录 {out.name}，当前阶段 {phase}，运行方式 {mode}")
    c = Ctx(root, out, phase, mode, r)
    if phase in "ABC":
        check_phase_a(c)
        check_phase_b(c)
        check_changes(c)
    else:
        check_other_modes(c)
    check_layout(c)
    check_svgs(c)
    check_apply(c)
    check_readme(c)
    check_secrets(c)
    return r


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="legacy-takeover 自检（只读）")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    args = parser.parse_args(argv)
    r = run(Path(args.root).resolve())
    for m in r.passed:
        print(f"[通过] {m}")
    for m in r.warnings:
        print(f"[提醒] {m}")
    for m in r.errors:
        print(f"[错误] {m}")
    print(f"\n错误 {len(r.errors)} 项，提醒 {len(r.warnings)} 项，通过 {len(r.passed)} 项")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
