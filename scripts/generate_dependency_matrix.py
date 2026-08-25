import ast
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SCOPES = ("services", "scripts", "tests")
OUTPUT_FILE = Path("working/output/dependency-matrix.md")
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}


def module_name(repo_root: Path, py_file: Path) -> str:
    rel = py_file.relative_to(repo_root).with_suffix("")
    return ".".join(rel.parts)


def node_id(name: str) -> str:
    return "n_" + re.sub(r"[^a-zA-Z0-9_]", "_", name)


def resolve_relative_import(
    current_module: str, level: int, imported_module: str | None
) -> str:
    parts = current_module.split(".")
    package = parts[:-1]
    trim = max(level - 1, 0)

    if trim > len(package):
        base = []
    else:
        base = package[: len(package) - trim]

    if imported_module:
        return ".".join(base + imported_module.split("."))

    return ".".join(base)


def collect_import_targets(py_module: str, source: str) -> set[str]:
    tree = ast.parse(source)
    targets: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                targets.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                base = resolve_relative_import(py_module, node.level, node.module)
                if node.module is None:
                    for alias in node.names:
                        targets.add(f"{base}.{alias.name}" if base else alias.name)
                else:
                    targets.add(base)
            elif node.module:
                targets.add(node.module)

    return targets


def best_match_repo_module(import_target: str, repo_modules: set[str]) -> str | None:
    current = import_target
    while current:
        if current in repo_modules:
            return current
        if "." not in current:
            return None
        current = current.rsplit(".", 1)[0]
    return None


def discover_py_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def in_scope(module: str) -> bool:
    return (
        module.startswith("services.")
        or module.startswith("scripts.")
        or module.startswith("tests.")
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_py = discover_py_files(repo_root)
    repo_modules = {module_name(repo_root, file) for file in all_py}

    scope_files = [
        file for file in all_py if any(scope in file.parts for scope in SCOPES)
    ]
    scope_modules = {module_name(repo_root, file) for file in scope_files}

    edges_internal: dict[str, set[str]] = defaultdict(set)
    edges_outside_scope: dict[str, set[str]] = defaultdict(set)
    unresolved_external: dict[str, set[str]] = defaultdict(set)

    for file in scope_files:
        src_mod = module_name(repo_root, file)
        source = file.read_text(encoding="utf-8")
        imports = collect_import_targets(src_mod, source)

        for imp in sorted(imports):
            matched = best_match_repo_module(imp, repo_modules)
            if matched:
                if in_scope(matched):
                    edges_internal[src_mod].add(matched)
                else:
                    edges_outside_scope[src_mod].add(matched)
            else:
                unresolved_external[src_mod].add(imp)

    nodes = sorted(scope_modules)

    lines: list[str] = []
    lines.append("# Complete Code Dependency Matrix")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("- Scope: `services/`, `scripts/`, `tests/`")
    lines.append("")

    lines.append("## Mermaid Dependency Graph (Internal Scope)")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")

    for section in ("services", "scripts", "tests"):
        section_nodes = [module for module in nodes if module.startswith(f"{section}.")]
        lines.append(f'  subgraph {section}["{section}"]')
        for module in section_nodes:
            lines.append(f'    {node_id(module)}["{module}"]')
        lines.append("  end")

    for src in sorted(edges_internal):
        for dst in sorted(edges_internal[src]):
            lines.append(f"  {node_id(src)} --> {node_id(dst)}")

    lines.append("```")
    lines.append("")

    lines.append("## Dependency Matrix (Adjacency)")
    lines.append("")
    lines.append(
        "| Module | Internal Dependencies (services/scripts/tests) | Repo Dependencies Outside Scope | Unresolved/External Imports |"
    )
    lines.append("|---|---|---|---|")

    for src in nodes:
        internal = (
            ", ".join(f"`{dep}`" for dep in sorted(edges_internal.get(src, set())))
            or "—"
        )
        outside = (
            ", ".join(f"`{dep}`" for dep in sorted(edges_outside_scope.get(src, set())))
            or "—"
        )
        external = (
            ", ".join(f"`{dep}`" for dep in sorted(unresolved_external.get(src, set())))
            or "—"
        )
        lines.append(f"| `{src}` | {internal} | {outside} | {external} |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
