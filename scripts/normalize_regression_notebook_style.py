import json
import re
from pathlib import Path

NOTEBOOK_PATH = Path(__file__).resolve().parents[1] / "Life_Expectancy_Regression.ipynb"


def _replace_common_pl(text: str) -> str:
    # Polish wording in human-facing text
    text = text.replace("Preprocessing", "Przygotowanie danych")
    text = text.replace("preprocessing", "przygotowanie danych")
    text = text.replace("preprocessingu", "przygotowania danych")
    return text


def _normalize_markdown_line(line: str) -> str:
    original = line

    # Remove/replace any explicit Pipeline mentions (human-facing)
    if "Uwaga techniczna:" in line and "Pipeline" in line:
        return "Uwaga techniczna: przygotowanie danych wykonujemy etapami (dopasowanie na train → zastosowanie na train/test)."

    if "Nie używamy" in line and "Pipeline" in line:
        return (
            "Przygotowanie danych wykonujemy etapami (dopasowanie na train → zastosowanie na train/test), "
            "a modele trenujemy na macierzy cech po transformacji."
        )

    # Specific headings that existed in older draft
    if re.search(r"^##\s*6\)\s*Preprocessing", line):
        return "## 6) Przygotowanie danych: uzupełnianie braków + standaryzacja + kodowanie `Status`"

    if re.search(r"^##\s*15\)\s*Zapis:.*preprocess", line):
        return "## 15) Zapis: model + przygotowanie danych"

    # General cleanups
    line = line.replace("(bez Pipeline)", "")
    line = line.replace("(bez pipeline)", "")
    line = line.replace("bez `Pipeline`", "")

    # Replace remaining wording
    line = _replace_common_pl(line)
    line = line.replace(" model + preprocess ", " model + przygotowanie danych ")

    # Collapse double spaces introduced by removals
    line = re.sub(r"\s{2,}", " ", line).rstrip()

    return line if line != original else line


def _normalize_code_line(line: str) -> str:
    # Keep identifiers untouched; only adjust comments, docstrings, and human-facing print strings.

    # Comments
    if line.lstrip().startswith("#"):
        line = line.replace("Preprocessing bez Pipeline", "Przygotowanie danych (ręczne fit/transform)")
        line = line.replace("Preprocessing bez `Pipeline`", "Przygotowanie danych")
        line = line.replace("Feature selection", "Dobór cech")
        line = line.replace("Cross-validation", "Walidacja krzyżowa")
        line = line.replace("Permutation importance", "Ważność cech – permutation importance")
        line = line.replace("Country-holdout", "Podział po krajach (country-holdout)")

        line = line.replace("(bez Pipeline)", "")
        line = line.replace("(bez pipeline)", "")
        line = line.replace("– bez sklearn.Pipeline", "")
        line = line.replace("– bez Pipeline", "")
        line = line.replace("– bez pipeline", "")

        line = _replace_common_pl(line)
        line = line.replace("preprocessingu", "przygotowania danych")
        line = line.replace("preprocessu", "przygotowania danych")
        line = re.sub(r"\s{2,}", " ", line).rstrip()
        return line

    # Docstrings / strings (but avoid changing function/variable names)
    if "\"\"\"" in line:
        line = line.replace("Dopasuj preprocess", "Dopasuj przygotowanie danych")
        line = line.replace("Zastosuj dopasowany preprocess", "Zastosuj dopasowane przygotowanie danych")
        line = line.replace("Jeśli jest selector", "Jeśli jest selektor")
        line = line.replace("preprocess", "przygotowanie danych")
        line = line.replace("Pipeline", "")
        return line

    # Print strings
    if "print(" in line and "preprocess" in line:
        line = line.replace("OK: preprocess_bundle gotowy", "OK: przygotowanie danych gotowe")
        line = line.replace("preprocess", "przygotowanie danych")
        return line

    # Other human-facing strings in code
    if "preprocess" in line and "def fit_preprocess" not in line and "def transform_preprocess" not in line:
        # avoid touching identifiers; only adjust obvious narrative strings
        if "#" not in line and "\"" in line:
            line = line.replace("preprocess", "przygotowanie danych")
        return line

    return line


def main() -> None:
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(NOTEBOOK_PATH)

    nb = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    changed = False

    for cell in nb.get("cells", []):
        src = cell.get("source")
        if not isinstance(src, list):
            continue

        new_src = []
        for line in src:
            if not isinstance(line, str):
                new_src.append(line)
                continue

            if cell.get("cell_type") == "markdown":
                new_line = _normalize_markdown_line(line)
            else:
                new_line = _normalize_code_line(line)

            if new_line != line:
                changed = True
            new_src.append(new_line)

        cell["source"] = new_src

    if changed:
        NOTEBOOK_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=4), encoding="utf-8")
        print(f"Updated: {NOTEBOOK_PATH}")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
