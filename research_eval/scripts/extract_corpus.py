#!/usr/bin/env python3
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT.parent / "sampledocs"
OUTPUT_DIR = ROOT / "research_eval" / "corpus"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_pdf(path: Path) -> str:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext is required for PDF extraction")
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_docx(path: Path) -> str:
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as archive:
        xml = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for paragraph in xml.iter(namespace + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(namespace + "t"))
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def extract_xlsx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(
            archive.read("xl/_rels/workbook.xml.rels")
        )
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            shared_strings = [
                "".join(node.text or "" for node in item.iter(ns + "t"))
                for item in root.findall(ns + "si")
            ]

        rel_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
        rels = {
            relationship.attrib["Id"]: relationship.attrib["Target"]
            for relationship in relationships.findall(rel_ns + "Relationship")
        }
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        lines = []
        for sheet in workbook.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets"):
            title = sheet.attrib.get("name", "Sheet")
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rels[rid].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            sheet_xml = ElementTree.fromstring(archive.read(target))
            lines.append(f"[Sheet: {title}]")
            for row in sheet_xml.iter(ns + "row"):
                values = []
                for cell in row.findall(ns + "c"):
                    value = cell.find(ns + "v")
                    value_text = "" if value is None else (value.text or "")
                    if cell.attrib.get("t") == "s" and value_text:
                        value_text = shared_strings[int(value_text)]
                    values.append(value_text)
                if any(values):
                    lines.append("\t".join(values))
        return "\n".join(lines)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for path in sorted(SOURCE_DIR.iterdir()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                text = extract_pdf(path)
            elif suffix == ".docx":
                text = extract_docx(path)
            elif suffix == ".xlsx":
                text = extract_xlsx(path)
            else:
                continue
        except Exception as exc:
            print(f"ERROR {path.name}: {exc}", file=sys.stderr)
            continue

        text_path = OUTPUT_DIR / f"{path.stem}.txt"
        text_path.write_text(text, encoding="utf-8")
        manifest.append(
            {
                "document_id": path.stem,
                "source": str(path),
                "source_sha256": sha256(path),
                "extracted_text": str(text_path),
                "characters": len(text),
                "words": len(text.split()),
            }
        )
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Extracted {len(manifest)} documents into {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
