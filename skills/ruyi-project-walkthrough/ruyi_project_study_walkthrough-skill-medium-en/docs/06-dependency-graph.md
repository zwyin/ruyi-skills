# Dependency Graph Extraction

The `import_graph.py` script (239 lines) extracts module-level import dependencies from source code. It supports Python, TypeScript/JavaScript, and Rust, producing a text-based dependency graph that walkthrough authors use to draw accurate architecture diagrams.

## Why It Exists

Architecture diagrams in walkthroughs must be grounded in actual imports, not guessed from directory structure. Two modules in the same directory might have no relationship, while modules in different directories might be tightly coupled. The script provides ground truth.

## Usage

```text
// Simplified from: scripts/import_graph.py:1-11
"""
import_graph.py — Extract module-level import dependencies

Usage:
  python scripts/import_graph.py /path/to/source/project
  python scripts/import_graph.py /path/to/source/project --lang python
  python scripts/import_graph.py /path/to/source/project --lang typescript
"""
```

## Multi-Language Support

Three extraction functions handle language-specific import syntax:

### TypeScript/JavaScript

```python
// Simplified from: scripts/import_graph.py:36-55
def extract_imports_ts(filepath: Path, _root: str) -> set[str]:
    patterns = [
        r'''import\s+.*?from\s+['"](\.[^'"]+)['"]''',
        r'''import\s+['"](\.[^'"]+)['"]''',
        r'''import\s*\(\s*['"](\.[^'"]+)['"]\s*\)''',
        r'''require\s*\(\s*['"](\.[^'"]+)['"]\s*\)''',
        r'''export\s+(?:\{[^}]*\}|\*)\s+from\s+['"](\.[^'"]+)['"]''',
    ]
```

Captures relative imports (`from './...'`), dynamic imports, require calls, and re-exports.

### Python

```python
// Simplified from: scripts/import_graph.py:58-84
def extract_imports_python(filepath: Path, _root: str) -> set[str]:
    # Relative imports: from . import X / from ..sub import X
    m = re.match(r'^from\s+(\.{1,}[a-zA-Z0-9_.]*)\s+import', line)
    # Absolute imports within project: from package.module import X
    m = re.match(r'^from\s+([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)\s+import', line)
    if (Path(_root) / top_pkg).is_dir():
        imports.add(m.group(1))
```

Distinguishes relative imports (`.`, `..`) from absolute imports by checking if the top-level package directory exists in the project.

### Rust

```python
// Simplified from: scripts/import_graph.py:87-105
def extract_imports_rust(filepath: Path, _root: str) -> set[str]:
    for m in re.finditer(r'use\s+(crate::[a-zA-Z0-9_:]+)', content):
        imports.add(m.group(1))
    for m in re.finditer(r'use\s+(super::[a-zA-Z0-9_:]+)', content):
        imports.add(m.group(1))
    for m in re.finditer(r'^\s*mod\s+([a-zA-Z0-9_]+)\s*;', content, re.MULTILINE):
        imports.add(f"mod::{m.group(1)}")
```

Captures `crate::`, `super::`, `self::`, and module declarations.

## Graph Construction

The `build_graph()` function maps files to modules at configurable depth:

```python
// Simplified from: scripts/import_graph.py:108-181
def build_graph(root: str, lang: str, depth: int = 2) -> tuple[dict, dict]:
    ...
    for filepath in files:
        rel = filepath.relative_to(root)
        parts = list(rel.parts[:-1])
        if len(parts) > depth:
            parts = parts[:depth]
        module = "/".join(parts) if parts else "(root)"

        file_imports = extractor(filepath, root)
        for imp in file_imports:
            target = (file_dir / imp).resolve()
            target_rel = target.relative_to(Path(root).resolve())
            target_module = "/".join(target_parts)
            if target_module != module:
                graph[module].add(target_module)
```

The `--depth` flag controls how many directory levels are used for module grouping. At depth 2, `src/services/auth/login.py` becomes `services/auth`.

## Parallel Sibling Detection

A unique feature: the script detects modules that share a dependency without importing each other — "parallel siblings":

```python
// Simplified from: scripts/import_graph.py:214-235
# Parallel modules (share a dependency, don't import each other):
common_deps: dict[str, list[str]] = defaultdict(list)
for module, deps in graph.items():
    for dep in deps:
        common_deps[dep].append(module)

for dep, dependents in sorted(common_deps.items()):
    if len(dependents) > 1:
        mutual = False
        for i, m1 in enumerate(dependents):
            for m2 in dependents[i+1:]:
                if m2 in graph.get(m1, set()) or m1 in graph.get(m2, set()):
                    mutual = True
        if not mutual:
            print(f"   {dep} ← {', '.join(dependents)} (parallel siblings)")
```

This is useful for architecture diagrams — it identifies modules that are independently wired to the same dependency, which is often a sign of a shared abstraction layer.

## Output Format

The script produces human-readable text output:

```
# Import Dependency Graph: my-project
# Modules found: 8
# Files scanned: 23

## services/
   imports from: models, utils
   dependency count: 2

## handlers/
   imports from: services, utils
   dependency count: 2

# Parallel modules (share a dependency, don't import each other):
   utils ← services, handlers (parallel siblings)
```

[Previous: Accuracy System](05-accuracy-system.md) | [Next: Multi-Platform Distribution](07-multi-platform-distribution.md)
