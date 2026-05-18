import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const useStore = create((set, get) => ({
    library: [],
    isLoading: false,
    scanPath: 'C:/Users/StudioPC/Music',
    stats: {
        totalTracks: 0,
        genres: 0,
        untagged: 0
    },
    _hasHydrated: false,

    setScanPath: (path) => {
        set({ scanPath: path });
        localStorage.setItem('musiclib_scanPath', path);
    },

    _persistLibrary: (library) => {
        try {
            localStorage.setItem('musiclib_library', JSON.stringify(library));
            localStorage.setItem('musiclib_lastUpdate', new Date().toISOString());
        } catch (e) {
            console.error('Failed to persist library:', e);
        }
    },

    restoreLibrary: () => {
        try {
            const savedLibrary = localStorage.getItem('musiclib_library');
            const savedPath = localStorage.getItem('musiclib_scanPath');

            if (savedLibrary) {
                const library = JSON.parse(savedLibrary);
                set({
                    library,
                    scanPath: savedPath || get().scanPath,
                    stats: {
                        totalTracks: library.length,
                        genres: new Set(library.map(f => f.metadata.genre)).size,
                        untagged: library.filter(f => !f.metadata.title || !f.metadata.artist).length
                    },
                    _hasHydrated: true
                });

                console.log(`Restored ${library.length} tracks from localStorage`);
                return true;
            }
            set({ _hasHydrated: true });
            return false;
        } catch (e) {
            console.error('Failed to restore library:', e);
            set({ _hasHydrated: true });
            return false;
        }
    },

    scanLibrary: async () => {
        set({ isLoading: true });
        try {
            const res = await axios.post(`${API_URL}/scan`, { path: get().scanPath });
            const library = res.data.files;

            const stats = {
                totalTracks: library.length,
                genres: new Set(library.map(f => f.metadata.genre)).size,
                untagged: library.filter(f => !f.metadata.title || !f.metadata.artist).length
            };

            set({ library, stats });
            get()._persistLibrary(library);
        } catch (error) {
            console.error("Scan failed", error);
            alert("Scan failed: " + (error.response?.data?.detail || error.message));
        } finally {
            set({ isLoading: false });
        }
    },

    improveTags: async (filePath) => {
        try {
            const res = await axios.post(`${API_URL}/improve-tags`, { file_path: filePath });
            if (res.data.success) {
                const newLibrary = get().library.map(f =>
                    f.path === filePath
                        ? { ...f, metadata: { ...f.metadata, ...res.data.metadata } }
                        : f
                );
                set({ library: newLibrary });
                get()._persistLibrary(newLibrary);
                return true;
            } else {
                console.warn(`Could not improve tags for ${filePath}: ${res.data.error}`);
                return false;
            }
        } catch (error) {
            console.error("Improve tags failed", error);
            return false;
        }
    },

    improveAllUntagged: async () => {
        const state = get();
        const untagged = state.library.filter(f => !f.metadata.title || !f.metadata.artist || f.metadata.title === 'Unknown Title');

        if (untagged.length === 0) {
            alert("No untagged files found!");
            return;
        }

        if (!confirm(`Found ${untagged.length} untagged files. This might take a while. Start auto-tagging?`)) return;

        set({ isLoading: true });
        let successCount = 0;

        for (const file of untagged) {
            const success = await get().improveTags(file.path);
            if (success) successCount++;
        }

        set({ isLoading: false });
        get()._persistLibrary(get().library);
        alert(`Batch tagging complete! Improved ${successCount} of ${untagged.length} files.`);
    },

    organizeLibrary: async (dryRun = true, outputPath = null) => {
        set({ isLoading: true });
        try {
            const res = await axios.post(`${API_URL}/organize`, {
                dry_run: dryRun,
                output_path: outputPath
            });
            if (!dryRun) {
                // Re-scan to get updated paths
                await get().scanLibrary();
            }
            return res.data.results;
        } catch (error) {
            console.error("Organize failed", error);
            alert("Organize failed");
        } finally {
            set({ isLoading: false });
        }
    }
}));
