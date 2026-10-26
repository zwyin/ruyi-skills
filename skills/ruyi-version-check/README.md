# ruyi-version-check

[![version](https://img.shields.io/badge/version-0.1.2-blue)](./CHANGELOG.md)

版本一致性检查器——核对 ruyi-skills 合集里每一处版本号是否与 canonical（SKILL.md frontmatter）一致。

## 快速使用

```bash
# 检查整个合集
python3 skills/ruyi-version-check/scripts/validate_versions.py --root .

# 只查单个 skill
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --skill ruyi-project-walkthrough

# JSON 输出（CI 用）
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --format json

# 严格模式（发版前建议）：WARN 也算不通过
python3 skills/ruyi-version-check/scripts/validate_versions.py --root . --strict
```

退出码：`2` 有 FAIL；默认模式只有 WARN 时 `0`（WARN 不阻塞 CI）；`--strict` 时只有 WARN → `1`。

## 检查范围

- **合集层**：marketplace.json version vs CHANGELOG 最新条目
- **每个 skill**：frontmatter / plugin.json / marketplace.json / Phase 0 banner / `--version` 文档 / README badge / CHANGELOG
- **dist 副本**（WARN）：opencode / cursor / windsurf 的 frontmatter + banner 漂移
- **测试字面量**（WARN）：tests/*.py 里硬编码的过期版本

## 设计

- **纯只读**：不改任何文件，靠退出码 + 报告传达结果
- **canonical 单一源**：以 SKILL.md frontmatter `version` 为准，所有其他位置必须与之一致
- **FAIL vs WARN**：源文件不一致是 FAIL（发版阻塞）；dist 漂移和测试字面量是 WARN（重跑 convert / 人工判断）
- **evals 自评估**：本 skill 自带 trigger-eval + 行为 fixture + 结构回归，验证触发质量和检查逻辑

详见 [SKILL.md](./skills/ruyi-version-check/SKILL.md)。
