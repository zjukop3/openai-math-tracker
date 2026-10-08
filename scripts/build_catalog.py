#!/usr/bin/env python3
"""Build the structured catalog for openai-math-tracker.

Parses upstream data files (fetched by scripts/fetch_upstream.sh):
  - data/overview.tex        -> disciplines, families, descriptions, manuscript links
  - data/CONTENTS.md         -> manuscript titles, PDF paths, abstracts
  - data/formalization.yaml  -> formalized sources, Lean main results, review status
  - data/reasoning_traces.txt-> reasoning-trace file names (one per line)

Outputs:
  - data/catalog.json        nested: disciplines -> families -> manuscripts
  - data/manuscripts.csv     flat table, one row per manuscript
  - data/stats.json          headline numbers for README / badges
  - docs/VERIFICATION.md     verification tracker table (regenerated)
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ---------------------------------------------------------------- TeX helpers

def read_balanced(text: str, start: int) -> tuple[str, int]:
    """Read a {...} group starting at text[start] == '{'. Returns (content, end)."""
    assert text[start] == "{"
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif c == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
    raise ValueError("unbalanced braces")

ACCENTS = {
    "'e": "é", "'E": "É", "`e": "è", '"u': "ü", '"o': "ö", '"a': "ä",
    "'a": "á", "~n": "ñ", "'c": "ć", "'o": "ó", "^o": "ô", "'i": "í",
    '"U': "Ü", '"O': "Ö", '"A': "Ä", "'u": "ú", "`a": "à",
}

SYMBOLS = {
    "pi": "π", "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "epsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "rho": "ρ", "sigma": "σ",
    "tau": "τ", "phi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Sigma": "Σ",
    "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω", "log": "log", "infty": "∞",
    "mathbb": "", "mathcal": "", "mathrm": "", "operatorname": "",
    "overline": "", "widetilde": "", "widehat": "", "sqrt": "√", "ell": "ℓ",
    "le": "≤", "ge": "≥", "ne": "≠", "pm": "±", "times": "×", "otimes": "⊗",
    "enspace": " ", "enskip": " ", "quad": " ", "qquad": " ", ",": " ", ";": " ",
}

def clean_tex(s: str) -> str:
    """Light TeX -> Unicode cleanup for display fields."""
    s = re.sub(r"\\([`'^\"~])([a-zA-Z])", lambda m: ACCENTS.get(m.group(1) + m.group(2), m.group(2)), s)
    s = s.replace("--", "–")
    s = re.sub(r"\\([a-zA-Z]+)\s*", lambda m: SYMBOLS.get(m.group(1), ""), s)
    s = re.sub(r"[$}{]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    # fix spacing artifacts like "below nn" from "$n\log n$"
    s = re.sub(r"(\w)log(\w)", r"\1 log \2", s)
    return s

# ------------------------------------------------------------- overview.tex

def parse_overview(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    disciplines = []
    # Split on \cataloguesection{...}{...}
    for m in re.finditer(r"\\cataloguesection\{", text):
        disc, pos = read_balanced(text, m.end() - 1)
        _num, pos = read_balanced(text, text.index("{", pos))
        # section body runs to next \cataloguesection or end
        nxt = text.find("\\cataloguesection{", pos)
        body = text[pos : nxt if nxt != -1 else len(text)]
        families = []
        for rm in re.finditer(r"\\resultentry\{", body):
            num_raw, p = read_balanced(body, rm.end() - 1)
            title, p = read_balanced(body, body.index("{", p))
            desc, p = read_balanced(body, body.index("{", p))
            links_raw, p = read_balanced(body, body.index("{", p))
            links = []
            for lm in re.finditer(
                r"\\href\{https://github\.com/openai/math/blob/main/preprints/([^/}]+)/[^}]*\}\{", links_raw
            ):
                link_text, _ = read_balanced(links_raw, links_raw.index("{", lm.end() - 1))
                links.append({"dir": lm.group(1), "short_title": clean_tex(link_text)})
            families.append(
                {
                    "id": num_raw.strip(),
                    "title": clean_tex(title),
                    "description": clean_tex(desc),
                    "links": links,
                }
            )
        disciplines.append({"name": clean_tex(disc), "families": families})
    return disciplines

# ------------------------------------------------------------ CONTENTS.md

FAMILY_RE = re.compile(r"^\*\*(\d{3})\.\s+(.*?)\.\*\*\s+(.*)$", re.S)
MANUSCRIPT_RE = re.compile(r"^&emsp;\[(.*?)\]\((.*?)\)\s*$")

def parse_contents(path: Path) -> dict[str, dict]:
    """Returns {family_id: {description, manuscripts: [{title, pdf, abstract}]}}"""
    families: dict[str, dict] = {}
    current = None
    current_ms = None
    abstract_lines: list[str] = []
    state = None  # None | "family" | "manuscript"

    def flush_abstract():
        nonlocal abstract_lines, current_ms
        if current_ms is not None and abstract_lines:
            current_ms["abstract"] = " ".join(abstract_lines).strip()
        abstract_lines = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        fm = FAMILY_RE.match(line)
        if fm:
            flush_abstract()
            fid, title, desc = fm.groups()
            current = fid
            families[fid] = {
                "title": clean_tex(title),
                "description": clean_tex(desc),
                "manuscripts": [],
            }
            current_ms = None
            state = "family"
            continue
        mm = MANUSCRIPT_RE.match(line)
        if mm and current is not None:
            flush_abstract()
            title, pdf = mm.groups()
            mdir = pdf.split("/")[1] if "/" in pdf else ""
            current_ms = {"title": clean_tex(title), "pdf": pdf, "dir": mdir, "abstract": ""}
            families[current]["manuscripts"].append(current_ms)
            state = "manuscript"
            continue
        if state == "manuscript" and line and not line.startswith("<") and not line.startswith("&emsp"):
            abstract_lines.append(clean_tex(line))
        elif line.startswith("</td>"):
            flush_abstract()
            current_ms = None if state == "manuscript" else current_ms
            state = None
    flush_abstract()
    return families

# ------------------------------------------------------- formalization.yaml

def parse_formalization(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # formalized preprint dirs from sources[].id
    formalized_dirs = sorted(set(re.findall(r"id:\s*\.\./preprints/([^/\n]+)/", text)))
    # main results
    main_results = []
    for m in re.finditer(
        r"-\s*comparator_config:\s*(\S+)\s*\n\s*declaration:\s*(\S+)\s*\n\s*file:\s*(\S+)", text
    ):
        main_results.append(
            {"comparator_config": m.group(1), "declaration": m.group(2), "file": m.group(3)}
        )
    scope = re.search(r"scope:\s*\"([^\"]*)\"", text)
    review = re.search(r"review:\s*\n\s*status:\s*(\S+)", text)
    return {
        "formalized_dirs": formalized_dirs,
        "main_results": main_results,
        "scope": scope.group(1) if scope else "",
        "review_status": review.group(1) if review else "unknown",
    }

# ------------------------------------------------------------------- main

def main() -> int:
    disciplines = parse_overview(DATA / "overview.tex")
    contents = parse_contents(DATA / "CONTENTS.md")
    formal = parse_formalization(DATA / "formalization.yaml")
    traces = [
        l.strip()
        for l in (DATA / "reasoning_traces.txt").read_text().splitlines()
        if l.strip().endswith(".pdf")
    ]

    formalized_set = set(formal["formalized_dirs"])

    n_manuscripts = 0
    n_formalized = 0
    rows = []
    for disc in disciplines:
        for fam in disc["families"]:
            c = contents.get(fam["id"], {"manuscripts": [], "description": "", "title": fam["title"]})
            # Prefer the (fuller) CONTENTS.md description when available.
            if c.get("description"):
                fam["description"] = c["description"]
            mss = []
            for link in fam["links"]:
                ms = next((m for m in c["manuscripts"] if m["dir"] == link["dir"]), None)
                entry = {
                    "dir": link["dir"],
                    "short_title": link["short_title"],
                    "title": ms["title"] if ms else link["short_title"],
                    "pdf": ms["pdf"] if ms else "",
                    "abstract": ms["abstract"] if ms else "",
                    "formalized": link["dir"] in formalized_set,
                }
                mss.append(entry)
                n_manuscripts += 1
                n_formalized += entry["formalized"]
                rows.append(
                    {
                        "family_id": fam["id"],
                        "discipline": disc["name"],
                        "family_title": fam["title"],
                        "manuscript_title": entry["title"],
                        "preprint_dir": entry["dir"],
                        "pdf_url": f"https://github.com/openai/math/blob/main/{entry['pdf']}" if entry["pdf"] else "",
                        "formalized": entry["formalized"],
                    }
                )
            # manuscripts present in CONTENTS.md but missing from overview.tex links
            linked = {l["dir"] for l in fam["links"]}
            for m in c["manuscripts"]:
                if m["dir"] not in linked:
                    entry = {
                        "dir": m["dir"], "short_title": m["title"], "title": m["title"],
                        "pdf": m["pdf"], "abstract": m["abstract"],
                        "formalized": m["dir"] in formalized_set,
                    }
                    mss.append(entry)
                    n_manuscripts += 1
                    n_formalized += entry["formalized"]
                    rows.append(
                        {
                            "family_id": fam["id"], "discipline": disc["name"],
                            "family_title": fam["title"], "manuscript_title": m["title"],
                            "preprint_dir": m["dir"],
                            "pdf_url": f"https://github.com/openai/math/blob/main/{m['pdf']}",
                            "formalized": entry["formalized"],
                        }
                    )
            fam["manuscripts"] = mss
            fam.pop("links", None)

    stats = {
        "manuscripts": n_manuscripts,
        "families": sum(len(d["families"]) for d in disciplines),
        "disciplines": {d["name"]: len(d["families"]) for d in disciplines},
        "formalized_manuscripts": n_formalized,
        "formalization_scope": formal["scope"],
        "lean_review_status": formal["review_status"],
        "lean_main_results": len(formal["main_results"]),
        "reasoning_traces": len(traces),
        "reasoning_trace_files": traces,
    }

    (DATA / "catalog.json").write_text(
        json.dumps({"disciplines": disciplines}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (DATA / "manuscripts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (DATA / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------ VERIFICATION.md
    overrides_path = DATA / "verification_overrides.json"
    overrides = {}
    if overrides_path.exists():
        overrides = json.loads(overrides_path.read_text(encoding="utf-8")).get("overrides", {})
    status_icon = {
        "confirmed": "✅ confirmed",
        "partial": "🟡 partial",
        "issue-found": "🟠 issue found",
        "refuted": "🔴 refuted",
    }
    lines = [
        "# Verification tracker / 验证状态追踪",
        "",
        "> Auto-generated by `scripts/build_catalog.py`. Do not edit by hand; edit `data/verification_overrides.json` instead.",
        "",
        "Status legend / 状态说明:",
        "- **Lean**: manuscript has an accompanying Lean formalization upstream (per `lean/formalization.yaml`). Upstream review status: `%s` (%s)."
        % (formal["review_status"], formal["scope"]),
        "- **Community**: independent human/AI check status. `⬜ unchecked` by default; PR `data/verification_overrides.json` to update.",
        "",
        "| Family | Discipline | Result | Manuscripts | Lean | Community | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for disc in disciplines:
        for fam in disc["families"]:
            n_lean = sum(1 for m in fam["manuscripts"] if m["formalized"])
            lean_cell = f"{n_lean}/{len(fam['manuscripts'])}" if n_lean else "—"
            ov = overrides.get(fam["id"], {})
            community = status_icon.get(ov.get("status", ""), "⬜ unchecked")
            notes = ov.get("notes", "")
            if ov.get("evidence"):
                notes = (notes + " " if notes else "") + f"[evidence]({ov['evidence']})"
            lines.append(
                "| %s | %s | %s | %d | %s | %s | %s |"
                % (fam["id"], disc["name"], fam["title"], len(fam["manuscripts"]), lean_cell, community, notes)
            )
    (ROOT / "docs" / "VERIFICATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    json.dump(stats, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
