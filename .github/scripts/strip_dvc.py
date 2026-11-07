"""Retire le frontend DVC obscurci d'une version upstream de dreame-vacuum.

Usage : python3 strip_dvc.py <version>   (ex. v2.0.4.1)

Échoue (code 1) si la structure upstream a changé au point que le retrait
n'est plus sûr : dans ce cas, aucune version n'est publiée.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG = ROOT / "custom_components" / "dreame_vacuum"


def fail(msg: str) -> None:
    print(f"ERREUR : {msg}", file=sys.stderr)
    sys.exit(1)


def main(version: str) -> None:
    init = (PKG / "__init__.py").read_text(encoding="utf-8")
    # frontend.py doit rester optionnel côté upstream
    if "frontend = None" not in init or "ModuleNotFoundError" not in init:
        fail("__init__.py ne gère plus l'absence de frontend.py")

    frontend = PKG / "frontend.py"
    if frontend.exists():
        frontend.unlink()

    # Bloc FRONTEND retiré en binaire pour préserver les fins de ligne mixtes
    const = PKG / "const.py"
    data = const.read_bytes()
    match = re.search(rb"^FRONTEND: Final = \(.*?^\)\r?\n(\r?\n)?", data, re.S | re.M)
    if match:
        data = data[: match.start()] + data[match.end() :]
        const.write_bytes(data)

    # Plus aucune trace du code retiré
    for path in PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "api.tasshack.com" in text:
            fail(f"api.tasshack.com encore présent dans {path.relative_to(ROOT)}")
        if re.search(r"\bFRONTEND\b", text):
            fail(f"référence à FRONTEND restante dans {path.relative_to(ROOT)}")
        compile(text, str(path), "exec")

    hacs_path = ROOT / "hacs.json"
    hacs = json.loads(hacs_path.read_text(encoding="utf-8"))
    hacs.pop("zip_release", None)
    hacs.pop("filename", None)
    hacs["name"] = "Dreame Vacuum (sans DVC)"
    hacs["content_in_root"] = False
    hacs_path.write_text(json.dumps(hacs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest_path = PKG / "manifest.json"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_text, count = re.subn(r'("version"\s*:\s*")[^"]*(")', rf"\g<1>{version}\g<2>", manifest_text)
    if count != 1:
        fail("champ version introuvable dans manifest.json")
    manifest_path.write_text(manifest_text, encoding="utf-8")

    print(f"OK : frontend DVC retiré, version {version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage : strip_dvc.py <version>")
    main(sys.argv[1])
