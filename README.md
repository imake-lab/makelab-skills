# make-skills

**马克LAB 在真实项目里打磨出来的 AI 编程技能合集。每个技能都能单独复制走，放进项目就能用。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Claude Code Skills](https://img.shields.io/badge/Claude%20Code-Skills-8A63D2)

> 让 AI 把事做完，验清楚，交出去。

## 技能目录

| 技能 | 一句话 | 适合谁 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| [legacy-takeover](legacy-takeover/) | 接手跑了多年的陌生老项目：AI 自主摸清项目、写好护栏和改造方案，交付几份关键文档；默认只读，说「跑起来」才动手 | 接手老系统的开发者、技术负责人；基于开源做二次开发的人；想给开源项目提 PR 的人 | v0.1 草稿 | [README](legacy-takeover/README.md) |

后续的技能会继续加到这张表里。

## 仓库约定

每个技能是一个独立的目录，直接放在仓库根目录下，可以单独复制使用：

```text
make-skills/
├── README.md               本文件：技能目录
├── LICENSE
└── <技能名>/
    ├── SKILL.md            技能入口（Claude Code 读取的就是这个文件）
    ├── README.md           这个技能的完整说明：做什么、架构、流程、怎么用、限制
    ├── LICENSE             随技能一起复制走
    ├── references/         按需加载的详细规格（可选）
    ├── templates/          产出模板（可选）
    ├── assets/             附带的资源（可选）
    └── scripts/            脚本和测试（可选）
```

- **自包含**：一个技能需要的东西都在自己的目录里，不依赖仓库里的其他技能。
- **产出集中在一个文件夹**：技能在你的项目里生成的所有东西，都放在 `make-skill-<技能名>-output/` 下。这个名字不会和项目已有的目录重名；不想要了，删掉这个文件夹即可。
- **图都是 SVG**：技能产出的图一律是 SVG 文件，可以放大、可以编辑，GitHub 上能直接显示。
- **有最终说明**：每次运行结束，产出文件夹里都会有一份 README，写清做了什么、有哪些产出、每个产出的作用。
- **先说清边界**：每个技能的 README 都会写明它不做什么、哪些事必须由人来做、有哪些安全边界。
- **能验证**：带脚本的技能，脚本都附有测试。

## 怎么安装

以 legacy-takeover 为例，其他技能的装法一样，换个目录名就行。

```bash
git clone https://github.com/imake-lab/make-skills.git

# 只在某个项目里用
mkdir -p <你的项目>/.claude/skills
cp -r make-skills/legacy-takeover <你的项目>/.claude/skills/

# 或者装到用户级，所有项目都能用
mkdir -p ~/.claude/skills
cp -r make-skills/legacy-takeover ~/.claude/skills/
```

装完以后**完全退出 Claude Code 再重新启动**，技能才会被识别。具体怎么触发、会产出什么，见各技能自己的 README。

用其他智能体（Codex 等）的话，可以让它直接读技能目录里的 `SKILL.md`，按里面的规程执行。只是不会被自动触发。

## 参与贡献

欢迎提 issue 和 PR：
- 用某个技能时发现的问题（请附上技术栈、触发语句、实际现象）；
- 对现有技能的改进；
- 新技能的建议。

改动某个技能时，请先在它的目录下跑通自带的测试（如果有的话）。

## License

[MIT](LICENSE) © 2026 马克

## 关于作者

马克LAB。扛过大型系统的架构师，十几年技术，带过几十人团队。公开记录用 AI 编程做真项目，含翻车现场。

- X：[@imakelabs](https://x.com/imakelabs)
- 网站：[imakelabs.net](https://imakelabs.net)

本项目与 Anthropic 没有隶属、背书或合作关系。Claude Code 是 Anthropic 的产品，文中出现这个名称，只用于说明兼容方式。
