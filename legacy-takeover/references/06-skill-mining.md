# 挖 SKILL

CLAUDE.md 是静态常识，SKILL 是动态的操作流程。反复要做的操作写进 CLAUDE.md，会让它越来越臃肿，应该放进 SKILL。

| | CLAUDE.md | SKILL |
| --- | --- | --- |
| 位置 | 项目根目录，一份 | `.claude/skills/`，多份 |
| 加载 | 每次启动自动读 | 按场景触发 |
| 内容 | 全局稳定的项目常识 | 局部、模块化的操作模板 |
| 类比 | AI 进门就能看到的公告栏 | 挂在墙上的专项工具箱 |
| 维护 | 写一次，偶尔更新 | 挖一个，用一段时间，再挖下一个 |

## 三个特征（同时满足才值得做）

- **可复制**：同样的动作序列反复执行过；
- **可参数化**：只有几个变量在变，骨架是一样的；
- **可自动化**：起点和终点清晰，不靠临场发挥。

偶尔做一次的事，写成文档就够了；本身就很发散的事，留在脑子里。

老项目里的四类典型流程：
- 技术文档自动更新（对抗文档腐烂）；
- 改造前体检（测试是否全绿、能否编译、中间件能否连上）；
- 提交 PR 前检查（测试、格式化、changelog、文档、找谁 review）；
- 新增接口前对齐（路径风格、统一响应、错误码）。

另外，同一套分层文件反复出现的项目，可以考虑 CRUD 脚手架。

## M1　列候选

执行规格：

```plain
扫一下当前项目（包括 git log、CLAUDE.md、make-skill-legacy-takeover-output/、docs/、README、CONTRIBUTING、
.github/），找出团队反复在做的操作流程。
判断标准是三特征：可复制、可参数化、可自动化。
三个都满足才算值得做 SKILL 的候选。

把找到的候选列出来，每个写明：流程名、为什么是反复的、能参数化的部分、
是什么、起点和终点是什么。最后给我用一个表格总结。
```

「为什么是反复的」要给出证据，用 git log 里的返工痕迹（同一类手工修补的提交）。候选表写进总说明 `make-skill-legacy-takeover-output/README.md` 第八节的「SKILL 候选」。

## M2　Top 3

执行规格：

```plain
从上面的清单里挑 3 个最高优先级的，给我做成候选 SKILL。
每个候选写：name（英文）、description、预期 steps、allowed-tools。
优先级判断标准：频率高、痛点深、自动化收益大。用表格总结，包含类型和理由。
```

每条都按「频率、痛点、自动化收益」三个维度写理由。阶段 A 落地 docs-auto-sync，阶段 B 落地 env-bootstrap，其余候选写进总说明。

## M2b　可选：CRUD 脚手架 SKILL

M1 候选里有 CRUD 脚手架，并且有证据（项目里有多组结构相同的 Controller / Service / Entity / DTO 分层文件）时才生成。它计入「不超过 5 个」的上限。

执行规格：

```plain
生成代码中 CRUD 的 SKILL。
注意按照标准格式和放在标准目录。
结果放到 make-skill-legacy-takeover-output/apply/.claude/skills/ 目录中。
```

产出 `make-skill-legacy-takeover-output/apply/.claude/skills/add-crud-module/SKILL.md`。参数一般是 moduleName、fields、operations。终点是对应的分层文件、DDL 和项目地图接口清单里的新章节都已生成，并且能编译。生成以后，docs-auto-sync 的 Step 7 可以提示用户用 `/add-crud-module` 补新模块。

## M3　生成 SKILL.md

要求：
- `name`；
- `description` 写清楚在什么场景触发、产出是什么；
- 步骤清晰，可以直接执行；
- `allowed-tools` 限制到最小；
- 会改文件的操作，默认改成「只汇报差异，由人决定怎么处理」。

保存到 `make-skill-legacy-takeover-output/apply/.claude/skills/<name>/SKILL.md`（用户运行 apply.sh 后进入 `.claude/skills/`）。现成的底稿在 `assets/project-skills/`。

## M4　测触发（三项全过才算上线）

1. 说一句匹配的话（比如「我刚改完一批 Controller，帮我看看文档还对不对得上」），应该自动加载。
2. 说一句不匹配的话（比如「帮我检查一下这段代码」），不应该加载。加载了，说明 description 写得太宽。
3. 真跑一次：看它有没有按步骤走、有没有列出具体的不一致点、有没有自作主张改文件。

改完 SKILL 以后，要**完全退出 Claude Code 再重新启动**才会生效。你当前会话里没办法重启的，就按 SKILL 的步骤手动走一遍，代替第 3 项；第 1、2 项写进总说明，交给用户验证。

## 数量和成熟路径

- 一个老项目 5–10 个就够用了，有的甚至不到 3 个。建议不超过 5 个，先挖 3 个，用一个月再扩展。SKILL 一多，一句话会同时匹配好几个，AI 反而判断不清。
- AI 第一版大约 60 分 → 人工调整 description、steps，收紧 allowed-tools，1–2 小时能到 70–80 分 → 用一个月，按误触发和漏触发迭代到 80 分以上 → 持续打磨到 90 分以上，成为团队标配。

## 反模式

- 一上来就研究 YAML 格式，而不是先挖场景；
- 没有重复的流程，硬写一个；
- 写完不验证；
- description 写得太宽；
- 追求第一版就完美。

场景驱动用工具：先有问题，才去写 SKILL。
