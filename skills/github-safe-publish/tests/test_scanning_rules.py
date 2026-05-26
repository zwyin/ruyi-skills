"""Validate scanning rules in docs/scanning-rules.md."""
import re


def test_rules_file_exists(rules_text):
    assert len(rules_text) > 5000


def test_all_six_dimensions_covered(rules_text):
    dimensions = ["密钥", "PII", "内部基础设施", "文件黑名单", "Git 历史", "数据库连接字符串"]
    for dim in dimensions:
        assert dim in rules_text, f"Missing dimension: {dim}"


def test_regex_patterns_are_valid(rules_text):
    """All regex patterns in backtick blocks that look like regexes must be valid."""
    pattern_blocks = re.findall(r"`([^`]+)`", rules_text)
    for p in pattern_blocks:
        # Skip non-regex strings: plain words, URLs, file paths, quoted strings
        if p.startswith("http") or p.startswith(".") or p.startswith("/"):
            continue
        # Must contain regex metacharacters to be considered a regex
        if not any(c in p for c in r"\[](){}*+?.^$|"):
            continue
        # Skip patterns that are clearly not regex (e.g., markdown formatting)
        stripped = p.strip('"\'')
        if stripped in ('***', '**', '___', '---', '*'):
            continue
        try:
            re.compile(p)
        except re.error as e:
            assert False, f"Invalid regex: {p!r} — {e}"


def test_entropy_detection_defined(rules_text):
    assert "熵" in rules_text or "entropy" in rules_text.lower()
    assert "4.5" in rules_text


def test_secret_detection_covers_major_providers(rules_text):
    providers = ["AWS", "GitHub", "OpenAI", "Stripe"]
    lower_text = rules_text.lower()
    for provider in providers:
        assert provider.lower() in lower_text, f"Missing provider: {provider}"


def test_pii_covers_chinese_patterns(rules_text):
    assert "1[3-9]" in rules_text or "手机" in rules_text
    assert "身份证" in rules_text or "ID number" in rules_text


def test_infrastructure_covers_internal_patterns(rules_text):
    assert "192.168" in rules_text
    assert "/Users/" in rules_text or "C:\\\\Users" in rules_text


def test_database_connection_strings_covered(rules_text):
    for proto in ["postgresql://", "mysql://", "mongodb://", "redis://"]:
        assert proto in rules_text, f"Missing database connection string: {proto}"


def test_vault_tokens_covered(rules_text):
    assert "hvs." in rules_text, "Missing HashiCorp Vault service token (hvs.)"
    assert "hvb." in rules_text, "Missing HashiCorp Vault batch token (hvb.)"
    assert "hvr." in rules_text, "Missing HashiCorp Vault recovery token (hvr.)"


def test_key_rule_count_matches_claim(rules_text):
    """Verify the actual number of KEY rules matches claimed count."""
    key_section = re.search(
        r'## 维度 A：密钥与凭证.*?\n---', rules_text, re.DOTALL
    )
    assert key_section, "Cannot find KEY dimension section"
    rules = re.findall(r'^### (?!概览|严重|扫描|数据)', key_section.group(), re.MULTILINE)
    assert len(rules) == 100, f"KEY dimension has {len(rules)} rules, expected 100"


def test_cloud_platform_tokens_covered(rules_text):
    """Modern cloud/deployment platforms must be covered."""
    lower = rules_text.lower()
    for platform in ["vercel", "netlify", "supabase", "flyio", "deno"]:
        assert platform in lower, f"Missing cloud platform: {platform}"


def test_ai_provider_tokens_comprehensive(rules_text):
    """AI/ML providers beyond OpenAI and Anthropic."""
    lower = rules_text.lower()
    for provider in ["gemini", "deepseek", "xai", "replicate"]:
        assert provider in lower, f"Missing AI provider: {provider}"


def test_bitbucket_tokens_covered(rules_text):
    lower = rules_text.lower()
    assert "bitbucket" in lower, "Missing Bitbucket detection"


def test_connection_string_dimension_exists(rules_text):
    assert "数据库连接字符串" in rules_text


def test_total_rule_count(rules_text):
    """Verify total rule count across all dimensions."""
    all_rules = re.findall(r"^### ([a-z0-9][a-z0-9-]*)$", rules_text, re.MULTILINE)
    skip = {"计算方法", "阈值", "示例", "数据库连接字符串"}
    all_rules = [r for r in all_rules if r not in skip]
    assert len(all_rules) == 135, f"Expected 135 rules, found {len(all_rules)}"
