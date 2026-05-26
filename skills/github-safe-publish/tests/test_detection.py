"""Validate that scanning rules actually detect their target patterns."""
import re
from pathlib import Path

RULES_TEXT = (Path(__file__).resolve().parent.parent / "docs" / "scanning-rules.md").read_text()


def _extract_regex(rule_name):
    """Extract the regex pattern for a given rule name from scanning-rules.md."""
    pattern = re.compile(
        rf'### {re.escape(rule_name)}\s*\n.*?- \*\*正则\*\*: `([^`]+)`',
        re.DOTALL,
    )
    match = pattern.search(RULES_TEXT)
    assert match, f"Rule '{rule_name}' not found in scanning-rules.md"
    return match.group(1)


def _extract_pattern(rule_name):
    """Extract the file-pattern regex for FILE dimension rules (uses '模式' not '正则')."""
    pattern = re.compile(
        rf'### {re.escape(rule_name)}\s*\n.*?- \*\*模式\*\*: `([^`]+)`',
        re.DOTALL,
    )
    match = pattern.search(RULES_TEXT)
    assert match, f"FILE rule '{rule_name}' not found in scanning-rules.md"
    return match.group(1)


def _detects(rule_name, test_string):
    """Assert that the rule's regex matches the test string."""
    pattern = _extract_regex(rule_name)
    assert re.search(pattern, test_string), \
        f"Rule '{rule_name}' failed to match in: {test_string[:80]}"


def _detects_file(rule_name, file_path):
    """Assert that a FILE rule's pattern matches the given file path."""
    pattern = _extract_pattern(rule_name)
    assert re.search(pattern, file_path), \
        f"FILE rule '{rule_name}' failed to match path: {file_path}"


# --- Dimension A: Keys/Credentials ---

class TestKeyDetection:
    def test_aws_access_token(self):
        _detects("aws-access-token", "AKIAIOSFODNN7EXAMPLE")

    def test_github_pat(self):
        _detects("github-pat", "ghp_" + "A" * 36)

    def test_openai_api_key(self):
        _detects("openai-api-key", "sk-proj-" + "a" * 74 + "T3BlbkFJ" + "b" * 74)

    def test_stripe_access_token(self):
        _detects("stripe-access-token", "sk_live_" + "a" * 24)

    def test_slack_bot_token(self):
        # Split to avoid GitHub push protection flagging test data
        prefix = "xox" + "b-"
        _detects("slack-bot-token", f"{prefix}0000000000-0000000000000-TESTFAKETOKEN")

    def test_slack_webhook_url(self):
        _detects("slack-webhook-url",
                 "https://hooks.slack.com/services/TXXXXXXX/BXXXXXXX/xxxxxxxxxxxxxxxxxxxxxxxxx")

    def test_twilio_api_key(self):
        _detects("twilio-api-key", "SK" + "a" * 32)

    def test_anthropic_api_key(self):
        _detects("anthropic-api-key", "sk-ant-api03-" + "a" * 93 + "AA")

    def test_sendgrid_api_token(self):
        _detects("sendgrid-api-token", "SG." + "a" * 22 + "." + "b" * 43)

    def test_npm_access_token(self):
        _detects("npm-access-token", "npm_" + "a" * 36)

    def test_pypi_upload_token(self):
        _detects("pypi-upload-token", "pypi-AgEIcHlwaS5vcmc" + "a" * 60)

    def test_gitlab_pat(self):
        _detects("gitlab-pat", "glpat-" + "a" * 20)


# --- Dimension A2: Database Connection Strings ---

class TestDatabaseDetection:
    def test_postgres(self):
        _detects("postgres-connection-string", "postgresql://user:pass@host:5432/db")

    def test_mysql(self):
        _detects("mysql-connection-string", "mysql://root:password@localhost:3306/testdb")

    def test_mongodb(self):
        _detects("mongodb-connection-string",
                 "mongodb://admin:secret@cluster.example.com:27017/prod")

    def test_redis(self):
        _detects("redis-connection-string", "redis://:password@localhost:6379/0")

    def test_jdbc(self):
        _detects("jdbc-connection-string",
                 "jdbc:postgresql://db.example.com:5432/mydb?user=admin&password=secret")


# --- Dimension B: PII ---

class TestPIIDetection:
    def test_chinese_phone(self):
        _detects("chinese-phone-number", "13912345678")

    def test_email(self):
        _detects("email-address", "user@example.com")


# --- Dimension C: Infrastructure ---

class TestInfraDetection:
    def test_internal_domain(self):
        _detects("internal-domain-pattern", "http://nas.company.local:8080")


# --- Dimension A: Additional providers ---

class TestAdditionalProviders:
    def test_vault_service_token(self):
        _detects("vault-service-token", "hvs." + "a" * 24)

    def test_vault_batch_token(self):
        _detects("vault-batch-token", "hvb." + "a" * 24)

    def test_vault_recovery_token(self):
        _detects("vault-recovery-token", "hvr." + "a" * 24)

    def test_heroku_api_key(self):
        _detects("heroku-api-key",
                 "heroku_api_key = 12345678-1234-1234-1234-123456789012")

    def test_bitbucket_client_secret(self):
        _detects("bitbucket-client-secret",
                 'BITBUCKET_CLIENT_SECRET = "' + "a" * 45 + '"')


# --- Dimension A: GitHub tokens ---

class TestGitHubTokens:
    def test_github_app_token(self):
        _detects("github-app-token", "ghs_" + "a" * 36)

    def test_github_fine_grained_pat(self):
        _detects("github-fine-grained-pat", "github_pat_" + "a" * 82)

    def test_github_oauth(self):
        _detects("github-oauth", "gho_" + "a" * 36)

    def test_github_refresh_token(self):
        _detects("github-refresh-token", "ghr_" + "a" * 36)


# --- Dimension A: Cloud providers ---

class TestCloudProviders:
    def test_gcp_api_key(self):
        _detects("gcp-api-key", "AIza" + "a" * 35)

    def test_digitalocean_pat(self):
        _detects("digitalocean-pat", "dop_v1_" + "a" * 64)

    def test_digitalocean_access_token(self):
        _detects("digitalocean-access-token", "doo_v1_" + "a" * 64)

    def test_vercel_access_token(self):
        _detects("vercel-access-token", "VERCEL_" + "a" * 32)

    def test_netlify_access_token(self):
        _detects("netlify-access-token", "nfp_" + "a" * 42)

    def test_supabase_access_token(self):
        _detects("supabase-access-token", "sbp_" + "a" * 32)

    def test_flyio_access_token(self):
        _detects("flyio-access-token", "fo1_" + "a" * 32)

    def test_deno_access_token(self):
        _detects("deno-access-token", "deno_" + "a" * 32)

    def test_scaleway_api_key(self):
        _detects("scaleway-api-key", "SCW" + "a" * 32)


# --- Dimension A: AI providers ---

class TestAIProviders:
    def test_anthropic_admin_api_key(self):
        _detects("anthropic-admin-api-key",
                 "sk-ant-admin01-" + "a" * 93 + "AA")

    def test_huggingface_token(self):
        _detects("huggingface-access-token", "hf_" + "a" * 34)

    def test_perplexity_api_key(self):
        _detects("perplexity-api-key", "pplx-" + "a" * 48)

    def test_xai_api_key(self):
        _detects("xai-api-key", "xai-" + "a" * 42)

    def test_replicate_api_token(self):
        _detects("replicate-api-token", "r8_" + "a" * 32)

    def test_deepseek_api_token(self):
        _detects("deepseek-api-token", "sk-" + "a" * 32)


# --- Dimension A: DevOps / CI ---

class TestDevOpsTokens:
    def test_gitlab_deploy_token(self):
        _detects("gitlab-deploy-token", "gldt-" + "a" * 20)

    def test_gitlab_runner_token(self):
        _detects("gitlab-runner-token", "glrt-" + "a" * 20)

    def test_gitlab_cicd_job_token(self):
        _detects("gitlab-cicd-job-token", "glcbt-" + "a" * 20)

    def test_gitlab_feed_token(self):
        _detects("gitlab-feed-token", "glft-" + "a" * 20)

    def test_gitlab_kubernetes_agent_token(self):
        _detects("gitlab-kubernetes-agent-token", "glagent-" + "a" * 20)

    def test_databricks_token(self):
        _detects("databricks-api-token", "dapi" + "a" * 32)

    def test_planetscale_token(self):
        _detects("planetscale-api-token", "pscale_tkn_" + "a" * 42)

    def test_pulumi_api_token(self):
        _detects("pulumi-api-token", "pul-" + "a" * 40)

    def test_linear_api_key(self):
        _detects("linear-api-key", "lin_api_" + "a" * 40)


# --- Dimension A: SaaS / Communication ---

class TestSaaSTokens:
    def test_notion_api_token(self):
        _detects("notion-api-token",
                 "ntn_00000000000" + "a" * 32 + "abc")

    def test_shopify_access_token(self):
        _detects("shopify-access-token", "shpat_" + "a" * 32)

    def test_shopify_shared_secret(self):
        _detects("shopify-shared-secret", "shpss_" + "a" * 32)

    def test_sendinblue_token(self):
        _detects("sendinblue-api-token", "xkeysib-" + "a" * 64)

    def test_rubygems_token(self):
        _detects("rubygems-api-token", "rubygems_" + "a" * 48)

    def test_postman_token(self):
        _detects("postman-api-token",
                 "PMAK-" + "a" * 24 + "-" + "b" * 34)

    def test_artifactory_token(self):
        _detects("artifactory-api-key", "AKCp" + "a" * 69)


# --- Dimension A: Private key / JWT ---

class TestCryptoPatterns:
    def test_private_key(self):
        _detects("private-key",
                 "-----BEGIN RSA PRIVATE KEY-----\n" + "a" * 64 + "\n-----END RSA PRIVATE KEY-----")

    def test_jwt_token(self):
        _detects("jwt-token",
                 "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456")

    def test_kubernetes_secret_yaml(self):
        _detects("kubernetes-secret-yaml",
                 "kind: Secret\ndata:\n  password: " + "a" * 20)


# --- Dimension B: PII extended ---

class TestPIIDetectionExtended:
    def test_chinese_id_card(self):
        _detects("chinese-id-card", "110101199001011234")

    def test_us_ssn(self):
        _detects("us-ssn", "123-45-6789")

    def test_password_in_code(self):
        _detects("password-in-code", 'password = "mysecretpassword123"')


# --- Dimension C: Infrastructure extended ---

class TestInfraDetectionExtended:
    def test_internal_ip(self):
        _detects("internal-ip-address", "192.168.1.100")

    def test_internal_hostname(self):
        _detects("internal-hostname", "gitlab.internal")

    def test_local_filesystem_path(self):
        _detects("local-filesystem-path", "/Users/john/projects/secret/")

    def test_vpn_or_proxy_config(self):
        _detects("vpn-or-proxy-config", 'proxy = "10.0.0.1"')


# --- Dimension A: AWS extended ---

class TestAWSExtended:
    def test_aws_secret_access_key(self):
        _detects("aws-secret-access-key",
                 'aws_secret = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij0123"')

    def test_aws_bedrock_api_key(self):
        _detects("aws-amazon-bedrock-api-key",
                 "ABSK" + "a" * 109)


# --- Dimension A: Stripe / Payment ---

class TestPaymentTokens:
    def test_stripe_restricted_key(self):
        _detects("stripe-restricted-key", "rk_live_" + "a" * 24)

    def test_square_access_token(self):
        _detects("square-access-token",
                 "EAAA" + "a" * 30)

    def test_flutterwave_secret_key(self):
        _detects("flutterwave-secret-key",
                 "FLWSECK_TEST-" + "a" * 32 + "-X")

    def test_plaid_secret_key(self):
        _detects("plaid-secret-key",
                 'plaid_secret = "' + "a" * 30 + '"')


# --- Dimension A: Azure / Okta / Dynatrace ---

class TestEnterpriseTokens:
    def test_azure_ad_client_secret(self):
        _detects("azure-ad-client-secret",
                 "abc1Q~" + "a" * 32)

    def test_okta_access_token(self):
        _detects("okta-access-token",
                 'OKTA_API_TOKEN = "00' + "a" * 40 + '"')

    def test_dynatrace_api_token(self):
        _detects("dynatrace-api-token",
                 "dt0c01." + "a" * 24 + "." + "a" * 64)

    def test_hashicorp_tf_token(self):
        _detects("hashicorp-tf-api-token",
                 "abcdefghijklmn.atlasv1." + "a" * 65)


# --- Dimension A: SaaS monitoring ---

class TestMonitoringTokens:
    def test_datadog_token(self):
        _detects("datadog-access-token",
                 'datadog_api_key = "' + "a" * 40 + '"')

    def test_snyk_token(self):
        _detects("snyk-api-token",
                 'snyk_api_key = "12345678-1234-1234-1234-123456789012"')

    def test_sentry_token(self):
        _detects("sentry-access-token",
                 'sentry_auth_token = "' + "a" * 64 + '"')

    def test_grafana_api_key(self):
        _detects("grafana-api-key",
                 "eyJrIjoi" + "a" * 72)

    def test_new_relic_key(self):
        _detects("new-relic-user-api-key",
                 'NEW_RELIC_API_KEY = "NRAK-' + "a" * 27 + '"')

    def test_sentry_dsn(self):
        _detects("sentry-dsn",
                 "https://" + "a" * 32 + "@o123456.ingest.sentry.io/789012")


# --- Dimension A: Communication extended ---

class TestCommsExtended:
    def test_slack_user_token(self):
        prefix = "xoxp-"
        _detects("slack-user-token",
                 f"{prefix}0000000000-0000000000000-0000000000000-"
                 + "a" * 30)

    def test_telegram_bot_token(self):
        _detects("telegram-bot-api-token",
                 'telegram_token = "123456789:A' + "b" * 34 + '"')

    def test_discord_token(self):
        _detects("discord-api-token",
                 'discord_token = "' + "a" * 55 + '"')

    def test_mattermost_token(self):
        _detects("mattermost-access-token",
                 'mattermost_token = "' + "a" * 26 + '"')

    def test_microsoft_teams_webhook(self):
        _detects("microsoft-teams-webhook",
                 "https://abc.webhook.office.com/webhookb2/"
                 "12345678-1234-1234-1234-123456789012@"
                 "12345678-1234-1234-1234-123456789012/"
                 "IncomingWebhook/" + "a" * 32 + "/"
                 "12345678-1234-1234-1234-123456789012")


# --- Dimension A: Cloudflare / CDN ---

class TestCDNTokens:
    def test_cloudflare_origin_ca_key(self):
        _detects("cloudflare-origin-ca-key",
                 "v1.0-" + "a" * 24 + "-" + "b" * 146)

    def test_fastly_token(self):
        _detects("fastly-api-token",
                 'fastly_api_key = "' + "a" * 32 + '"')

    def test_ngrok_token(self):
        _detects("ngrok-auth-token",
                 'ngrok_authtoken = "' + "a" * 24 + "_" + "b" * 32 + '"')


# --- Dimension A: Misc SaaS ---

class TestMiscSaaS:
    def test_mailchimp_key(self):
        _detects("mailchimp-api-key",
                 'mailchimp_key = "' + "a" * 32 + '-us01"')

    def test_mailgun_token(self):
        _detects("mailgun-private-api-token",
                 'mailgun_api_key = "key-' + "a" * 32 + '"')

    def test_contentful_token(self):
        _detects("contentful-delivery-api-token",
                 'contentful_access_token = "' + "a" * 43 + '"')

    def test_atlassian_token(self):
        _detects("atlassian-api-token",
                 "ATATT3" + "a" * 186)

    def test_confluent_access_token(self):
        _detects("confluent-access-token",
                 'confluent_api_key = "' + "a" * 20 + '"')

    def test_clickhouse_secret(self):
        _detects("clickhouse-cloud-api-secret",
                 'clickhouse_api_secret = "' + "a" * 32 + '"')

    def test_dropbox_token(self):
        _detects("dropbox-api-token",
                 'dropbox_access_token = "sl.' + "a" * 110 + '"')


# --- Dimension A: Generic patterns ---

class TestGenericPatterns:
    def test_curl_auth_header(self):
        _detects("curl-auth-header",
                 'curl -H "Authorization: Bearer abc123def456ghi789"')

    def test_generic_api_key(self):
        _detects("generic-api-key",
                 'api_key = "aB3dE7fG9hJ2kL5mN8pQ"')


# --- Dimension B: PII financial ---

class TestPIIFinancial:
    def test_credit_card_visa(self):
        _detects("credit-card-number",
                 "4111111111111111")

    def test_bank_card_cn(self):
        _detects("bank-card-number-cn",
                 "6222021234567890123")


# --- Dimension C: Infrastructure URL ---

class TestInfraURL:
    def test_internal_url(self):
        _detects("internal-url",
                 "http://nas.local:8080/api/config")


# --- Dimension A: Remaining KEY rules ---

class TestRemainingKeyRules:
    def test_cloudflare_api_key(self):
        _detects("cloudflare-api-key",
                 'cloudflare_api_key = "' + "a" * 40 + '"')

    def test_algolia_api_key(self):
        _detects("algolia-api-key",
                 'algolia_api_key = "' + "a" * 32 + '"')

    def test_cohere_api_token(self):
        _detects("cohere-api-token",
                 'CO_API_KEY = "' + "a" * 40 + '"')

    def test_facebook_access_token(self):
        _detects("facebook-access-token",
                 "123456789012345|" + "a" * 30)

    def test_launchdarkly_token(self):
        _detects("launchdarkly-access-token",
                 'launchdarkly_sdk_key = "' + "a" * 32 + '"')

    def test_codecov_token(self):
        _detects("codecov-access-token",
                 'codecov_token = "' + "a" * 32 + '"')

    def test_doppler_token(self):
        _detects("doppler-api-token",
                 'doppler_token = "' + "a" * 42 + '"')

    def test_gcp_service_account(self):
        _detects("gcp-service-account",
                 '"type": "service_account"')

    def test_google_gemini_api_key(self):
        _detects("google-gemini-api-key",
                 'GOOGLE_API_KEY = "AIza' + "a" * 35 + '"')

    def test_cloudflare_global_api_key(self):
        _detects("cloudflare-global-api-key",
                 "a" * 37)

    def test_bitbucket_client_id(self):
        _detects("bitbucket-client-id",
                 'BITBUCKET_CLIENT_ID = "' + "a" * 32 + '"')

    def test_confluent_secret_key(self):
        _detects("confluent-secret-key",
                 'confluent_secret = "' + "a" * 42 + '=="')


# --- Dimension B: PII remaining ---

class TestPIIRemaining:
    def test_ip_address_ipv4(self):
        _detects("ip-address-ipv4", "203.0.113.50")


# --- Dimension D: File blacklist (uses 模式 not 正则) ---

class TestFileBlacklist:
    def test_env_files(self):
        _detects_file("env-files", ".env")
        _detects_file("env-files", ".env.production")

    def test_credential_files(self):
        _detects_file("credential-files", "credentials.json")
        _detects_file("credential-files", "id_rsa")

    def test_database_dumps(self):
        _detects_file("database-dumps", "backup.sql")
        _detects_file("database-dumps", "data.db")

    def test_ide_config_files(self):
        _detects_file("ide-config-files", ".idea/workspace.xml")
        _detects_file("ide-config-files", ".vscode/settings.json")

    def test_os_specific_files(self):
        _detects_file("os-specific-files", ".DS_Store")

    def test_log_files(self):
        _detects_file("log-files", "app.log")
        _detects_file("log-files", "error.log.1")

    def test_cache_temp_files(self):
        _detects_file("cache-temp-files", "__pycache__/module.cpython-312.pyc")

    def test_docker_sensitive_files(self):
        _detects_file("docker-sensitive-files", "docker-compose.override.yml")

    def test_terraform_state_files(self):
        _detects_file("terraform-state-files", "terraform.tfstate")

    def test_large_binary_files(self):
        _detects_file("large-binary-files", "app.exe")
        _detects_file("large-binary-files", "data.zip")

    def test_ssh_config_files(self):
        _detects_file("ssh-config-files", ".ssh/config")

    def test_backup_files(self):
        _detects_file("backup-files", "config.yaml.bak")
        _detects_file("backup-files", "data.json.backup")


# --- Dimension E: Git history (with 正则) ---

class TestGitHistory:
    def test_binary_secrets_in_history(self):
        _detects("binary-secrets-in-history", ".env")
        _detects("binary-secrets-in-history", "server.pem")

    def test_author_email_leak(self):
        _detects("author-email-leak", "john.doe@company.com")

    def test_removed_sensitive_file(self):
        _detects("removed-sensitive-file", "secrets.json")
        _detects("removed-sensitive-file", "credentials.yml")
