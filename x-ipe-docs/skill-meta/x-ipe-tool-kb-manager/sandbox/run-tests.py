#!/usr/bin/env python3
"""Test runner for x-ipe-tool-kb-manager skill validation."""
import re, os, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # project root
SKILL = ROOT / ".github/skills/x-ipe-tool-kb-manager/SKILL.md"
EXAMPLES = ROOT / ".github/skills/x-ipe-tool-kb-manager/references/examples.md"
TEMPLATES_DIR = ROOT / ".github/skills/x-ipe-tool-kb-manager/templates"

results = []

def record(tc_id, name, priority, passed, detail=""):
    results.append({"id": tc_id, "name": name, "priority": priority, "passed": passed, "detail": detail})

# Read SKILL.md
content = SKILL.read_text() if SKILL.exists() else ""
lines = content.split("\n")

# Parse frontmatter
fm = {}
if content.startswith("---"):
    end = content.index("---", 3)
    fm_text = content[3:end].strip()
    for line in fm_text.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()

# TC-S01: SKILL.md exists with valid frontmatter
ok = SKILL.exists() and fm.get("name") == "x-ipe-tool-kb-manager" and "knowledge" in fm.get("description", "").lower()
record("TC-S01", "SKILL.md exists with valid frontmatter", "must", ok,
       f"exists={SKILL.exists()}, name={fm.get('name')}, desc_has_knowledge={'knowledge' in fm.get('description','').lower()}")

# TC-S02: references/examples.md exists with examples
ex_content = EXAMPLES.read_text() if EXAMPLES.exists() else ""
ex_count = len(re.findall(r"##\s+Example\s+\d+", ex_content))
ok = EXAMPLES.exists() and ex_count >= 2
record("TC-S02", "references/examples.md with examples", "must", ok,
       f"exists={EXAMPLES.exists()}, example_count={ex_count}")

# TC-S03: Under 500 lines
ok = len(lines) < 500
record("TC-S03", "SKILL.md under 500 lines", "must", ok, f"lines={len(lines)}")

# TC-C01: Required sections in order
required_sections = ["Purpose", "Important Notes", "About", "When to Use", "Input Parameters",
                     "Definition of Ready", "Operations", "Output Result", "Definition of Done",
                     "Error Handling", "Examples"]
section_positions = []
for sec in required_sections:
    pat = re.compile(r"^##\s+" + re.escape(sec), re.MULTILINE)
    m = pat.search(content)
    section_positions.append((sec, m.start() if m else -1))
all_found = all(p >= 0 for _, p in section_positions)
in_order = all(section_positions[i][1] < section_positions[i+1][1] for i in range(len(section_positions)-1)) if all_found else False
missing = [s for s, p in section_positions if p < 0]
record("TC-C01", "Sections present in order", "must", all_found and in_order,
       f"all_found={all_found}, in_order={in_order}, missing={missing}")

# TC-C02: Operations use XML structure
ops = ["classify", "search", "reorganize", "cancel"]
op_found = {op: f'<operation name="{op}">' in content for op in ops}
ok = all(op_found.values())
record("TC-C02", "Operations use XML structure", "must", ok, f"found={op_found}")

# TC-C03: Error Handling table columns
err_section = content[content.find("## Error Handling"):] if "## Error Handling" in content else ""
ok = all(col in err_section for col in ["Error", "Cause", "Resolution"])
record("TC-C03", "Error table columns", "must", ok, "checked Error, Cause, Resolution in table")

# TC-C04: Four operations defined
ok = all(op in content for op in ops)
record("TC-C04", "Four operations defined", "must", ok, f"ops={ops}")

# TC-B01: POST /api/kb/process
ok = "POST /api/kb/process" in content
record("TC-B01", "Classify refs POST /api/kb/process", "must", ok)

# TC-B02: GET /api/kb/search
ok = "GET /api/kb/search" in content
record("TC-B02", "Search refs GET /api/kb/search", "must", ok)

# TC-B03: Trigger phrases in description
desc = fm.get("description", "").lower()
ok = all(t in desc for t in ["classify", "search", "reorganize"])
record("TC-B03", "Triggers in frontmatter", "must", ok, f"desc_lower contains classify/search/reorganize")

# TC-C05: When to Use has triggers
wtu_section = ""
m = re.search(r"## When to Use(.*?)(?=\n## )", content, re.DOTALL)
if m: wtu_section = m.group(1)
ok = "triggers:" in wtu_section.lower() or "trigger" in wtu_section.lower()
record("TC-C05", "When to Use has triggers", "should", ok)

# TC-C06: Key Concepts in About
about_section = ""
m = re.search(r"## About(.*?)(?=\n## )", content, re.DOTALL)
if m: about_section = m.group(1)
ok = "Key Concepts" in about_section
record("TC-C06", "Key Concepts in About", "should", ok)

# TC-C07: Templates dir exists
ok = TEMPLATES_DIR.exists() and TEMPLATES_DIR.is_dir()
record("TC-C07", "Templates directory", "could", ok, f"exists={TEMPLATES_DIR.exists()}")

# Summary
must_tests = [r for r in results if r["priority"] == "must"]
should_tests = [r for r in results if r["priority"] == "should"]
could_tests = [r for r in results if r["priority"] == "could"]

must_pass = sum(1 for r in must_tests if r["passed"])
should_pass = sum(1 for r in should_tests if r["passed"])
could_pass = sum(1 for r in could_tests if r["passed"])

print("=" * 60)
print("SKILL VALIDATION: x-ipe-tool-kb-manager")
print("=" * 60)
for r in results:
    status = "✅ PASS" if r["passed"] else "❌ FAIL"
    print(f"  [{r['priority'].upper():6s}] {r['id']}: {status} - {r['name']}")
    if r["detail"]: print(f"           {r['detail']}")
print("-" * 60)
print(f"MUST:   {must_pass}/{len(must_tests)} ({100*must_pass//len(must_tests) if must_tests else 0}%)")
print(f"SHOULD: {should_pass}/{len(should_tests)} ({100*should_pass//len(should_tests) if should_tests else 0}%)")
print(f"COULD:  {could_pass}/{len(could_tests)} ({100*could_pass//len(could_tests) if could_tests else 0}%)")
overall = "PASS" if must_pass == len(must_tests) and (not should_tests or should_pass/len(should_tests) >= 0.8) else "FAIL"
print(f"\nOVERALL: {overall}")
print("=" * 60)

# Write execution-log.json
log = {
    "execution_log": {
        "skill": "x-ipe-tool-kb-manager",
        "timestamp": "2026-02-12T10:42:00Z",
        "results": results,
        "summary": {
            "must": {"passed": must_pass, "total": len(must_tests), "rate": f"{100*must_pass//len(must_tests)}%"},
            "should": {"passed": should_pass, "total": len(should_tests), "rate": f"{100*should_pass//len(should_tests) if should_tests else 0}%"},
            "could": {"passed": could_pass, "total": len(could_tests), "rate": f"{100*could_pass//len(could_tests) if could_tests else 0}%"},
            "overall": overall
        }
    }
}
log_path = Path(__file__).parent / "execution-log.json"
with open(log_path, "w") as f:
    json.dump(log, f, indent=2)
print(f"\nExecution log saved to: {log_path}")
