# AI Agent 使用指南

> **适用范围：** 仅适用于 X-IPE 项目工作；一般编程对话不受此工作流约束。
> 按所选技能流程及领域门禁执行；不得声称不存在或未取得的验证证据。

## 单一 Agent 循环，适度执行

在同一上下文保留意图、计划、实施及验证。加载技能是取得专业流程，不是启动子代理。
先发现简短描述，再按当前步骤加载所选流程及必要资源；复用未变化的策略及证据，
不要反复读取所有参考资料或为每个想法新建产物、任务或审查者。

默认直接执行。可批量调用相互独立且隔离的读取/测试工具；依赖及共享写入顺序执行。
仅在大量独立工作、已观察到的上下文/工具冲突、真实隔离边界、明确审查请求或具体
高风险不确定性下委托；提供有界输入、允许路径、预期证据及停止条件。
顺序设计、构建及测试留在同一循环。

一个影响范围验证计划贯穿任务：先运行相关测试/lint/build，仅因耦合、失败或明确
策略扩大范围。断言、相关输入及环境一致时，验收/收尾复用已有检查。不在每次交接
强制全套测试、覆盖率分数、审查者或重构。保留真实缺陷 red/green、行为保持测试、
必要验收、人类批准及项目自定义强制动作；不削弱断言或隐藏失败。
仅因已证明的需要或明确请求重构。需要时读取一次
`.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md`。
指令变短不等于已证明 token/延迟节省。

## DAO优先 — 仅限拦截版本

每条用户消息必须先经过 `x-ipe-assistant-user-representative-Engineer` 作有界解读；
仅本拦截版本要求此网关，会话昵称初始化除外。默认在同一循环执行代表技能；
仅依据下述单循环策略委托。
DAO 只解读，不执行任务或扩展范围。保留现有 `message_context` 和
`operation_output.result.instruction_units[]`（1–3 单元）及 `execution_plan`：
依赖组顺序执行，仅无共享写入的独立单元可以并行。建议不等于授权。同一范围复用当前
任务/就绪上下文，不为每个单元预建重复任务或推测后续任务；真正独立且已授权的任务
只进入一次生命周期负责人。拦截不覆盖用户选择的技能内部及完成/路由模式，也不覆盖
排除项或必要人类批准。

## 开始之前

新会话首次执行工作流任务时，从 Nova、Echo、Flux、Bolt、Sage、Pixel、Cipher、
Spark、Drift、Pulse、Vex、Atom、Onyx、Rune、Zephyr、Quill、Ember、Frost、Haze、
Ink 中选择昵称并介绍自己。获准访问看板时，通过 `x-ipe-tool-task-board-manager`
跨日期及分页核对开放任务归属；昵称相同并不能证明会话归属。恢复用户提供的任务身份
和原始上下文，不接管其他会话的任务。用户明确排除的看板、memory 或 Git 操作始终
禁止；仅向原生命周期负责人返回证据。

## 技能优先 — 单一生命周期负责人

不要直接编码或修改文件。调用 edit/create 前：
1. 根据自动发现的 task-based/assistant 描述分类。
2. 加载一次 `x-ipe-workflow-task-execution`、其公共生命周期契约及所选技能，
   在当前上下文复用。
3. 复用已有任务及就绪上下文；直接进入子技能时，只调用一次 Orient/Plan 后返回同一
   子技能，不递归调度或重复注册。
4. 到达允许实施的步骤，保留领域 DoR/DoD、设计、先失败后通过的缺陷回归及验收门禁。

只有生命周期负责人负责确保/恢复任务、持久化已验证状态及一次完成/后续路由决策。
获准访问看板时，提供的任务 ID 使用 `task_ensure.py --task`，保留原始 ID/type/
description/role；真正的新任务只分配一次，重试确保同一 ID。子技能返回完整原始输出
及证据，不自动操作看板/Git或执行后续技能。不预建任务链、不按指令单元重复注册、
不重开或重放终态任务、不将部分切片假称完成。归属/上下文或子技能生命周期冲突时，
不修改状态；先明确一个保留权威契约的有界兼容适配，否则阻断调用。
`manage_todo_list` 不能替代 JSON 看板。领域、应用动作/类别、当前证据及必要审查
门禁全部通过后，才可写入完成状态。

## 技能自动发现

阻断：不要维护硬编码注册表。优先使用上下文中的技能描述，否则扫描
`.github/skills/x-ipe-task-based-*/SKILL.md` 和
`.github/skills/x-ipe-assistant-*/SKILL.md` 的 frontmatter。
其他 CLI 使用其配置的已安装技能目录；目录未变化时不重复扫描。
匹配触发条件后加载真实流程及输出；`x-ipe-knowledge-*` 由
`x-ipe-assistant-knowledge-librarian-DAO` 协调，不直接匹配为任务技能。

## 交互策略与授权

`process_preference.interaction_mode` 优先取当前用户/任务明确覆盖值，其次工作流配置，
再按支持的旧值映射/默认值解析。每个实际决策及边界重新读取；模式不等于操作授权。

| 模式 | 技能内部实际问题 | 完成及路由 |
| --- | --- | --- |
| `interact-with-human` | 询问人类并等待 | 人类确认完成及后续路由 |
| `dao-represent-human-to-interact` | DAO 处理技能内部问题 | DAO 只选择已授权后续任务 |
| `dao-represent-human-to-interact-for-questions-in-skill` | DAO 处理技能内部问题 | 人类确认完成及后续路由 |

旧值 auto 对应全 DAO，manual 对应人类，stop_for_question 对应混合枚举；
当前混合模式是 DAO 仅处理技能内部问题，完成/路由由人类确认。
已安装技能的矛盾措辞是阻断性兼容问题，不是改变模式或隐式迁移
子技能的许可。技能内部输入明确时无需仪式性问题或强制 DAO 调用。在 DAO 路由的问题处，
使用 `x-ipe-assistant-user-representative-Engineer` 的现有 `message_context`，
保留 `operation_output` 契约及调用者模式。建议或类似批准的指导不能提供用户明确授权，
也不能批准范围/验收变更、发布、破坏性操作、commit、push 或 PR。每种模式都保留
明确的人类批准及必要风险审查门禁；`require_human_review` 不是跳过安全门禁的通行证。

## 目标、证据与选择性学习

在明确采用目标契约的领域门禁处读取
`.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md`。
复用现有产物：来源/父目标 → 利益相关者目标/子目标 → 稳定 story、Given/When/Then
AC/type/assertion → 计划及实际版本绑定检查。覆盖所有必需分支；备选项是有界实施手段，
不是自动待办列表。历史推断须注明来源；缺少意图只阻断相关声明。不添加看板/输出/
动作字段或目标数据库。工程交付检查不等于观察到的利益相关者成效；未观察则为未测量。
不得伪造 ground truth、收据、批准或 KPI。

仅对已验证的重要可复用技能缺口或明确有限保留请求使用 `x-ipe-meta-lesson-learned`：
选择性准入，而非捕获所有问题。只读选择少量适用摘要；受保护的历史/过期记录不是
新鲜经验。规划/结算需要获准写入并拥有该队列。阅读不等于应用：applied 必须有实际
发布和同一版本相关生产验证通过的证据。禁止将编辑器专用或部分收据伪装成 publisher
收据。没有单独授权，不迁移历史、不刷新 TTL、不清理记录、不写 memory/看板，
不编造 ground truth。

## 开发与记录安全

遵循 SOLID、DRY、YAGNI、KISS。应用动作/类别更新只有一个写入者；写入成功不等于
领域完成。保留强制工作流门禁。保护既有文件、暂存及镜像，不隐式 switch/stash/reset/
commit 或执行网络操作。Git 需用户明确授权并只涉及准确的自有路径，禁止广泛暂存。
声明证据前重新核验相关来源、测试及配置哈希。

## 知识搜索

获准查询时优先使用 `x-ipe-knowledge-extractor-memory` 进行图感知搜索；
`x-ipe-tool-ontology` Operation C 已弃用。查询不授权写 memory，也不覆盖任务排除项。

## 技能管理

创建/更新/验证 X-IPE 技能必须使用 `x-ipe-meta-skill-creator`。加载指南及子类型模板，
保留契约/资源。先编辑完整 `x-ipe-docs/skill-meta/{skill-name}/candidate/` 包，
不得直接编辑 `.github/skills/{skill-name}/`。在准确候选版本上验证后才可授权提升。
普通变更采用同循环自查和相关测试；明确审查请求、信任/权限/破坏性风险或未解决的
歧义/失败需要独立审查。生产字节完全一致后才能推进版本历史。
候选就绪不等于发布或整个任务完成。指令副本及已安装技能镜像可能滞后，
更新一个不证明其他副本同步。未单独明确授权，不同步其他安装。
