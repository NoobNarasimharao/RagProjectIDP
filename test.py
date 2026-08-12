from pathlib import Path
from markitdown import MarkItDown
import ast
import os
import subprocess
import json


# ============================================================
# CONFIG
# ============================================================

OUTPUT_FILE = "PROJECT_DOCUMENTATION.md"

# Directories that should NOT be documented
IGNORE_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".idea",
    "coverage",
    "site-packages",
}

# Files that should NOT be included
IGNORE_FILES = {
    OUTPUT_FILE,
    ".gitignore",
    ".gitattributes",
}

# Binary / generated files
IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".mp3",
    ".mp4",
    ".wav",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}


# ============================================================
# MARKITDOWN
# ============================================================

md_converter = MarkItDown()


# ============================================================
# LANGUAGE DETECTION
# ============================================================

LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sql": "sql",
    ".sh": "bash",
    ".bat": "bat",
    ".ps1": "powershell",
    ".md": "markdown",
    ".txt": "text",
    ".env": "dotenv",
}


# ============================================================
# FILE HELPERS
# ============================================================

def should_ignore(path: Path):
    """
    Decide whether a file/directory should be ignored.
    """

    for part in path.parts:

        if part in IGNORE_DIRS:
            return True

    if path.name in IGNORE_FILES:
        return True

    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True

    return False


def get_language(path: Path):
    return LANGUAGES.get(path.suffix.lower(), "")


def read_text_file(path: Path):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    ]

    for encoding in encodings:

        try:

            return path.read_text(
                encoding=encoding,
                errors="strict"
            )

        except UnicodeDecodeError:
            continue

    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


# ============================================================
# TREE
# ============================================================

def generate_tree(root: Path):

    lines = []

    all_paths = sorted(root.rglob("*"))

    for path in all_paths:

        if should_ignore(path):
            continue

        relative = path.relative_to(root)

        depth = len(relative.parts) - 1

        prefix = "    " * depth

        if path.is_dir():

            lines.append(
                f"{prefix}📁 {path.name}/"
            )

        else:

            lines.append(
                f"{prefix}📄 {path.name}"
            )

    return "\n".join(lines)


# ============================================================
# PYTHON ANALYSIS
# ============================================================

def analyze_python(path: Path):

    result = {
        "imports": [],
        "functions": [],
        "classes": [],
        "variables": [],
    }

    try:

        source = read_text_file(path)

        tree = ast.parse(source)

    except Exception:

        return result

    for node in ast.walk(tree):

        # Imports
        if isinstance(node, ast.Import):

            for alias in node.names:

                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            for alias in node.names:

                result["imports"].append(
                    f"{module}.{alias.name}"
                )

        # Functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            args = []

            for arg in node.args.args:

                args.append(arg.arg)

            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "arguments": args,
                "docstring": ast.get_docstring(node),
            })

        # Classes
        elif isinstance(node, ast.ClassDef):

            methods = []

            for child in node.body:

                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):

                    methods.append(child.name)

            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods,
                "docstring": ast.get_docstring(node),
            })

    return result


# ============================================================
# FILE ANALYSIS
# ============================================================

def analyze_file(path: Path, root: Path):

    relative = path.relative_to(root)

    output = []

    output.append(f"## `{relative}`")

    output.append("")

    output.append(
        f"**File type:** `{path.suffix or 'no extension'}`"
    )

    output.append(
        f"**Size:** `{path.stat().st_size:,} bytes`"
    )

    output.append("")

    # --------------------------------------------------------
    # Python analysis
    # --------------------------------------------------------

    if path.suffix.lower() == ".py":

        analysis = analyze_python(path)

        if analysis["imports"]:

            output.append("### Imports")

            for item in sorted(set(analysis["imports"])):

                output.append(
                    f"- `{item}`"
                )

            output.append("")

        if analysis["classes"]:

            output.append("### Classes")

            for cls in analysis["classes"]:

                output.append(
                    f"#### `{cls['name']}`"
                )

                output.append(
                    f"- Line: `{cls['line']}`"
                )

                if cls["methods"]:

                    output.append("- Methods:")

                    for method in cls["methods"]:

                        output.append(
                            f"  - `{method}()`"
                        )

                if cls["docstring"]:

                    output.append(
                        f"- Description: {cls['docstring']}"
                    )

                output.append("")

        if analysis["functions"]:

            output.append("### Functions")

            for func in analysis["functions"]:

                args = ", ".join(func["arguments"])

                output.append(
                    f"#### `{func['name']}({args})`"
                )

                output.append(
                    f"- Line: `{func['line']}`"
                )

                if func["docstring"]:

                    output.append(
                        f"- Description: {func['docstring']}"
                    )

                output.append("")

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    try:

        content = read_text_file(path)

        language = get_language(path)

        output.append("### Source Code")

        output.append("")

        output.append(
            f"```{language}"
        )

        output.append(content)

        output.append("```")

        output.append("")

    except Exception as e:

        output.append(
            f"> Could not read this file: `{e}`"
        )

        output.append("")

    return "\n".join(output)


# ============================================================
# DOCUMENT CONVERSION
# ============================================================

def convert_document(path: Path):

    try:

        result = md_converter.convert(str(path))

        return result.text_content

    except Exception as e:

        return f"Conversion failed: {e}"


# ============================================================
# REPOSITORY METADATA
# ============================================================

def get_git_info():

    info = {}

    commands = {
        "remote": [
            "git",
            "remote",
            "-v",
        ],

        "branch": [
            "git",
            "branch",
            "--show-current",
        ],

        "commit": [
            "git",
            "log",
            "-1",
            "--pretty=%H",
        ],

        "commit_message": [
            "git",
            "log",
            "-1",
            "--pretty=%s",
        ],
    }

    for key, command in commands.items():

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
            )

            info[key] = result.stdout.strip()

        except Exception:

            info[key] = ""

    return info


# ============================================================
# DEPENDENCY DETECTION
# ============================================================

def detect_dependencies(root: Path):

    dependencies = []

    files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "Pipfile",
        "environment.yml",
        "pom.xml",
        "build.gradle",
        "Cargo.toml",
    ]

    for filename in files:

        path = root / filename

        if path.exists():

            dependencies.append(
                f"- `{filename}`"
            )

    return dependencies


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_documentation():

    root = Path.cwd()

    print("Scanning repository...")
    print(f"Root: {root}")

    git = get_git_info()

    output = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    output.append(
        "# Complete Repository Documentation"
    )

    output.append("")

    output.append(
        "> Automatically generated repository documentation."
    )

    output.append(
        "> Source code and repository structure are included below."
    )

    output.append("")

    # --------------------------------------------------------
    # Repository information
    # --------------------------------------------------------

    output.append(
        "## Repository Information"
    )

    output.append("")

    if git.get("remote"):

        output.append(
            f"**Git Remote:** `{git['remote']}`"
        )

    if git.get("branch"):

        output.append(
            f"**Branch:** `{git['branch']}`"
        )

    if git.get("commit"):

        output.append(
            f"**Latest Commit:** `{git['commit']}`"
        )

    if git.get("commit_message"):

        output.append(
            f"**Latest Commit Message:** `{git['commit_message']}`"
        )

    output.append("")

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    output.append(
        "## Dependency / Configuration Files"
    )

    output.append("")

    dependencies = detect_dependencies(root)

    if dependencies:

        output.extend(dependencies)

    else:

        output.append(
            "No common dependency files detected."
        )

    output.append("")

    # --------------------------------------------------------
    # Repository tree
    # --------------------------------------------------------

    output.append(
        "## Repository Structure"
    )

    output.append("")

    output.append("```text")

    output.append(
        generate_tree(root)
    )

    output.append("```")

    output.append("")

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    output.append(
        "# File-by-File Documentation"
    )

    output.append("")

    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        files.append(path)

    files.sort(
        key=lambda x: str(x.relative_to(root)).lower()
    )

    print(
        f"Found {len(files)} files to document."
    )

    for index, path in enumerate(files, 1):

        print(
            f"[{index}/{len(files)}] {path.relative_to(root)}"
        )

        # ----------------------------------------------------
        # Standard source/document files
        # ----------------------------------------------------

        if path.suffix.lower() in {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".html",
            ".htm",
            ".css",
            ".scss",
            ".sass",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".md",
            ".txt",
            ".env",
        }:

            output.append(
                analyze_file(path, root)
            )

        # ----------------------------------------------------
        # Documents supported by MarkItDown
        # ----------------------------------------------------

        elif path.suffix.lower() in {
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".csv",
            ".html",
            ".xml",
        }:

            relative = path.relative_to(root)

            output.append(
                f"## `{relative}`"
            )

            output.append("")

            output.append(
                "### Converted Content"
            )

            output.append("")

            output.append(
                convert_document(path)
            )

            output.append("")

        # ----------------------------------------------------
        # Unknown files
        # ----------------------------------------------------

        else:

            relative = path.relative_to(root)

            output.append(
                f"## `{relative}`"
            )

            output.append("")

            output.append(
                "> Binary or unsupported file type skipped."
            )

            output.append("")

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    output_path = root / OUTPUT_FILE

    output_path.write_text(
        "\n".join(output),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("DOCUMENTATION GENERATED")
    print("=" * 60)
    print()
    print(output_path)


if __name__ == "__main__":

    generate_documentation()