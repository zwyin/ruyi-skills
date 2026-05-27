#!/usr/bin/env python3
"""
import_graph.py — 从源码中提取模块间依赖关系

用脚本自动提取 import/require/from 语句，生成依赖图。
LLM 用这个数据画架构图，不用凭直觉判断模块关系。

用法：
  python scripts/import_graph.py /path/to/source/project
  python scripts/import_graph.py /path/to/source/project --lang python
  python scripts/import_graph.py /path/to/source/project --lang typescript
"""

import argparse
import re
from pathlib import Path
from collections import defaultdict


def find_source_files(root: str, extensions: list[str]) -> list[Path]:
    """递归查找源码文件"""
    files = []
    skip_dirs = {
        "node_modules", "target", "build", "dist",
        ".git", "__pycache__", ".venv", "venv",
    }
    for ext in extensions:
        for path in Path(root).rglob(f"*{ext}"):
            parts = path.parts
            if any(p in parts for p in skip_dirs):
                continue
            files.append(path)
    return sorted(files)


def extract_imports_ts(filepath: Path, _root: str) -> set[str]:
    """提取 TypeScript/JavaScript 的 import 语句"""
    imports = set()
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return imports

    patterns = [
        r'''import\s+.*?from\s+['"](\.[^'"]+)['"]''',
        r'''import\s+['"](\.[^'"]+)['"]''',
        r'''import\s*\(\s*['"](\.[^'"]+)['"]\s*\)''',
        r'''require\s*\(\s*['"](\.[^'"]+)['"]\s*\)''',
        r'''export\s+(?:\{[^}]*\}|\*)\s+from\s+['"](\.[^'"]+)['"]''',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            imports.add(match.group(1))

    return imports


def extract_imports_python(filepath: Path, _root: str) -> set[str]:
    """提取 Python 的 import 语句（相对 + 项目内绝对）"""
    imports = set()
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return imports

    # 合并反斜杠续行
    content = re.sub(r'\\\n', '', content)

    for line in content.split("\n"):
        line = line.strip()
        # from . import X / from .. import X / from .module import X / from ..sub import X
        m = re.match(r'^from\s+(\.{1,}[a-zA-Z0-9_.]*)\s+import', line)
        if m:
            imports.add(m.group(1))
            continue

        # from package.module import X (absolute within project)
        m = re.match(r'^from\s+([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)\s+import', line)
        if m:
            top_pkg = m.group(1).split('.')[0]
            if (Path(_root) / top_pkg).is_dir():
                imports.add(m.group(1))

    return imports


def extract_imports_rust(filepath: Path, _root: str) -> set[str]:
    """提取 Rust 的 use/crate/mod 语句"""
    imports = set()
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return imports

    for m in re.finditer(r'use\s+(crate::[a-zA-Z0-9_:]+)', content):
        imports.add(m.group(1))
    for m in re.finditer(r'use\s+(super::[a-zA-Z0-9_:]+)', content):
        imports.add(m.group(1))
    for m in re.finditer(r'use\s+(self::[a-zA-Z0-9_:]+)', content):
        imports.add(m.group(1))
    # mod declarations (not inline mod { ... })
    for m in re.finditer(r'^\s*mod\s+([a-zA-Z0-9_]+)\s*;', content, re.MULTILINE):
        imports.add(f"mod::{m.group(1)}")

    return imports


def build_graph(root: str, lang: str, depth: int = 2) -> tuple[dict, dict]:
    """构建依赖图"""
    ext_map: dict[str, list[str]] = {
        "typescript": [".ts", ".tsx", ".js", ".jsx"],
        "python": [".py"],
        "rust": [".rs"],
    }

    if lang == "auto":
        if (Path(root) / "Cargo.toml").exists():
            lang = "rust"
        elif (Path(root) / "pyproject.toml").exists() or (Path(root) / "setup.py").exists():
            lang = "python"
        elif (Path(root) / "package.json").exists() or (Path(root) / "tsconfig.json").exists():
            lang = "typescript"
        else:
            lang = "all"

    if lang == "all":
        extensions = [".ts", ".tsx", ".js", ".jsx", ".py", ".rs"]
    else:
        extensions = ext_map.get(lang, [".ts"])

    extractors: dict[str, callable] = {
        ".ts": extract_imports_ts,
        ".tsx": extract_imports_ts,
        ".js": extract_imports_ts,
        ".jsx": extract_imports_ts,
        ".py": extract_imports_python,
        ".rs": extract_imports_rust,
    }

    files = find_source_files(root, extensions)

    graph: dict[str, set[str]] = defaultdict(set)
    dir_files: dict[str, list[str]] = defaultdict(list)

    for filepath in files:
        rel = filepath.relative_to(root)
        parts = list(rel.parts[:-1])

        # Apply depth truncation
        if len(parts) > depth:
            parts = parts[:depth]

        if not parts:
            module = "(root)"
        else:
            module = "/".join(parts)

        dir_files[module].append(str(rel))

        ext = filepath.suffix
        extractor = extractors.get(ext)
        if not extractor:
            continue

        file_imports = extractor(filepath, root)
        for imp in file_imports:
            file_dir = filepath.parent
            target = (file_dir / imp).resolve()
            try:
                target_rel = target.relative_to(Path(root).resolve())
                target_parts = list(target_rel.parts[:-1]) if target_rel.parts else []
                # Apply depth truncation to target
                if len(target_parts) > depth:
                    target_parts = target_parts[:depth]
                target_module = "/".join(target_parts) if target_parts else "(root)"
                if target_module != module:
                    graph[module].add(target_module)
            except ValueError:
                pass

    return graph, dir_files


def main():
    parser = argparse.ArgumentParser(description="Extract import dependency graph from source code")
    parser.add_argument("source_dir", help="Path to source project root")
    parser.add_argument("--lang", default="auto", choices=["auto", "typescript", "python", "rust", "all"],
                        help="Language to analyze (default: auto-detect)")
    parser.add_argument("--depth", type=int, default=2,
                        help="Directory depth for module grouping (default: 2)")
    args = parser.parse_args()

    root = Path(args.source_dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        return

    graph, dir_files = build_graph(str(root), args.lang, depth=args.depth)

    modules = sorted(set(list(graph.keys()) + [k for s in graph.values() for k in s]))
    print(f"# Import Dependency Graph: {root.name}")
    print(f"# Modules found: {len(modules)}")
    print(f"# Files scanned: {sum(len(v) for v in dir_files.values())}")
    print()

    for module in sorted(graph.keys(), key=lambda m: len(graph[m]), reverse=True):
        deps = sorted(graph[module])
        if deps:
            print(f"## {module}/")
            print(f"   imports from: {', '.join(deps)}")
            print(f"   dependency count: {len(deps)}")
            print()

    # Parallel siblings
    print("# Parallel modules (share a dependency, don't import each other):")
    common_deps: dict[str, list[str]] = defaultdict(list)
    for module, deps in graph.items():
        for dep in deps:
            common_deps[dep].append(module)

    found_parallel = False
    for dep, dependents in sorted(common_deps.items()):
        if len(dependents) > 1:
            mutual = False
            for i, m1 in enumerate(dependents):
                for m2 in dependents[i+1:]:
                    if m2 in graph.get(m1, set()) or m1 in graph.get(m2, set()):
                        mutual = True
                        break
            if not mutual:
                print(f"   {dep} ← {', '.join(dependents)} (parallel siblings)")
                found_parallel = True

    if not found_parallel:
        print("   (none detected)")


if __name__ == "__main__":
    main()
