// ==========================================
// Robust Universal Backup & Restore Engine
// ==========================================

function exportAllUserData() {
    try {
        const backupPayload = {
            app: "bilingual_bible_app",
            version: "2.0",
            exported_at: new Date().toISOString(),
            data: {
                bookmarks: getBookmarks(),
                highlights: getHighlights(),
                read_chapters: getReadChapters(),
                theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'light',
                font_size: localStorage.getItem(STORAGE_KEYS.FONT_SIZE) || '16',
                plans: {}
            }
        };

        // Safely extract reading plans without crashing on non-JSON entries
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('bible_plan_')) {
                try {
                    backupPayload.data.plans[key] = JSON.parse(localStorage.getItem(key) || '[]');
                } catch (e) {
                    backupPayload.data.plans[key] = [];
                }
            }
        }

        const jsonString = JSON.stringify(backupPayload, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.setAttribute('download', `bible_backup_${new Date().toISOString().split('T')[0]}.json`);
        
        document.body.appendChild(a);
        a.click();

        // Delay cleanup so the browser has time to finish handing off the download
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 1500);

        showToast("Backup downloaded successfully! 💾");
    } catch (err) {
        console.error("Backup failed:", err);
        alert("Failed to export backup: " + err.message);
    }
}

// Backward-compatibility alias in case any template calls the old name
window.exportProgress = exportAllUserData;
window.exportAllUserData = exportAllUserData;