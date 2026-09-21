import sqlite3
import json
import os

DB_PATH = "data/bible.sqlite.db"
OUT_DIR = os.path.join("static", "plans")
os.makedirs(OUT_DIR, exist_ok=True)

# Standard English Book Names mapped by book id (1 to 66)
BOOK_NAMES_EN = {
    1: "Genesis", 2: "Exodus", 3: "Leviticus", 4: "Numbers", 5: "Deuteronomy",
    6: "Joshua", 7: "Judges", 8: "Ruth", 9: "1 Samuel", 10: "2 Samuel",
    11: "1 Kings", 12: "2 Kings", 13: "1 Chronicles", 14: "2 Chronicles", 15: "Ezra",
    16: "Nehemiah", 17: "Esther", 18: "Job", 19: "Psalms", 20: "Proverbs",
    21: "Ecclesiastes", 22: "Song of Solomon", 23: "Isaiah", 24: "Jeremiah", 25: "Lamentations",
    26: "Ezekiel", 27: "Daniel", 28: "Hosea", 29: "Joel", 30: "Amos",
    31: "Obadiah", 32: "Jonah", 33: "Micah", 34: "Nahum", 35: "Habakkuk",
    36: "Zephaniah", 37: "Haggai", 38: "Zechariah", 39: "Malachi",
    40: "Matthew", 41: "Mark", 42: "Luke", 43: "John", 44: "Acts",
    45: "Romans", 46: "1 Corinthians", 47: "2 Corinthians", 48: "Galatians", 49: "Ephesians",
    50: "Philippians", 51: "Colossians", 52: "1 Thessalonians", 53: "2 Thessalonians", 54: "1 Timothy",
    55: "2 Timothy", 56: "Titus", 57: "Philemon", 58: "Hebrews", 59: "James",
    60: "1 Peter", 61: "2 Peter", 62: "1 John", 63: "2 John", 64: "3 John",
    65: "Jude", 66: "Revelation"
}

# Curated blessing promises for book clusters
BOOK_BLESSINGS = {
    1: {"ref": "Genesis 1:28", "ta": "தேவன் அவர்களை ஆசீர்வதித்து, நீங்கள் பலுகிப் பெருகி, பூமியை நிரப்புங்கள் என்றார்.", "en": "And God blessed them, saying, Be fruitful, and multiply, and fill the earth."},
    2: {"ref": "Exodus 14:14", "ta": "கர்த்தர் உங்களுக்காக யுத்தம்பண்ணுவார்; நீங்கள் சும்மாயிருப்பீர்கள்.", "en": "The Lord will fight for you; you need only to be still."},
    19: {"ref": "Psalm 23:1", "ta": "கர்த்தர் என் மேய்ப்பராயிருக்கிறார்; நான் தாழ்ச்சியடையேன்.", "en": "The Lord is my shepherd; I shall not want."},
    20: {"ref": "Proverbs 3:5-6", "ta": "உன் முழு இருதயத்தோடும் கர்த்தரில் நம்பிக்கையாயிரு; அவர் உன் பாதைகளைச் செவ்வைப்படுத்துவார்.", "en": "Trust in the Lord with all your heart; and he shall direct your paths."},
    23: {"ref": "Isaiah 40:31", "ta": "கர்த்தருக்குக் காத்திருக்கிறவர்களோ புதுப்பெலன் அடைந்து, கழுகுகளைப்போலச் செட்டைகளை அடித்து எழும்புவார்கள்.", "en": "They that wait upon the Lord shall renew their strength; they shall mount up with wings as eagles."},
    40: {"ref": "Matthew 11:28", "ta": "வருத்தப்பட்டுப் பாரஞ்சுமக்கிறவர்களே! நீங்கள் எல்லாரும் என்னிடத்தில் வாருங்கள்; நான் உங்களுக்கு இளைப்பாறுதல் தருவேன்.", "en": "Come unto me, all ye that labour and are heavy laden, and I will give you rest."},
    43: {"ref": "John 14:27", "ta": "சமாதானத்தை உங்களுக்கு வைத்துப்போகிறேன், என்னுடைய சமாதானத்தையே உங்களுக்குக் கொடுக்கிறேன்.", "en": "Peace I leave with you, my peace I give unto you."},
    45: {"ref": "Romans 8:28", "ta": "தேவனிடத்தில் அன்புகூருகிறவர்களுக்குச் சகலமும் நன்மைக்கு ஏதுவாக நடக்கிறது.", "en": "All things work together for good to them that love God."},
    50: {"ref": "Philippians 4:19", "ta": "என் தேவன் தம்முடைய ஐசுவரியத்தின்படி உங்கள் குறைவையெல்லாம் கிறிஸ்து இயேசுவுக்குள் மகிமையிலே நிறைவாக்குவார்.", "en": "My God shall supply all your need according to his riches in glory by Christ Jesus."},
    66: {"ref": "Revelation 22:21", "ta": "நம்முடைய கர்த்தராகிய இயேசு கிறிஸ்துவின் கிருபை உங்கள் அனைவரோடுங்கூட இருப்பதாக. ஆமென்.", "en": "The grace of our Lord Jesus Christ be with you all. Amen."}
}

DEFAULT_BLESSING = {
    "ref": "Numbers 6:24-26",
    "ta": "கர்த்தர் உன்னை ஆசீர்வதித்து, உன்னைக் காக்கக்கடவர்; கர்த்தர் தம்முடைய முகத்தை உன்மேல் பிரகாசிக்கப்பண்ணி, உன்மேல் கிருபையாயிருக்கக்கடவர்.",
    "en": "The Lord bless you and keep you; the Lord make his face shine on you and be gracious to you."
}

def get_chapter_word_counts(start_book=1, end_book=66):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Selecting only existing columns: b.id, b.code, b.name_ta
    cur.execute("""
        SELECT b.id, b.code, b.name_ta, v.chapter, COUNT(v.verse) as verse_count,
               SUM(LENGTH(v.text_en) - LENGTH(REPLACE(v.text_en, ' ', '')) + 1) as word_count
        FROM verses v
        JOIN books b ON v.book_id = b.id
        WHERE b.id >= ? AND b.id <= ?
        GROUP BY b.id, v.chapter
        ORDER BY b.id, v.chapter
    """, (start_book, end_book))
    rows = cur.fetchall()
    conn.close()

    chapters = []
    for r in rows:
        book_id = r[0]
        chapters.append({
            "book_id": book_id,
            "book_code": r[1],
            "book_name_en": BOOK_NAMES_EN.get(book_id, r[1]),
            "book_name_ta": r[2],
            "chapter": r[3],
            "verse_count": r[4],
            "word_count": int(r[5]) if r[5] else 500
        })
    return chapters

def split_into_100_days(chapters, plan_id, plan_name_en, plan_name_ta):
    total_words = sum(c["word_count"] for c in chapters)
    days = []
    curr_idx = 0
    num_chapters = len(chapters)

    for day_num in range(1, 101):
        if curr_idx >= num_chapters:
            break
            
        remaining_days = 101 - day_num
        remaining_words = sum(c["word_count"] for c in chapters[curr_idx:])
        dynamic_target = remaining_words / float(remaining_days)

        day_chapters = []
        day_words = 0

        while curr_idx < num_chapters:
            ch = chapters[curr_idx]
            
            if not day_chapters:
                day_chapters.append(ch)
                day_words += ch["word_count"]
                curr_idx += 1
                continue

            if (day_words + ch["word_count"] * 0.5) > dynamic_target and remaining_days > 1:
                break
                
            day_chapters.append(ch)
            day_words += ch["word_count"]
            curr_idx += 1

        first_ch = day_chapters[0]
        last_ch = day_chapters[-1]

        blessing = BOOK_BLESSINGS.get(last_ch["book_id"], DEFAULT_BLESSING)

        days.append({
            "day": day_num,
            "title": f"Day {day_num}",
            "word_count": day_words,
            "intro": {
                "duration_sec": 5,
                "display_en": f"{first_ch['book_name_en']} {first_ch['chapter']} - {last_ch['book_name_en']} {last_ch['chapter']}",
                "display_ta": f"{first_ch['book_name_ta']} {first_ch['chapter']} முதல் {last_ch['book_name_ta']} {last_ch['chapter']} வரை"
            },
            "chapters": [
                {"book_id": c["book_id"], "chapter": c["chapter"]} for c in day_chapters
            ],
            "outro": {
                "duration_sec": 5,
                "ref": blessing["ref"],
                "ta": blessing["ta"],
                "en": blessing["en"]
            }
        })

    while curr_idx < num_chapters:
        ch = chapters[curr_idx]
        days[-1]["chapters"].append({"book_id": ch["book_id"], "chapter": ch["chapter"]})
        days[-1]["word_count"] += ch["word_count"]
        curr_idx += 1

    return {
        "id": plan_id,
        "name_en": plan_name_en,
        "name_ta": plan_name_ta,
        "total_days": len(days),
        "total_words": total_words,
        "days": days
    }

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at '{DB_PATH}'")
        return

    print("Generating Whole Bible 100-Day Plan...")
    wb_chapters = get_chapter_word_counts(1, 66)
    wb_plan = split_into_100_days(wb_chapters, "plan_100_whole_bible", "100-Day Whole Bible Read-Along", "100 நாட்கள் முழு வேதாகம வாசிப்பு")
    wb_file = os.path.join(OUT_DIR, "plan_100_whole_bible.json")
    with open(wb_file, "w", encoding="utf-8") as f:
        json.dump(wb_plan, f, ensure_ascii=False, indent=2)
    print(f"Generated: {wb_file}")

    print("Generating New Testament 100-Day Plan...")
    nt_chapters = get_chapter_word_counts(40, 66)
    nt_plan = split_into_100_days(nt_chapters, "plan_100_new_testament", "100-Day New Testament Read-Along", "100 நாட்கள் புதிய ஏற்பாடு வாசிப்பு")
    nt_file = os.path.join(OUT_DIR, "plan_100_new_testament.json")
    with open(nt_file, "w", encoding="utf-8") as f:
        json.dump(nt_plan, f, ensure_ascii=False, indent=2)
    print(f"Generated: {nt_file}")

if __name__ == "__main__":
    main()
