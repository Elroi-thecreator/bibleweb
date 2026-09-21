/**
 * storage.js - LocalStorage & State Management for BibleWeb
 * Handles user bookmarks, verse highlights, and reading plan progress.
 */

const StorageManager = {
    // ------------------------------------------------------------------------
    // Bookmarks Management
    // ------------------------------------------------------------------------

    /**
     * Retrieve all saved bookmarks.
     * @returns {Array<Object>} Array of bookmark objects: { book, chapter, verse, text, timestamp }
     */
    getBookmarks() {
        try {
            const raw = localStorage.getItem("bible_bookmarks");
            return raw ? JSON.parse(raw) : [];
        } catch (err) {
            console.error("StorageManager: Failed to parse bookmarks from storage", err);
            return [];
        }
    },

    /**
     * Add a bookmark or remove it if it already exists for this verse.
     * @param {Object} item { book: string, chapter: number|string, verse: number|string, text: string }
     * @returns {boolean} true if added, false if removed
     */
    saveBookmark(item) {
        if (!item || !item.book || item.chapter === undefined || item.verse === undefined) {
            console.warn("StorageManager: Invalid bookmark item supplied", item);
            return false;
        }

        const bookmarks = this.getBookmarks();
        const index = bookmarks.findIndex(
            b => b.book.toLowerCase() === item.book.toLowerCase() &&
                 Number(b.chapter) === Number(item.chapter) &&
                 Number(b.verse) === Number(item.verse)
        );

        if (index > -1) {
            // Verse is already bookmarked; toggle it off
            bookmarks.splice(index, 1);
            localStorage.setItem("bible_bookmarks", JSON.stringify(bookmarks));
            return false;
        } else {
            // Add new bookmark at the beginning of list
            bookmarks.unshift({
                book: item.book,
                chapter: Number(item.chapter),
                verse: Number(item.verse),
                text: (item.text || "").trim(),
                timestamp: Date.now()
            });
            localStorage.setItem("bible_bookmarks", JSON.stringify(bookmarks));
            return true;
        }
    },

    /**
     * Check if a specific verse is bookmarked.
     * @param {string} book
     * @param {number|string} chapter
     * @param {number|string} verse
     * @returns {boolean}
     */
    isBookmarked(book, chapter, verse) {
        if (!book || chapter === undefined || verse === undefined) return false;
        const bookmarks = this.getBookmarks();
        return bookmarks.some(
            b => b.book.toLowerCase() === book.toLowerCase() &&
                 Number(b.chapter) === Number(chapter) &&
                 Number(b.verse) === Number(verse)
        );
    },

    /**
     * Delete a single bookmark by reference.
     * @param {string} book
     * @param {number|string} chapter
     * @param {number|string} verse
     */
    removeBookmark(book, chapter, verse) {
        const bookmarks = this.getBookmarks().filter(
            b => !(b.book.toLowerCase() === book.toLowerCase() &&
                   Number(b.chapter) === Number(chapter) &&
                   Number(b.verse) === Number(verse))
        );
        localStorage.setItem("bible_bookmarks", JSON.stringify(bookmarks));
    },

    /**
     * Remove all saved bookmarks.
     */
    clearBookmarks() {
        localStorage.removeItem("bible_bookmarks");
    },

    // ------------------------------------------------------------------------
    // Verse Highlights Management
    // ------------------------------------------------------------------------

    /**
     * Retrieve all verse highlights.
     * @returns {Object} Map of verseKey => CSS class (e.g. { "Genesis_1_1": "bg-yellow-100" })
     */
    getHighlights() {
        try {
            const raw = localStorage.getItem("bible_highlights");
            return raw ? JSON.parse(raw) : {};
        } catch (err) {
            console.error("StorageManager: Failed to parse highlights from storage", err);
            return {};
        }
    },

    /**
     * Toggle or update a highlight on a verse key.
     * @param {string} key Unique verse key, typically "Book_Chapter_Verse"
     * @param {string} colorClass Tailwind or custom CSS class for background color
     * @returns {string|null} Applied class string if active, or null if removed
     */
    toggleHighlight(key, colorClass = "bg-yellow-100") {
        if (!key) return null;
        const highlights = this.getHighlights();

        if (highlights[key]) {
            delete highlights[key];
        } else {
            highlights[key] = colorClass;
        }

        localStorage.setItem("bible_highlights", JSON.stringify(highlights));
        return highlights[key] || null;
    },

    /**
     * Remove all highlights across all chapters.
     */
    clearHighlights() {
        localStorage.removeItem("bible_highlights");
    },

    // ------------------------------------------------------------------------
    // Reading Plans Progress Management
    // ------------------------------------------------------------------------

    /**
     * Get completion records for a given plan ID.
     * @param {string} planId Identifier (e.g., "100_whole_bible", "100_new_testament")
     * @returns {Object} Map of dayNumber => boolean (e.g., { "1": true, "2": false })
     */
    getPlanProgress(planId) {
        if (!planId) return {};
        try {
            const raw = localStorage.getItem(`bible_plan_${planId}`);
            return raw ? JSON.parse(raw) : {};
        } catch (err) {
            console.error(`StorageManager: Failed to parse progress for ${planId}`, err);
            return {};
        }
    },

    /**
     * Mark a specific day completed or pending.
     * @param {string} planId
     * @param {number|string} day
     * @param {boolean} isCompleted
     * @returns {Object} The updated progress map
     */
    setDayProgress(planId, day, isCompleted) {
        if (!planId || day === undefined) return {};
        const progress = this.getPlanProgress(planId);
        progress[day] = Boolean(isCompleted);
        localStorage.setItem(`bible_plan_${planId}`, JSON.stringify(progress));
        return progress;
    },

    /**
     * Reset progress for a specific plan.
     * @param {string} planId
     */
    clearPlanProgress(planId) {
        if (planId) {
            localStorage.removeItem(`bible_plan_${planId}`);
        }
    }
};

// Expose globally for vanilla browser scripts
window.StorageManager = StorageManager;