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

1. **将工作分类到对应技能** — 使用自动发现（扫描 `.github/skills/x-ipe-task-based-*/`）
2. **在 task-board.md 上创建任务** 通过 `x-ipe+all+task-board-management` 技能 ← **阻断操作**
3. **加载对应技能** 从 `.github/skills/` 文件夹
4. **按照技能的执行流程** 逐步执行
5. **完成技能的完成定义 (DoD)** 才能标记完成
6. **更新 task-board.md** 的完成状态 ← **必须操作**

### 技能自动发现

阻断：不要维护硬编码的注册表。技能通过自动发现获取。

**发现规则：**
1. 扫描 `.github/skills/x-ipe-task-based-*/SKILL.md`
2. 每个技能的 Output Result YAML 声明：`category`、`next_task_based_skill`、`require_human_review`
3. 每个技能 frontmatter 中的 `description` 包含用于请求匹配的触发关键词

**中文请求匹配关键词：**

| 中文关键词 | 对应技能 |
|-----------|---------|
| 优化创意、完善想法、头脑风暴、分析我的想法 | x-ipe-task-based-ideation-v2 |
| 收集需求、新功能、我想构建 | x-ipe-task-based-requirement-gathering |
| 分解功能、拆分功能、创建功能列表 | x-ipe-task-based-feature-breakdown |
| 细化功能、详细规格、明确需求 | x-ipe-task-based-feature-refinement |
| 技术设计、架构规划、设计功能 | x-ipe-task-based-technical-design |
| 生成测试、编写测试、TDD | x-ipe-task-based-test-generation |
| 实现功能、编写代码、开发功能 | x-ipe-task-based-code-implementation |
| 修复bug、出错了、不工作 | x-ipe-task-based-bug-fix |
| 重构代码、代码重构 | x-ipe-task-based-code-refactor |
| 变更请求、修改功能、更新需求 | x-ipe-task-based-change-request |
| 创建原型、可视化想法、设计原型 | x-ipe-task-based-idea-mockup |
| 创建架构图、系统设计、架构图 | x-ipe-task-based-idea-to-architecture |
| 初始化项目、启动新项目、配置项目 | x-ipe-task-based-project-init |
| 搭建环境、开发环境、配置工作空间 | x-ipe-task-based-dev-environment |
| 创建文档、用户手册、更新README | x-ipe-task-based-user-manual |
| 运行验收测试、测试功能UI | x-ipe-task-based-feature-acceptance-test |
| 关闭功能、创建PR、发布功能 | x-ipe-task-based-feature-closing |
| 创建演示、人工测试、交互演示 | x-ipe-task-based-human-playground |
| 分享想法、转换为PPT、制作演示 | x-ipe-task-based-share-idea |
| 重构分析、评估重构范围 | x-ipe-task-based-refactoring-analysis |
| 提升代码质量、同步文档与代码 | x-ipe-task-based-improve-code-quality |

> **注意：** 当**自动继续已启用**（全局或任务级别）时，无论技能的默认设置如何，`require_human_review` 都会被**跳过**。

### 🛑 停下来思考：预检清单

**在修改任何代码或做任何更改之前，问自己：**

```
1. 这是什么任务技能？ → 扫描 `.github/skills/x-ipe-task-based-*/` 描述
2. 我在 task-board.md 上创建了任务吗？ → 如果没有，停下来创建
3. 我加载了对应的技能吗？ → 如果没有，停下来加载
4. 我在按照技能的流程执行吗？ → 如果没有，停下来阅读
```

### ⚠️ 不要跳过技能

**禁止的操作：**
- ❌ 没有在 task-board.md 上创建任务就开始工作
- ❌ 用 `manage_todo_list` 替代 task-board.md
- ❌ 完成工作后不更新 task-board.md
- ❌ 不检查已有测试就直接写代码
- ❌ 不先写失败测试就修复 bug
- ❌ 不阅读技术设计就实现功能
- ❌ 不按照技能执行流程做更改
- ❌ 不使用 `x-ipe-task-based-code-refactor` 技能就重构代码

**必须的操作：**
- ✅ 开始工作前必须在 task-board.md 上创建任务
- ✅ 必须先识别对应的任务技能
- ✅ 必须加载并遵循对应技能
- ✅ 必须检查前置条件 (DoR)
- ✅ 必须完成完成定义 (DoD)
- ✅ 完成工作后必须更新 task-board.md

---

## 下一步建议 (OpenCode & Claude CLI)

> **CLI 代理的注意事项：** 完成 X-IPE 任务流程中的任务时，响应结尾的"下一步"建议**必须**基于已完成技能的 Output Result YAML 中的 `next_task_based_skill` 字段。
>
> 例如，如果已完成技能声明 `next_task_based_skill: "Feature Acceptance Test"`，建议："下一步：运行功能验收测试 (x-ipe-task-based-feature-acceptance-test)"。
>
> 如果 `next_task_based_skill` 为空或任务是独立的，可以建议一般性的下一步操作。

---

## 人机交互

### 审批识别

- 除非人类明确说出以下词语，否则不要假设已获批准：`approve`、`confirmed`、`lgtm`、`looks good`、`go ahead`、`proceed`、`批准`、`确认`、`通过`、`可以`、`继续`
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

**时机：** 创建新技能、更新现有技能或验证技能结构
**操作：** 必须使用 `x-ipe-meta-skill-creator` 技能

```
1. 加载技能：`x-ipe-meta-skill-creator`
2. 按照技能创建流程执行
3. 根据技能类型使用对应模板
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