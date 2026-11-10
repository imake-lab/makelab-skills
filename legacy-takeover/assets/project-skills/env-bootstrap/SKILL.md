---
name: env-bootstrap
description: 一键准备本项目的本地开发环境，依次执行：依赖盘点、安装中间件、启停脚本、编译启动、接口冒烟，并记录踩坑。在新接手项目、重置环境、换了新机器，或者定期验证环境是否健康时使用。
allowed-tools: Read, Bash, Write
---

# env-bootstrap

把这个项目从「clone 下来」带到「跑起来，核心接口冒烟通过」。

> 本文件由 legacy-takeover 根据项目实际情况生成。尖括号里的内容在接手时已填入本项目的实际值。
> 接手时如果是只读方式，下面的命令是从配置文件推出来的，没有在本机实测过。第一次执行时以实际结果为准，把修正写回本文件和 `make-skill-legacy-takeover-output/2-dev-setup.md`。

## 触发场景

- 新接手项目，或者新同事第一次搭环境
- 重置环境、换了新机器
- 定期验证环境健康（例如每周一次，或者升级依赖之后）

## 输入（都在项目里）

- `make-skill-legacy-takeover-output/scripts/dev-env.sh`：`install` / `start` / `stop` / `status` 四个子命令
- `make-skill-legacy-takeover-output/scripts/docker-compose.dev.yml`（Docker 备选方式，有这个文件时）
- `make-skill-legacy-takeover-output/2-dev-setup.md`：第 1 节依赖清单（版本、端口、初始化要求），第 2 节上手步骤和常见踩坑，第 5 节选好的冒烟接口

## 步骤

### Step 1：依赖盘点

读 `make-skill-legacy-takeover-output/2-dev-setup.md` 第 1 节依赖清单，再和 `<构建文件>`、`<配置文件>` 对一遍。配置里出现了清单上没有的依赖，就先补进清单。

### Step 2：安装中间件

- 已经装好的跳过，只验证版本。
- 没装的，执行 `bash make-skill-legacy-takeover-output/scripts/dev-env.sh install`；偏好 Docker 的，执行 `docker compose -f make-skill-legacy-takeover-output/scripts/docker-compose.dev.yml up -d`。
- 自主修复：先看报错，判断原因（版本、源、权限、缺少前置依赖），然后修，再重试。**同一个错误连续 3 次修不好就停下**，汇报卡在哪一步。
- 需要 sudo 的步骤不自动执行，把命令列给用户。
- 过程追加到 `make-skill-legacy-takeover-output/2-dev-setup.md` 第 3 节「安装记录」。

### Step 3：启动依赖

执行 `bash make-skill-legacy-takeover-output/scripts/dev-env.sh start`（按依赖顺序串行启动，每个都等到就绪），然后用 `bash make-skill-legacy-takeover-output/scripts/dev-env.sh status` 确认所有依赖都在运行、端口在监听。

### Step 4：编译启动

```bash
<构建命令>
<启动命令>
```

成功的标准：日志没有 ERROR，`<应用端口>` 在监听，`<管理界面 / 健康检查地址>` 能打开。有前端的，一并启动：`<前端启动命令>`，访问 `<前端地址>`。

失败和修复的过程追加到 `make-skill-legacy-takeover-output/2-dev-setup.md` 第 4 节「启动记录」。常见问题和解法见同一文档的「常见踩坑」。

### Step 5：接口冒烟

用 `<默认账号来源>` 里的账号登录，拿到 token，然后 curl 下面这些核心接口：

| # | 接口 | 预期 |
| --- | --- | --- |
| 1 | <方法 路径> | 200，返回 <结构> |
| 2 | … | … |

200 算通过，返回错误的如实列出来。结果覆盖写入 `make-skill-legacy-takeover-output/2-dev-setup.md` 第 5 节「冒烟结果」（加上日期）。

### Step 6：汇报

用一张表汇报：依赖状态、应用和前端地址、冒烟的通过数和失败数、遇到的新坑。新坑要补进 `make-skill-legacy-takeover-output/2-dev-setup.md` 的「常见踩坑」。

## 不做的事

- 不改项目里已有的配置文件，需要本地覆盖时，新建本地配置文件
- 不打印、不提交任何凭据
- 不停止或卸载本机上与本项目无关的服务
