#!/usr/bin/env bash
# check_update.sh — Hybrid update checker (git SHA + local time fallback)
#
# Primary: compare installed gitCommitSha against remote HEAD
# Fallback: time-based reminder when network is unavailable
#
# Output: upgrade reminder text (stdout) or nothing if up-to-date
set -euo pipefail

CACHE_DIR="${HOME}/.cache/skill-update"
CACHE_FILE="${CACHE_DIR}/project-walkthrough.json"

REPO="zwyin/ruyi-skills"
PLUGIN_KEY="ruyi-skills"
CHECK_INTERVAL_HOURS=24

# --- 1. Read local version ---
LOCAL_VERSION=""
LOCAL_SHA=""
if [ -f "${HOME}/.claude/plugins/installed_plugins.json" ]; then
    read -r LOCAL_VERSION LOCAL_SHA < <(python3 -c "
import json, sys
with open('${HOME}/.claude/plugins/installed_plugins.json') as f:
    data = json.load(f)
for key, entries in data.get('plugins', {}).items():
    if '${PLUGIN_KEY}' in key:
        e = entries[0]
        print(e.get('version',''), e.get('gitCommitSha',''))
        break
" 2>/dev/null || true) || true
fi

if [ -z "$LOCAL_SHA" ]; then
    exit 0
fi

# --- 2. Check cache (skip if checked within 24h) ---
if [ -f "$CACHE_FILE" ]; then
    CACHE_TIME=$(python3 -c "import json; print(json.load(open('$CACHE_FILE')).get('lastCheck',''))" 2>/dev/null || true)
    if [ -n "$CACHE_TIME" ]; then
        HOURS_SINCE=$(python3 -c "
from datetime import datetime, timezone
last = datetime.fromisoformat('${CACHE_TIME}'.replace('Z','+00:00'))
now = datetime.now(timezone.utc)
print(int((now - last).total_seconds() / 3600))
" 2>/dev/null || echo "999")
        if [ "$HOURS_SINCE" -lt "$CHECK_INTERVAL_HOURS" ]; then
            # Already checked recently — replay cached result if it was an update
            CACHE_SHA=$(python3 -c "import json; print(json.load(open('$CACHE_FILE')).get('remoteSha',''))" 2>/dev/null || true)
            if [ -n "$CACHE_SHA" ] && [ "$CACHE_SHA" != "$LOCAL_SHA" ]; then
                LOCAL_SHORT="${LOCAL_SHA:0:7}"
                REMOTE_SHORT="${CACHE_SHA:0:7}"
                echo "🔄 有新版本可用（${LOCAL_SHORT} → ${REMOTE_SHORT}）"
                echo "   升级命令：claude plugin update ${PLUGIN_KEY}"
            fi
            exit 0
        fi
    fi
fi

# --- 3. Primary: compare remote HEAD SHA ---
mkdir -p "$CACHE_DIR"
REMOTE_SHA=""

# Try gh api first (faster, structured output)
if command -v gh &>/dev/null; then
    REMOTE_SHA=$(timeout 5 gh api "repos/${REPO}/commits/main" --jq '.sha' 2>/dev/null || true)
fi

# Fallback: git ls-remote (no gh needed, works for public repos)
if [ -z "$REMOTE_SHA" ] && command -v git &>/dev/null; then
    REMOTE_SHA=$(timeout 10 git -c http.proxy="" -c https.proxy="" ls-remote "https://github.com/${REPO}.git" HEAD 2>/dev/null | awk '{print $1}' || true)
fi

# Update cache
if [ -n "$REMOTE_SHA" ]; then
    python3 -c "
import json
json.dump({'remoteSha': '$REMOTE_SHA', 'lastCheck': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'}, open('$CACHE_FILE', 'w'))
" 2>/dev/null || true
    if [ "$REMOTE_SHA" != "$LOCAL_SHA" ]; then
        LOCAL_SHORT="${LOCAL_SHA:0:7}"
        REMOTE_SHORT="${REMOTE_SHA:0:7}"
        echo "🔄 有新版本可用（${LOCAL_SHORT} → ${REMOTE_SHORT}）"
        echo "   升级命令：claude plugin update ${PLUGIN_KEY}"
    fi
    exit 0
fi

# --- 4. Fallback: time-based reminder ---
if [ -n "$LOCAL_VERSION" ]; then
    echo "💡 无法检查远程更新，当前版本 v${LOCAL_VERSION}"
    echo "   建议定期运行：claude plugin update ${PLUGIN_KEY}"
fi
