# <项目名>

给 Claude Code 看的项目速查手册，详细文档见 make-skill-legacy-takeover-output/。本文件不超过 300 行。

## 项目定位

<项目名>：<一句话定义>。核心能力：<一行列举>。上游仓库：<地址，没有就删掉这一项>。

## 核心架构

<一段话>

- 项目地图：[make-skill-legacy-takeover-output/1-project-map.md](make-skill-legacy-takeover-output/1-project-map.md)（应用架构、技术架构、模块说明、模块依赖、外部依赖、接口清单、数据模型、核心时序）
- 应用架构图：[make-skill-legacy-takeover-output/diagrams/app-architecture.svg](make-skill-legacy-takeover-output/diagrams/app-architecture.svg)　技术架构图：[make-skill-legacy-takeover-output/diagrams/architecture.svg](make-skill-legacy-takeover-output/diagrams/architecture.svg)
- 风险地带：[make-skill-legacy-takeover-output/1-project-map.md](make-skill-legacy-takeover-output/1-project-map.md) 的「风险地带」一节。改动前先看，碰到的要先锁行为、先问人
- 模块依赖图：[make-skill-legacy-takeover-output/diagrams/module-deps.svg](make-skill-legacy-takeover-output/diagrams/module-deps.svg)　ER 图：[make-skill-legacy-takeover-output/diagrams/data-model-er.svg](make-skill-legacy-takeover-output/diagrams/data-model-er.svg)

## 关键模块

| 模块 | 职责 |
| --- | --- |

依赖链：`a ← b ← c`（无循环依赖 / 循环依赖：…）。每个模块的入口、核心类、表、改动风险见项目地图「模块说明」。

| 数据库 / 存储 | 存放内容 |
| --- | --- |

## 关键约定

只写本项目特有的硬规则，每条附一个代码位置做例子。

- 

## 怎么跑

见 [make-skill-legacy-takeover-output/2-dev-setup.md](make-skill-legacy-takeover-output/2-dev-setup.md) 第 2 节。依赖启停：`bash make-skill-legacy-takeover-output/scripts/dev-env.sh start|stop|status`。

## 禁区

<!-- 待人工填写：哪些代码不能动、哪些字段有对接方依赖、哪些配置改了会出事、哪些接口路径对外公开过。线索见 make-skill-legacy-takeover-output/README.md 第六节「疑点」。AI 不填写本节。 -->

## 历史包袱

<!-- 待人工填写：看起来奇怪但有原因的设计、不要顺手重构的地方。线索见 make-skill-legacy-takeover-output/README.md 第六节「疑点」。AI 不填写本节。 -->
