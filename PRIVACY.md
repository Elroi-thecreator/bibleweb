# Privacy Policy — Holy Bible (வேதம்)

**Effective Date:** October 13, 2026  
**Last Updated:** October 13, 2026  
**Application:** Holy Bible - வேதம் (`ElroiTheCreator.HolyBible`)  
**Publisher:** Elroi-thecreator  
**Repository:** [https://github.com/Elroi-thecreator/bibleweb](https://github.com/Elroi-thecreator/bibleweb)  
**Web Application:** [https://elroi-bible.vercel.app](https://elroi-bible.vercel.app)

---

## 1. Overview & Offline-First Design

**Holy Bible (வேதம்)** is designed as a privacy-respecting, **offline-first** bilingual (Tamil & English) desktop and web application.

- **No Mandatory Account:** You can read all bundled scripture canons, search verses, use Presenter mode, take interactive quizzes, follow reading plans, and listen to offline/cached audio without creating an account or providing any personal information.
- **No Telemetry, Ads, or Tracking:** The application contains **zero** advertising SDKs, **zero** behavioral analytics trackers, and **zero** background telemetry.

---

## 2. Information We Process & Purposes

### A. Local Device Data (Default — Stored Only on Your Device)
By default, all personal study data is stored locally in your browser or desktop WebView2 local storage (`localStorage`):
- **Reading History & Progress** (`bible_read_chapters`): Chapters marked as completed and reading streak dates.
- **Saved Verses / Bookmarks** (`bilingual_bible_bookmarks`): Bookmarked verse references and timestamps.
- **Verse Highlights** (`bilingual_bible_highlights`): Color highlight markers applied to verses.
- **Custom Reading Plans** (`bible_custom_reading_plans`): User-created reading schedules and chapter checkoffs.
- **Display & Audio Preferences** (`bible_app_theme`, `bible_font_size`, `bible_canon`, `bible_audio_voice_ta`, `bible_audio_voice_en`): Theme mode (Light/Sepia/Dark), font size, active canon (Protestant/Catholic), and preferred TTS voice.

**Purpose:** To persist your reading state and visual customization locally on your device without requiring network connectivity.

---

### B. Optional Cloud Synchronization & Passwordless Authentication
If you voluntarily choose to sign in via **Settings (⚙️) → Cloud Sync → Sign In with Email**, the application processes:
1. **Email Address**: Used solely to send a passwordless one-time sign-in link (OTP/Magic Link) and identify your cloud sync record.
2. **Synchronized Study Data (`user_bible_sync`)**: Your bookmarks, verse highlights, completed chapter history, custom reading plans, and theme/font-size preferences.
3. **Optional Web Push Notification Subscriptions (`user_push_subscriptions`)**: If you explicitly click **Enable** under *Daily Reminder / Push Notifications* and grant browser notification permission, the application stores your Web Push endpoint URL, cryptographic public keys (`p256dh`, `auth`), selected reminder time, and optional `user_id`.

**Purpose:** To back up and synchronize your Bible study progress across multiple devices at your explicit request, and to deliver optional daily reading reminders.

---

### C. Text-to-Speech (TTS) Audio Synthesis
When you click **Listen (▶)** on a chapter or **Test Voice Sample** in Settings (`/api/audio/stream`), the application transmits:
- **Selected Scripture Text**: Only the plain text of the scripture verse(s) being read aloud, along with the language code (`ta` or `en`), voice identifier (e.g., `ta-IN-ValluvarNeural`, `en-US-JennyNeural`), and playback rate.
- **No Personal Identifiers**: Your email address, account ID, bookmarks, and reading history are **never** included in TTS audio requests.

**Purpose:** To synthesize spoken audio MP3 streams of scripture verses for read-along listening and accessibility.

---

## 3. Third-Party Service Providers (Processors)

Holy Bible (வேதம்) does not sell, rent, or trade user data with any third parties. Data is transmitted only to the following infrastructure processors when you invoke the corresponding feature:

| Feature | Processor | Data Transmitted | Processor Privacy Policy |
| :--- | :--- | :--- | :--- |
| **Optional Email Sign-In, Cloud Sync & Push Reminders** | **Supabase, Inc.** | Email address, authentication session token, synced JSON study state (`bookmarks`, `highlights`, `read_chapters`, `custom_reading_plans`, `theme`, `font_size`), and optional Web Push subscription keys. | [https://supabase.com/privacy](https://supabase.com/privacy) |
| **Primary Neural Text-to-Speech (TTS)** | **Microsoft Corporation** (Microsoft Edge Neural TTS / `edge-tts`) | Selected scripture verse text, language code, neural voice name, and speech rate. | [https://privacy.microsoft.com/privacystatement](https://privacy.microsoft.com/privacystatement) |
| **Fallback Text-to-Speech (TTS)** | **Google LLC** (Google Translate TTS / `gTTS`) | Selected scripture verse text and language code (`ta` or `en`) when primary neural TTS is unreachable. | [https://policies.google.com/privacy](https://policies.google.com/privacy) |
| **Web Font Delivery & Song Embeds** | **Google Fonts / YouTube (Google LLC)** | Standard HTTP requests for typography (`Noto Serif Tamil`, `Cinzel`, `Lora`) and optional user-initiated YouTube song video playback on song detail pages. | [https://policies.google.com/privacy](https://policies.google.com/privacy) |

---

## 4. Data Retention, Deletion & Account Removal

### Local Data Retention & Deletion
- Local study data remains on your device until you clear it or uninstall the application.
- You can export a full copy of your data at any time via **Settings (⚙️) → Export Backup** (downloads a portable `.json` file).
- You can clear local data at any time via **Settings (⚙️) → Reset Local Data** or by clearing site/application data.

### Cloud Data Retention & Self-Service Account/Data Removal
- Cloud-synchronized data in Supabase (`user_bible_sync` and `user_push_subscriptions`) is retained only until you delete it.
- **Instant Self-Service Cloud Deletion**: When signed in, open **Settings (⚙️) → Cloud Sync** and click **Delete Cloud Data (🗑️)**. This immediately deletes your synchronized records from `user_bible_sync` and `user_push_subscriptions` in Supabase and signs out your session.
- **Manual Account Deletion Request**: You may also request complete deletion of your authentication email record (`auth.users`) and any associated cloud rows at any time by opening a request at [https://github.com/Elroi-thecreator/bibleweb/issues](https://github.com/Elroi-thecreator/bibleweb/issues). All requests are fulfilled within 7 days.

---

## 5. Security Measures

- **Encryption in Transit**: All communications with Supabase, Microsoft Edge TTS, and Google gTTS are encrypted over HTTPS/TLS (`wss://` / `https://`).
- **Passwordless Authentication**: No user passwords are ever created, stored, or transmitted; authentication relies exclusively on short-lived cryptographic email OTP/Magic Links.
- **Database Isolation**: Bundled scripture (`data/bible.sqlite.db`) and song lyrics (`data/songs.sqlite.db`) databases are read-only local SQLite files packaged inside the application.

---

## 6. User Controls Summary

| Control | How to Access |
| :--- | :--- |
| **Use 100% Offline / Anonymous** | Simply use the app without signing in to Cloud Sync. |
| **Export Local Data Backup** | **Settings (⚙️) → Export Backup** |
| **Sign Out of Cloud Sync** | **Settings (⚙️) → Cloud Sync → Sign Out** |
| **Delete All Cloud-Synced Data** | **Settings (⚙️) → Cloud Sync → Delete Cloud Data** |
| **Disable Push Notifications** | Revoke notification permissions in your browser/OS settings or click **Delete Cloud Data**. |

---

## 7. Contact

For privacy questions, data deletion requests, or compliance inquiries, please contact the maintainer via:
- **GitHub Issues / Support**: [https://github.com/Elroi-thecreator/bibleweb/issues](https://github.com/Elroi-thecreator/bibleweb/issues)
- **Publisher Profile**: [https://github.com/Elroi-thecreator](https://github.com/Elroi-thecreator)
