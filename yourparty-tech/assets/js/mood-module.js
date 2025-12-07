/**
 * Mood & Genre Tagging (YourParty)
 * - Modern modal (single source of truth)
 * - Separate mood / genre grids with live counts
 * - Works with theme styles (.mood-dialog__*)
 */
const MoodModule = (function () {
  'use strict';

  const MOODS = [
    { id: 'energetic', label: 'Energetic', color: '#f59e0b' },
    { id: 'chill', label: 'Chill', color: '#10b981' },
    { id: 'euphoric', label: 'Euphoric', color: '#fbbf24' },
    { id: 'dark', label: 'Dark', color: '#6b7280' },
    { id: 'groovy', label: 'Groovy', color: '#ec4899' },
    { id: 'melodic', label: 'Melodic', color: '#8b5cf6' },
    { id: 'melancholic', label: 'Melancholic', color: '#6366f1' },
    { id: 'aggressive', label: 'Aggressive', color: '#ef4444' },
    { id: 'hypnotic', label: 'Hypnotic', color: '#a78bfa' },
    { id: 'trippy', label: 'Trippy', color: '#c084fc' },
    { id: 'warm', label: 'Warm', color: '#fb923c' },
    { id: 'uplifting', label: 'Uplifting', color: '#3b82f6' }
  ];

  const GENRES = [
    'house',
    'techno',
    'tech-house',
    'deep-house',
    'progressive-house',
    'afro-house',
    'bass-house',
    'dnb',
    'trance',
    'psytrance',
    'disco',
    'funk',
    'hiphop',
    'trap',
    'dubstep',
    'garage',
    'breakbeat',
    'ambient',
    'downtempo',
    'indie',
    'pop',
    'rock',
    'schlager'
  ];

  let currentSongId = null;
  let currentTrack = { title: '', artist: '' };
  let currentMoods = {};
  let currentGenres = {};
  let selectedMood = '';
  let selectedGenre = '';

  function init() {
    createDialog();
    bindGlobalEvents();
  }

  function bindGlobalEvents() {
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

    const overlay = document.createElement('div');
    overlay.id = 'mood-dialog';
    overlay.className = 'mood-dialog';

    overlay.innerHTML = `
      <div class="mood-dialog__backdrop" data-close="true"></div>
      <div class="mood-dialog__content">
        <div class="mood-dialog__header">
          <div>
            <h3>Track taggen</h3>
            <p class="mood-dialog__subtitle">Waehle Vibe & Genre fuer bessere Playlists</p>
          </div>
          <button class="mood-dialog__close" data-close="true" aria-label="Schliessen">&times;</button>
        </div>

        <div class="mood-dialog__track" id="mood-dialog-track">
          <div class="mood-dialog__track-title">-</div>
          <div class="mood-dialog__track-artist">-</div>
        </div>

        <div class="mood-dialog__grid">
          <section class="mood-dialog__section">
            <div class="mood-dialog__section-head">
              <h4>Stimmung</h4>
              <div class="mood-dialog__pill">Top Votes live</div>
            </div>
            <div class="mood-dialog__options" id="mood-options">
              ${MOODS.map((m) => `
                <button class="mood-option" data-type="mood" data-value="${m.id}" style="--mood-color:${m.color}">
                  <span class="mood-option__label">${m.label}</span>
                  <span class="mood-option__count" data-count="${m.id}">0</span>
                </button>
              `).join('')}
            </div>
          </section>

          <section class="mood-dialog__section">
            <div class="mood-dialog__section-head">
              <h4>Genre</h4>
              <div class="mood-dialog__pill">Mehr Auswahl fÃ¼r Kuratoren</div>
            </div>
            <div class="mood-dialog__options" id="genre-options">
              ${GENRES.map((g) => `
                <button class="mood-option" data-type="genre" data-value="${g}">
                  <span class="mood-option__label">${formatLabel(g)}</span>
                  <span class="mood-option__count" data-count="${g}">0</span>
                </button>
              `).join('')}
            </div>
          </section>
        </div>

        <div class="mood-dialog__footer">
          <div class="mood-dialog__stats" id="mood-dialog-stats"></div>
          <div class="mood-dialog__actions">
            <button class="btn-ghost" data-close="true">Abbrechen</button>
            <button class="btn-primary" id="mood-submit" disabled>Tag senden</button>
          </div>
          <div class="mood-dialog__feedback" id="tag-status"></div>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    overlay.addEventListener('click', (e) => {
      const btn = e.target.closest('.mood-option');
      if (btn) {
        handleSelection(btn);
        return;
      }
      if (e.target.dataset.close === 'true') {
        closeDialog();
      }
    });

    const submitBtn = overlay.querySelector('#mood-submit');
    if (submitBtn) {
      submitBtn.addEventListener('click', submitTag);
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeDialog();
    });
  }

  function handleSelection(btn) {
    const type = btn.dataset.type;
    const val = btn.dataset.value;
    if (!type || !val) return;

    const selector = `.mood-option[data-type="${type}"]`;
    document.querySelectorAll(selector).forEach((b) => b.classList.remove('selected'));
    btn.classList.add('selected');

    if (type === 'mood') selectedMood = val;
    if (type === 'genre') selectedGenre = val;

    const submitBtn = document.getElementById('mood-submit');
    if (submitBtn) {
      submitBtn.disabled = !selectedMood && !selectedGenre;
    }
  }

  function formatLabel(str) {
    return str.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function openDialog() {
    const dialog = document.getElementById('mood-dialog');
    if (!dialog) return;

    const title = document.getElementById('track-title')?.textContent || '-';
    const artist = document.getElementById('track-artist')?.textContent || '-';
    currentTrack = { title, artist };

    const info = dialog.querySelector('#mood-dialog-track');
    if (info) {
      info.querySelector('.mood-dialog__track-title').textContent = title;
      info.querySelector('.mood-dialog__track-artist').textContent = artist;
    }

    preselectCurrent();
    renderCounts();
    renderStats();

    dialog.classList.add('open');
  }

  function closeDialog() {
    const dialog = document.getElementById('mood-dialog');
    if (!dialog) return;
    dialog.classList.remove('open');
  }

  function preselectCurrent() {
    document.querySelectorAll('.mood-option').forEach((btn) => btn.classList.remove('selected'));
    if (selectedMood) {
      const btn = document.querySelector(`.mood-option[data-type="mood"][data-value="${selectedMood}"]`);
      if (btn) btn.classList.add('selected');
    }
    if (selectedGenre) {
      const btn = document.querySelector(`.mood-option[data-type="genre"][data-value="${selectedGenre}"]`);
      if (btn) btn.classList.add('selected');
    }
    const submitBtn = document.getElementById('mood-submit');
    if (submitBtn) submitBtn.disabled = !selectedMood && !selectedGenre;
  }

  async function submitTag() {
    if (!currentSongId) return;

    const submitBtn = document.getElementById('mood-submit');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Speichere...';
    }

    const config = window.YourPartyConfig || {};
    const endpoint = config.restBase ? `${config.restBase}/mood-tag` : 'https://api.yourparty.tech/mood-tag';

    const payload = {
      song_id: currentSongId,
      title: currentTrack.title,
      artist: currentTrack.artist,
      mood: selectedMood || '',
      genre: selectedGenre || ''
    };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (response.ok) {
        showStatus('Gespeichert! Danke.', 'success');
        setTimeout(() => {
          closeDialog();
          if (window.YourPartyApp) window.YourPartyApp.fetchStatus();
        }, 900);
      } else {
        showStatus(data.error || 'Fehler beim Speichern.', 'error');
      }
    } catch (err) {
      console.error(err);
      showStatus('Netzwerkfehler.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Tag senden';
      }
    }
  }

  function showStatus(msg, type) {
    const el = document.getElementById('tag-status');
    if (!el) return;
    el.textContent = msg;
    el.className = `mood-dialog__feedback ${type}`;
    setTimeout(() => (el.textContent = ''), 3000);
  }

  function renderCounts() {
    const moodCounts = currentMoods || {};
    const genreCounts = currentGenres || {};

    document.querySelectorAll('.mood-option[data-type="mood"]').forEach((btn) => {
      const key = btn.dataset.value;
      const count = moodCounts[key] || 0;
      const counter = btn.querySelector('.mood-option__count');
      if (counter) counter.textContent = count;
    });

    document.querySelectorAll('.mood-option[data-type="genre"]').forEach((btn) => {
      const key = btn.dataset.value;
      const count = genreCounts[key] || 0;
      const counter = btn.querySelector('.mood-option__count');
      if (counter) counter.textContent = count;
    });
  }

  function renderStats() {
    const stats = document.getElementById('mood-dialog-stats');
    if (!stats) return;

    const topMood = getTop(currentMoods);
    const topGenre = getTop(currentGenres);
    const moodLine = topMood ? `Top Mood: ${formatLabel(topMood.key)} (${topMood.value})` : 'Noch keine Moods';
    const genreLine = topGenre ? `Top Genre: ${formatLabel(topGenre.key)} (${topGenre.value})` : 'Noch keine Genres';

    stats.innerHTML = `
      <div class="mood-dialog__stat-line">${moodLine}</div>
      <div class="mood-dialog__stat-line">${genreLine}</div>
    `;
  }

  function getTop(obj = {}) {
    const entries = Object.entries(obj || {});
    if (!entries.length) return null;
    entries.sort((a, b) => b[1] - a[1]);
    return { key: entries[0][0], value: entries[0][1] };
  }

  function updateBadgeDisplay(topMood, moods, topGenre, genres) {
    const containers = document.querySelectorAll('#current-mood-tags, .current-mood-tags, #immersive-mood-tags');
    const moodEntries = Object.entries(moods || {}).sort((a, b) => b[1] - a[1]);
    const genreEntries = Object.entries(genres || {}).sort((a, b) => b[1] - a[1]);

    const moodChips = moodEntries.slice(0, 4).map(([key, count]) => {
      const moodDef = MOODS.find((m) => m.id === key);
      const label = moodDef ? moodDef.label : formatLabel(key);
      return `<span class="mood-badge" style="--mood-color:${moodDef ? moodDef.color : '#444'}">${label} (${count})</span>`;
    }).join('');

    const genreChips = genreEntries.slice(0, 4).map(([key, count]) => {
      return `<span class="mood-badge mood-genre">${formatLabel(key)} (${count})</span>`;
    }).join('');

    containers.forEach((el) => {
      if (!el) return;
      if (!moodChips && !genreChips) {
        el.innerHTML = `<span class="mood-badge mood-empty">+ Tag hinzufuegen</span>`;
        return;
      }
      el.innerHTML = `${moodChips}${genreChips}`;
    });
  }

  function setMoodData(songId, topMood, moods = {}, topGenre = '', genres = {}) {
    currentSongId = songId;
    currentMoods = moods || {};
    currentGenres = genres || {};
    selectedMood = topMood || '';
    selectedGenre = topGenre || '';
    updateBadgeDisplay(topMood, currentMoods, topGenre, currentGenres);
  }

  const api = {
    init,
    setMoodData,
    openDialog,
    closeDialog
  };

  window.MoodModule = api;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
  return api;
})();
