# Scanning Rules Reference (Layer 1)

> 本文档定义 github-safe-publish 脱敏扫描第 1 层（确定性正则匹配）的全部规则。
> 参考来源：Gitleaks v8.25+ 默认配置（120+ 规则）+ TruffleHog 800+ 检测器提取 + 中国本地化扩展 + 内部基础设施检测。
> 最后更新：2026-05-25 (v2)

## 概览

| 维度 | 代号 | 说明 | 规则数 |
|------|------|------|--------|
| A. 密钥与凭证 | KEY | API Key、Token、Secret 等确定性模式 | 100 |
| A2. 数据库连接字符串 | DB | 含密码的数据库连接字符串 | 5 |
| B. 个人身份信息 | PII | 邮箱、手机号、身份证号等 | 8 |
| C. 内部基础设施 | INF | 内部 IP、域名、文件路径、URL | 6 |
| D. 文件黑名单 | FILE | 不应出现在公开仓库的文件类型 | 12 |
| E. Git 历史污染 | GIT | Git 中的二进制密钥、历史痕迹 | 4 |

**通用参数**：
- 熵值阈值（entropy threshold）：**4.5**（Shannon entropy，用于 generic-api-key 等通用规则的辅助判定）
- 匹配模式：多行（`re.MULTILINE` + `re.DOTALL`），忽略大小写按规则单独标注 `(?i)`

---

## 维度 A：密钥与凭证 (KEY)

### aws-access-token
- **正则**: `\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b`
- **关键字**: `a3t`, `akia`, `asia`, `abia`, `acca`
- **熵值**: 3
- **严重级别**: CRITICAL
- **误报排除**: 环境变量引用 `${AWS_ACCESS_KEY_ID}` 不匹配（无引号赋值形式）

### aws-secret-access-key
- **正则**: `(?i)[\w.-]{0,50}?(?:aws)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([A-Za-z0-9/+=]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `aws`
- **严重级别**: CRITICAL
- **误报排除**: 长度不足 40 或值为 placeholder 时排除

### aws-amazon-bedrock-api-key
- **正则**: `\b(ABSK[A-Za-z0-9+/]{109,269}={0,2})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `absk`
- **严重级别**: CRITICAL
- **误报排除**: 仅匹配 ABSK 前缀

### github-pat
- **正则**: `\bghp_[0-9a-zA-Z]{36}\b`
- **关键字**: `ghp_`
- **严重级别**: CRITICAL
- **误报排除**: 示例/placeholder 值如 `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### github-app-token
- **正则**: `(?:ghu|ghs)_[0-9a-zA-Z]{36}`
- **关键字**: `ghu_`, `ghs_`
- **严重级别**: CRITICAL
- **误报排除**: 同上 placeholder 模式

### github-fine-grained-pat
- **正则**: `github_pat_\w{82}`
- **关键字**: `github_pat_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### github-oauth
- **正则**: `gho_[0-9a-zA-Z]{36}`
- **关键字**: `gho_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### github-refresh-token
- **正则**: `ghr_[0-9a-zA-Z]{36}`
- **关键字**: `ghr_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### openai-api-key
- **正则**: `\b(sk-(?:proj|svcacct|admin)-(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})T3BlbkFJ(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})\b|sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `t3blbkfj`
- **严重级别**: CRITICAL
- **误报排除**: 无（T3BlbkFJ 为 Base64 编码的固定标识）

### anthropic-api-key
- **正则**: `\b(sk-ant-api03-[a-zA-Z0-9_\-]{93}AA)(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sk-ant-api03`
- **严重级别**: CRITICAL
- **误报排除**: 无

### anthropic-admin-api-key
- **正则**: `\b(sk-ant-admin01-[a-zA-Z0-9_\-]{93}AA)(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sk-ant-admin01`
- **严重级别**: CRITICAL
- **误报排除**: 无

### stripe-access-token
- **正则**: `\b((?:sk|rk)_(?:test|live|prod)_[a-zA-Z0-9]{10,99})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sk_test`, `sk_live`, `sk_prod`, `rk_test`, `rk_live`, `rk_prod`
- **严重级别**: CRITICAL
- **误报排除**: `sk_test_` 前缀的测试 key 仍需脱敏（可泄露计费信息）

### stripe-restricted-key
- **正则**: `\brk_(?:test|live|prod)_[a-zA-Z0-9]{10,99}\b`
- **关键字**: `rk_test`, `rk_live`, `rk_prod`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gcp-api-key
- **正则**: `\b(AIza[\w-]{35})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `aiza`
- **熵值**: 4
- **严重级别**: CRITICAL
- **误报排除**: 嵌入在前端代码中的浏览器 key 需人工确认

### azure-ad-client-secret
- **正则**: `(?:^|['"\x60\s>=:(,) ])([a-zA-Z0-9_~.]{3}\dQ~[a-zA-Z0-9_~.-]{31,34})(?:$|['"\x60\s<),])`
- **关键字**: `q~`
- **严重级别**: CRITICAL
- **误报排除**: 无（`Q~` 为 Azure AD client secret 固定标识）

### slack-bot-token
- **正则**: `xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*`
- **关键字**: `xoxb`
- **严重级别**: CRITICAL
- **误报排除**: 无

### slack-user-token
- **正则**: `xox[pe](?:-[0-9]{10,13}){3}-[a-zA-Z0-9-]{28,34}`
- **关键字**: `xoxp-`, `xoxe-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### slack-webhook-url
- **正则**: `(?:https?://)?hooks\.slack\.com/(?:services|workflows|triggers)/[A-Za-z0-9+/]{43,56}`
- **关键字**: `hooks.slack.com`
- **严重级别**: CRITICAL
- **误报排除**: 无

### sendgrid-api-token
- **正则**: `\b(SG\.[a-zA-Z0-9=_\-\.]{66})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sg.`
- **严重级别**: CRITICAL
- **误报排除**: 无

### twilio-api-key
- **正则**: `SK[0-9a-fA-F]{32}`
- **关键字**: `sk`
- **熵值**: 3
- **严重级别**: CRITICAL
- **误报排除**: 注意 SK 前缀仅匹配十六进制格式

### private-key
- **正则**: `(?i)-----BEGIN[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----[\s\S-]{64,}?KEY(?: BLOCK)?-----`
- **关键字**: `-----begin`
- **严重级别**: CRITICAL
- **误报排除**: 测试用的空 key 或 mock key 需人工确认

### jwt-token
- **正则**: `\b(ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9/\\_-]{17,}\.(?:[a-zA-Z0-9/\\_-]{10,}={0,2})?)(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `ey`
- **熵值**: 3
- **严重级别**: WARNING
- **误报排除**: 短 JWT（测试 mock）可标记为 WARNING；硬编码长期 JWT 为 CRITICAL

### gitlab-pat
- **正则**: `glpat-[\w-]{20}`
- **关键字**: `glpat-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gitlab-deploy-token
- **正则**: `gldt-[0-9a-zA-Z_\-]{20}`
- **关键字**: `gldt-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gitlab-runner-token
- **正则**: `glrt-[0-9a-zA-Z_\-]{20}`
- **关键字**: `glrt-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### npm-access-token
- **正则**: `(?i)\b(npm_[a-z0-9]{36})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `npm_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### pypi-upload-token
- **正则**: `pypi-AgEIcHlwaS5vcmc[\w-]{50,1000}`
- **关键字**: `pypi-ageichlwas5vcmc`
- **严重级别**: CRITICAL
- **误报排除**: 无

### heroku-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:heroku)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `heroku`
- **严重级别**: CRITICAL
- **误报排除**: 无

### databricks-api-token
- **正则**: `\b(dapi[a-f0-9]{32}(?:-\d)?)(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `dapi`
- **严重级别**: CRITICAL
- **误报排除**: 无

### digitalocean-pat
- **正则**: `\b(dop_v1_[a-f0-9]{64})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `dop_v1_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### cloudflare-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:cloudflare)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9_-]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `cloudflare`
- **严重级别**: CRITICAL
- **误报排除**: 无

### mailgun-private-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:mailgun)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}(key-[a-f0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `mailgun`
- **严重级别**: CRITICAL
- **误报排除**: `pubkey-` 前缀为公开 key，降为 WARNING

### shopify-access-token
- **正则**: `shpat_[a-fA-F0-9]{32}`
- **关键字**: `shpat_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### postman-api-token
- **正则**: `\b(PMAK-[a-fA-F0-9]{24}\-[a-fA-F0-9]{34})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `pmak-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### notion-api-token
- **正则**: `\b(ntn_[0-9]{11}[A-Za-z0-9]{32}[A-Za-z0-9]{3})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `ntn_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### telegram-bot-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:telegr)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([0-9]{5,16}:(?-i:A)[a-z0-9_\-]{34})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `telegr`
- **严重级别**: CRITICAL
- **误报排除**: 无

### discord-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:discord)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([A-Za-z0-9._-]{50,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `discord`
- **严重级别**: CRITICAL
- **误报排除**: 无

### algolia-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:algolia)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `algolia`
- **严重级别**: CRITICAL
- **误报排除**: 前端搜索 only key 可标记 WARNING

### huggingface-access-token
- **正则**: `\b(hf_[a-zA-Z0-9]{34})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `hf_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### grafana-api-key
- **正则**: `(?i)\b(eyJrIjoi[A-Za-z0-9]{70,400}={0,3})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `eyjrijoi`
- **严重级别**: CRITICAL
- **误报排除**: 无

### datadog-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:datadog)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `datadog`
- **严重级别**: CRITICAL
- **误报排除**: 无

### snyk-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:snyk[_.-]?(?:(?:api|oauth)[_.-]?)?(?:key|token))(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `snyk`
- **严重级别**: CRITICAL
- **误报排除**: 无

### sentry-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:sentry)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-f0-9]{64})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sentry`
- **严重级别**: CRITICAL
- **误报排除**: 无

### square-access-token
- **正则**: `\b((?:EAAA|sq0atp-)[\w-]{22,60})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sq0atp-`, `eaaa`
- **严重级别**: CRITICAL
- **误报排除**: 无

### okta-access-token
- **正则**: `[\w.-]{0,50}?(?i:[\w.-]{0,50}?(?:(?-i:[Oo]kta|OKTA))(?:[ \t\w.-]{0,20})[\s'"]{0,3})(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}(00[\w=\-]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `okta`
- **严重级别**: CRITICAL
- **误报排除**: 无

### dynatrace-api-token
- **正则**: `dt0c01\.[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{64}`
- **关键字**: `dt0c01.`
- **严重级别**: CRITICAL
- **误报排除**: 无

### mailchimp-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:MailchimpSDK\.initialize|mailchimp)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-f0-9]{32}-us\d\d)(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `mailchimp`
- **严重级别**: CRITICAL
- **误报排除**: 无

### new-relic-user-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:new-relic|newrelic|new_relic)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}(NRAK-[a-z0-9]{27})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `nrak`
- **严重级别**: CRITICAL
- **误报排除**: 无

### pulumi-api-token
- **正则**: `\b(pul-[a-f0-9]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `pul-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### rubygems-api-token
- **正则**: `\b(rubygems_[a-f0-9]{48})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `rubygems_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### perplexity-api-key
- **正则**: `\b(pplx-[a-zA-Z0-9]{48})(?:[\x60'"\s;]|\\[nr]|$|\b)`
- **关键字**: `pplx-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### cohere-api-token
- **正则**: `[\w.-]{0,50}?(?i:[\w.-]{0,50}?(?:cohere|CO_API_KEY)(?:[ \t\w.-]{0,20})[\s'"]{0,3})(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `cohere`, `co_api_key`
- **严重级别**: CRITICAL
- **误报排除**: 无

### facebook-access-token
- **正则**: `(?i)\b(\d{15,16}(\||%)[0-9a-z\-_]{27,40})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `facebook`
- **严重级别**: CRITICAL
- **误报排除**: 无

### atlassian-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:(?-i:ATLASSIAN|[Aa]tlassian)|(?-i:CONFLUENCE|[Cc]onfluence)|(?-i:JIRA|[Jj]ira))(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9]{20}[a-f0-9]{4})(?:[\x60'"\s;]|\\[nr]|$)|\b(ATATT3[A-Za-z0-9_\-=]{186})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `atlassian`, `confluence`, `jira`, `atatt3`
- **严重级别**: CRITICAL
- **误报排除**: 无

### linear-api-key
- **正则**: `lin_api_[a-zA-Z0-9]{40}`
- **关键字**: `lin_api_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### flutterwave-secret-key
- **正则**: `FLWSECK(?:_(?:TEST|LIVE))?-[a-hA-H0-9]{32}-X`
- **关键字**: `flwseck_test`
- **严重级别**: CRITICAL
- **误报排除**: `_TEST_` 前缀的测试 key 仍需脱敏

### plaid-secret-key
- **正则**: `(?i)[\w.-]{0,50}?(?:plaid)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9]{30})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `plaid`
- **严重级别**: CRITICAL
- **误报排除**: 无

### kubernetes-secret-yaml
- **正则**: `(?i)(?:\bkind:[ \t]*["']?\bsecret\b["']?(?s:.){0,200}?\bdata:(?s:.){0,100}?\s+([\w.-]+:(?:[ \t]*(?:\||>[-+]?)\s+)?[ \t]*(?:["']?[a-z0-9+/]{10,}={0,3}["']?|\{\{[ \t\w"|$:=,.-]+\}\}|""|''))|\bdata:(?s:.){0,100}?\s+([\w.-]+:(?:[ \t]*(?:\||>[-+]?)\s+)?[ \t]*(?:["']?[a-z0-9+/]{10,}={0,3}["']?|\{\{[ \t\w"|$:=,.-]+\}\}|""|'')))`
- **关键字**: `secret`
- **严重级别**: WARNING
- **误报排除**: Helm template 引用 `{{ .Values.* }}` 不算硬编码密钥

### artifactory-api-key
- **正则**: `\bAKCp[A-Za-z0-9]{69}\b`
- **关键字**: `akcp`
- **熵值**: 4.5
- **严重级别**: CRITICAL
- **误报排除**: 无

### hashicorp-tf-api-token
- **正则**: `(?i)[a-z0-9]{14}\.(?-i:atlasv1)\.[a-z0-9\-_=]{60,70}`
- **关键字**: `atlasv1`
- **严重级别**: CRITICAL
- **误报排除**: 无

### curl-auth-header
- **正则**: `\bcurl\b(?:.*?|.*?(?:[\r\n]{1,2}.*?){1,5})[ \t\r](?:-H|--header)(?:=|[ \t]{0,5})("(?:[Aa]uthorization:[ \t]{0,5}(?:[Bb]asic[ \t]([a-zA-Z0-9+/]{8,}={0,3})|(?:[Bb]earer|(?:[Aa]pi-)?[Tt]oken)[ \t]([\w=~@.+/-]{8,})|([\w=~@.+/-]{8,}))|(?:(?:[Xx]-(?:[a-z]+-)?)?(?:[Aa]pi-?)?(?:[Kk]ey|[Tt]oken)):[ \t]{0,5}([\w=~@.+/-]{8,}))")`
- **关键字**: `curl`
- **熵值**: 2.75
- **严重级别**: WARNING
- **误报排除**: 脚本中的示例 curl 命令需人工确认

### generic-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:access|auth|(?-i:[Aa]pi|API)|credential|creds|key|passw(?:or)?d|secret|token)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([\w.=-]{10,150}|[a-z0-9][a-z0-9+/]{11,}={0,3})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `access`, `api`, `auth`, `key`, `credential`, `creds`, `passwd`, `password`, `secret`, `token`
- **熵值**: 3.5（**阈值 4.5** 用于二次过滤：低于阈值的匹配降为 WARNING）
- **严重级别**: WARNING（高熵匹配升级为 CRITICAL）
- **误报排除**: 变量名本身含 key/token 但值为空/placeholder；`example.com`、`localhost` 等测试地址中的 key

### vercel-access-token
- **正则**: `\b(VERCEL_[a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `vercel`
- **严重级别**: CRITICAL
- **误报排除**: 无

### netlify-access-token
- **正则**: `\b(nfp_[a-zA-Z0-9]{40,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `nfp_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### supabase-access-token
- **正则**: `\b(sb[pv]_[a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `sbp_`, `sbv_`
- **严重级别**: CRITICAL
- **误报排除**: `anon` key（公开密钥，用于前端）标记为 WARNING

### flyio-access-token
- **正则**: `\b(FlyV1 [a-zA-Z0-9_\-]{40,}|fo1_[a-zA-Z0-9_\-]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `flyv1`, `fo1_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### deno-access-token
- **正则**: `\b(deno_[a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `deno_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### cloudflare-global-api-key
- **正则**: `\b([a-f0-9]{37})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `cloudflare`, `x-auth-key`
- **熵值**: 3.5
- **严重级别**: CRITICAL
- **误报排除**: 需与 Cloudflare 上下文关键字共现（变量名/注释/URL 含 cloudflare）

### cloudflare-origin-ca-key
- **正则**: `\b(v1\.0-[a-f0-9]{24}-[a-f0-9]{146})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `v1.0-`
- **严重级别**: CRITICAL
- **误报排除**: 无（`v1.0-` 前缀为 Cloudflare Origin CA 固定格式）

### digitalocean-access-token
- **正则**: `\b(doo_v1_[a-f0-9]{64})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `doo_v1_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### vault-service-token
- **正则**: `\b(hvs\.[a-zA-Z0-9]{20,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `hvs.`
- **严重级别**: CRITICAL
- **误报排除**: 无（`hvs.` 为 HashiCorp Vault service token 固定前缀）

### vault-batch-token
- **正则**: `\b(hvb\.[a-zA-Z0-9]{20,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `hvb.`
- **严重级别**: CRITICAL
- **误报排除**: 无（`hvb.` 为 HashiCorp Vault batch token 固定前缀）

### vault-recovery-token
- **正则**: `\b(hvr\.[a-zA-Z0-9]{20,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `hvr.`
- **严重级别**: CRITICAL
- **误报排除**: 无（`hvr.` 为 HashiCorp Vault recovery token 固定前缀，Vault 1.10+）

### bitbucket-client-id
- **正则**: `(?i)[\w.-]{0,50}?(?:bitbucket)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `bitbucket`
- **严重级别**: WARNING
- **误报排除**: Client ID 单独泄露风险较低，需与 Client Secret 共现才升级 CRITICAL

### bitbucket-client-secret
- **正则**: `(?i)[\w.-]{0,50}?(?:bitbucket)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9_\-]{40,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `bitbucket`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gitlab-cicd-job-token
- **正则**: `\bglcbt-[a-zA-Z0-9]{20,}(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `glcbt-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gitlab-feed-token
- **正则**: `\bglft-[a-zA-Z0-9]{20,}(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `glft-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gitlab-kubernetes-agent-token
- **正则**: `\bglagent-[a-zA-Z0-9]{20,}(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `glagent-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### confluent-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:confluent)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{16,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `confluent`
- **严重级别**: CRITICAL
- **误报排除**: 无

### confluent-secret-key
- **正则**: `(?i)[\w.-]{0,50}?(?:confluent)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9+/]{40,}={0,2})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `confluent`
- **严重级别**: CRITICAL
- **误报排除**: 无

### launchdarkly-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:launchdarkly)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-z0-9][-a-z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `launchdarkly`
- **严重级别**: CRITICAL
- **误报排除**: 无

### fastly-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:fastly)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `fastly`
- **严重级别**: CRITICAL
- **误报排除**: 无

### codecov-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:codecov)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-f0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `codecov`
- **严重级别**: CRITICAL
- **误报排除**: 无

### doppler-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:doppler)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{40,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `doppler`
- **严重级别**: CRITICAL
- **误报排除**: 无

### dropbox-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:dropbox)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}(sl\.[a-zA-Z0-9_-]{100,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `dropbox`, `sl.`
- **严重级别**: CRITICAL
- **误报排除**: 无

### gcp-service-account
- **正则**: `(?i)(?:"type"\s*:\s*"service_account"|GOOGLE_APPLICATION_CREDENTIALS)`
- **关键字**: `service_account`, `google_application_credentials`
- **严重级别**: CRITICAL
- **误报排除**: 仅匹配 JSON key 文件标识，需进一步检查文件内容

### clickhouse-cloud-api-secret
- **正则**: `(?i)[\w.-]{0,50}?(?:clickhouse)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `clickhouse`
- **严重级别**: CRITICAL
- **误报排除**: 无

### planetscale-api-token
- **正则**: `\b(pscale_tkn_[a-zA-Z0-9_\-=]{40,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `pscale_tkn_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### shopify-shared-secret
- **正则**: `\b(shpss_[a-fA-F0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `shpss_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### google-gemini-api-key
- **正则**: `(?i)[\w.-]{0,50}?(?:gemini|GOOGLE_API_KEY|GOOGLE_GENERATIVE_AI)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}(AIza[\w-]{35})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `gemini`, `google_api_key`
- **熵值**: 4
- **严重级别**: CRITICAL
- **误报排除**: 与 gcp-api-key 重叠，此规则侧重变量名含 gemini 的匹配

### deepseek-api-token
- **正则**: `\b(sk-[a-f0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `deepseek`
- **严重级别**: CRITICAL
- **误报排除**: `sk-` 前缀与 OpenAI 重叠，此规则仅匹配 DEEPSEEK 上下文

### xai-api-key
- **正则**: `\b(xai-[a-zA-Z0-9]{40,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `xai-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### replicate-api-token
- **正则**: `\b(r8_[a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `r8_`
- **严重级别**: CRITICAL
- **误报排除**: 无

### sendinblue-api-token
- **正则**: `\b(xkeysib-[a-fA-F0-9]{64})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `xkeysib-`
- **严重级别**: CRITICAL
- **误报排除**: 无

### mattermost-access-token
- **正则**: `(?i)[\w.-]{0,50}?(?:mattermost)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-zA-Z0-9]{26})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `mattermost`
- **严重级别**: CRITICAL
- **误报排除**: 无

### microsoft-teams-webhook
- **正则**: `https://[a-zA-Z0-9]+\.webhook\.office\.com/webhookb2/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}@[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/IncomingWebhook/[a-f0-9]{32}/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}`
- **关键字**: `webhook.office.com`
- **严重级别**: CRITICAL
- **误报排除**: 无

### contentful-delivery-api-token
- **正则**: `(?i)[\w.-]{0,50}?(?:contentful)(?:[ \t\w.-]{0,20})[\s'"]{0,3}(?:=|>|:{1,3}=|\|\||:|=>|\?=|,)[\x60'"\s=]{0,5}([a-f0-9]{43})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `contentful`
- **严重级别**: WARNING
- **误报排除**: Contentful delivery API token 为公开只读，但暴露仍不推荐

### scaleway-api-key
- **正则**: `\b(SCW[a-zA-Z0-9]{30,})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `scw`
- **严重级别**: CRITICAL
- **误报排除**: 无

### ngrok-auth-token
- **正则**: `\b([a-zA-Z0-9]{24}_[a-zA-Z0-9]{32})(?:[\x60'"\s;]|\\[nr]|$)`
- **关键字**: `ngrok`, `authtoken`
- **严重级别**: CRITICAL
- **误报排除**: 需与 ngrok 上下文共现

### sentry-dsn
- **正则**: `https://[a-f0-9]{32}@o\d+\.ingest\.sentry\.io/\d+`
- **关键字**: `sentry`, `ingest.sentry.io`
- **严重级别**: WARNING
- **误报排除**: Sentry DSN 通常为公开只读（错误上报），但暴露内部项目 ID

---

### 数据库连接字符串

### postgres-connection-string
- **正则**: `(?i)(?:postgres(?:ql)?://[\w.-]{1,256}:[\w!@#$%^&*()\-_=+]{1,256}@[\w.-]{1,256}(?::\d{1,5})?(?:/[\w.-]{1,256})?(?:\?[\w&%=]*)?)`
- **关键字**: `postgresql://`, `postgres://`
- **严重级别**: CRITICAL
- **误报排除**: `localhost`/`127.0.0.1` 且无密码的本地开发连接可降为 WARNING

### mysql-connection-string
- **正则**: `(?i)(?:mysql://[\w.-]{1,256}:[\w!@#$%^&*()\-_=+]{1,256}@[\w.-]{1,256}(?::\d{1,5})?(?:/[\w.-]{1,256})?(?:\?[\w&%=]*)?)`
- **关键字**: `mysql://`
- **严重级别**: CRITICAL
- **误报排除**: 同上，本地开发连接可降为 WARNING

### mongodb-connection-string
- **正则**: `(?i)(?:mongodb(?:\+srv)?://[\w.-]{1,256}:[\w!@#$%^&*()\-_=+]{1,256}@[\w.-]{1,256}(?::\d{1,5})?(?:/[\w.-]{1,256})?(?:\?[\w&%=]*)?)`
- **关键字**: `mongodb://`, `mongodb+srv://`
- **严重级别**: CRITICAL
- **误报排除**: 同上

### redis-connection-string
- **正则**: `(?i)(?:rediss?://:[\w!@#$%^&*()\-_=+]{1,256}@[\w.-]{1,256}(?::\d{1,5})?(?:/\d{0,3})?)`
- **关键字**: `redis://`
- **严重级别**: CRITICAL
- **误报排除**: 无密码连接 `redis://localhost:6379` 降为 WARNING

### jdbc-connection-string
- **正则**: `(?i)(?:jdbc:(?:mysql|postgresql|sqlserver|oracle|sqlite|mariadb)://[\w.-]{1,256}(?::\d{1,5})?(?:/[\w.-]{1,256})?.*(?:password|pwd)=[\w!@#$%^&*()\-_=+]{1,256})`
- **关键字**: `jdbc:`
- **严重级别**: CRITICAL
- **误报排除**: 无密码的 JDBC URL 降为 WARNING

---

## 维度 B：个人身份信息 (PII)

### email-address
- **正则**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`
- **严重级别**: WARNING
- **误报排除**: `noreply@github.com`、`user@example.com`、`TODO@example.com` 等明显 placeholder；项目作者自己的公开邮箱由用户确认

### chinese-phone-number
- **正则**: `(?<!\d)1[3-9]\d{9}(?!\d)`
- **严重级别**: WARNING
- **误报排除**: 注释中的示例号码（如 `13800138000`）；连续数字中的非手机号（如 timestamp 中的子串）

### chinese-id-card
- **正则**: `[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]`
- **严重级别**: CRITICAL
- **误报排除**: 测试用例中明确标注为示例的号码

### ip-address-ipv4
- **正则**: `\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b`
- **严重级别**: WARNING
- **误报排除**: `0.0.0.0`、`127.0.0.1`、`255.255.255.255`、`localhost` 等保留地址

### us-ssn
- **正则**: `\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b`
- **严重级别**: CRITICAL
- **误报排除**: 无（格式非常精确）

### credit-card-number
- **正则**: `\b(?:4\d{12,18}|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12}|3(?:0[0-5]|[68]\d)\d{11})\b`
- **严重级别**: CRITICAL
- **误报排除**: 需通过 Luhn 校验的二次确认

### bank-card-number-cn
- **正则**: `\b(?:62|64|65|68)\d{14,17}\b`
- **严重级别**: CRITICAL
- **误报排除**: 短于 16 位的数字串；明显为 order ID / tracking number

### password-in-code
- **正则**: `(?i)(?:password|passwd|pwd)\s*(?:=|:|=>)\s*["'][^"']{8,}["']`
- **严重级别**: WARNING
- **误报排除**: 值为 placeholder 如 `"REPLACE_ME"`、`"changeme"`、`"<your-password>"`、`"***"`

---

## 维度 C：内部基础设施 (INF)

### internal-ip-address
- **正则**: `\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b`
- **严重级别**: WARNING
- **误报排除**: 文档中明确说明为示例的 IP；`192.168.1.1` 等常见默认地址在配置模板中可接受

### internal-hostname
- **正则**: `(?i)(?:nas|gitlab|jenkins|jira|wiki|redmine|sonar|nexus|harbor|k8s|staging)\.(?:internal|local|lan|corp|intra|office|home)(?:\.\w+)?`
- **严重级别**: WARNING
- **误报排除**: 公开的 `jenkins.io`、`sonarsource.com` 等外部域名

### local-filesystem-path
- **正则**: `(?:/Users/|/home/)[\w.-]+/|(?:C:\\Users\\)[\w.-]+\\`
- **严重级别**: WARNING
- **误报排除**: CI 配置中的 `/home/runner/`、`/home/ubuntu/` 等标准 CI 路径；文档中的示例路径

### internal-url
- **正则**: `(?i)https?://(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|localhost|127\.0\.0\.1|[\w.-]+\.(?:internal|local|lan|corp|intra))(?::\d+)?(?:/|$)`
- **严重级别**: WARNING
- **误报排除**: `http://localhost:3000` 在开发文档中出现的常见端口

### internal-domain-pattern
- **正则**: `(?i)\b[\w.-]+\.(?:internal|local|lan|corp|intra|office|home|nas)\b`
- **严重级别**: WARNING
- **误报排除**: DNS 配置示例；RFC 2606 保留域名

### vpn-or-proxy-config
- **正则**: `(?i)(?:vpn|proxy|socks5?|tunnel)\s*(?:=|:|=>)\s*["']?(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w.-]+\.(?:internal|local|corp))`
- **严重级别**: WARNING
- **误报排除**: 公开代理列表；配置模板中的 placeholder

---

## 维度 D：文件黑名单 (FILE)

以下文件类型/名称不应出现在公开仓库中。扫描时按文件路径匹配。

### env-files
- **模式**: `(?i)(?:^|/)\.env(?:\.(?:local|development|production|staging|test))?$`
- **严重级别**: CRITICAL
- **误报排除**: `.env.example`、`.env.template`、`.env.sample`（不匹配，因为规则要求无后缀或特定后缀）

### credential-files
- **模式**: `(?i)(?:^|/)(?:credentials|secrets|\.netrc|\.pypirc|\.npmrc|\.p12|\.pfx|\.jks|\.keystore|id_rsa|id_ed25519|id_ecdsa)(?:\.\w+)?$`
- **严重级别**: CRITICAL
- **误报排除**: `.npmrc` 中仅含 `registry=https://registry.npmjs.org/` 的可接受

### database-dumps
- **模式**: `(?i)(?:^|/).*\.(?:sql(?:\.gz|\.bz2)?|db|sqlite|sqlite3|dump|bak)(?:\.\w+)?$`
- **严重级别**: CRITICAL
- **误报排除**: 测试 fixture 中的 `.sql` 文件（需人工确认内容）

### ide-config-files
- **模式**: `(?i)(?:^|/)(?:\.idea/.*|\.vscode/settings\.json|\.vscode/launch\.json)$`
- **严重级别**: WARNING
- **误报排除**: `.vscode/extensions.json`（推荐扩展列表，适合开源）

### os-specific-files
- **模式**: `(?i)(?:^|/)(?:\.DS_Store|Thumbs\.db|desktop\.ini)$`
- **严重级别**: WARNING
- **误报排除**: 无

### log-files
- **模式**: `(?i)(?:^|/).*\.(?:log|logs)(?:\.\d+)?$`
- **严重级别**: WARNING
- **误报排除**: 空日志文件

### cache-temp-files
- **模式**: `(?i)(?:^|/)(?:__pycache__/.*|\.cache/.*|\.tmp/.*|\.temp/.*|\.pytest_cache/.*|node_modules/.*)`
- **严重级别**: WARNING
- **误报排除**: `.gitignore` 中已列出的目录不会出现在 git 跟踪文件中

### docker-sensitive-files
- **模式**: `(?i)(?:^|/)docker-compose\.(?:override|prod|staging)\.(?:yml|yaml)$`
- **严重级别**: WARNING
- **误报排除**: `docker-compose.yml`（基础文件通常可公开）

### terraform-state-files
- **模式**: `(?i)(?:^|/).*\.tfstate(?:\.backup)?$`
- **严重级别**: CRITICAL
- **误报排除**: 无

### large-binary-files
- **模式**: `(?i)(?:^|/).*\.(?:exe|dll|so|dylib|bin|dat|iso|dmg|pkg|deb|rpm|msi|zip|tar|gz|rar|7z)$`
- **严重级别**: WARNING
- **误报排除**: 项目必要的发行包（需人工确认）

### ssh-config-files
- **模式**: `(?i)(?:^|/)(?:\.ssh/config|\.ssh/known_hosts|ssh_config|sshd_config)$`
- **严重级别**: WARNING
- **误报排除**: 无

### backup-files
- **模式**: `(?i)(?:^|/).*\.(?:bak|backup|orig|old|swp|swo|save|copy)(?:\.\w+)?$`
- **严重级别**: WARNING
- **误报排除**: 无

---

## 维度 E：Git 历史 (GIT)

### binary-secrets-in-history
- **检测方法**: `git log --all --diff-filter=A --summary` 搜索历史中添加过的 `.env`、`.pem`、`.key`、`.p12` 等文件
- **正则**: `(?i)(?:^|/)(?:\.env$|.*\.pem$|.*\.key$|.*\.p12$|.*\.pfx$|.*\.jks$|id_rsa$|id_ed25519$)`
- **严重级别**: CRITICAL
- **误报排除**: 文件在后续 commit 中已删除（仍需确认 git 历史中残留）

### large-file-in-history
- **检测方法**: `git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)'` 筛选 > 1MB 的 blob
- **阈值**: 1MB
- **严重级别**: WARNING
- **误报排除**: LFS 追踪的文件

### author-email-leak
- **检测方法**: `git log --all --format='%ae' | sort -u` 收集所有 commit author email
- **正则**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- **严重级别**: WARNING
- **误报排除**: GitHub noreply 地址 `^\d+\+username@users\.noreply\.github\.com$`

### removed-sensitive-file
- **检测方法**: `git log --all --diff-filter=D --summary` 搜索历史中删除过的敏感文件
- **正则**: `(?i)(?:^|/)(?:\.env$|credentials\.yml$|secrets\.json$|config/database\.yml$)`
- **严重级别**: CRITICAL
- **误报排除**: 无（文件虽已删除，但内容仍可通过 git 历史恢复）

---

## 熵值检测

用于辅助判定 generic-api-key 等通用规则中的匹配结果是否为真实密钥。

### 计算方法
- Shannon entropy: `H = -sum(p_i * log2(p_i))`，其中 `p_i` 为每个字符出现的频率
- 仅对字母数字字符集 `{a-z, A-Z, 0-9, +, /, =, -, _}` 计算

### 阈值
- **4.5**：通用密钥检测阈值
- 低于 4.5 的 generic-api-key 匹配降为 WARNING
- 高于 4.5 的匹配升级为 CRITICAL

### 示例

| 字符串 | 熵值 | 判定 |
|--------|------|------|
| `AKIAIOSFODNN7EXAMPLE` | ~3.7 | WARNING（低熵，可能是示例） |
| `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` | ~4.7 | WARNING（接近阈值但含重复模式） |
| `wJalrXUtnFEMI/K7MDENG/bPxRfiCY+realkeyXyz` | ~4.9 | CRITICAL |

---

## 严重级别定义

| 级别 | 含义 | 默认动作 |
|------|------|----------|
| CRITICAL | 真实密钥/凭证/敏感 PII，泄露后果严重 | 必须替换或删除 |
| WARNING | 可疑模式或低风险信息泄露 | 需人工确认，可选择忽略 |
| SAFE | 已确认为非敏感 | 无需处理 |

## 扫描范围

- **默认范围**: `git ls-files` 输出的所有被跟踪文件
- **排除**: `.git/` 目录、`.gitignore` 中列出的文件
- **文件大小限制**: 单文件 > 10MB 跳过（避免性能问题）
- **二进制文件**: 跳过无法以 UTF-8 解码的文件
