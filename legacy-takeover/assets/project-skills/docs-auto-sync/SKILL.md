---
name: docs-auto-sync
description: 对照代码（接口入口、实体、建表 SQL）和文档（make-skill-legacy-takeover-output/1-project-map.md 的「接口清单」「数据模型」两节）做交叉比对，输出一份不一致清单，不修改任何文件。在新增或修改了接口、实体、表结构之后，怀疑文档和代码已经偏移时，或者 PR review 之前使用。
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(grep:*)
---

# docs-auto-sync

对照代码（Controller、Entity、SQL）和文档（`make-skill-legacy-takeover-output/1-project-map.md` 的「接口清单」「数据模型」两节），输出一份不一致清单。**不自动修改任何文件**，由人决定怎么处理。

> 本文件由 legacy-takeover 根据项目实际情况生成。下文的扫描命令以 Java / Spring 为例；接手时已按本项目的技术栈改写，改写依据见 legacy-takeover 的 `references/stack-map.md`。

## 触发场景

- 新增或修改了 Controller（接口变更、路径变更、参数变更）
- 新增或修改了 Entity 类或 SQL 表定义（字段变更、新增表、删除表）
- 怀疑文档和代码已经偏移，想做一次全量对齐检查
- PR review 前，确认文档是否跟上了代码变更

## 产出

一份结构化的差异报告，分两节：

1. **接口差异**（代码 vs 项目地图「接口清单」）：新增接口、删除接口、路径或方法变更、入参或返回类型变更
2. **数据模型差异**（Entity / SQL vs 项目地图「数据模型」）：新增表或实体、删除表或实体、字段增删、类型变更、枚举值变更

每条差异都标注：来源文件和行号、代码里的实际值、文档里记录的值、建议动作（更新文档 / 核实代码 / 忽略）。

## 用法

```text
/docs-auto-sync [targetModule] [docTarget]
```

| 参数 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `targetModule` | 否 | `all` | 模块名，或者 `all` 表示全量扫描 |
| `docTarget` | 否 | `both` | `api`（只查接口）、`model`（只查数据模型）、`both` |

示例：`/docs-auto-sync`、`/docs-auto-sync prompt api`

## 步骤

### Step 0：解析参数

1. `targetModule` 默认 `all`，`docTarget` 默认 `both`。
2. `targetModule` 不是 `all` 时，后面所有的 find / grep 都只限定在包含这个模块名的文件里，大小写不敏感，模糊匹配。

### Step 1：收集代码侧的接口清单（docTarget 为 `api` 或 `both` 时）

```bash
grep -rlE "@(Rest)?Controller" --include=*.java .
grep -nE "@(Request|Get|Post|Put|Delete|Patch)Mapping" <Controller 文件>
```

对每个 endpoint，记录：
- HTTP 方法；
- 完整路径（类上的 `@RequestMapping` 前缀，拼上方法注解里的路径）；
- 入参类型（`@RequestBody`、`@RequestParam`、`@PathVariable`）；
- 返回类型（`Result<T>`、`Flux<T>`、`SseEmitter` 等）；
- 所在文件和行号。

### Step 2：收集代码侧的数据模型清单（docTarget 为 `model` 或 `both` 时）

**2a 实体**

```bash
grep -rlE "@(Entity|Table|TableName)" --include=*.java .
```

对每个实体，提取：表名（`@TableName` 或 `@Table(name=…)`）、字段名和类型、主键（`@TableId` / `@Id`）、列名映射（`@TableField` / `@Column`）。

**2b SQL**

```bash
find . -name "*.sql" -not -path "*/target/*" -not -path "*/node_modules/*"
grep -nE "CREATE TABLE" <SQL 文件>
```

对每张表，记录：表名、列名、列类型、是否 NOT NULL、默认值、注释。

### Step 3：读取现有文档

用 Read 读取 `make-skill-legacy-takeover-output/1-project-map.md`，从「接口清单」和「数据模型」两节解析出：
- 每个模块的接口（方法 + 路径 + 入参 + 返回）；
- 每张表的字段（字段名 + 类型 + 说明）。

### Step 4：比对接口

匹配规则：**HTTP 方法和路径都完全相同，才算同一个接口。**

| 情况 | 标记 |
| --- | --- |
| 代码有，文档没有 | `[新增接口]`（文档缺失） |
| 文档有，代码没有 | `[已删接口]`（文档过期） |
| 路径相同，方法不同 | `[方法变更]` |
| 入参类型和文档描述不符 | `[入参变更]` |
| 返回类型和文档描述不符 | `[返回变更]` |
| 完全一致 | 不输出，只计入通过数 |

### Step 5：比对数据模型

| 情况 | 标记 |
| --- | --- |
| 代码或 SQL 里有这张表，文档里没有对应章节 | `[新增表]` |
| 文档有这一章，代码和 SQL 里都没有这张表 | `[已删表]` |
| 代码里有这个字段，文档里没有 | `[新增字段]` |
| 文档里有这个字段，代码里没有 | `[已删字段]` |
| 字段类型不符 | `[类型变更]` |
| 枚举值说明不符 | `[枚举变更]` |
| 完全一致 | 不输出，只计入通过数 |

### Step 5b：两份文档互相校对

接口清单和数据模型的互相校对要固化下来，防止两份资产慢慢漂移：

- 「接口清单」里出现的每个入参、返回实体，都应该能在「数据模型」找到定义。找不到就标 `[实体缺失]`。
- 两份文档里的同一个实体，名字要一致。类名重构以后新旧名字混用的，标 `[名称不一致]`。

### Step 6：输出差异报告

```text
# docs-auto-sync 报告
扫描范围：<targetModule> / <docTarget>　时间：<时间>
摘要：接口 通过 N / 差异 M；数据模型 通过 N / 差异 M

## 接口差异
| 标记 | 方法 路径 | 来源（文件:行号） | 代码实际 | 文档记录 | 建议动作 |

## 数据模型差异
| 标记 | 表.字段 | 来源（文件:行号） | 代码实际 | 文档记录 | 建议动作 |

## 文档互校
| 标记 | 实体 | 接口清单位置 | 数据模型位置 | 建议动作 |

## 无需处理的已知情况
- <例如：非主库实体跳过 SQL 比对>
```

### Step 7：结束

- **不修改任何文件。**
- 告诉用户：要逐条修复的话，手动编辑对应的章节，或者明确授权让 AI 按报告更新文档。
- 差异数为 0 时，输出「文档与代码完全一致，无需更新」。

## 说明

- 比对时忽略注释风格、空行和措辞上的差异，只关注结构性的不一致：路径、方法、字段名、类型。
- 实体字段用驼峰，文档字段用 snake_case 的，统一转换以后再匹配。
- `targetModule` 做模糊匹配：输入 `mcp`，可以匹配 `McpServerController` 和 `mcp_server` 表。
- 同一路径出现在多个 Controller 里（继承或覆盖）时，以最终注册生效的那个为准；扫描时注意类级前缀会叠加。
- `make-skill-legacy-takeover-output/1-project-map.md` 数据模型里「非主库存储」一节列出的实体，不参与 SQL 比对：<接手时填入，例如存放在 Redis / ES 里的实体>。
