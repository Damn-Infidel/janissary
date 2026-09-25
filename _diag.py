from pathlib import Path

p = Path("WORKFLOW.md")
print("exists:", p.exists())
src = p.read_text(encoding="utf-8")
print("length before:", len(src))

old = "- [ ] P3.1 SQLi UNION extractor (gated behind --attack-confirm)"
print("checklist match:", old in src)

print("current step match:", "## Current step" in src)
print("git note match:", "## Git status note (deferred)" in src)
print("legal match:", "## Legal framework" in src)
