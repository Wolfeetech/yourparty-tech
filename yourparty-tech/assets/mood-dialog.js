// MOOD & GENRE TAGGING SYSTEM
(function () {
  const MOODS = [
    { id: 'energetic', label: 'Energetic', emoji: '🔥' },
    { id: 'chill', label: 'Chill', emoji: '😌' },
    { id: 'dark', label: 'Dark', emoji: '🌑' },
    { id: 'euphoric', label: 'Euphoric', emoji: '✨' },
    { id: 'melancholic', label: 'Melancholic', emoji: '💙' },
    { id: 'groovy', label: 'Groovy', emoji: '🎵' },
    { id: 'hypnotic', label: 'Hypnotic', emoji: '🌀' },
    { id: 'aggressive', label: 'Aggressive', emoji: '😤' },
    { id: 'trippy', label: 'Trippy', emoji: '🍄' },
    { id: 'warm', label: 'Warm', emoji: '☀️' }
  ];

  const GENRES = [
    { id: 'house', label: 'House', emoji: '🏠' },
    { id: 'techno', label: 'Techno', emoji: '🎹' },
    { id: 'trance', label: 'Trance', emoji: '🌌' },
    { id: 'dnb', label: 'DnB', emoji: '🥁' },
    { id: 'dubstep', label: 'Dubstep', emoji: '🔊' },
    { id: 'ambient', label: 'Ambient', emoji: '☁️' },
    { id: 'downtempo', label: 'Downtempo', emoji: '🐢' },
    { id: 'hardstyle', label: 'Hardstyle', emoji: '🔨' },
    { id: 'psytrance', label: 'Psytrance', emoji: '🕉️' },
    { id: 'garage', label: 'Garage', emoji: '🚗' },
    { id: 'disco', label: 'Disco', emoji: '🕺' },
    { id: 'synthwave', label: 'Synthwave', emoji: '🌆' },
    { id: 'lofi', label: 'Lo-Fi', emoji: '☕' },
    { id: 'idm', label: 'IDM', emoji: '🧠' },
    { id: 'electro', label: 'Electro', emoji: '⚡' },
    { id: 'breakbeat', label: 'Breakbeat', emoji: '💔' },
    { id: 'jungle', label: 'Jungle', emoji: '🌴' },
    { id: 'minimal', label: 'Minimal', emoji: '🔹' },
    { id: 'deep-house', label: 'Deep House', emoji: '🌊' },
    { id: 'tech-house', label: 'Tech House', emoji: '🔧' }
  ];

  let currentTrack = null;
  let selectedMood = null;
  let selectedGenre = null;

  // Create dialog HTML
  const createMoodDialog = () => {
    const overlay = document.createElement('div');
    overlay.className = 'mood-overlay';
    overlay.id = 'mood-overlay';

    const moodOptions = MOODS.map(mood => `
      <button class="mood-btn" data-type="mood" data-value="${mood.id}">
        <span class="mood-btn__emoji">${mood.emoji}</span>
        <span>${mood.label}</span>
      </button>
    `).join('');

    const genreOptions = GENRES.map(genre => `
      <button class="mood-btn" data-type="genre" data-value="${genre.id}">
        <span class="mood-btn__emoji">${genre.emoji}</span>
        <span>${genre.label}</span>
      </button>
    `).join('');

    overlay.innerHTML = `
      <div class="mood-dialog">
        <div class="mood-dialog__header">
          <h3 class="mood-dialog__title">Track taggen</h3>
          <p class="mood-dialog__subtitle">Hilf uns, bessere Playlists zu erstellen</p>
        </div>
        
        <div class="mood-dialog__track" id="mood-track-info">
          <div class="mood-dialog__track-title">—</div>
          <div class="mood-dialog__track-artist">—</div>
        </div>

        <div class="mood-dialog__scroll-area">
            <div class="mood-section">
                <h4>Stimmung</h4>
                <div class="mood-options" id="mood-options">
                ${moodOptions}
                </div>
            </div>

            <div class="mood-section">
                <h4>Genre</h4>
                <div class="mood-options" id="genre-options">
                ${genreOptions}
                </div>
            </div>
        </div>

        <div class="mood-dialog__actions">
          <button class="mood-dialog__btn-cancel" id="mood-cancel">Abbrechen</button>
          <button class="mood-dialog__btn-submit" id="mood-submit" disabled>Tag senden</button>
        </div>

        <div class="mood-dialog__feedback" id="mood-feedback"></div>
      </div>
    `;

    document.body.appendChild(overlay);
    return overlay;
  };

  // Initialize dialog
  const moodOverlay = createMoodDialog();
  const moodSubmit = document.getElementById('mood-submit');
  const moodCancel = document.getElementById('mood-cancel');
  const moodFeedback = document.getElementById('mood-feedback');
  const trackInfo = document.getElementById('mood-track-info');

  // Show dialog
  window.openMoodDialog = (track) => {
    if (!track && window.currentTrackInfo) {
      track = window.currentTrackInfo;
    }

    if (!track || !track.id) {
      console.warn('Mood Tagging: No track info available');
      return;
    }

    currentTrack = track;
    selectedMood = null;
    selectedGenre = null;

    trackInfo.innerHTML = `
      <div class="mood-dialog__track-title">${track.title || 'Unknown Title'}</div>
      <div class="mood-dialog__track-artist">${track.artist || 'Unknown Artist'}</div>
    `;

    moodFeedback.textContent = '';
    moodSubmit.disabled = true;

    document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('selected'));
    moodOverlay.classList.add('active');
  };

  // Close dialog
  const closeMoodDialog = () => {
    moodOverlay.classList.remove('active');
  };

  // Selection Handler (Delegation)
  moodOverlay.addEventListener('click', (e) => {
    const btn = e.target.closest('.mood-btn');
    if (!btn) return;

    const type = btn.dataset.type;
    const value = btn.dataset.value;

    // Deselect others of same type
    document.querySelectorAll(`.mood-btn[data-type="${type}"]`).forEach(b => b.classList.remove('selected'));

    // Select clicked
    btn.classList.add('selected');

    if (type === 'mood') selectedMood = value;
    if (type === 'genre') selectedGenre = value;

    // Enable submit if at least one is selected
    moodSubmit.disabled = (!selectedMood && !selectedGenre);
  });

  // Submit mood/genre tag
  moodSubmit.addEventListener('click', async () => {
    if ((!selectedMood && !selectedGenre) || !currentTrack || !currentTrack.id) return;

    moodSubmit.disabled = true;
    moodFeedback.textContent = 'Wird gespeichert...';

    try {
      const response = await fetch('/wp-json/yourparty/v1/mood-tag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          song_id: currentTrack.id,
          mood: selectedMood || '',
          genre: selectedGenre || '',
          title: currentTrack.title,
          artist: currentTrack.artist
        })
      });

      if (response.ok) {
        moodFeedback.textContent = 'Gespeichert! Danke.';
        setTimeout(closeMoodDialog, 1500);
      } else {
        moodFeedback.textContent = 'Fehler beim Speichern.';
        moodSubmit.disabled = false;
      }
    } catch (e) {
      console.error(e);
      moodFeedback.textContent = 'Netzwerkfehler.';
      moodSubmit.disabled = false;
    }
  });

  // Cancel
  moodCancel.addEventListener('click', closeMoodDialog);

  // Close on overlay click
  moodOverlay.addEventListener('click', (e) => {
    if (e.target === moodOverlay) closeMoodDialog();
  });

  // ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && moodOverlay.classList.contains('active')) {
      closeMoodDialog();
    }
  });

  // Attach to button (if present)
  document.addEventListener('DOMContentLoaded', () => {
    const triggerBtn = document.getElementById('mood-tag-button');
    if (triggerBtn) {
      triggerBtn.addEventListener('click', () => {
        // Get current track info from DOM if window.currentTrackInfo is missing
        const title = document.getElementById('track-title')?.textContent;
        const artist = document.getElementById('track-artist')?.textContent;
        // songId is usually stored in window.currentSongId by app.js

        const track = {
          id: window.currentSongId,
          title: title,
          artist: artist
        };
        window.openMoodDialog(track);
      });
    }
  });

})();
