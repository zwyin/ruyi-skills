# Competitive Research: GitHub Safe Publish

调研日期：2026-05-25

## 核心结论

**市场空白已确认。** 现有任何工具或 skill 都没有将多维度脱敏扫描 + 仓库创建 + 链接更新 + SEO 优化整合到一个工作流中。

---

## 1. Claude Code Skills

### sync-skills-public (dazuck / LobeHub)
- URL: https://lobehub.com/skills/dazuck-claude-code-skills-sync-skills-public
- 功能：将 Claude Code skills 的脱敏副本导出到 public 仓库。基于模式检测扫描 API key、凭证、PII 和 token。
- 差异：只扫描 skill 文件（非完整仓库），单次扫描（非多轮），维度较少。无 SEO、无仓库创建、无链接更新。

### github-release (jezweb/claude-skills)
- URL: https://github.com/jezweb/claude-skills (799 star)
- 功能：创建和发布 GitHub Release 的多阶段工作流。阶段 1 清理密钥（阻断器），删除个人制品，验证 LICENSE/README/.gitignore。
- 差异：专注 release 管理，非"走向开源"。单轮清理。无 SEO、无链接更新。

### publish-to-github (joogy06 / LobeHub)
- URL: https://lobehub.com/it/skills/joogy06-agent-foundry-publish-to-github
- 功能：将 skills/agents 目录转换为干净、公开安全的输出并发布到 GitHub。
- 差异：范围极窄——只处理 skills/agents 目录。无多轮扫描、无 SEO。

### Anthropic Cybersecurity Skills
- URL: https://github.com/mukul975/Anthropic-Cybersecurity-Skills (8,723 star)
- 功能：教学性质——指导 Claude 如何使用 Gitleaks，设置 pre-commit hooks 和 CI/CD 集成。
- 差异：教学而非自动化，不覆盖完整发布流程。

---

## 2. 密钥/凭证扫描器（CLI 工具）

| 工具 | Star | 语言 | 许可证 | 特点 |
|------|------|------|--------|------|
| [Gitleaks](https://github.com/gitleaks/gitleaks) | 27,267 | Go | MIT | 200+ 密钥类型，pre-commit hook，GitHub Action，基线支持 |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | 26,483 | Go | AGPL-3.0 | 可验证密钥有效性（调 API 检查），700+ 检测规则 |
| [git-secrets](https://github.com/awslabs/git-secrets) | 13,315 | Shell | Apache-2.0 | AWS 出品，较老，已被 Gitleaks/TruffleHog 取代 |
| [detect-secrets](https://github.com/Yelp/detect-secrets) | 4,519 | Python | Apache-2.0 | 启发式检测（非纯正则），审计工作流 |
| [ggshield](https://github.com/gitguardian/ggshield) | 1,954 | Python | MIT | GitGuardian 开源 CLI，500+ 密钥类型 |

**共同局限**：全部只做密钥/令牌这一个维度。无 PII 检测、无内部 URL/路径检测、无品牌名称检测、无 SEO、无仓库创建。

---

## 3. Git 历史清理工具

| 工具 | Star | 特点 |
|------|------|------|
| [git-filter-repo](https://github.com/newren/git-filter-repo) | 12,440 | Git 官方推荐的 filter-branch 替代品，Python |
| [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) | 12,117 | 更简单的界面，Scala，维护较少 |

**局限**：单一功能——重写历史。不扫描新密钥，不处理 SEO。

---

## 4. 开源准备自动化

### World Bank Open Source Kit
- URL: https://github.com/worldbank/open-source-kit (4 star)
- 功能：可复用的 GitHub Actions 工作流和清单。检查 LICENSE、README、密钥、数据文件、依赖许可证、代码质量。
- 差异：最接近"自动化开源准备"的 GitHub Action。但只检查不修复，无 SEO、无仓库创建。

### FINOS Open Source Readiness
- URL: https://www.finos.org/open-source-readiness
- 功能：金融科技开源基金会的合规工作流和 GitHub Actions。
- 差异：专注治理/合规，非技术清理。

---

## 5. 代码去标识化工具

| 工具 | Star | 特点 |
|------|------|------|
| [stoken](https://github.com/laorange/stoken) | 3 | 代码去标识化 CLI，替换 token/密钥 |
| [repobee-sanitizer](https://github.com/repobee/repobee-sanitizer) | 2 | RepoBee 插件，基于标记的内容删除/替换，教育用途 |
| [git-splitter](https://github.com/operasoftware/git-splitter) | 31 | 从内部仓库拆分子目录到公开仓库，带历史 |

**共同局限**：星标极低，社区采用少。都是单功能。

---

## 功能对比矩阵

| 功能 | github-safe-publish | Gitleaks | TruffleHog | sync-skills-public | github-release | git-filter-repo | World Bank Kit |
|------|---------------------|----------|------------|-------------------|----------------|-----------------|----------------|
| 多轮扫描 (5轮收敛) | 5 轮 | 1 轮 | 1 轮 | 1 轮 | 1 轮 | - | 清单 |
| 扫描维度 | 7 维 | 1(密钥) | 1(密钥) | 3(密钥/PII/token) | 2(密钥/制品) | - | 清单 |
| GitHub 仓库创建 | 有 | 无 | 无 | 部分 | 无 | 无 | 无 |
| 占位链接更新 | 有 | 无 | 无 | 无 | 无 | 无 | 无 |
| SEO 优化 | 有 | 无 | 无 | 无 | 无 | 无 | 无 |
| CI 设置指导 | 有 | Action | Action | 无 | 无 | 无 | 有 |
| Git 历史清理 | 指导 | - | - | - | - | 有 | - |

## 差异化定位

github-safe-publish 的核心优势：

1. **多轮迭代扫描**（5 轮带收敛检查）— 没有任何现有工具做到
2. **7 维度分析**（密钥、PII、内部 URL、硬编码路径、品牌/名称、注释泄露、许可证合规）— 现有工具主要覆盖 1-2 维
3. **端到端流程**（脱敏 → 仓库创建 → 链接更新 → 推送 → SEO → CI）— 现有工具只做其中一个环节
4. **Claude Code 原生**（作为 skill 运行，无需安装额外 CLI 工具）

目标用户：希望将个人/团队项目开源的开发者，希望用一个 skill 完成全流程，而不是手动编排 5+ 个独立工具。
