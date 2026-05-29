# Changelog

## [0.3.0] - 2026-05-29

### 🔧 工程化与健壮性

**新增功能：**
- 🩺 `hermes-team doctor` 命令 — 诊断配置问题，支持 `--fix` 自动修复
- 💥 `hermes-team destroy` 命令 — 清理团队（停止 Gateway、删除 Profile）
- 📄 `CONTRIBUTING.md` — 贡献指南，包含开发环境搭建和 PR 流程

**模板更新：**
- 📐 所有 SOUL.md 模板新增 Hub-and-Spoke 协作模式说明
- 🎯 明确成员间不互相 @、一切通过总管协调的协作规则

**工程化：**
- 🧪 新增测试套件（pytest），覆盖核心命令逻辑
- 🔄 新增 GitHub Actions CI（lint + test on push/PR）
- 📦 修复 `templates` 目录未被打包进 wheel/sdist 的问题

**文档：**
- 📚 README 新增「项目定位」章节（CLI 工具 + Hermes Skill 双模式）
- 📚 README 命令列表补充 `doctor`、`destroy`
- 📚 CHANGELOG 记录本轮工程化改进

## [0.2.0] - 2026-05-29

### 🔄 架构升级：Hub-and-Spoke 协作模式

**新增功能：**
- 📐 **Hub-and-Spoke 协作架构**：明确总管作为中心节点的协调模式
- 🎯 **Skill 定位描述**：每个角色的核心职责和产出物定义
- 📚 **README 更新**：新增协作模式说明和角色职责表

**改进：**
- ✅ 优化团队协作流程，避免 Agent 间直接通信
- ✅ 强化角色边界，每个 Agent 专注自己的专业领域
- ✅ 完善文档，提升新用户理解效率

**文档更新：**
- README 新增「Hub-and-Spoke 协作模式」章节
- README 新增「Skill 定位（角色职责）」章节
- CHANGELOG 记录本轮架构升级

## [0.1.0] - 2026-05-29

### 🎉 Initial Release

**核心功能：**
- `hermes-team init` — 一键创建 Hermes profiles + 生成 SOUL.md 人设模板
- `hermes-team configure` — 交互式配置飞书 App 凭证
- `hermes-team start` — 批量启动所有 gateway
- `hermes-team collect-ids` — 自动从 gateway 日志提取 per-app open_id
- `hermes-team verify` — 全面验证团队配置是否正确
- `hermes-team status` — 团队状态一览

**支持的角色模板：**
- 总管/协调员 (coordinator)
- 产品经理 (pm)
- 前端开发 (frontend)
- 后端开发 (backend)
- 测试QA (qa)
- UI设计 (designer)

**自动处理的已知问题：**
- ✅ 飞书 open_id per-app 隔离
- ✅ bot-to-bot 通信配置 (FEISHU_ALLOW_BOTS, FEISHU_REQUIRE_MENTION)
- ✅ 事件订阅范围检查
- ✅ SOUL.md 中 @mention 格式校验
- ✅ .env 凭证配置
