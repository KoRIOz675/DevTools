#!/usr/bin/env python3
"""
project_to_text.py
------------------
Convertit un projet multi-fichiers en un seul document texte structuré,
avec un prompt, l'arborescence du projet, puis le contenu de chaque fichier.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# ── Extensions de fichiers texte reconnus ────────────────────────────────────
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".r",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env",
    ".xml", ".svg", ".graphql", ".sql",
    ".md", ".mdx", ".rst", ".txt", ".tex",
    ".dockerfile", ".makefile", ".gitignore", ".gitattributes",
    ".editorconfig", ".prettierrc", ".eslintrc", ".babelrc",
    ""  # fichiers sans extension (Makefile, Dockerfile, etc.)
}

# ── Dossiers à ignorer par défaut ─────────────────────────────────────────────
IGNORED_DIRS = {
    ".git", ".svn", ".hg", ".mvn", ".claude", "neo4j",
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
    "venv", ".venv", "env", ".env",
    "dist", "build", "out", ".next", ".nuxt", "target",
    ".idea", ".vscode",
    "coverage", ".coverage",
}

DEFAULT_PROMPT = """Tu es un assistant expert en développement logiciel.
Voici le code source complet d'un projet. Analyse-le en détail :
- Comprends l'architecture globale et le rôle de chaque fichier
- Identifie les dépendances entre les modules
- Repère les points d'amélioration potentiels (performance, lisibilité, sécurité)
- Sois prêt à répondre à toutes les questions sur ce code

Le projet est présenté ci-dessous avec sa structure et le contenu de chaque fichier."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_text_file(path: Path) -> bool:
    """Vérifie si un fichier est un fichier texte selon son extension."""
    suffix = path.suffix.lower()
    name_lower = path.name.lower()
    # Fichiers connus sans extension
    if name_lower in {"makefile", "dockerfile", "rakefile", "gemfile",
                      "procfile", "readme", "license", "changelog"}:
        return True
    return suffix in TEXT_EXTENSIONS


def build_tree(root: Path, prefix: str = "", ignored_dirs: set = None) -> list[str]:
    """Génère l'arborescence ASCII du projet."""
    if ignored_dirs is None:
        ignored_dirs = IGNORED_DIRS

    lines = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return [f"{prefix}[Permission refusée]"]

    entries = [e for e in entries if not (e.is_dir() and e.name in ignored_dirs)]

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        extension = "/" if entry.is_dir() else ""
        lines.append(f"{prefix}{connector}{entry.name}{extension}")
        if entry.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(build_tree(entry, new_prefix, ignored_dirs))
    return lines


def collect_files(root: Path, ignored_dirs: set = None) -> list[Path]:
    """Collecte tous les fichiers texte du projet de manière récursive."""
    if ignored_dirs is None:
        ignored_dirs = IGNORED_DIRS

    collected = []
    for entry in sorted(root.rglob("*")):
        # Ignorer les dossiers exclus (à n'importe quel niveau)
        if any(part in ignored_dirs for part in entry.parts):
            continue
        if entry.is_file() and is_text_file(entry):
            collected.append(entry)
    return collected


def read_file_safe(path: Path) -> tuple[str, bool]:
    """Lit un fichier de manière sécurisée. Retourne (contenu, succès)."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return path.read_text(encoding=enc), True
        except (UnicodeDecodeError, PermissionError):
            continue
    return "[Impossible de lire ce fichier : encodage non supporté ou permission refusée]", False


def format_separator(title: str, char: str = "=", width: int = 80) -> str:
    return f"\n{char * width}\n{title}\n{char * width}\n"


# ── Fonction principale ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("   Project → Text Converter")
    print("=" * 60)

    # ── 1. Chemin du projet ───────────────────────────────────────────────────
    while True:
        folder_input = input("\n📁 Chemin du dossier projet : ").strip()
        # Enlever les guillemets éventuels (drag & drop sur certains OS)
        folder_input = folder_input.strip('"').strip("'")
        project_path = Path(folder_input).expanduser().resolve()

        if project_path.is_dir():
            print(f"   ✅ Dossier trouvé : {project_path}")
            break
        else:
            print(f"   ❌ Chemin introuvable ou ce n'est pas un dossier. Réessayez.")

    # ── 2. Choix du prompt ────────────────────────────────────────────────────
    print("\n📝 Choix du prompt :")
    print("   [1] Prompt par défaut")
    print("   [2] Prompt personnalisé")

    while True:
        choice = input("\nVotre choix (1 ou 2) : ").strip()
        if choice == "1":
            prompt = DEFAULT_PROMPT
            print("   ✅ Prompt par défaut sélectionné.")
            break
        elif choice == "2":
            print("\nEntrez votre prompt (terminez avec une ligne contenant uniquement 'FIN') :")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "FIN":
                    break
                lines.append(line)
            prompt = "\n".join(lines).strip()
            if not prompt:
                print("   ⚠️  Prompt vide, utilisation du prompt par défaut.")
                prompt = DEFAULT_PROMPT
            else:
                print("   ✅ Prompt personnalisé enregistré.")
            break
        else:
            print("   ❌ Entrez 1 ou 2.")

    # ── 3. Collecte des fichiers ──────────────────────────────────────────────
    print("\n🔍 Analyse du projet en cours...")
    files = collect_files(project_path)
    print(f"   {len(files)} fichier(s) texte trouvé(s).")

    # ── 4. Construction du document ──────────────────────────────────────────
    project_name = project_path.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_lines = []

    # En-tête
    output_lines.append(f"PROJET : {project_name}")
    output_lines.append(f"Généré le : {timestamp}")
    output_lines.append(f"Chemin source : {project_path}")
    output_lines.append("")

    # Prompt
    output_lines.append(format_separator("PROMPT"))
    output_lines.append(prompt)
    output_lines.append("")

    # Arborescence
    output_lines.append(format_separator("STRUCTURE DU PROJET"))
    output_lines.append(f"{project_name}/")
    tree_lines = build_tree(project_path)
    output_lines.extend(tree_lines)
    output_lines.append("")

    # Contenu des fichiers
    output_lines.append(format_separator("CONTENU DES FICHIERS"))

    for file_path in files:
        relative_path = file_path.relative_to(project_path)
        output_lines.append(format_separator(f"📄 {relative_path}", char="-", width=60))
        content, success = read_file_safe(file_path)
        output_lines.append(content)
        output_lines.append("")

    full_output = "\n".join(output_lines)

    # ── 5. Sauvegarde ─────────────────────────────────────────────────────────
    output_path = project_path / f"{project_name}_context.txt"

    try:
        output_path.write_text(full_output, encoding="utf-8")
        size_kb = output_path.stat().st_size / 1024
        print(f"\n✅ Document généré avec succès !")
        print(f"   📄 Fichier : {output_path}")
        print(f"   📦 Taille  : {size_kb:.1f} Ko")
        print(f"   📋 Fichiers inclus : {len(files)}")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'écriture : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
