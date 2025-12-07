/**
 * YourParty Mood Tagging Module
 */
const MoodModule = (function () {
  'use strict';

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
  };

  const GENRES = {
    'house': 'House',
    'techno': 'Techno',
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
                <button class="close-btn" onclick="MoodModule.closeDialog()">×</button>
                <h3>Tag this Track!</h3>
                <p class="track-info" id="dialog-track-info">Select Vibe & Genre</p>
                
                <div class="tag-section">
                    <h4>Vibe</h4>
                    <div class="mood-grid">
                        ${Object.entries(MOODS).map(([key, data]) => `
                            <button class="mood-btn" data-type="mood" data-value="${key}" style="--btn-color: ${data.color}">
                                <span class="emoji">${data.emoji}</span>
                                <span class="label">${data.label}</span>
                            </button>
                        `).join('')}
                    </div>
                </div>

                <div class="tag-section">
                    <h4>Genre</h4>
                     <div class="genre-grid">
                        ${Object.entries(GENRES).map(([key, label]) => `
                            <button class="mood-btn genre-btn" data-type="genre" data-value="${key}">
                                <span class="label">${label}</span>
                            </button>
                        `).join('')}
                    </div>
                </div>

                <div class="dialog-footer">
                   <p class="status-msg" id="tag-status"></p>
                </div>
            </div>
            <div class="mood-dialog-backdrop" onclick="MoodModule.closeDialog()"></div>
        `;

    document.body.appendChild(dialog);

    // Bind clicks inside dialog
    dialog.querySelectorAll('.mood-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const type = btn.dataset.type;
        const val = btn.dataset.value;
        submitTag(type, val, btn);
      });
    });
  }

  function openDialog() {
    const dialog = document.getElementById('mood-dialog');
    if (dialog) {
      dialog.classList.add('active');
      dialog.style.display = 'flex';
    }
  }

  function closeDialog() {
    const dialog = document.getElementById('mood-dialog');
    if (dialog) {
      dialog.classList.remove('active');
      setTimeout(() => dialog.style.display = 'none', 200);
    }
  }

  async function submitTag(type, value, btnElement) {
    if (!currentSongId) return;

    // Feedback
    btnElement.classList.add('loading');

    const config = window.YourPartyConfig || {};
    const endpoint = (config.restBase) ? `${config.restBase}/mood-tag` : 'https://api.yourparty.tech/mood-tag';

    // Construct payload for Python API
    const payload = {
      song_id: currentSongId,
      title: document.getElementById('track-title')?.innerText || '',
      artist: document.getElementById('track-artist')?.innerText || ''
    };

    if (type === 'mood') payload.mood = value;
    if (type === 'genre') payload.genre = value;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        showStatus('Tag saved!', 'success');
        btnElement.classList.add('active');

        // Refresh status/moods after short delay
        setTimeout(() => {
          if (window.YourPartyApp) window.YourPartyApp.fetchStatus();
        }, 1000);
      } else {
        showStatus(data.message || 'Error saving tag', 'error');
      }

    } catch (err) {
      console.error(err);
      showStatus('Network error', 'error');
    } finally {
      btnElement.classList.remove('loading');
    }
  }

  function showStatus(msg, type) {
    const el = document.getElementById('tag-status');
    if (el) {
      el.textContent = msg;
      el.className = `status-msg ${type}`;
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
