# check_takeover.py：交付物自检

只读，不改任何文件。需要 Python 3.8 以上，只依赖标准库。智能体在每个阶段结束时会自动运行它，用户也可以随时手动运行。

```bash
python3 <技能目录>/scripts/check_takeover.py --root <项目根目录>
```

有「错误」时退出码为 1；只有「提醒」或者全部通过时为 0。

## 检查什么

所有产出都在 `<项目根>/make-skill-legacy-takeover-output/` 下。目录名冲突时用 `-2` 后缀。总说明 `README.md` 兼做进度文件，「当前阶段：A–E」和「运行方式：只读 / 运行」两行从它的进度一节读取。

某个阶段的产出缺失时：还在这个阶段，只给「提醒」；已经进入后面的阶段，就算「错误」。

| 项 | 规则 | 级别 |
| --- | --- | --- |
| 起点 | 有产出目录，里面有由 legacy-takeover 生成的 `README.md` | 错误 |
| **只有约定的文件** | 顶层只允许 `README.md`、`1-project-map.md`、`2-dev-setup.md`、`3-test-guard.md`、`4-change-*.md`（二次开发、提 PR 模式各自的两份文档）；`diagrams/` 只允许约定的几种 SVG；`scripts/` 只允许 `dev-env.sh` 和 `docker-compose.dev.yml`；`apply/`、`screenshots/` 不限 | 错误 |
| 阶段 A | `1-project-map.md` 十节齐全（应用架构、技术架构、模块说明、风险地带、模块依赖、外部依赖、接口清单、数据模型、时序、互校）；`diagrams/` 下 `app-architecture.svg`、`architecture.svg`、`module-deps.svg`、`data-model-er.svg`；`apply/CLAUDE.md`；`apply/.claude/skills/docs-auto-sync/` | 随阶段 |
| 时序图 | `diagrams/sequence-*.svg` 至少一张 | 提醒 |
| 接口清单 | 小节开头写了扫描来源和数量 | 提醒 |
| CLAUDE.md | `apply/CLAUDE.md` 不超过 300 行；「禁区」「历史包袱」两节都在；前五节齐全 | 错误 / 提醒 |
| 禁区 / 历史包袱 | 还是占位时只给提醒：按设计由人填写，AI 不填 | 提醒 |
| 阶段 B | `2-dev-setup.md` 五节、`3-test-guard.md` 五节、`scripts/dev-env.sh`、env-bootstrap、`apply/` 下的 CI 配置 | 随阶段 |
| 只读方式 | `2-dev-setup.md` 要标「未实测」 | 提醒 |
| 运行方式 | 测试护栏有「实际运行结果」，冒烟结果不是「未执行」 | 随阶段 |
| 风险地带 | 风险清单 ≤15 条（错误）；进入阶段 C 以后，「测试兜底」还写着「待阶段 B」的给提醒 | 错误 / 提醒 |
| 清单上限 | 核心链路 ≤8；测试缺口总数 ≤20，P0 ≤10（少于 5 给提醒），P1 ≤10；补测试计划每批 ≤3 | 错误 |
| 改造文档 | `4-change-<feature>.md` 有「一、需求」「二、方案」两部分：需求六维齐全，边界场景 ≥8 条且每条有依据；方案七节齐全，第 7 节每条都有「最终决策」。残留「待产品决策」或决策点空着时，实现前给提醒、实现后算错误；还要有 `diagrams/change-<feature>.svg` 和「三、验证」 | 错误 / 提醒 |
| 独立 review | 方案写完（决策点有内容）却没有对象为「方案」的 review 记录，给提醒；有了提交却没有对象为「代码」的记录，给提醒；严重程度为高、处理栏为空的，给提醒 | 提醒 |
| **护栏状态** | 总说明开头要有「护栏状态」（阶段 B 起，缺了给提醒）；只读方式下写成「已建立」算错误 | 错误 / 提醒 |
| **只读不改代码** | 只读方式下，改造点表的「提交」列不能有内容 | 错误 |
| **图全部是 SVG** | 每个 `.svg` 都能被 XML 解析，根元素是 svg；`diagrams/` 里不允许出现位图；产出的 Markdown 里不允许内嵌 Mermaid 代码 | 错误 |
| **apply/** | 里面有文件时，必须附带 `apply.sh` | 错误 |
| **总说明** | `README.md` 有「做了什么」「需要你做的事」「产出物」三节；产出目录里的**每个文件**都被提到（写出路径或所在目录即可；截图只要求提到 `screenshots/`） | 错误 |
| 疑似密钥 | 扫描产出目录下的 `.md` `.yml` `.sh`；只报文件和行号，不回显内容 | 错误 |

表格和小节的解析依赖模板里的标题和表头（「链路」「优先级」「缺口」「场景」「依据」「提交」「最终决策」，以及各文档的小节名）。改模板时要同步改脚本。

## 测试

```bash
python3 -m unittest discover -s scripts/tests -v
```

测试里也覆盖了两个脚本模板：`templates/apply.sh` 的 `--dry-run` 不复制任何文件、已存在的文件跳过不覆盖；`templates/dev-env.sh` 语法正确、不带参数时打印用法。
