# Copilot 使用指南

## 开始之前
**时机：** 开始新对话时
**操作：**
1. **从以下名称池中随机选择一个昵称：**
   - Nova, Echo, Flux, Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr, Quill, Ember, Frost, Haze, Ink
2. **验证昵称是否已被使用：**
   - 检查 `x-ipe-docs/planning/task-board.md` 的活跃任务部分
   - 如果有其他会话使用相同昵称且状态为 `🔄 in_progress` → 换一个名字
   - 如果是当前会话的任务 → 保留原名
   - 重复直到找到未使用的名字
3. 介绍自己："你好，我是 [昵称]"
4. 此昵称是你的任务分配标识
5. 检查分配给你的待办任务
6. 只处理分配给你或未分配的任务

**时机：** 开始任何工作之前
**操作：**

1. 检查 Agent 模型是否支持 Anthropic skills protocol。
2. 如果支持，加载技能：`x-ipe-workflow-task-execution`。
2. 如果不支持，执行以下操作：
   - 阅读 `.github/skills/x-ipe-workflow-task-execution/` 文件夹下的文件以理解任务执行指南。
   - **重要：** 指南中提到的每种任务类型都必须有对应的技能文件在 `.github/skills/` 文件夹下。SKILL.md 是理解每个技能的入口。

---

## ⚠️ 关键：DAO优先 — 每条消息都经过人类代表

**每条用户消息必须先经过 `x-ipe-dao-end-user-representative` 处理，然后再执行任何其他操作。**

这是通用网关。无论用户说什么 — 命令、问题、反馈、批准 — 消息都先经过人类代表技能。DAO 解读消息、选择处置方式，Agent 根据结构化输出采取行动。

### 消息处理流程

当你收到用户消息时（会话初始化之后）：

1. **内部调用 `x-ipe-dao-end-user-representative`**，传入：
   ```yaml
   message_context:
     source: "human"
     calling_skill: "copilot-instructions"
     task_id: "{当前任务ID 或 N/A}"
     feature_id: "{当前功能ID 或 N/A}"
     workflow_name: "{当前工作流 或 N/A}"
     downstream_context: "{当前Agent状态 — 活跃任务、待回答问题、技能阶段}"
     messages:
       - content: "{用户原始消息}"
   human_shadow: false
   ```

2. **根据 DAO 处置结果行动：**

   | 处置方式 | 含义 | Agent行动 |
   |---------|------|----------|
   | `instruction` | 用户在下达指令（如"修复这个bug"、"实现功能X"） | → 进入下方**技能分类**流程 |
   | `approval` | 用户在批准待处理工作（如"lgtm"、"继续"、"自动继续"） | → 继续当前技能/工作流的下一步 |
   | `answer` | 用户在提供请求的信息 | → 输入到当前任务上下文，继续当前技能 |
   | `clarification` | 用户在澄清之前的问题 | → 用澄清信息更新当前任务，继续 |
   | `critique` | 用户在给出当前工作的反馈 | → 根据反馈调整当前方案，留在当前技能 |
   | `reframe` | 用户在完全重定向焦点 | → 重新评估 — 可能需要切换任务或技能 |
   | `pass_through` | 消息不需要调解 | → Agent直接处理，不经过技能路由 |

3. **只有在 DAO 处理之后** → 才能进行技能分类、任务创建或执行。

### 模型要求

当 `x-ipe-dao-end-user-representative` 被委托给子Agent执行时（如通过 `task` 工具），**必须使用最强大的（premium）LLM 模型**（如 `model: "claude-opus-4.6"`）。七步骨架需要精细推理 — 权衡三方视角、分析得失、场景推演 — 快速/廉价模型无法可靠处理。如果在主Agent内联执行，则自动使用主Agent的模型。

### 为什么 DAO优先 很重要

- **一致的解读** — 每条消息都获得结构化分析，而非临时模式匹配
- **上下文感知路由** — DAO 在解读时考虑当前任务、功能和工作流状态
- **处置驱动分支** — Agent的下一步行动由清晰、有界的信号决定，而非原始文本解析
- **有界范围** — DAO 仅解读意图。它不执行任务、不编写代码、不承担技能职责

---

## ⚠️ 关键：技能优先，而非直接编码

**当 DAO 返回处置 `instruction`（用户在下达指令）时，不要直接跳到编码或修改文件。**

### 🚫 硬性门禁：未加载技能禁止调用 `edit` / `create`

在调用 **任何** 文件编辑工具（`edit`、`create` 或通过 `bash` 写代码）之前，你必须：
1. ✅ 已通过 `x-ipe-dao-end-user-representative` 处理消息（处置 = `instruction`）
2. ✅ 已将请求分类到对应的任务技能
3. ✅ 已在 `task-board.md` 上创建任务
4. ✅ 已加载对应技能（通过 `skill` 工具或阅读其 `SKILL.md`）
5. ✅ 已到达技能流程中允许修改代码的步骤

如果以上任何一项缺失 → **停下来，不要修改代码。**

### 分析 DAO 输出

当 DAO 处置为 `instruction` 时：

1. **使用 DAO 的解读** — 消息已被理解和分类
2. **匹配对应技能** — 扫描 `.github/skills/x-ipe-task-based-*/SKILL.md` 描述找到正确的技能
3. **加载并遵循该技能** — 技能定义了正确的流程、前置条件和完成定义

### 为什么这很重要

即使修复看起来很简单（例如"修改默认端口"），正确的做法是：
- 用户说"修复这个 bug" → 使用 `x-ipe-task-based-bug-fix`（先写失败测试，再修复）
- 用户说"这个配置不对" → 仍然是 bug 修复 → 使用 `x-ipe-task-based-bug-fix`
- 用户说"添加一个新接口" → 使用 `x-ipe-task-based-code-implementation`
- 用户说"重构这个模块" → 使用 `x-ipe-task-based-code-refactor`

**技能确保质量** — 它强制执行测试覆盖、文档更新和审查步骤，这些都是直接编码会跳过的。

### ⛔ 反模式：未经 DAO + 技能 直接修复

```
❌ 用户："默认端口不对，修复一下"
   Agent：*直接编辑 config.py 并更新 3 个文件*

✅ 用户："默认端口不对，修复一下"
   Agent：*DAO 解读 → 处置: instruction →
           分类为 bug 修复 → 加载 x-ipe-task-based-bug-fix →
           在看板创建任务 → 写失败测试 → 修复代码 →
           验证测试通过 → 更新看板*
```

### ⛔ 真实案例教训：TASK-681

```
❌ 实际发生的：
   用户："CLI 适配器返回 copilot 而不是 opencode"
   Agent：*直接找到 _read_active_cli()，加了 isinstance 检查，
           修复之后才写测试，没有任务看板记录*

✅ 应该这样做：
   Agent：*DAO 解读 → 处置: instruction →
           分类为 bug 修复 → 加载 x-ipe-task-based-bug-fix →
           在看板创建 TASK-681 → 诊断根因 →
           执行冲突分析 → 先写失败测试 →
           实现修复 → 验证测试通过 → 更新看板*
```

技能发现了直接修复遗漏的内容：冲突分析（检查所有调用方）、TDD 验证（证明测试在修复前失败）、任务追踪。

---

## ⚠️ 关键：任务看板是唯一的真实来源

**任务看板 (`x-ipe-docs/planning/task-board.md`) 是所有工作的必备工具。**

### 开始任何工作之前：
1. **在 task-board.md 上创建任务** 使用 `x-ipe+all+task-board-management` 技能
2. **验证任务已在看板上**（x-ipe-workflow-task-execution 的第2步）
3. **然后才能** 开始实际工作

### 完成工作之后：
1. **更新 task-board.md** — 将任务移至已完成部分
2. **更新 Quick Stats** — 增加完成计数

### ⛔ 绝对不要：
- 用 `manage_todo_list` 替代 task-board.md（那是 VS Code 内部功能）
- 在看板上没有任务ID就开始工作
- 完成工作后不更新看板

---

## ⚠️ 严格要求：任务匹配与技能执行

### 强制任务分类

**在做任何工作之前**，Agent 必须：

1. **通过 DAO 处理消息** — 调用 `x-ipe-dao-end-user-representative` 解读用户意图
2. **将工作分类到对应技能** — 使用自动发现（扫描 `.github/skills/x-ipe-task-based-*/`）
3. **在 task-board.md 上创建任务** 通过 `x-ipe+all+task-board-management` 技能 ← **阻断操作**
4. **加载对应技能** 从 `.github/skills/` 文件夹
5. **按照技能的执行流程** 逐步执行
6. **完成技能的完成定义 (DoD)** 才能标记完成
7. **更新 task-board.md** 的完成状态 ← **必须操作**

### 技能自动发现

阻断：不要维护硬编码的注册表。技能通过自动发现获取。

**发现规则：**
1. 扫描 `.github/skills/x-ipe-task-based-*/SKILL.md`
2. 每个技能的 Output Result YAML 声明：`category`、`next_task_based_skill`、`process_preference.auto_proceed`
3. 每个技能 frontmatter 中的 `description` 包含用于请求匹配的触发关键词

**请求匹配：** 将用户请求与每个技能描述中的触发关键词进行匹配（如"修复bug" → `x-ipe-task-based-bug-fix`，"实现功能" → `x-ipe-task-based-code-implementation`）。

> **注意：** 当**自动继续已启用**（全局或任务级别）时，无论技能的默认设置如何，`require_human_review` 都会被**跳过**。`process_preference.auto_proceed` 枚举值（`manual | auto | stop_for_question`）控制此行为。

> **注意：** DAO优先 是通用的 — 它适用于所有模式（`auto`、`manual`、`stop_for_question`）。模式影响的是技能*内部*决策点是否也经过 DAO（auto）或直接询问人类（manual/stop_for_question）。但初始消息始终经过 DAO。

### 🛑 停下来思考：预检清单

**在修改任何代码或做任何更改之前，问自己：**

```
0. 我是否通过 DAO 处理了这条消息？ → 如果没有，停下来调用 x-ipe-dao-end-user-representative
1. 这是什么任务技能？ → 扫描 `.github/skills/x-ipe-task-based-*/` 描述
2. 我在 task-board.md 上创建了任务吗？ → 如果没有，停下来创建
3. 我加载了对应的技能吗？ → 如果没有，停下来加载
4. 我在按照技能的流程执行吗？ → 如果没有，停下来阅读
5. 技能流程是否已到达允许修改代码的步骤？ → 如果没有，停下来
```

**如果你发现自己即将调用 `edit`、`create` 或通过 `bash` 写代码，但没有完成上述步骤 0-5 — 立即停下来。回去遵循流程。**

**常见错误：**
- 用户说"重构这个" → 你必须使用 `x-ipe-task-based-code-refactor` 技能，不要直接开始编码
- 用户说"修复这个" → 你必须使用 `x-ipe-task-based-bug-fix` 技能，不要直接修复
- 用户说"添加这个功能" → 你必须先识别正确的任务技能

### ⚠️ 不要跳过技能

**禁止的操作：**
- ❌ 不经过 DAO 就处理用户消息
- ❌ 没有在 task-board.md 上创建任务就开始工作
- ❌ 用 `manage_todo_list` 替代 task-board.md
- ❌ 完成工作后不更新 task-board.md
- ❌ 不检查已有测试就直接写代码
- ❌ 不先写失败测试就修复 bug
- ❌ 不阅读技术设计就实现功能
- ❌ 不按照技能执行流程做更改
- ❌ 不使用 `x-ipe-task-based-code-refactor` 技能就重构代码

**必须的操作：**
- ✅ 始终先通过 `x-ipe-dao-end-user-representative` 处理用户消息
- ✅ 开始工作前必须在 task-board.md 上创建任务
- ✅ 必须先识别对应的任务技能
- ✅ 必须加载并遵循对应技能
- ✅ 必须检查前置条件 (DoR)
- ✅ 必须完成完成定义 (DoD)
- ✅ 完成工作后必须更新 task-board.md

---

## 下一步建议 (OpenCode & Claude CLI)

> **CLI 代理的注意事项：** 完成 X-IPE 任务流程中的任务时，响应结尾的"下一步"建议**必须**基于已完成技能的 Output Result YAML 中的 `next_task_based_skill` 字段 — 而非通用建议。阅读技能的 `task_completion_output` 部分确定推荐的下一步操作并呈现给用户。
>
> 例如，如果已完成技能声明 `next_task_based_skill: "Feature Acceptance Test"`，建议：*"下一步：运行功能验收测试 (x-ipe-task-based-feature-acceptance-test)"*，而非通用的"您接下来想做什么？"。
>
> 如果 `next_task_based_skill` 为空或任务是独立的，可以建议一般性的下一步操作。

---

## 人机交互

### 审批识别

- 除非人类明确说出以下词语，否则不要假设已获批准：`approve`、`confirmed`、`lgtm`、`looks good`、`go ahead`、`proceed`
- 如果人类给出反馈但没有批准 → 保持任务在当前状态
- 如有疑问，询问："是否批准继续？"

---

## 开发原则

始终遵循：
1. **SOLID** - 设计原则
3. **YAGNI** - 你不会需要它
4. **KISS** - 保持简单

---

## 技能管理

### 创建、更新或验证 X-IPE 技能

**时机：** 创建新技能、更新现有技能或验证技能结构（适用于所有技能类型：task-based、tool、workflow-orchestration、task-category、meta）
**操作：** 必须使用 `x-ipe-meta-skill-creator` 技能

关键：任何对已定义类型技能（x-ipe-task-based、x-ipe-tool、x-ipe-workflow-orchestration、x-ipe-task-category、x-ipe-meta）的修改必须通过 `x-ipe-meta-skill-creator`。不要在不加载和遵循技能创建流程的情况下直接编辑 SKILL.md 文件。

⛔ **禁止直接编辑 `.github/skills/{skill-name}/` 下的文件。** 所有修改必须先在候选目录（`x-ipe-docs/skill-meta/{skill-name}/candidate/`）中进行，验证通过后再合并到生产目录。直接编辑线上技能会跳过验证流程，可能导致生产环境异常。

```
1. 加载技能：`x-ipe-meta-skill-creator`
2. 按照技能创建流程执行
3. 根据技能类型使用对应模板：
   - Task-Based → templates/x-ipe-task-based.md
   - Tool Skill → templates/x-ipe-tool.md
   - Workflow Orchestration → templates/x-ipe-workflow-orchestration.md
   - Meta Skill → templates/x-ipe-meta.md
4. 完成前验证技能创建检查清单
```

### 记录技能改进经验

**时机：** 技能执行有问题、人类提供反馈或 Agent 观察到次优行为
**操作：** 使用 `x-ipe-meta-lesson-learned` 技能

```
1. 加载技能：`x-ipe-meta-lesson-learned`
2. 按照经验记录流程执行
3. 经验存储在 x-ipe-docs/skill-meta/{skill}/lesson-learned.md
4. 下次更新技能时会纳入这些经验
```
