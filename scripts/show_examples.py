# -*- coding: utf-8 -*-
import sqlite3
import io
import re

db = sqlite3.connect("data/bible.sqlite.db")
c = db.cursor()

c.execute("""
    SELECT v.id, b.code, b.name_ta, v.chapter, v.verse, v.text_ta, v.text_ta_poc
    FROM verses v
    JOIN books b ON v.book_id = b.id
    WHERE v.text_ta_poc LIKE '[%-%]%'
    ORDER BY v.id
""")
rows = c.fetchall()

# Find 10 unique ranges across different books
found_examples = []
seen_ranges = set()

for r in rows:
    vid, code, name_ta, ch, v, text_ta, text_ta_poc = r
    m = re.match(r'\[(\d+)-(\d+)\]', text_ta_poc)
    if m:
        v_start, v_end = int(m.group(1)), int(m.group(2))
        key = (code, ch, v_start, v_end)
        if key not in seen_ranges:
            seen_ranges.add(key)
            found_examples.append((code, name_ta, ch, v_start, v_end))
            if len(found_examples) >= 10:
                break

output_lines = []
for code, name_ta, ch, v_s, v_e in found_examples:
    output_lines.append(f"\n==================================================")
    output_lines.append(f"EXAMPLE: {name_ta} ({code}) {ch}:{v_s}-{v_e}")
    output_lines.append(f"==================================================")
    
    c.execute("""
        SELECT v.verse, v.text_ta, v.text_ta_poc
        FROM verses v
        JOIN books b ON v.book_id = b.id
        WHERE b.code = ? AND v.chapter = ? AND v.verse >= ? AND v.verse <= ?
        ORDER BY v.verse
    """, (code, ch, v_s, v_e))
    v_rows = c.fetchall()
    
    output_lines.append("\n[PROTESTANT (BSI - Distinct/Separated Verses)]")
    for v_num, p_ta, c_ta in v_rows:
        output_lines.append(f"  வசனம் {v_num}: {p_ta}")
        
    output_lines.append(f"\n[CATHOLIC (POC திருவிவிலியம் - Combined Sentence/Unit {v_s}-{v_e})]")
    # Show the combined text
    output_lines.append(f"  வசனம் {v_s}-{v_e}: {v_rows[0][2]}")

with io.open("examples_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Wrote 10 examples to examples_output.txt")
