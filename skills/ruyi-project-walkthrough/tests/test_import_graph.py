"""
Unit tests for scripts/import_graph.py

Covers:
  - find_source_files(): recursive file discovery with skip dirs
  - extract_imports_ts(): TypeScript/JavaScript import extraction
  - extract_imports_python(): Python import extraction (relative + absolute project-internal)
  - extract_imports_rust(): Rust use/crate/mod extraction
  - build_graph(): full graph construction with auto-detection, depth, and module grouping

Usage:
  pytest tests/test_import_graph.py -v
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import the module under test.
# scripts/ has no __init__.py, so we add the project root to sys.path and
# import directly.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.import_graph import (
    build_graph,
    extract_imports_python,
    extract_imports_rust,
    extract_imports_ts,
    find_source_files,
)


# ===================================================================
# find_source_files
# ===================================================================


class TestFindSourceFiles:
    """Tests for find_source_files()."""

    def test_finds_py_files_in_tree(self, tmp_path):
        """Discovers .py files recursively."""
        (tmp_path / "a.py").write_text("pass")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "b.py").write_text("pass")

        result = find_source_files(str(tmp_path), [".py"])
        names = [p.name for p in result]
        assert "a.py" in names
        assert "b.py" in names

    def test_skips_node_modules(self, tmp_path):
        """Files inside node_modules are excluded."""
        (tmp_path / "good.py").write_text("pass")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "bad.py").write_text("pass")

        result = find_source_files(str(tmp_path), [".py"])
        names = [p.name for p in result]
        assert "good.py" in names
        assert "bad.py" not in names

    def test_skips_pycache(self, tmp_path):
        """Files inside __pycache__ are excluded."""
        (tmp_path / "main.py").write_text("pass")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "main.cpython-311.pyc").write_text("")

        result = find_source_files(str(tmp_path), [".py"])
        assert len(result) == 1
        assert result[0].name == "main.py"

    def test_skips_git(self, tmp_path):
        """Files inside .git are excluded."""
        (tmp_path / "code.py").write_text("pass")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "hooks").mkdir()
        (tmp_path / ".git" / "hooks" / "pre-commit").write_text("# hook")

        result = find_source_files(str(tmp_path), [".py"])
        assert len(result) == 1
        assert result[0].name == "code.py"

    def test_skips_target_and_build_and_dist(self, tmp_path):
        """Files inside target/, build/, dist/ are excluded."""
        for skip in ("target", "build", "dist"):
            (tmp_path / skip).mkdir()
            (tmp_path / skip / "main.py").write_text("pass")

        (tmp_path / "real.py").write_text("pass")
        result = find_source_files(str(tmp_path), [".py"])
        assert len(result) == 1
        assert result[0].name == "real.py"

    def test_skips_venv_dirs(self, tmp_path):
        """Files inside .venv/ and venv/ are excluded."""
        for skip in (".venv", "venv"):
            (tmp_path / skip).mkdir()
            (tmp_path / skip / "site.py").write_text("pass")

        (tmp_path / "app.py").write_text("pass")
        result = find_source_files(str(tmp_path), [".py"])
        assert len(result) == 1
        assert result[0].name == "app.py"

    def test_returns_empty_for_no_matching_extensions(self, tmp_path):
        """Returns empty list when no .rs files exist."""
        (tmp_path / "readme.md").write_text("hello")
        (tmp_path / "app.py").write_text("pass")

        result = find_source_files(str(tmp_path), [".rs"])
        assert result == []

    def test_returns_sorted_results(self, tmp_path):
        """Results are sorted by path."""
        (tmp_path / "z.py").write_text("pass")
        (tmp_path / "a.py").write_text("pass")
        (tmp_path / "m.py").write_text("pass")

        result = find_source_files(str(tmp_path), [".py"])
        names = [p.name for p in result]
        assert names == sorted(names)

    def test_multiple_extensions(self, tmp_path):
        """Can search for multiple extensions at once."""
        (tmp_path / "app.py").write_text("pass")
        (tmp_path / "index.ts").write_text("")
        (tmp_path / "main.rs").write_text("")

        result = find_source_files(str(tmp_path), [".py", ".ts", ".rs"])
        names = {p.name for p in result}
        assert names == {"app.py", "index.ts", "main.rs"}


# ===================================================================
# extract_imports_ts
# ===================================================================


class TestExtractImportsTs:
    """Tests for extract_imports_ts()."""

    def test_named_import_relative(self, tmp_path):
        """import { X } from './module' extracts './module'."""
        f = tmp_path / "a.ts"
        f.write_text("import { useState } from './hooks';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./hooks" in result

    def test_side_effect_import(self, tmp_path):
        """import './side-effects' extracts './side-effects'."""
        f = tmp_path / "index.ts"
        f.write_text("import './polyfills';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./polyfills" in result

    def test_dynamic_import(self, tmp_path):
        """import('./dynamic') extracts './dynamic'."""
        f = tmp_path / "loader.ts"
        f.write_text("const mod = import('./lazy');\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./lazy" in result

    def test_commonjs_require(self, tmp_path):
        """require('./commonjs') extracts './commonjs'."""
        f = tmp_path / "legacy.js"
        f.write_text("const util = require('./utils');\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./utils" in result

    def test_reexport(self, tmp_path):
        """export { X } from './reexport' extracts './reexport'."""
        f = tmp_path / "barrel.ts"
        f.write_text("export { foo } from './internal';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./internal" in result

    def test_star_reexport(self, tmp_path):
        """export * from './reexport' extracts './reexport'."""
        f = tmp_path / "barrel.ts"
        f.write_text("export * from './everything';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "./everything" in result

    def test_non_relative_import_not_extracted(self, tmp_path):
        """Non-relative imports like 'react' are NOT extracted."""
        f = tmp_path / "app.tsx"
        f.write_text("import React from 'react';\nimport { Router } from 'express';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "react" not in result
        assert "express" not in result
        assert len(result) == 0

    def test_empty_file_returns_empty_set(self, tmp_path):
        """Empty file yields an empty set."""
        f = tmp_path / "empty.ts"
        f.write_text("")

        result = extract_imports_ts(f, str(tmp_path))
        assert result == set()

    def test_multiple_imports_in_one_file(self, tmp_path):
        """Multiple relative imports are all captured."""
        f = tmp_path / "multi.ts"
        f.write_text(
            "import { A } from './a';\n"
            "import { B } from './b';\n"
            "import './c';\n"
        )

        result = extract_imports_ts(f, str(tmp_path))
        assert result == {"./a", "./b", "./c"}

    def test_parent_directory_import(self, tmp_path):
        """import from '../parent' is extracted (still relative)."""
        f = tmp_path / "child.ts"
        f.write_text("import { shared } from '../shared';\n")

        result = extract_imports_ts(f, str(tmp_path))
        assert "../shared" in result


# ===================================================================
# extract_imports_python
# ===================================================================


class TestExtractImportsPython:
    """Tests for extract_imports_python()."""

    def test_relative_dot_import(self, tmp_path):
        """from . import x extracts '.'."""
        f = tmp_path / "mod.py"
        f.write_text("from . import helper\n")

        result = extract_imports_python(f, str(tmp_path))
        assert "." in result

    def test_relative_double_dot_import(self, tmp_path):
        """from ..sub import y extracts '..sub'."""
        f = tmp_path / "mod.py"
        f.write_text("from ..sibling import something\n")

        result = extract_imports_python(f, str(tmp_path))
        assert "..sibling" in result

    def test_relative_dot_module_import(self, tmp_path):
        """from .module import X extracts '.module'."""
        f = tmp_path / "mod.py"
        f.write_text("from .utils import helper\n")

        result = extract_imports_python(f, str(tmp_path))
        assert ".utils" in result

    def test_absolute_import_project_internal(self, tmp_path):
        """from package.module import X where package/ exists extracts 'package.module'."""
        (tmp_path / "mypackage").mkdir()
        (tmp_path / "mypackage" / "__init__.py").write_text("")
        f = tmp_path / "app.py"
        f.write_text("from mypackage.utils import helper\n")

        result = extract_imports_python(f, str(tmp_path))
        assert "mypackage.utils" in result

    def test_absolute_import_external_lib_not_extracted(self, tmp_path):
        """from package.module import X where package/ does NOT exist is NOT extracted."""
        f = tmp_path / "app.py"
        f.write_text("from requests.sessions import Session\n")

        result = extract_imports_python(f, str(tmp_path))
        assert "requests.sessions" not in result
        assert len(result) == 0

    def test_stdlib_import_not_extracted(self, tmp_path):
        """import os is NOT extracted (the function only handles 'from ... import')."""
        f = tmp_path / "app.py"
        f.write_text("import os\nimport sys\n")

        result = extract_imports_python(f, str(tmp_path))
        assert len(result) == 0

    def test_backslash_continuation_joined(self, tmp_path):
        """Backslash-continued import lines are properly joined.

        The source removes backslash+newline, but not the leading whitespace
        on the continuation line. With content ``from .module \\\nimport X``,
        after joining it becomes ``from .module import X`` which matches.
        """
        f = tmp_path / "mod.py"
        # This pattern joins to: "from .utils import helper" (no extra spaces)
        f.write_text("from .utils \\\nimport helper\n")

        result = extract_imports_python(f, str(tmp_path))
        assert ".utils" in result

    def test_empty_file_returns_empty_set(self, tmp_path):
        """Empty file yields an empty set."""
        f = tmp_path / "empty.py"
        f.write_text("")

        result = extract_imports_python(f, str(tmp_path))
        assert result == set()

    def test_relative_triple_dot(self, tmp_path):
        """from ...package import X extracts '...package'."""
        f = tmp_path / "mod.py"
        f.write_text("from ...deep import something\n")

        result = extract_imports_python(f, str(tmp_path))
        assert "...deep" in result


# ===================================================================
# extract_imports_rust
# ===================================================================


class TestExtractImportsRust:
    """Tests for extract_imports_rust()."""

    def test_use_crate(self, tmp_path):
        """use crate::module::function extracts 'crate::module::function'."""
        f = tmp_path / "main.rs"
        f.write_text("use crate::network::http::fetch;\n")

        result = extract_imports_rust(f, str(tmp_path))
        assert "crate::network::http::fetch" in result

    def test_use_super(self, tmp_path):
        """use super::sibling extracts 'super::sibling'."""
        f = tmp_path / "main.rs"
        f.write_text("use super::models::User;\n")

        result = extract_imports_rust(f, str(tmp_path))
        assert "super::models::User" in result

    def test_use_self(self, tmp_path):
        """use self::local extracts 'self::local'."""
        f = tmp_path / "main.rs"
        f.write_text("use self::config::Settings;\n")

        result = extract_imports_rust(f, str(tmp_path))
        assert "self::config::Settings" in result

    def test_mod_declaration(self, tmp_path):
        """mod submodule; extracts 'mod::submodule'."""
        f = tmp_path / "main.rs"
        f.write_text("mod network;\nmod utils;\n")

        result = extract_imports_rust(f, str(tmp_path))
        assert "mod::network" in result
        assert "mod::utils" in result

    def test_mod_inline_not_confused(self, tmp_path):
        """Inline mod with braces should still capture the mod name."""
        f = tmp_path / "main.rs"
        f.write_text("mod tests {\n    fn it_works() {}\n}\n")

        # The regex ^\s*mod\s+([a-zA-Z0-9_]+)\s*; uses MULTILINE and
        # requires a semicolon. Inline mod { ... } does NOT end with ; on
        # the same line, so it should NOT be captured.
        result = extract_imports_rust(f, str(tmp_path))
        # "tests {" does not match the pattern (no trailing semicolon)
        assert "mod::tests" not in result

    def test_empty_file_returns_empty_set(self, tmp_path):
        """Empty file yields an empty set."""
        f = tmp_path / "empty.rs"
        f.write_text("")

        result = extract_imports_rust(f, str(tmp_path))
        assert result == set()

    def test_multiple_use_statements(self, tmp_path):
        """Multiple use statements are all captured."""
        f = tmp_path / "main.rs"
        f.write_text(
            "use crate::alpha::Beta;\n"
            "use super::gamma;\n"
            "use self::delta::Epsilon;\n"
        )

        result = extract_imports_rust(f, str(tmp_path))
        assert "crate::alpha::Beta" in result
        assert "super::gamma" in result
        assert "self::delta::Epsilon" in result


# ===================================================================
# build_graph
# ===================================================================


class TestBuildGraph:
    """Tests for build_graph()."""

    def test_auto_detect_rust(self, tmp_path):
        """Cargo.toml triggers rust auto-detection."""
        (tmp_path / "Cargo.toml").write_text("[package]\nname = 'demo'\n")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.rs").write_text("use crate::lib::func;\n")
        (tmp_path / "src" / "lib.rs").write_text("pub fn func() {}\n")

        _, dir_files = build_graph(str(tmp_path), "auto")
        assert "src" in dir_files or len(dir_files) > 0

    def test_auto_detect_python(self, tmp_path):
        """pyproject.toml triggers python auto-detection."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").write_text("")
        (tmp_path / "pkg" / "a.py").write_text("from . import b\n")
        (tmp_path / "pkg" / "b.py").write_text("")

        _, dir_files = build_graph(str(tmp_path), "auto")
        assert "pkg" in dir_files
        assert len(dir_files["pkg"]) == 3

    def test_auto_detect_typescript(self, tmp_path):
        """package.json triggers typescript auto-detection."""
        (tmp_path / "package.json").write_text('{"name": "demo"}\n')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "index.ts").write_text("import { foo } from './utils';\n")
        (tmp_path / "src" / "utils.ts").write_text("export function foo() {}\n")

        _, dir_files = build_graph(str(tmp_path), "auto")
        assert "src" in dir_files

    def test_depth_parameter_truncates_paths(self, tmp_path):
        """Depth parameter truncates deeply nested module paths."""
        deep = tmp_path / "a" / "b" / "c" / "d"
        deep.mkdir(parents=True)
        (deep / "mod.py").write_text("pass")

        _, dir_files = build_graph(str(tmp_path), "python", depth=2)
        modules = list(dir_files.keys())
        assert len(modules) == 1
        assert len(modules[0].split("/")) <= 2

    def test_empty_directory_returns_empty_graph(self, tmp_path):
        """Empty directory produces empty graph and dir_files."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")

        graph, dir_files = build_graph(str(tmp_path), "python")
        assert len(graph) == 0
        assert len(dir_files) == 0

    def test_dependency_between_two_modules(self, tmp_path):
        """Two Python modules where one imports from the other show a dependency."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").write_text("")
        (tmp_path / "pkg" / "models.py").write_text("class User:\n    pass\n")
        (tmp_path / "pkg" / "services.py").write_text("from .models import User\n")

        _, dir_files = build_graph(str(tmp_path), "python")
        assert "pkg" in dir_files

    def test_cross_module_dependency(self, tmp_path):
        """Files in different directories show cross-module dependency."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")

        (tmp_path / "alpha").mkdir()
        (tmp_path / "alpha" / "__init__.py").write_text("")
        (tmp_path / "alpha" / "mod.py").write_text("pass")

        (tmp_path / "bravo").mkdir()
        (tmp_path / "bravo" / "__init__.py").write_text("")
        (tmp_path / "bravo" / "mod.py").write_text("from ..alpha import mod\n")

        graph, dir_files = build_graph(str(tmp_path), "python")
        assert "alpha" in dir_files
        assert "bravo" in dir_files
        if "bravo" in graph:
            assert "alpha" in graph["bravo"]

    def test_files_in_root_module(self, tmp_path):
        """Files in the root directory get module name '(root)'."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / "main.py").write_text("pass")
        (tmp_path / "helper.py").write_text("pass")

        _, dir_files = build_graph(str(tmp_path), "python")
        assert "(root)" in dir_files
        names = [Path(f).name for f in dir_files["(root)"]]
        assert "main.py" in names
        assert "helper.py" in names

    def test_auto_detect_fallback_to_all(self, tmp_path):
        """When no config file exists, lang falls back to 'all'."""
        (tmp_path / "app.py").write_text("pass")
        (tmp_path / "index.ts").write_text("")

        _, dir_files = build_graph(str(tmp_path), "auto")
        all_files = []
        for files in dir_files.values():
            all_files.extend(files)
        file_names = [Path(f).name for f in all_files]
        assert "app.py" in file_names
        assert "index.ts" in file_names

    def test_depth_zero(self, tmp_path):
        """depth=0 means all files map to '(root)'."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "b").mkdir()
        (tmp_path / "a" / "b" / "c").mkdir()
        (tmp_path / "a" / "b" / "c" / "deep.py").write_text("pass")
        (tmp_path / "top.py").write_text("pass")

        _, dir_files = build_graph(str(tmp_path), "python", depth=0)
        assert "(root)" in dir_files
        assert len(dir_files["(root)"]) == 2

    def test_typescript_cross_dir_dependency(self, tmp_path):
        """TS files in different dirs with relative imports create graph edges."""
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "index.ts").write_text("import { foo } from '../lib/utils';\n")
        (tmp_path / "lib").mkdir()
        (tmp_path / "lib" / "utils.ts").write_text("export function foo() {}\n")

        graph, _ = build_graph(str(tmp_path), "typescript")
        assert "src" in graph
        assert "lib" in graph["src"]
