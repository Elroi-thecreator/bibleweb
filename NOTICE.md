# Third-Party Content & Scripture Corpus Notices (`NOTICE.md`)

This document establishes the provenance, copyright status, redistribution rights, and required attribution notices for every scripture corpus bundled in **Holy Bible (வேதம்)** (`ElroiTheCreator.HolyBible`), in compliance with [Windows Package Manager Policy 2.2 (Third-Party Content)](https://learn.microsoft.com/windows/package-manager/package/windows-package-manager-policies#22-content-including-names-logos-original-and-third-party).

---

## 1. Bundled Scripture Corpora (`data/bible.sqlite.db`)

All copyrighted 2012 Tamil Ecumenical / POC (*Tiruviviliyam*) text has been completely removed from `data/bible.sqlite.db`. The database bundles only the following four verifiably open-licensed and Public Domain scripture corpora:

### A. Tamil Indian Revised Version (IRV) — தமிழ் (`verses.text_ta_poc`, Books 1–66)
- **Title:** இண்டியன் ரிவைஸ்டு வெர்ஸன் (IRV) - தமிழ் (*The Indian Revised Version Holy Bible in the Tamil language of India*)
- **Copyright Holder:** Copyright © 2017, 2019 [Bridge Connectivity Solutions Pvt. Ltd.](https://bridgeconn.com/)
- **Upstream Archive:** [https://ebible.org/Scriptures/tam2017_vpl.zip](https://ebible.org/Scriptures/tam2017_vpl.zip) / [https://ebible.org/tam2017/](https://ebible.org/tam2017/)
- **License:** [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
- **Verifiable Redistribution Terms (from `tam2017_about.htm` in upstream archive):**
  > *"copyright © 2017, 2019 Bridge Connectivity Solutions. Translation by: Bridge Connectivity Solutions Pvt. Ltd. This translation is made available to you under the terms of the Creative Commons Attribution Share-Alike license 4.0. You have permission to share and redistribute this Bible translation in any format and to make reasonable revisions and adaptations of this translation, provided that: You include the above copyright and source information; If you make any changes to the text, you must indicate that you did so in a way that makes it clear that the original licensor is not necessarily endorsing your changes; If you redistribute this text, you must distribute your contributions under the same license as the original."*
- **Required Attribution Statement:**
  - *Tamil Indian Revised Version (IRV) — இண்டியன் ரிவைஸ்டு வெர்ஸன் (IRV) - தமிழ், Copyright © 2017, 2019 Bridge Connectivity Solutions Pvt. Ltd. (https://bridgeconn.com/). Sourced from eBible.org (https://ebible.org/tam2017/). Distributed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).*

---

### B. Tamil Old Version — 1871 Bower Translation (`verses.text_ta`, Books 1–66)
- **Title:** பரிசுத்த வேதாகமம் (*Tamil Old Version, 1871*)
- **Translator & Original Publisher:** Translated by Rev. Henry Bower (d. 1885) and committee for the Madras Auxiliary Bible Society, published in 1871.
- **License / Legal Status:** **Public Domain Worldwide** (published in 1871, over 150 years ago; translator died in 1885, over 140 years ago; copyright expired under Section 52 of the Indian Copyright Act, 1957 and US Copyright Law 17 U.S.C.).

---

### C. King James Version — 1769 Blayney Standard Text (`verses.text_en`, Books 1–66)
- **Title:** *The Holy Bible, Conteyning the Old Testament, and the New: Newly Translated out of the Originall Tongues (Authorized King James Version, 1611 / 1769 Oxford Standard Text)*
- **Upstream Archive:** [https://ebible.org/Scriptures/eng-kjv2006_vpl.zip](https://ebible.org/Scriptures/eng-kjv2006_vpl.zip)
- **License / Legal Status:** **Public Domain Worldwide** (published 1769; digital redistribution dedicated to the Public Domain).

---

### D. Douay-Rheims Bible — 1752 Challoner Revision (`verses.text_en_drb`, Books 1–73)
- **Title:** *The Holy Bible, Translated from the Latin Vulgate (Douay-Rheims, 1582–1609; revised by Bishop Richard Challoner, 1749–1752)*
- **Coverage:** All 73 books of the Catholic Canon, including the 7 Deuterocanonical books (*Tobit, Judith, Wisdom of Solomon, Sirach / Ecclesiasticus, Baruch, 1 Maccabees, and 2 Maccabees*).
- **Upstream Archive:** [https://ebible.org/Scriptures/engDRA_vpl.zip](https://ebible.org/Scriptures/engDRA_vpl.zip) / [https://ebible.org/engDRA/](https://ebible.org/engDRA/)
- **License / Legal Status:** **Public Domain Worldwide** (published 1752; Bishop Richard Challoner died 1781; upstream `engDRA_about.htm` states: *"This work is in the Public Domain. You may copy and use it freely."*).

---

## 2. Reproduction & Verification Script

The script [`scripts/ingest_open_licensed_corpora.py`](scripts/ingest_open_licensed_corpora.py) downloads `tam2017_vpl.zip` (CC BY-SA 4.0) and `engDRA_vpl.zip` (Public Domain) directly from `eBible.org`, populates `data/bible.sqlite.db`, purges any non-open verses, and runs `VACUUM`.
