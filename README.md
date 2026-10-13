# Holy Bible — வேதம் (`ElroiTheCreator.HolyBible`)

A fast, offline-first bilingual **Tamil & English Holy Bible** web and Windows desktop application featuring parallel scripture study, 100-day audio read-along plans, church projector/presenter slides, interactive scripture trivia, and Tamil Christian hymnals.

- **Web App:** [https://elroi-bible.vercel.app](https://elroi-bible.vercel.app)
- **Windows Portable Release:** [GitHub Releases](https://github.com/Elroi-thecreator/bibleweb/releases)
- **Privacy Policy:** [PRIVACY.md](PRIVACY.md) (`https://github.com/Elroi-thecreator/bibleweb/blob/main/PRIVACY.md`)
- **Scripture Licenses & Attribution Notices:** [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE)

---

## Bundled Scripture Corpora & Licenses

All scripture corpora bundled in `data/bible.sqlite.db` are either in the **Public Domain** or openly licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**:

| Corpus | Column / Scope | Copyright & Provenance | License |
| :--- | :--- | :--- | :--- |
| **Tamil Old Version (1871 Bower)** | `verses.text_ta` (Books 1–66) | Translated by Rev. Henry Bower (d. 1885), Madras Auxiliary Bible Society (1871) | **Public Domain** |
| **Tamil Indian Revised Version (IRV 2019)** | `verses.text_ta_poc` (Books 1–66) | Copyright © 2017, 2019 [Bridge Connectivity Solutions Pvt. Ltd.](https://bridgeconn.com/) ([eBible.org `tam2017`](https://ebible.org/tam2017/)) | **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)** |
| **King James Version (KJV 1769)** | `verses.text_en` (Books 1–66) | 1769 Oxford Blayney Standard Text ([eBible.org `eng-kjv2006`](https://ebible.org/Scriptures/)) | **Public Domain** |
| **Douay-Rheims Bible (1752 Challoner)** | `verses.text_en_drb` (Books 1–73, incl. 7 Deuterocanonical books) | Revised by Bishop Richard Challoner (1749–1752, d. 1781) ([eBible.org `engDRA`](https://ebible.org/engDRA/)) | **Public Domain** |

See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE) for complete attribution notices and license terms.

---

## Privacy & Data Controls

- **Offline-First by Default:** Reading history, bookmarks, verse highlights, custom reading plans, and theme/font preferences are stored locally on your device (`localStorage`).
- **Optional Cloud Sync:** Users may optionally sign in with an email magic link via **Supabase** to synchronize progress across devices, and can permanently delete their cloud data at any time via **Settings (⚙️) → Cloud Sync → Delete Cloud Data**.
- **Text-to-Speech (TTS):** Audio playback transmits only the selected scripture verse text to **Microsoft Edge Neural TTS** (`edge-tts`) with **Google `gTTS`** as fallback.
- Read the full [Privacy Policy (`PRIVACY.md`)](PRIVACY.md).
