# Copilot 使用指南

> **⚠️ AI Agent 执行建议技能时的关键规则：**
> 严格按照技能中的步骤执行！不得跳过、重排或自行发挥。
> 严格按照技能中的步骤执行！不得跳过、重排或自行发挥。
> 严格按照技能中的步骤执行！不得跳过、重排或自行发挥。

> **适用范围：** 这些规则仅适用于 X-IPE 项目代码库的工作。一般编程问题、解释或不涉及修改 X-IPE 文件的对话不受技能/任务看板工作流约束。

## 开始之前

**时机：** 在新会话中开始第一个 x-ipe 工作流任务时
**操作：**
1. **从以下名称池中随机选择一个昵称：**
   - Nova, Echo, Flux, Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr, Quill, Ember, Frost, Haze, Ink
2. **验证昵称是否已被使用：**
   - 通过 `x-ipe-tool-task-board-manager` (task_query.py --status in_progress) 查询活跃任务
   - 如果有其他会话使用相同昵称且状态为 `🔄 in_progress` → 换一个名字
   - 如果是当前会话的任务 → 保留原名
   - 重复直到找到未使用的名字
3. 介绍自己："你好，我是 [昵称]"
4. 此昵称是你的任务分配标识
5. 检查分配给你的待办任务
6. 只处理分配给你或未分配的任务

---

## ⚠️ 关键：技能优先，而非直接编码

**不要直接跳到编码或修改文件。**

### 🚫 硬性门禁：未加载技能禁止调用 `edit` / `create`

在调用任何文件编辑工具（`edit`、`create` 或通过 `bash` 写代码）之前，你必须：
1. ✅ 已将请求分类到对应的任务技能（通过自动发现）
2. ✅ 已通过 `x-ipe-tool-task-board-manager` 创建任务
3. ✅ 已加载对应技能（通过 `skill` 工具或阅读其 `SKILL.md`）
4. ✅ 已到达技能流程中允许修改代码的步骤

如果以上任一步骤缺失 → **停下来，不要修改代码。**


### ⛔ 真实案例教训：

```
❌ 实际发生的：
   用户："CLI 适配器返回 copilot 而不是 opencode"
   Agent：*直接找到 _read_active_cli()，加了 isinstance 检查，
           修复之后才写测试，没有任务看板记录*

✅ 应该这样做：
   Agent：*分类为 bug 修复 → 加载 x-ipe-task-based-bug-fix →
           Phase 0：通过 x-ipe-tool-task-board-manager 在看板创建 TASK-681 →
           诊断根因 → 先写失败测试 →
           实现修复 → 验证测试通过 →
           最终步骤：通过 x-ipe-tool-task-board-manager 更新看板（任务完成）*
```

---

## ⚠️ 关键：任务看板是唯一的真实来源

**任务看板（JSON格式，由 `x-ipe-tool-task-board-manager` 管理）是所有工作的必备工具。**

### 开始任何工作之前：
1. **使用 `x-ipe-tool-task-board-manager` 技能创建任务**（每个任务型技能在其 Phase 0 中自动执行）
2. **验证任务已在看板上** 后再继续
3. **然后才能** 开始实际工作

### 完成工作之后：
1. **更新任务状态** — 通过 `x-ipe-tool-task-board-manager` 设为已完成
2. **更新 Quick Stats** — 增加完成计数

### ⛔ 绝对不要：
- 用 `manage_todo_list` 替代 JSON 任务看板（那是 VS Code 内部功能）
- 在看板上没有任务ID就开始工作
- 完成工作后不更新看板

---

## ⚠️ 严格要求：任务匹配与技能执行

### 强制工作流

所有工作遵循下方的预检清单。使用 `x-ipe-tool-task-board-manager` 创建/更新任务。

### 任务技能识别

## 技能自动发现

阻断：不要维护硬编码的注册表。技能通过自动发现获取。

**发现规则：**
1. 如果上下文中已有技能附件列表，直接用于匹配（无需扫描文件系统）
2. 否则，扫描 `.github/skills/x-ipe-task-based-*/SKILL.md`
3. 每个技能的 `description` 包含用于请求匹配的触发关键词

**请求匹配：** 将用户请求与每个技能描述中的触发关键词进行匹配（如"修复bug" → `x-ipe-task-based-bug-fix`，"实现功能" → `x-ipe-task-based-code-implementation`）。

> **注意：** 当**交互模式为 DAO 模式**（全局或任务级别）时，无论技能的默认设置如何，`require_human_review` 都会被**跳过**。`process_preference.interaction_mode` 枚举值（`interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill`）控制此行为。

> **注意：** `interaction_mode` 控制技能*内部*决策点是通过 `x-ipe-dao-end-user-representative` 技能（作为人类代表）处理，还是直接询问人类。这是技能内部的关注点 — 当 `interaction_mode == "dao-represent-human-to-interact"` 时，技能在自己的决策点调用 DAO。

### 🛑 停下来思考：预检清单

**在修改任何代码或做任何更改之前，问自己：**

```
1. 这是什么任务技能？ → 扫描 `.github/skills/x-ipe-task-based-*/` 描述
2. 我在任务看板上创建了任务吗？ → 如果没有，停下来创建
3. 我加载了对应的技能吗？ → 如果没有，停下来加载
4. 我在按照技能的流程执行吗？ → 如果没有，停下来阅读
5. 技能流程是否已到达允许修改代码的步骤？ → 如果没有，停下来
```

**如果你发现自己即将调用 `edit`、`create` 或通过 `bash` 写代码，但没有完成上述步骤 1-5 — 立即停下来。回去遵循流程。**

**常见错误：**
- 用户说"重构这个" → 你必须使用 `x-ipe-task-based-code-refactor` 技能，不要直接开始编码
- 用户说"修复这个" → 你必须使用 `x-ipe-task-based-bug-fix` 技能，不要直接修复
- 用户说"添加这个功能" → 你必须先识别正确的任务技能

---

## 开发原则

始终遵循：
1. **SOLID** - 设计原则
2. **DRY** - 不要重复自己
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
