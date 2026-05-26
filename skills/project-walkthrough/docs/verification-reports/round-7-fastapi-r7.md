# Verification Report: FastAPI Walkthrough Round 7

**Date:** 2026-05-08
**Walkthrough:** `examples/fastapi-r7/docs/`
**Source:** `examples/_src_fastapi/`
**Depth:** brief
**Manifest:** `examples/fastapi-r7/docs/sources-manifest.json`

---

## 1. Code Block Audit (5 random blocks)

### Block 1: ParamTypes enum (03-technical-highlights.md)
- Citation: `# Source: fastapi/params.py:19-23`
- Actual source (params.py:19-23):
```python
class ParamTypes(Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"
```
- **Result: PASS** -- Character-for-character exact match.

### Block 2: request_response (03-technical-highlights.md)
- Citation: `<!-- Simplified from: fastapi/routing.py:97-136 (removed type: ignore comments) -->`
- Actual source contains `# type: ignore[assignment]`, `# type: ignore[call-arg]`, `# ty: ignore[unused-ignore-comment]` comments on lines 105, 107, 108. The walkthrough block omits these.
- **Result: PASS** -- Correctly marked as Simplified. Omission of type-ignore comments is documented.

### Block 3: Depends dataclass (03-technical-highlights.md)
- Citation: `# Source: fastapi/params.py:745-749`
- Actual source (params.py:745-749):
```python
@dataclass(frozen=True)
class Depends:
    dependency: Callable[..., Any] | None = None
    use_cache: bool = True
    scope: Literal["function", "request"] | None = None
```
- **Result: PASS** -- Character-for-character exact match.

### Block 4: OAuth2PasswordBearer.__call__ (03-technical-highlights.md)
- Citation: `# Source: fastapi/security/oauth2.py:536-544`
- Actual source (oauth2.py:536-544):
```python
    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
        return param
```
- **Result: PASS** -- Character-for-character exact match (indentation matches the method within the class).

### Block 5: run_endpoint_function (04-core-workflow.md)
- Citation: `# Source: fastapi/routing.py:320-330`
- Actual source (routing.py:320-330):
```python
async def run_endpoint_function(
    *, dependant: Dependant, values: dict[str, Any], is_coroutine: bool
) -> Any:
    # Only called by get_request_handler. Has been split into its own function to
    # facilitate profiling endpoints, since inner functions are harder to profile.
    assert dependant.call is not None, "dependant.call must be a function"

    if is_coroutine:
        return await dependant.call(**values)
    else:
        return await run_in_threadpool(dependant.call, **values)
```
- **Result: PASS** -- Character-for-character exact match.

**Code Block Audit: 5/5 PASS**

---

## 2. Version Verification

- Walkthrough states: `0.136.1`
- Source file `fastapi/__init__.py` line 3: `__version__ = "0.136.1"`
- **Result: PASS** -- Version matches exactly.

---

## 3. Security Directory Verification

- Walkthrough states: "fastapi/security/ contains: __init__.py, api_key.py, base.py, http.py, oauth2.py, open_id_connect_url.py, utils.py. NO jwt.py."
- Actual `ls` output: `__init__.py  api_key.py  base.py  http.py  oauth2.py  open_id_connect_url.py  utils.py`
- **Result: PASS** -- All 7 files listed, no jwt.py present.

---

## 4. API Signature Verification (3 checks)

### Signature 1: FastAPI class
- Walkthrough claim: `class FastAPI(Starlette):`
- Source `applications.py:41`: `class FastAPI(Starlette):`
- **PASS**

### Signature 2: APIRouter class
- Walkthrough claim: `class APIRouter(routing.Router):`
- Source `routing.py:1005`: `class APIRouter(routing.Router):`
- **PASS**

### Signature 3: Depends dataclass
- Walkthrough claim: frozen dataclass with `dependency`, `use_cache=True`, `scope: Literal["function", "request"] | None = None`
- Source `params.py:745-749`:
```python
@dataclass(frozen=True)
class Depends:
    dependency: Callable[..., Any] | None = None
    use_cache: bool = True
    scope: Literal["function", "request"] | None = None
```
- **PASS**

**API Signatures: 3/3 PASS**

---

## 5. Architecture Claims Verification (5 checks)

### Claim 1: FastAPI imports Starlette
- Stated: `from starlette.applications import Starlette` at applications.py:25
- Source verification: Line 25 reads `from starlette.applications import Starlette`
- **PASS**

### Claim 2: routing.py imports from fastapi.params
- Stated: `from fastapi import params` at routing.py:35
- Source verification: Line 35 reads `from fastapi import params`
- **PASS**

### Claim 3: routing.py imports from fastapi.dependencies.utils
- Stated: import block at routing.py:42-52
- Source verification: Lines 42-52 contain `from fastapi.dependencies.models import Dependant` and `from fastapi.dependencies.utils import (get_dependant, solve_dependencies, ...)`
- **PASS**

### Claim 4: routing.py imports from fastapi.sse
- Stated: import block at routing.py:61-67
- Source verification: Lines 61-67 contain `from fastapi.sse import (_PING_INTERVAL, KEEPALIVE_COMMENT, EventSourceResponse, ServerSentEvent, format_sse_event,)`
- **PASS**

### Claim 5: HTTPException inherits from StarletteHTTPException
- Stated: `class HTTPException(StarletteHTTPException)` at exceptions.py:17
- Source verification: Line 17 reads `class HTTPException(StarletteHTTPException):`
- **PASS**

**Architecture Claims: 5/5 PASS**

---

## 6. Line Range Verification (3 checks)

### Range 1: request_response (claim-018)
- Claimed: routing.py:97-136
- Line 97: `def request_response(` (start of function)
- Line 136: `    return app` (last line of function)
- Line 137: blank/next section
- **PASS** -- Range covers the complete function.

### Range 2: run_endpoint_function (claim-019)
- Claimed: routing.py:320-330
- Line 320: `async def run_endpoint_function(` (start)
- Line 330: `        return await run_in_threadpool(dependant.call, **values)` (last line)
- Line 331: blank
- **PASS** -- Range covers the complete function.

### Range 3: ServerSentEvent (claim-021)
- Claimed: sse.py:42-143
- Line 42: `class ServerSentEvent(BaseModel):` (start of class)
- Line 143: `        return self` (last line of the model_validator)
- Line 144: blank
- **PASS** -- Range covers the complete class including validator.

**Line Ranges: 3/3 PASS**

---

## Summary

| Check | Result |
|-------|--------|
| Code blocks (5 random) | 5/5 PASS |
| Version | PASS (0.136.1) |
| Security directory | PASS (no jwt.py) |
| API signatures (3) | 3/3 PASS |
| Architecture claims (5) | 5/5 PASS |
| Line ranges (3) | 3/3 PASS |
| verify_sources.py | PASS (all checks passed) |

**Overall: PASS** -- All verification checks succeeded. No inaccuracies found.

### Source vs Simplified Audit Summary
- 4 code blocks use `Source:` (character-for-character exact)
- 3 code blocks use `Simplified from:` (correctly marked with what changed)
- All simplified blocks document their modifications

### Issues Found and Fixed During Generation
1. `__init__.py` line range was initially set to [1, 26] but file is only 25 lines. Fixed to [1, 25].
2. `request_response` code block was initially marked `Source:` but omitted `# type: ignore` comments from source. Fixed to `Simplified from:`.
3. `EventSourceResponse` code block was initially marked `Source:` but omitted the docstring. Fixed to `Simplified from:`.
4. `get_request_handler` line range was initially [351, 426] but function extends to line 731. Fixed to [351, 731].
