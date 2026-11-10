# <项目名> · 接手与改造说明

> 由 legacy-takeover 生成　·　模式：接手 / 改造 / 二次开发 / 提 PR　·　运行方式：只读（默认）/ 运行
> 日期：YYYY-MM-DD　·　基线提交：`<hash>`　·　本次本地提交：0 个　·　自检：错误 0，提醒 N
> **护栏状态：只有计划，未实测**——没有跑过测试、没有补测试，改代码前必须先说「跑起来」把护栏建起来 / **已建立**：P0 测试 N 个全部通过，测试健康度 <绿 / 黄 / 红>，CI 配置待推送

这个文件夹里是这次工作的全部产出，先读这一页。只读方式下，AI 只读了代码、写了文档，没有安装、启动、运行项目，也没有改动项目里的任何文件。

![应用架构图](diagrams/app-architecture.svg)

## 一、做了什么

### 阶段 A　摸项目（用时 约 N 分钟）

- 做了：<读了哪些文件、扫了多少个模块和入口、画了几张图>
- 关键发现：<比如：3 个业务域、4 个后端模块，无循环依赖；2 个模块改动风险高；共 N 个接口，其中 M 个对外；ER 图补了 K 条逻辑关联；疑点 N 条>
- 跳过或卡住：<无 / 哪一步、原因>

### 阶段 B　建护栏（用时 约 N 分钟）

- 做了：<只读：依赖清单、环境脚本、上手步骤（未实测）、核心链路、测试现状、缺口、补测试计划、CI 配置 / 运行：另外装了依赖、启动、冒烟、跑测试、补了 N 个 P0 测试>
- 关键发现：<比如：核心链路 6 条，3 条没有测试；测试健康度黄（78%，运行方式才有）>
- 跳过或卡住：<比如：只读方式，未运行项目；Redis 需要 sudo 安装，命令见第二节>

### 阶段 C　做改造：<需求名>（用时 约 N 分钟）

- 做了：<现状核对、需求、方案；运行方式下另有后端 N 批、前端、回灌>
- 关键发现：<比如：复用的老方法有打点副作用，方案改为抽内部方法>
- 跳过或卡住：<比如：只读方式，只出方案，没有改代码>

## 二、需要你做的事

> 按重要程度排序。这些是 AI 做不了的事，跳过它们是效果不好的头号原因。

1. **写 CLAUDE.md 的「禁区」「历史包袱」**：线索见第六节「疑点」（共 N 条）。这两节写得深不深，决定了 CLAUDE.md 有没有用。
2. **确认 apply/ 里的文件，再运行 apply.sh**：见第五节。
3. （改造）**打开产品点一遍，确认这个功能现在是否已经存在**：AI 扫代码发现不了已存在的功能。AI 的核对结论见 `4-change-<feature>.md` 开头。
4. （想实际跑起来时）对 AI 说「跑起来」：会安装依赖、启动项目、冒烟、跑测试、补测试；改造需求会按方案改代码。老项目在新环境里不一定跑得起来，所以默认不跑。
5. 

## 三、待你确认的 AI 推荐

| 出处 | 内容 | AI 推荐 | 理由 |
| --- | --- | --- | --- |
| 4-change-<feature>.md 需求第 1 节 | 业务目标 | | |
| 4-change-<feature>.md 独立 review | 没有采纳的高风险问题 | | |

## 四、产出物一览

> 文件夹里的每个文件都在这里，写清是什么、有什么用、什么时候用。

| 文件 | 是什么 | 作用 / 什么时候用 |
| --- | --- | --- |
| [README.md](README.md) | 本说明 | 了解做了什么、要你做什么、每个产出的作用；中断后说「继续」，AI 从第八节的进度接着做 |
| [1-project-map.md](1-project-map.md) | 项目地图 | 应用架构、技术架构、模块说明、风险地带、模块依赖、外部依赖、接口清单、数据模型、核心时序。新人入门、改模块改接口改表之前先查，尤其是「风险地带」；docs-auto-sync 的比对基准 |
| [2-dev-setup.md](2-dev-setup.md) | 环境手册 | 依赖清单、上手步骤、安装与启动记录、冒烟结果。搭环境、启动报错时看 |
| [3-test-guard.md](3-test-guard.md) | 测试护栏 | 核心链路、测试现状、缺口、补测试计划、CI。改造前判断风险、决定测哪里 |
| [4-change-<feature>.md](4-change-<feature>.md) | 改造：<需求名> | 需求、方案、验证。review 方案、拍板决策点、验收 |
| [diagrams/app-architecture.svg](diagrams/app-architecture.svg) | 应用架构图 | 系统做什么、有哪些业务域和模块、谁在用；新人和业务方先看这张 |
| [diagrams/architecture.svg](diagrams/architecture.svg) | 技术架构图（含外部依赖） | 分层、技术组件、中间件和外部服务；搭环境、评估升级风险 |
| [diagrams/module-deps.svg](diagrams/module-deps.svg) | 模块依赖图 | 改一个模块会牵动谁；循环依赖标红 |
| [diagrams/data-model-er.svg](diagrams/data-model-er.svg) | ER 图 | 任何涉及数据库的改造 |
| [diagrams/sequence-<名>.svg](diagrams/) | 核心接口时序图 | 复现 bug、对照改造前后的调用链 |
| [diagrams/change-<feature>.svg](diagrams/) | 改造链路与流程图 | review 方案时看改了哪些节点 |
| [scripts/dev-env.sh](scripts/dev-env.sh) | 环境脚本 | `install` / `start` / `stop` / `status`。只读方式下未实测 |
| [apply/](apply/) | 要放进项目的文件 | 见第五节 |

## 五、apply/ 里的文件（需要你放到项目里）

这些文件要放到项目里的固定位置才能起作用。AI 不会自己放。确认内容后，在项目根目录运行：

```bash
bash make-skill-legacy-takeover-output/apply/apply.sh --dry-run   # 先看会做什么
bash make-skill-legacy-takeover-output/apply/apply.sh             # 实际复制，已存在的跳过，不覆盖
```

| 文件 | 放到哪里 | 作用 | 为什么必须放在那里 |
| --- | --- | --- | --- |
| apply/CLAUDE.md | 项目根目录 | AI 每次启动都会读到的项目常识 | Claude Code 只自动读根目录的 CLAUDE.md |
| apply/.claude/skills/docs-auto-sync/SKILL.md | `.claude/skills/` | 改完代码后，检查文档和代码是否一致（只报告，不改文件） | 放在这里才会被发现 |
| apply/.claude/skills/env-bootstrap/SKILL.md | `.claude/skills/` | 一键准备本地环境 | 同上 |
| apply/.github/workflows/test.yml | `.github/workflows/` | 每次 push、提 PR 时自动跑测试 | CI 平台只认这个目录 |

项目里已有同名文件的，`apply.sh` 会跳过。合并建议：<没有就写「无」>。放完技能以后，要完全退出 Claude Code 再重新启动，技能才会生效。

## 六、疑点

代码回答不了、需要人去问的问题。「可能归属」为禁区或历史包袱的，是写 CLAUDE.md 这两节的主要线索。最多 20 条。

| 编号 | 问题 | 证据 | 为什么重要 | 可能归属 | 该问谁 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | | 文件:行号 / 提交号 | | 禁区 / 历史包袱 / 其他 | 原作者 / 产品 / 运维 / 对接方 | 待问 |

## 七、代码改动

只读方式：本次没有改动项目里的任何文件。

<运行方式时改成下表>

| 提交 | 内容 | 改动的文件 |
| --- | --- | --- |
| `<hash>` | takeover: test 批次1 G01 | `<测试文件>` |

- 所有提交都在当前分支本地，**没有推送**。review 后由你推送。
- 整体撤回到开工前：`git reset --hard <基线提交>`（会丢掉这些提交，执行前先确认）。只撤回某一批：`git revert <hash>`。

## 八、进度（断点续跑用）

当前阶段：A
运行方式：只读
技术栈：
开始：YYYY-MM-DD　最后更新：YYYY-MM-DD

| 任务 | 状态 | 写在哪 | 备注 |
| --- | --- | --- | --- |
| A1 技术架构 | 未开始 | 1-project-map.md「技术架构」、diagrams/architecture.svg | |
| A1b 应用架构 | 未开始 | 1-project-map.md「应用架构」、diagrams/app-architecture.svg | |
| A2 模块依赖 | 未开始 | 1-project-map.md「模块依赖」、diagrams/module-deps.svg | |
| A3 外部依赖 | 未开始 | 1-project-map.md「外部依赖」、画进 diagrams/architecture.svg | |
| A4 接口清单 | 未开始 | 1-project-map.md「接口清单」 | |
| A5 数据模型、ER 图 | 未开始 | 1-project-map.md「数据模型」、diagrams/data-model-er.svg | |
| A5b 核心接口时序图 | 未开始 | 1-project-map.md「核心接口时序」、diagrams/sequence-<名>.svg | |
| A5c 模块说明 | 未开始 | 1-project-map.md「模块说明」 | |
| A6 互校 | 未开始 | 1-project-map.md「互校结果」 | |
| A7 疑点 | 未开始 | 本文第六节 | |
| A7b 风险地带 | 未开始 | 1-project-map.md「风险地带」 | 「测试兜底」一列在 B9 后回填 |
| A8 CLAUDE.md | 未开始 | apply/CLAUDE.md | 禁区、历史包袱待人填 |
| A9 docs-auto-sync | 未开始 | apply/.claude/skills/docs-auto-sync/SKILL.md | |
| B1–B2 依赖清单、环境脚本 | 未开始 | 2-dev-setup.md 第 1 节、scripts/dev-env.sh | |
| B3–B4 编译启动、冒烟 | 未开始 | 2-dev-setup.md 第 3–5 节 | 只读方式跳过 |
| B5 上手步骤、env-bootstrap | 未开始 | 2-dev-setup.md 第 2 节、apply/.claude/skills/env-bootstrap/ | |
| B6 核心链路 | 未开始 | 3-test-guard.md 第 1 节 | |
| B7–B8 测试现状 | 未开始 | 3-test-guard.md 第 2 节 | B8 只读方式跳过 |
| B9 缺口 | 未开始 | 3-test-guard.md 第 3 节 | |
| B10–B11 补测试 | 未开始 | 3-test-guard.md 第 4 节 + 测试代码 | B11 只读方式跳过 |
| B12–B13 CI | 未开始 | 3-test-guard.md 第 5 节、apply/.github/workflows/test.yml | 未推送 |

状态取值：未开始 / 进行中 / 完成 / 卡住（写原因）/ 跳过（写原因）

改造记录：

| feature | 阶段 | 各批提交号 | 备注 |
| --- | --- | --- | --- |

SKILL 候选（M1）：

| 流程名 | 为什么反复（证据） | 可参数化部分 | 起点 | 终点 |
| --- | --- | --- | --- | --- |

卡点：

| 事项 | 卡在哪 | 已尝试 | 需要你做的 |
| --- | --- | --- | --- |

## 九、以后怎么用

- 想实际跑起来：说「跑起来」。会接着现有进度装依赖、启动、冒烟、跑测试、补测试。
- 改了接口或实体以后，说「帮我看看文档还对不对得上」，触发 docs-auto-sync。
- 新同事搭环境，说「初始化开发环境」，触发 env-bootstrap，或者照 2-dev-setup.md 第 2 节做。
- 下一个需求，说「改造：<一句话需求>」，会多一篇 `4-change-<需求>.md`。只读方式只出方案；说「跑起来并改造」才会改代码。
- 中断以后，说「继续」。
