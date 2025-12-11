/**
 * YourParty Mood Tagging Module
 */
const MoodModule = (function () {
  'use strict';

<<<<<<< HEAD
  // Mood Definitions
  // Mood Definitions (Pro Electronic)
  const MOODS = {
    'hypnotic': { label: 'Hypnotic', emoji: '🌀', color: '#8b5cf6' }, // violet
    'driving': { label: 'Driving', emoji: '🏎️', color: '#ef4444' }, // red
    'euphoric': { label: 'Euphoric', emoji: '🤩', color: '#fbbf24' }, // amber
    'groovy': { label: 'Groovy', emoji: '🕺', color: '#f59e0b' }, // orange
    'chill': { label: 'Chill', emoji: '🌴', color: '#10b981' }, // emerald
    'dark': { label: 'Dark', emoji: '🌑', color: '#6b7280' }, // gray
    'atmospheric': { label: 'Atmospheric', emoji: '🌫️', color: '#3b82f6' }, // blue
    'raw': { label: 'Raw', emoji: '🏗️', color: '#78716c' } // stone
=======
  //  Mood Definitions - Extended
  const MOODS = {
    'energetic': { label: 'Energetic', emoji: '⚡', color: '#f59e0b' },
    'chill': { label: 'Chill', emoji: '🌴', color: '#10b981' },
    'euphoric': { label: 'Euphoric', emoji: '🤩', color: '#fbbf24' },
    'dark': { label: 'Dark', emoji: '🌑', color: '#6b7280' },
    'groovy': { label: 'Groovy', emoji: '💃', color: '#ec4899' },
    'melodic': { label: 'Melodic', emoji: '🎹', color: '#8b5cf6' },
    'melancholic': { label: 'Melancholic', emoji: '😢', color: '#6366f1' },
    'aggressive': { label: 'Aggressive', emoji: '😤', color: '#ef4444' },
    'hypnotic': { label: 'Hypnotic', emoji: '🌀', color: '#a78bfa' },
    'trippy': { label: 'Trippy', emoji: '🍄', color: '#c084fc' },
    'warm': { label: 'Warm', emoji: '☀️', color: '#fb923c' },
    'uplifting': { label: 'Uplifting', emoji: '🚀', color: '#3b82f6' }
>>>>>>> c56c5e38c7bdec486b44fa7d38fe126d7a47a7e2
  };

  const GENRES = {
    'deep_house': 'Deep House',
    'melodic_techno': 'Melodic Techno',
    'tech_house': 'Tech House',
    'progressive': 'Progressive',
    'organic_house': 'Organic House',
    'techno': 'Techno',
<<<<<<< HEAD
    'minimal': 'Minimal',
    'afro_house': 'Afro House'
=======
    'tech-house': 'Tech House',
    'deep-house': 'Deep House',
    'progressive-house': 'Progressive House',
    'afro-house': 'Afro House',
    'bass-house': 'Bass House',
    'dnb': 'Drum & Bass',
    'trance': 'Trance',
    'psytrance': 'Psytrance',
    'disco': 'Disco',
    'funk': 'Funk',
    'hiphop': 'HipHop',
    'trap': 'Trap',
    'dubstep': 'Dubstep',
    'garage': 'UK Garage',
    'breakbeat': 'Breakbeat',
    'ambient': 'Ambient',
    'downtempo': 'Downtempo',
    'indie': 'Indie',
    'pop': 'Pop',
    'rock': 'Rock',
    'schlager': 'Schlager'
>>>>>>> c56c5e38c7bdec486b44fa7d38fe126d7a47a7e2
  };

  let currentSongId = null;
  let currentMoods = {};

  function init() {
    console.log('[MoodModule] Init');
    // Initial bind for global buttons if any
    bindGlobalEvents();
    createDialog();
  }

  function bindGlobalEvents() {
    // Tag button in player (if it exists)
    const tagBtn = document.getElementById('mood-tag-button');
    if (tagBtn) {
      tagBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openDialog();
      });
    }
  }

  function createDialog() {
    if (document.getElementById('mood-dialog')) return;

    const dialog = document.createElement('div');
    dialog.id = 'mood-dialog';
    dialog.className = 'mood-dialog glass-panel';
    dialog.style.display = 'none'; // Hidden by default

    // HTML Structure
    dialog.innerHTML = `
            <div class="mood-dialog-content">
      <div class="mood-dialog-backdrop" id="mood-backdrop"></div>
      <div class="mood-dialog-content">
        <button class="close-btn" id="mood-close">&times;</button>
        <h3>Tag Verification</h3>
        <p class="track-info" id="mood-track-info">Loading...</p>
        
        <div class="tag-section">
          <h4>Vibe / Energy</h4>
          <div class="mood-grid">${moodGrid}</div>
        </div>

        <div class="tag-section">
          <h4>Genre</h4>
          <div class="genre-grid">${genreGrid}</div>
        </div>

        <div class="status-msg" id="mood-status"></div>
      </div>
    `;

    document.body.appendChild(dialog);

    // Bind Dialog Events
    document.getElementById('mood-close').addEventListener('click', closeDialog);
    document.getElementById('mood-backdrop').addEventListener('click', closeDialog);

    // Delegation for buttons
    dialog.querySelectorAll('.mood-btn').forEach(btn => {
      btn.addEventListener('click', handleSelection);
    });
  }

  function openDialog() {
    const dialog = document.getElementById('mood-dialog');
    const trackInfo = document.getElementById('mood-track-info');

    // Get current track info from App state or DOM
    const title = document.getElementById('track-title').textContent;
    const artist = document.getElementById('track-artist').textContent;

    // Safety check: Don't allow tagging "Waiting for signal..."
    if (title.includes("WAITING") || title.includes("OFFLINE")) {
      alert("Bitte warten bis ein Track läuft.");
      return;
    }

    trackInfo.textContent = `${artist} - ${title}`;

    // Fetch currently active tags for this song if possible
    // (Optimization: Passed in from API in future)

    dialog.classList.add('active'); // Use class for animation
    dialog.style.display = 'flex';
  }

  function closeDialog() {
    const dialog = document.getElementById('mood-dialog');
    dialog.classList.remove('active');
    setTimeout(() => {
      dialog.style.display = 'none';
      document.getElementById('mood-status').textContent = '';
    }, 200);
  }

  function handleSelection(e) {
    const btn = e.currentTarget;
    const mood = btn.dataset.mood;
    const genre = btn.dataset.genre;

    if (mood) submitMood(mood, 'mood', btn);
    if (genre) submitMood(genre, 'genre', btn);
  }

  async function submitMood(val, type, btnElement) {
    if (!YourPartyApp.currentSongId || YourPartyApp.currentSongId === '0') {
      showStatus('Kein valider Song-ID!', 'error');
      return;
    }

    // Visual feedback
    btnElement.style.transform = 'scale(0.95)';
    setTimeout(() => btnElement.style.transform = 'scale(1)', 100);

    try {
      // NOTE: Using window.YourPartyApp.currentSongId implies global access, 
      // better to use the checking logic
      const songId = currentSongId || (window.YourPartyApp ? window.YourPartyApp.currentSongId : '0');

      // Use dynamic config or fallback to relative path (proxy)
      const baseUrl = (window.YourPartyConfig && window.YourPartyConfig.restBase)
        ? window.YourPartyConfig.restBase
        : '/api'; // Fallback to relative proxy

      const response = await fetch(`${baseUrl}/mood-tag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          song_id: songId,
          tag: val,
          type: type
        })
      });

      if (response.ok) {
        showStatus(`${type === 'mood' ? 'Mood' : 'Genre'} gespeichert!`, 'success');
      } else {
        throw new Error('API Error');
      }
    } catch (err) {
      console.error(err);
      showStatus('Fehler beim Speichern.', 'error');
    }
  }

  function showStatus(msg, type) {
    const el = document.getElementById('mood-status');
    if (el) {
      el.textContent = msg;
      el.className = 'status-msg ' + type;
      setTimeout(() => el.textContent = '', 3000);
    }
  }

  function updateDisplay(topMood, moods) {
    const displays = document.querySelectorAll('.mood-display-area, .current-mood-tags, #current-mood-tags');

    displays.forEach(display => {
      if (!display) return;

      if (topMood && MOODS[topMood]) {
        const mood = MOODS[topMood];
        const count = moods[topMood] || 0;
        display.innerHTML = `
            <span class="mood-badge" style="--mood-color: ${mood.color}" role="button" onclick="MoodModule.openDialog()">
              ${mood.emoji} ${mood.label}${count > 1 ? ` (${count})` : ''}
            </span>
          `;
      } else {
        display.innerHTML = `
            <span class="mood-badge mood-empty" role="button" onclick="MoodModule.openDialog()">+ Tag hinzufügen</span>
          `;
      }
    });
  }

  /**
   * Set mood data for current song
   */
  function setMoodData(songId, topMood, moods = {}) {
    currentSongId = songId;
    currentMoods = moods;
    updateDisplay(topMood, moods);
  }

  // Public API
  const instance = {
    init,
    setMoodData,
    getMoods: () => MOODS,
    openDialog,
    closeDialog
  };

  window.MoodModule = instance;
  return instance;
})();

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MoodModule;
}
