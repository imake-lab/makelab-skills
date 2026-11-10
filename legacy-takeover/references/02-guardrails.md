# 阶段 B　建护栏

目标：理解了项目以后，再把项目跑通（环境），护住（测试 + CI）。这三件事做完，才有资格谈改造。

衡量标准不是覆盖率，而是**改造路径上的关键节点都有兜底**。摸清比补全重要十倍。

前提：阶段 A 的资产都在（`make-skill-legacy-takeover-output/1-project-map.md`、五张图、`apply/CLAUDE.md`）。不在就先执行阶段 A。

本阶段的产出只有两份文档、一个脚本和两个 apply 文件：
- `2-dev-setup.md`（模板 `templates/dev-setup.md`）：B1–B5；
- `3-test-guard.md`（模板 `templates/test-guard.md`）：B6–B13；
- `scripts/dev-env.sh`（模板 `templates/dev-env.sh`），需要时加 `scripts/docker-compose.dev.yml`；
- `apply/.claude/skills/env-bootstrap/SKILL.md`、`apply/.github/workflows/test.yml`。

**两种运行方式**（见 SKILL.md 第 2 节）：

| 任务 | 只读（默认） | 运行 |
| --- | --- | --- |
| B1 依赖盘点 | 做 | 做 |
| B2A 安装脚本 | 只生成 `dev-env.sh install`，不执行，标「未实测」 | 生成并执行 |
| B2B 启停 | 只生成 `start` / `stop` / `status`，不执行 | 生成并真跑一遍 |
| B2C Docker 备选 | 生成，不运行 | 生成，不运行 |
| B3 编译启动 | 跳过；构建和启动命令从构建文件、README 推出来，写进上手步骤，标「未实测」 | 做 |
| B4 冒烟 | 只挑出 5 个核心接口、写好 curl 命令，不执行 | 做 |
| B5 上手文档、env-bootstrap | 做，标「未实测」 | 做 |
| B6 核心链路、B7 静态摸底、B9 缺口、B10 补测试计划 | 做 | 做 |
| B8 跑测试、B11 补测试 | 跳过 | 做 |
| B12–B13 CI | 做（只生成文件） | 做（只生成文件） |

跳过的任务，在文档对应小节写「只读方式：未执行」，进度表标「跳过（只读）」。

贯穿本阶段的三条约束：
1. **不要大而全**：每个清单都写数量上限。
2. **不要一口气做完**：测试分批，每批 1–3 个，最好 1 个。
3. **自主修复加兜底**：同一个错误连续 3 次修不好，就停下这一项。

## 场景一　让 AI 当环境工程师

### B1　依赖盘点

执行规格：

```plain
综合看 make-skill-legacy-takeover-output/1-project-map.md 的「外部依赖」一节、application*.yml、pom.xml、README，
给我列一份这个项目运行需要的完整外部依赖清单。
每个依赖列出：名字、版本要求（精确到主版本）、默认端口、
连接信息、初始化要求（建库、配 Nacos 命名空间等）。
输出用表格总结。写进 make-skill-legacy-takeover-output/2-dev-setup.md 第 1 节「依赖清单」。
```

结构按 `templates/dev-setup.md` 第 1 节：
- 先写一行来源（读了哪些文件）；
- 再放「运行时依赖总览」表：依赖 | 版本 | 默认端口 | 连接信息 | 初始化要求 | 必须/可选 | 来源；
- 表后用脚注说明：去掉「可选」项以后，什么功能不可用。

README 往往列不全：有的中间件只出现在生产配置里，有的是被某个依赖间接带进来的。所有环境的配置文件都要看。

自检：
- [ ] 和项目地图的外部依赖对得上
- [ ] 每个版本号都标了来源（构建文件、README、compose 文件）
- [ ] 初始化要求写细了：建库、命名空间、推送配置、跑初始化 SQL
- [ ] 区分了必须和可选

### B2A　本地安装并执行

执行规格：

```plain
读 make-skill-legacy-takeover-output/2-dev-setup.md 的依赖清单，给我生成一份本地安装脚本，
写成 make-skill-legacy-takeover-output/scripts/dev-env.sh 的 install 子命令。
- 用 brew（macOS）或 apt（Linux）装中间件
- 包含每个中间件的初始化（建库 SQL、Nacos 配置等）
- 不会的依赖（比如某个 jar 包要下）写清楚下载链接和放哪

生成完直接执行这个脚本。执行过程遵循自主修复原则:
- 任何一步失败，先看报错信息
- 自己判断原因（版本不对、源问题、权限问题、依赖缺失）
- 自己修（换源、换版本、加 sudo、装前置依赖）
- 修完重试，跑通为止
- 不要每个错误都问我

如果同一个错误连续修 3 次还不行，停下来汇报具体卡在哪。
其他情况一律自己解决。

最终把每个中间件最终用了什么命令装上、过程中遇到什么问题、怎么修的，
记进 make-skill-legacy-takeover-output/2-dev-setup.md 第 3 节「安装记录」。
```

本技能对执行方式的调整：
- **只读方式：只生成脚本，不执行**。「生成完直接执行」以下的部分全部跳过，第 3 节写「只读方式：未执行」。
- 不执行需要 `sudo` 或改系统配置的命令。脚本照写，执行时跳过这些步骤，把要用户手动执行的命令写进总说明的卡点。
- 本机有 Docker 却没有安装权限时，改走 B2C 的 compose 方式起依赖。这算安装成功，在安装记录里注明。
- 已经装好并在运行的中间件，不重装，只验证版本和连通性。

自检：
- [ ] 脚本对每个中间件都包含「装、初始化、验证」三步
- [ ] （运行方式）安装记录如实记录了每一步的命令、问题和修法，包括没修好的
- [ ] 没有出现同一个错误重试超过 3 次的死循环

### B2B　依赖启停脚本

执行规格：

```plain
基于 Step 2A 装好的中间件，在 scripts/dev-env.sh 里加三个子命令：
- start：一键启动所有依赖中间件
- stop：一键停止所有依赖中间件
- status：查看每个中间件的运行状态

考虑混合场景：有的用 brew services 管，有的是手动 jar，
有的是 systemd。脚本要能处理这几种。
启动后等服务就绪再返回，不要"启动了但还没 ready"。
status 脚本要打印每个中间件的运行状态和端口监听情况。
```

自检：
- [ ] 启动顺序按依赖关系**串行**（数据库在应用之前，注册中心在依赖它的服务之前）。AI 默认容易写成并行，要检查
- [ ] 每个服务都等到就绪（探测端口或健康检查）才启动下一个
- [ ] （运行方式）真跑一遍 start → status → stop → start，四步都正常。只读方式下用 `bash -n` 检查语法

### B2C　Docker 备选

执行规格：

```plain
顺手给一份 make-skill-legacy-takeover-output/scripts/docker-compose.dev.yml，把所有依赖打包成 docker。
偏好 Docker 的同学可以用这个替代 Step 2A 和 2B。
版本号、端口、初始化脚本要齐全。
保存到 make-skill-legacy-takeover-output/scripts/。不用运行
```

（项目只依赖一两个中间件、本地装很简单时，可以不生成，在总说明里写明。运行方式下，只有在 B2A 无法本地安装时，才用它来起依赖。）

自检：
- [ ] 版本、端口和依赖清单一致
- [ ] 初始化脚本已经挂载
- [ ] `docker compose -f make-skill-legacy-takeover-output/scripts/docker-compose.dev.yml config` 校验通过（有 Docker 时；这只做语法校验，不起容器，只读方式也可以做）

### B3　编译启动（只读方式跳过）

只读方式：不执行。从构建文件、README、CI 配置里找出构建和启动命令、端口、管理界面地址，写进 `2-dev-setup.md` 第 2 节，标「未实测」。

运行方式的执行规格：

```plain
中间件已经起来了（用 make-skill-legacy-takeover-output/scripts/dev-env.sh status 确认）。
现在帮我跑 mvn clean package + 启动应用。
启动过程同样遵循自主修复原则
（参照 Step 2A 的兜底机制：连续 3 次同一错误才停下来汇报）。

启动成功后告诉我应用监听的端口、管理界面地址。
失败和修复的过程记到 make-skill-legacy-takeover-output/2-dev-setup.md 第 4 节「启动记录」。
```

（`mvn clean package` 换成项目实际的构建命令，见 `stack-map.md`。）

接着执行：

```plain
有前端页面吗？也启动一下，给我访问地址
```

常见卡点：
- 语言运行时版本不对（要 17，本地是 21 或 11）；
- 依赖仓库连不上，或者版本对不上；
- 端口被占用（8080、8848 等）；
- 某个环境的配置文件缺失，需要从主配置复制；
- 配置中心里的配置没推。

修改项目配置时，只新建本地配置文件（比如 `application-dev.yml`、`.env.local`），不改项目已有的配置文件。

自检：
- [ ] 日志里没有 ERROR
- [ ] 端口在监听
- [ ] 管理界面或健康检查能打开；有前端的，前端能打开
- [ ] 数据库表已经建好
- [ ] 启动记录写了每次失败和修复

### B4　接口冒烟

只读方式：只挑出 5 个核心接口，写好请求命令，放进 `2-dev-setup.md` 第 5 节，状态码一栏写「未执行」。

运行方式的执行规格：

```plain
读 make-skill-legacy-takeover-output/1-project-map.md 的接口清单，挑 5 个最核心的接口（覆盖<核心业务模块，如登录、
主数据的创建、核心业务流程>几大模块），用 curl 跑一遍。
返回 200 算通过，返回错误的列出来。
输出用表格总结，写进 make-skill-legacy-takeover-output/2-dev-setup.md 第 5 节「冒烟结果」。
```

登录要用账号的，从初始化 SQL 或种子数据里找默认账号。

自检：
- [ ] 选的是真核心接口（登录、核心数据写入、核心流程），不是最简单的 GET
- [ ] 每条都记了请求、状态码、响应摘要，并核对了返回结构和接口清单是否一致
- [ ] 失败的如实列出来，没有为了「全绿」只挑能过的

### B5　新人上手文档和 env-bootstrap SKILL

执行规格：

```plain
基于 make-skill-legacy-takeover-output/2-dev-setup.md 的安装记录和启动记录，
整理一份给新人看的上手步骤，
包含：前置条件、装中间件步骤、启动命令、常见踩坑、验证清单。
写进 make-skill-legacy-takeover-output/2-dev-setup.md 第 2 节「新人上手」。
```

```plain
基于这次环境搭建的全流程，给我生成一个 env-bootstrap 的 SKILL，
保存到 make-skill-legacy-takeover-output/apply/.claude/skills/env-bootstrap/SKILL.md。
触发场景：新接手项目、重置环境、定期验证环境健康。
步骤：依赖盘点 → 装中间件 → 启停脚本 → 编译启动 → 接口冒烟。
allowed-tools 限制到 Read, Bash, Write。
```

做法：
- 以 `assets/project-skills/env-bootstrap/SKILL.md` 为底稿，填入本项目的实际命令、端口、默认账号来源、冒烟接口。
- 只读方式下没有安装和启动记录，上手步骤从依赖清单和构建文件推出来，文档开头标「未实测」；env-bootstrap 里也注明「步骤未在本机实测」。常见踩坑只写从配置里能看出来的（版本要求、端口冲突、缺失的环境配置文件）。
- 回填 `make-skill-legacy-takeover-output/apply/CLAUDE.md` 的「怎么跑」一节：一句话加 `2-dev-setup.md` 第 2 节的链接。

## 场景二　摸清测试现状

为什么先摸再补：直接补的话，AI 会按通用质量标准列出 200 条，根本补不完。要先回答「什么是关键路径」，让缺口收敛到能执行的范围（5–10 个 P0）。

### B6　核心链路

执行规格：

```plain
基于 make-skill-legacy-takeover-output/1-project-map.md 的接口清单和数据模型、CLAUDE.md，给我列出
这个项目最值得测的核心链路。要求：
- 总数不超过 8 条，宁少勿多
- 必须是"改造时容易出问题"的链路，不是所有链路
- 每条写：链路名、起点（哪个接口）、关键节点（哪些 service / DB 操作）、终点（什么状态）

输出用表格总结。写进 make-skill-legacy-takeover-output/3-test-guard.md 第 1 节「核心链路」。
```

结构按 `templates/test-guard.md` 第 1 节：在链路名、起点、关键节点、终点四列之外，加一列「核心风险」，写出具体的代码陷阱。文末附一张「改造高危区速查」表（改造类型 → 受影响链路）。

自检：
- [ ] 是真核心：登录、核心数据的增删改、跑批、执行、写入算；详情查询、分页列表不算
- [ ] 终点写到能直接转成断言的程度，比如「POST 登录 → 校验密码 → 写 Token → 200 + accessToken」
- [ ] 核心风险写的是具体陷阱，比如两张表更新没有事务、外部调用失败被静默吞掉、状态机没有超时兜底、同一字段在两处命名不一致，而不是「可能出错」

### B7　摸现有测试（静态）

执行规格：

```plain
扫一下项目里所有的测试目录（src/test、tests/、e2e/ 等），
统计现有测试情况。要求：
- 单元测试 / 集成测试 / E2E 各多少个文件
- 哪些 Controller 有对应的测试，哪些没有
- 哪些核心 Service 有测试，哪些没有
- 不要给覆盖率百分比，那是 JaCoCo 干的事
- 不要列出每个测试方法，只关注"哪些核心链路被覆盖"

对照 make-skill-legacy-takeover-output/3-test-guard.md 的核心链路，标出每条核心链路当前的测试覆盖
情况（有 / 部分 / 没有）。输出用表格总结。
写进 make-skill-legacy-takeover-output/3-test-guard.md 第 2 节「测试现状」。
```

自检：
- [ ] 按链路判断，不是按文件判断：存在 `XxxControllerTest`，不等于 Xxx 的核心流程被覆盖了

### B8　跑一遍看实际状态（动态，只读方式跳过）

只读方式：不执行。「实际运行结果」小节写「只读方式：未运行」，并写出项目的标准测试命令，方便以后跑。

运行方式的执行规格：

```plain
跑一遍 mvn test（或项目的标准测试命令），统计真实结果：
- 通过 / 失败 / 跳过 各多少
- 失败的分类：代码 bug / 测试本身坏了 / 环境问题
- 跑总耗时多少
- 不要试图修复失败的测试，只汇报状态

最后给一个"测试健康度"的判断：绿（90% 通过）/ 黄（60-90%）/红（< 60%）。
输出用表格总结。
追加到 make-skill-legacy-takeover-output/3-test-guard.md 第 2 节的"实际运行结果"小节。
```

标准测试命令从构建脚本、Makefile、CI 配置里找，不要默认用语言的通用命令。

自检：
- [ ] 失败分类有依据。AI 容易把失败都归成「环境问题」，你要反问自己：「代码 bug」类到底有几个？
- [ ] 疑似真 bug 写进总说明的「待你确认」，并在第六节「疑点」里登记
- [ ] 健康度把跳过的和失败的合在一起看

### B9　缺口清单

执行规格：

```plain
对照 make-skill-legacy-takeover-output/3-test-guard.md 的核心链路（应该测什么）和测试现状
（现在测了什么），算出测试缺口。

严格遵守以下原则：
- 总数不超过 20 项，宁少勿多
- 只列在核心链路上的缺口，不在主链路上的不要列
- 每项标 P0（改造前必须有）/ P1（有了更好）
- 不要追求覆盖率指标，追求"关键路径有兜底"
- 每项写：场景描述、为什么必须、建议测试类型（集成 / 单元 / Characterization Test）

输出用表格总结。写进 make-skill-legacy-takeover-output/3-test-guard.md 第 3 节「测试缺口」。
```

结构按 `templates/test-guard.md` 第 3 节：先放汇总表（优先级 | 数量 | 涵盖链路），再放明细（编号 G01… | 优先级 | 链路 | 场景 | 为什么必须 | 建议类型 | 判断要点）。

自检：
- [ ] **P0 控制在 5–10 个，P1 不超过 10 个。** AI 第一版往往给出 100 多项，或者 14 个 P0，你要自己再砍一刀
- [ ] 每个 P0 都能回答「不补的话，AI 改坏了我发现不了什么」。答不上来的，就不是 P0
- [ ] 想到了但不在核心链路上的缺口，只写在文末备注里

做完缺口清单，回填 `1-project-map.md`「风险地带」：
- 每条风险的「测试兜底」一列，按测试现状和缺口填上有 / 部分 / 没有；
- 没有测试兜底的核心链路，作为「无测试的核心链路」类型补进风险清单（仍然不超过 15 条，超了就合并或砍掉最轻的）。

## 场景三　补出兜底测试

**Characterization Test**：不测「应该做什么」，只锁住「现在实际做什么」。先让代码跑一遍，记录下实际的输入输出，再把它们转成断言。改造前记一条基线，改造后对照，就知道行为有没有偏移。老项目的「应该」往往没人说得清，「现在」是确定的。

该补还是不该补：
- **必须补**：要改的接口或链路没有测试；改完以后没法验证；涉及核心业务逻辑（计费、权限、数据写入）。测试缺口里的 P0 全部必补。
- **可以不补**：改动极小（日志、文案）；已经被高质量的集成测试覆盖；项目马上要下线或重写。P1 可以先放着。

### B10　补测试计划

执行规格：

```plain
基于 make-skill-legacy-takeover-output/3-test-guard.md 的测试缺口，把 P0 缺口拆成多批，每批 1-3 个
（最好 1 个），给我一份补测试计划。每批写：批次号、测试类型
（Characterization Test / 集成测试 / 单元测试）、覆盖的核心
链路、预期工作量。

按"改造路径上的 Characterization > 核心链路集成 > 复杂逻辑
单元"的顺序排批次。简单 CRUD 不进计划。

输出用表格总结。写进 make-skill-legacy-takeover-output/3-test-guard.md 第 4 节「补测试计划」。
```

自检：
- [ ] 每批严格 1–3 个，最好 1 个
- [ ] 按价值排序；简单 CRUD（getter/setter、简单查询）确实没有进计划
- [ ] 一条从 HTTP 到 Service 再到 DB 的集成测试，比十个单元测试更能兜底，排序要体现这一点

### B11　一批一批补（只读方式跳过）

只读方式：不写测试代码。断言值必须来自实际运行，不运行就写不出合格的 Characterization Test。补测试计划就是交付物，用户说「跑起来」后按计划执行。

运行方式的执行规格（第 1 批）：

```plain
按 make-skill-legacy-takeover-output/3-test-guard.md 补测试计划的第 1 批，给项目补出对应的测试。

对 Characterization Test 类型：先跑一次现有代码记录实际行为，
再把行为转成断言。不要凭"应该是什么"写断言，凭"实际是什么"写。

对集成测试类型：需要真实启动应用 + 数据库。
用 SpringBootTest的方式起完整 context 跑。

补完跑一遍 mvn test 确保都通过。
输出用表格总结每个测试覆盖的场景、预期结果、实际跑出来的状态。
```

执行规格（第 2 批及以后）：

```plain
按 make-skill-legacy-takeover-output/3-test-guard.md 补测试计划的第 N 批补测试，
参考第 1 批已经跑通的测试风格，保持一致。
其他要求同前。
```

（SpringBootTest、mvn test 换成项目技术栈对应的写法，见 `stack-map.md`。）

执行纪律：
- 不创建分支，就在当前分支上做。开工前确认工作区干净，基线提交号已记在总说明里。每批跑通后本地提交一次，提交信息写 `takeover: test 批次<N> <缺口编号>`，不推送。
- 每批的汇总表追加到 `3-test-guard.md` 第 4 节的「批次记录」：批次 | 测试名 | 覆盖场景 | 断言值来源（实际运行输出）| 结果 | 提交。
- 失败的测试不能带进下一批，三选一处理：修测试（断言写错了）、确认是代码的真 bug（不改代码，标记出来，写进总说明）、如实标记「暂时跑不了」并写明原因。（不在这里修代码：护栏阶段不动业务代码，修 bug 要走阶段 C 的改造流程。）
- 实际行为和「应该」不一致时，不改代码，也不改断言去迎合「应该」。在测试旁边写注释说明，并登记到总说明第六节「疑点」。这种差异，往往就是历史包袱、对接方依赖或禁区。

自检（每批都过一遍，这是最关键的检查）：
- [ ] 每个断言值都能回答「这个值是从哪来的」，答案只能是「跑出来的」。看到 `amount == 100` 这类断言，就去确认 100 是不是运行输出
- [ ] 不只覆盖 happy path，测试缺口里列出的 edge case 也有对应的测试
- [ ] 本批全部通过以后，才开下一批

所有 P0 批次完成以后，跑一次项目的全量测试命令，把结果追加到 `3-test-guard.md` 第 2 节。

收尾时在总说明的「待你确认」里写一条：补了 N 个测试，断言值是否都来自实际运行输出（见 `3-test-guard.md` 的批次记录），以及哪几条出现了「实际行为 ≠ 应该的行为」（见第六节「疑点」）。这一点要单独标出来，因为它是最容易踩坑的 review 点。

## 场景四　让 CI 当兜底护栏

测试不持续跑，补了也是白补。靠自觉不可持续，CI 让它变成强制的。

### B12　分析 CI 现状

执行规格：

```plain
扫一下项目里有没有现成的 CI 配置（看 .github/workflows/、.gitlab-ci.yml、Jenkinsfile 之类）。
如果有，告诉我现在跑了什么、什么时候触发、有没有跑测试。
如果没有，告诉我项目代码托管在哪个平台，建议用哪种 CI。

输出用表格总结。
```

结论写进 `3-test-guard.md` 第 5 节「CI」。

三种情况：有 CI 但没跑测试，补一个 test job；完全没有，新建；有但已经过期，升级。

### B13　写完整的 CI workflow

执行规格：

```plain
基于上一步的分析，给我写一份完整的 CI workflow。要求：
- 触发条件：push 到任何分支 + 提 PR 时
- 运行环境：用项目对应的 JDK 版本（看 pom.xml 里 java.version）
- 启动需要的中间件（参考 make-skill-legacy-takeover-output/2-dev-setup.md 的依赖清单和 scripts/docker-compose.dev.yml）
- 跑 mvn clean test，失败就 block merge
- 输出测试报告到 CI artifact 区方便 review
- 加合理的 cache（Maven 依赖缓存）让跑得快一点

输出完整的 make-skill-legacy-takeover-output/apply/.github/workflows/test.yml（或对应平台的配置文件，同样放在 make-skill-legacy-takeover-output/apply/ 下、按它在项目里的位置建目录），
我直接 commit 进仓库就能跑。
```

本技能的调整：
- 只生成文件，放在 `apply/` 下，由用户运行 `apply.sh` 放进项目。**不推送，也不触发远端 CI**。
- 有 `actionlint` 或 `act` 时，用它们做本地校验。
- 「推送并跑通 CI」写进总说明的「需要你做的事」，附上推送命令和验收标准：CI 绿色、测试报告能下载、10 分钟以内跑完。同时附上下面这段提示词，用户 push 以后可以直接粘贴给 AI：

  ```plain
  push 一次代码触发 CI，看能不能跑通。失败就自己 debug 自己修，
  跟 install 脚本一样的自主修复原则（连续 3 次同错才停下来汇报）。
  最终跑通后告诉我 CI 跑一次需要多久。
  ```

自检：
- [ ] 触发条件对（团队只在 develop / master 跑 CI 的，按团队习惯来）
- [ ] 集成测试依赖的中间件，都在 workflow 里声明了（GitHub Actions 用 `services` 字段，或者用 compose 起）。不能默认中间件已经存在
- [ ] 运行时版本严格从构建文件读取（比如 pom.xml 的 `<java.version>`）。AI 容易默认写最新版本，项目要 17 就不能写成 21
- [ ] 常见失败已经预先处理：中间件启动等待、依赖源太慢或连不上（国内项目配置镜像）、本地缓存造成的差异

## B14　阶段收尾

1. 运行 `check_takeover.py`，修掉所有错误。
2. 更新总说明第八节「进度」。
3. 接手模式到这里结束，按 SKILL.md 第 9 节收尾：补全总说明 `make-skill-legacy-takeover-output/README.md`。

阶段 B 完成后的样子：

```text
<项目>/
├── make-skill-legacy-takeover-output/
│   ├── README.md                ← 总说明
│   ├── 1-project-map.md         ← 阶段 A
│   ├── 2-dev-setup.md           ← 环境手册
│   ├── 3-test-guard.md          ← 测试护栏
│   ├── diagrams/                ← 五张 SVG
│   ├── scripts/dev-env.sh       ← （+ docker-compose.dev.yml）
│   └── apply/                   ← CLAUDE.md、两个项目技能、CI 配置 + apply.sh
└── <测试目录>/                ← 已补的 P0 测试（只在运行方式下）
```
