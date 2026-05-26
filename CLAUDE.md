# ruyi-skills

Claude Code skill 合集的唯一开发仓库。

## 设计原则

### Skill 自包含
SKILL.md 及 references/ 内不得链接 skill 目录外的文件。每个 skill 必须能被独立提取使用。

### 单一 marketplace
一个 marketplace.json 列所有 skills，用户一次安装。

### 双层版本
- Skill 版本：各 SKILL.md frontmatter
- 合集版本：marketplace.json

## 推送命令

本地代理拦截 HTTPS，需显式绕过：

```bash
git -c http.proxy="" -c https.proxy="" push ruyi main
```

## 多品牌架构

ruyi-skills 是唯一开发仓库。其他品牌仓库（paoding/davinci/doraemon）
通过独立的 brand-sync-tool 从 ruyi-skills 生成，各自拥有独立的 git 历史。

转换工具不在本仓库中，维护在 private 仓库。

## Remotes

| Remote | GitHub 仓库 | 用途 |
|--------|-----------|------|
| ruyi | zwyin/ruyi-skills | 开发 + 推送 |

其他品牌通过 brand-sync-tool 生成，不再作为 remote 添加到本仓库。
