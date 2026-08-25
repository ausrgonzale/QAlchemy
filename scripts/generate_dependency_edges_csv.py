import ast
import csv
from collections import defaultdict
from pathlib import Path

SCOPES = ("services", "scripts", "tests")
OUTPUT_FILE = Path("working/output/dependency-edges.csv")
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


def resolve_relative_import(
    current_module: str, level: int, imported_module: str | None
) -> str:
    parts = current_module.split(".")
    package = parts[:-1]
    trim = max(level - 1, 0)
    base = package[: len(package) - trim] if trim <= len(package) else []
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


def bucket(module: str) -> str:
    if module.startswith("services."):
        return "services"
    if module.startswith("scripts."):
        return "scripts"
    if module.startswith("tests."):
        return "tests"
    return "other_repo"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / OUTPUT_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_py = discover_py_files(repo_root)
    repo_modules = {module_name(repo_root, file) for file in all_py}

    scope_files = [
        file for file in all_py if any(scope in file.parts for scope in SCOPES)
    ]

    rows: list[dict[str, str]] = []
    stats = defaultdict(int)

    for file in scope_files:
        source_module = module_name(repo_root, file)
        source_code = file.read_text(encoding="utf-8")
        imports = collect_import_targets(source_module, source_code)

        for imp in sorted(imports):
            matched = best_match_repo_module(imp, repo_modules)
            if matched:
                dep_type = (
                    "internal_scope"
                    if bucket(matched) in SCOPES
                    else "repo_outside_scope"
                )
                target = matched
            else:
                dep_type = "external_unresolved"
                target = imp

            stats[dep_type] += 1
            rows.append(
                {
                    "from": source_module,
                    "to": target,
                    "type": dep_type,
                    "from_bucket": bucket(source_module),
                    "to_bucket": (
                        bucket(target)
                        if dep_type != "external_unresolved"
                        else "external"
                    ),
                }
            )

    with out_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["from", "to", "type", "from_bucket", "to_bucket"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote: {out_path}")
    print("Counts -> " + ", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))


if __name__ == "__main__":
    main()
