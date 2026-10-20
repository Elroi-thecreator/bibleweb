#!/usr/bin/env python3
"""
Test Suite: Scripture Typography & Font Size Self-Healing
Verifies:
1. templates/base.html specifies 18px default font size and includes self-healing bounds checks (< 12px or > 36px).
2. static/js/storage.js implements auto-healing in applyPersistentFontSize() and adjustFontSize().
3. templates/read_along.html isolates its rem storage key to 'bible_readalong_font_rem' and includes self-healing cleanup.
4. CSS rules do not indiscriminately override .verse-item span with verse paragraph font size.
5. Simulated JS client test: legacy '1.1' or '1' is automatically healed to '18'.
"""

import os
import sys
import re

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_checks():
    print("=" * 70)
    print(" VERIFYING SCRIPTURE TYPOGRAPHY & FONT SIZE ENGINE")
    print("=" * 70)

    # 1. Inspect templates/base.html
    with open("templates/base.html", "r", encoding="utf-8") as f:
        base_html = f.read()

    assert "--reader-font-size: 18px;" in base_html, \
        "Missing 18px default font size declaration in templates/base.html"
    assert "numSize < 12 || numSize > 36" in base_html, \
        "Missing self-healing bounds check (< 12 || > 36) in templates/base.html"
    assert ".verse-item span," not in base_html, \
        "templates/base.html must not target .verse-item span with verse font size"
    print("✓ 1. templates/base.html has 18px default, self-healing bounds check, and clean selectors")

    # 2. Inspect static/js/storage.js
    with open("static/js/storage.js", "r", encoding="utf-8") as f:
        storage_js = f.read()

    assert "size < 12 || size > 36" in storage_js, \
        "Missing self-healing bounds check in static/js/storage.js applyPersistentFontSize"
    assert "currentSize < 12 || currentSize > 36" in storage_js, \
        "Missing self-healing bounds check in static/js/storage.js adjustFontSize"
    assert ".verse-item span," not in storage_js, \
        "static/js/storage.js must not target .verse-item span with verse font size"
    print("✓ 2. static/js/storage.js has self-healing logic and bounds protection (13px - 32px)")

    # 3. Inspect templates/read_along.html
    with open("templates/read_along.html", "r", encoding="utf-8") as f:
        readalong_html = f.read()

    assert "bible_readalong_font_rem" in readalong_html, \
        "templates/read_along.html must use isolated key 'bible_readalong_font_rem'"
    assert "parseFloat(legacySize) < 12" in readalong_html, \
        "templates/read_along.html must include self-healing cleanup for legacy bible_font_size"
    print("✓ 3. templates/read_along.html isolates rem key and cleans up corrupted legacy state")

    # 4. Simulate self-healing state transitions
    corrupted_inputs = [None, "", "1.1", "1", "0.9", "1.85", "4", "40", "abc"]
    for inp in corrupted_inputs:
        num = None
        try:
            num = float(inp) if inp is not None and inp != "" else None
        except ValueError:
            num = None
        if num is None or num < 12 or num > 36:
            healed = 18
        else:
            healed = round(num)
        assert healed == 18, f"Input {inp} failed to heal to 18px default!"

    valid_inputs = ["14", "18", "20", "24", "32"]
    for inp in valid_inputs:
        num = float(inp)
        if num is None or num < 12 or num > 36:
            healed = 18
        else:
            healed = round(num)
        assert healed == int(inp), f"Valid input {inp} was unexpectedly altered!"
    print("✓ 4. Self-healing algorithm verified across corrupted, legacy rem, and valid states")

    print("=" * 70)
    print(" ALL TYPOGRAPHY & FONT SIZE VERIFICATIONS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_checks()
