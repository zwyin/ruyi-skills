# Verification Report: FastAPI r11 Walkthrough

**Date:** 2026-05-08
**Round:** 11
**Source:** examples/_src_fastapi/ (FastAPI 0.136.1)
**Output:** examples/fastapi-r11/docs/

## Verification Checklist

### 1. Citation Format
- **Rule:** ALL code blocks must use `Simplified from:` (NOT `Source:`)
- **Result:** PASS
- **Evidence:** grep found 0 occurrences of `Source:` in code blocks. All 17 code block citations use `// Simplified from:` format.

### 2. Line Ranges
- **Rule:** End line <= file length for every cited range
- **Result:** PASS (1 issue found and fixed during generation)
- **Evidence:** All 33 manifest claims and 17 inline citations verified against actual file line counts:
  - fastapi/__init__.py: 25 lines (cited: 1-25, 3) -- OK
  - fastapi/applications.py: 4691 lines (cited: 21, 25, 41, 57, 1068-1099) -- OK
  - fastapi/routing.py: 4956 lines (cited: 35, 42-52, 61-67, 97-136, 320-330, 351-368, 1005, 1578-1630, 1831-1850) -- OK
  - fastapi/params.py: 754 lines (cited: 19-23, 26, 137-742, 745-754) -- OK
  - fastapi/sse.py: 222 lines (cited: 20-33, 42-95) -- OK
  - fastapi/security/oauth2.py: 693 lines (cited: 14-57, 536-540) -- OK
  - fastapi/security/http.py: 417 lines (cited: 69-102) -- OK
  - fastapi/exceptions.py: 256 lines (cited: 17, 161-243) -- OK
  - fastapi/dependencies/models.py: 193 lines (cited: 32-52) -- OK
  - fastapi/background.py: 61 lines (cited: 40-61) -- OK
  - pyproject.toml: 374 lines (cited: 44-50) -- OK

### 3. Version Exact Match
- **Rule:** Version must match fastapi/__init__.py exactly
- **Result:** PASS
- **Evidence:** `__version__ = "0.136.1"` at line 3 matches all doc references.

### 4. No jwt.py Mentioned
- **Rule:** fastapi/security/ has NO jwt.py; docs must not imply it exists
- **Result:** PASS
- **Evidence:** The word "jwt" appears only in the correct context: "There is NO jwt.py" and "There is no jwt.py" (negative assertions). Verified `ls fastapi/security/` shows: __init__.py, api_key.py, base.py, http.py, oauth2.py, open_id_connect_url.py, utils.py.

### 5. Directory Structure Verified
- **Rule:** All directory listings must match actual filesystem
- **Result:** PASS
- **Evidence:** Both the `fastapi/` and `fastapi/security/` directory listings in docs verified against actual `ls` output.

### 6. API Signatures Match
- **Rule:** All API signatures in docs must match source code
- **Result:** PASS
- **Evidence:**
  - `class FastAPI(Starlette)` at applications.py:41 -- confirmed
  - `class APIRouter(routing.Router)` at routing.py:1005 -- confirmed
  - `class Param(FieldInfo)` at params.py:26 -- confirmed
  - `@dataclass(frozen=True) class Depends` at params.py:745-749 -- confirmed
  - `class HTTPException(StarletteHTTPException)` at exceptions.py:17 -- confirmed
  - `class SecurityBase` at security/base.py:4 -- confirmed

### 7. Architecture Claims Backed by Imports
- **Rule:** Every arrow in architecture diagram must be backed by actual import
- **Result:** PASS
- **Evidence:**
  - FastAPI -> Starlette: `from starlette.applications import Starlette` at applications.py:25 -- confirmed
  - FastAPI -> get_openapi: `from fastapi.openapi.utils import get_openapi` at applications.py:21 -- confirmed
  - routing.py -> params: `from fastapi import params` at routing.py:35 -- confirmed
  - routing.py -> dependencies: `from fastapi.dependencies.utils import ...` at routing.py:42-52 -- confirmed
  - routing.py -> sse: `from fastapi.sse import ...` at routing.py:61-67 -- confirmed
  - params.py -> Pydantic: `from pydantic.fields import FieldInfo` at params.py:10 -- confirmed
  - HTTPException -> Starlette: `class HTTPException(StarletteHTTPException)` at exceptions.py:17 -- confirmed

### 8. Count Claims Accurate
- **Rule:** All numeric claims must be verified
- **Result:** PASS
- **Evidence:**
  - Security module files: docs list 5 files in table + __init__.py + utils.py = 7 files total; actual count = 7 -- confirmed
  - ServerSentEvent fields: docs say 6 fields (data, raw_data, event, id, retry, comment); actual Pydantic model has exactly 6 -- confirmed
  - Param subclass hierarchy: docs show 7 subclasses; actual grep finds Path:137, Query:221, Header:303, Cookie:387, Body:469, Form:581, File:663 -- confirmed (7 matches)

## Issues Found During Generation (Fixed)

1. **claim-007 line number:** Initially wrote `source_lines: [22, 22]` for get_openapi import. Actual line is 21. Fixed to `[21, 21]` before verification.

## verify_sources.py Result

```
python3 scripts/verify_sources.py examples/fastapi-r11/docs/sources-manifest.json --source-dir examples/_src_fastapi
  All checks passed
```

## Final Verdict

**ZERO ISSUES -- CLEAN ROUND**

All 33 manifest claims verified. All 17 inline code citations use `Simplified from:` format. All line ranges within file bounds. Version exact match. No jwt.py. Directory structure verified. API signatures match. Architecture claims backed by imports. Count claims accurate.
