// MOOD & GENRE TAGGING SYSTEM - Enhanced with Dual Voting
(function () {
  // Mood options matching backend VALID_MOODS
  const MOODS = [
    { id: 'energy', label: 'Energy', emoji: '🔥' },
    { id: 'chill', label: 'Chill', emoji: '😌' },
    { id: 'dark', label: 'Dark', emoji: '🌑' },
    { id: 'euphoric', label: 'Euphoric', emoji: '✨' },
    { id: 'melancholic', label: 'Melancholic', emoji: '💙' },
    { id: 'groove', label: 'Groove', emoji: '🎵' },
    { id: 'hypnotic', label: 'Hypnotic', emoji: '🌀' },
    { id: 'aggressive', label: 'Aggressive', emoji: '😤' },
    { id: 'trippy', label: 'Trippy', emoji: '🍄' },
    { id: 'warm', label: 'Warm', emoji: '☀️' }
  ];

  // Configuration
  const VOTE_COOLDOWN_MINUTES = 5;
  const STORAGE_KEY_COOLDOWN = 'yourparty_mood_cooldown';
  const STORAGE_KEY_PENDING = 'yourparty_pending_votes';

  let currentTrack = null;
  let selectedMoodCurrent = null;  // What mood IS this song
  let selectedMoodNext = null;     // What mood do you WANT next
  let activeTab = 'current';       // 'current' or 'next'

  // ========== LocalStorage Helpers ==========

  function getLastVoteTime(songId) {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY_COOLDOWN) || '{}');
      return data[songId] || 0;
    } catch { return 0; }
  }

  function setLastVoteTime(songId) {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY_COOLDOWN) || '{}');
      data[songId] = Date.now();
      localStorage.setItem(STORAGE_KEY_COOLDOWN, JSON.stringify(data));
    } catch (e) { console.warn('LocalStorage error:', e); }
  }

  function isOnCooldown(songId) {
    const lastVote = getLastVoteTime(songId);
    const cooldownMs = VOTE_COOLDOWN_MINUTES * 60 * 1000;
    return (Date.now() - lastVote) < cooldownMs;
  }

  function getRemainingCooldown(songId) {
    const lastVote = getLastVoteTime(songId);
    const cooldownMs = VOTE_COOLDOWN_MINUTES * 60 * 1000;
    const remaining = cooldownMs - (Date.now() - lastVote);
    return Math.max(0, Math.ceil(remaining / 60000)); // minutes
  }

  // Offline queue support
  function addPendingVote(voteData) {
    try {
      const pending = JSON.parse(localStorage.getItem(STORAGE_KEY_PENDING) || '[]');
      pending.push({ ...voteData, queued_at: Date.now() });
      localStorage.setItem(STORAGE_KEY_PENDING, JSON.stringify(pending));
    } catch (e) { console.warn('Could not queue vote:', e); }
  }

  function getPendingVotes() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY_PENDING) || '[]');
    } catch { return []; }
  }

  function clearPendingVotes() {
    localStorage.removeItem(STORAGE_KEY_PENDING);
  }

  async function syncPendingVotes() {
    const pending = getPendingVotes();
    if (!pending.length || !navigator.onLine) return;

    for (const vote of pending) {
      try {
        await submitVoteToServer(vote);
      } catch (e) {
        console.warn('Could not sync pending vote:', e);
        return; // Stop on first failure
      }
    }
    clearPendingVotes();
  }

  // ========== Dialog Creation ==========

  const createMoodDialog = () => {
    const overlay = document.createElement('div');
    overlay.className = 'mood-overlay';
    overlay.id = 'mood-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'mood-dialog-title');

    const moodButtonsHTML = MOODS.map(mood => `
      <button class="mood-btn" data-value="${mood.id}" 
              aria-label="${mood.label} Stimmung wählen"
              role="radio" aria-checked="false">
        <span class="mood-btn__emoji" aria-hidden="true">${mood.emoji}</span>
        <span>${mood.label}</span>
      </button>
    `).join('');

    overlay.innerHTML = `
      <div class="mood-dialog" role="document">
        <div class="mood-dialog__header">
          <h3 class="mood-dialog__title" id="mood-dialog-title">Mood Voting</h3>
          <p class="mood-dialog__subtitle">Bewerte den aktuellen Track & wähle den nächsten Vibe</p>
        </div>
        
        <div class="mood-dialog__track" id="mood-track-info" aria-live="polite">
          <div class="mood-dialog__track-title">—</div>
          <div class="mood-dialog__track-artist">—</div>
        </div>

        <!-- Vote Mode Tabs -->
        <div class="mood-tabs" role="tablist" aria-label="Abstimmungsmodus">
          <button class="mood-tab active" data-tab="current" 
                  role="tab" aria-selected="true" id="tab-current"
                  aria-controls="panel-current">
            🎵 Aktueller Song
          </button>
          <button class="mood-tab" data-tab="next" 
                  role="tab" aria-selected="false" id="tab-next"
                  aria-controls="panel-next">
            ⏭️ Nächster Vibe
          </button>
        </div>

        <!-- Current Song Mood Panel -->
        <div class="mood-panel active" id="panel-current" 
             role="tabpanel" aria-labelledby="tab-current">
          <p class="mood-panel__hint">Welche Stimmung hat dieser Track?</p>
          <div class="mood-options" role="radiogroup" aria-label="Stimmung des aktuellen Songs">
            ${moodButtonsHTML.replace(/data-value/g, 'data-target="current" data-value')}
          </div>
        </div>

        <!-- Next Mood Preference Panel -->
        <div class="mood-panel" id="panel-next" 
             role="tabpanel" aria-labelledby="tab-next" hidden>
          <p class="mood-panel__hint">Welchen Vibe wünschst du dir als nächstes?</p>
          <div class="mood-options" role="radiogroup" aria-label="Gewünschte Stimmung für den nächsten Song">
            ${moodButtonsHTML.replace(/data-value/g, 'data-target="next" data-value')}
          </div>
        </div>

        <div class="mood-dialog__selection" id="mood-selection" aria-live="polite">
          <span id="selection-current"></span>
          <span id="selection-next"></span>
        </div>

        <div class="mood-dialog__actions">
          <button class="mood-dialog__btn-cancel" id="mood-cancel">Abbrechen</button>
          <button class="mood-dialog__btn-submit" id="mood-submit" disabled 
                  aria-describedby="mood-feedback">Vote senden</button>
        </div>

        <div class="mood-dialog__feedback" id="mood-feedback" role="status" aria-live="assertive"></div>
      </div>
    `;

    document.body.appendChild(overlay);
    return overlay;
  };

  // ========== Initialize ==========

  const moodOverlay = createMoodDialog();
  const moodSubmit = document.getElementById('mood-submit');
  const moodCancel = document.getElementById('mood-cancel');
  const moodFeedback = document.getElementById('mood-feedback');
  const trackInfo = document.getElementById('mood-track-info');
  const selectionCurrent = document.getElementById('selection-current');
  const selectionNext = document.getElementById('selection-next');

  // ========== Tab Switching ==========

  moodOverlay.querySelectorAll('.mood-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      activeTab = target;

      // Update tabs
      moodOverlay.querySelectorAll('.mood-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === target);
        t.setAttribute('aria-selected', t.dataset.tab === target);
      });

      // Update panels
      moodOverlay.querySelectorAll('.mood-panel').forEach(p => {
        const isActive = p.id === `panel-${target}`;
        p.classList.toggle('active', isActive);
        p.hidden = !isActive;
      });
    });
  });

  // ========== Show Dialog ==========

  window.openMoodDialog = (track) => {
    if (!track && window.currentTrackInfo) {
      track = window.currentTrackInfo;
    }

    if (!track || !track.id) {
      console.warn('[MoodDialog] No track info available');
      return;
    }

    // Check cooldown
    if (isOnCooldown(track.id)) {
      const remaining = getRemainingCooldown(track.id);
      alert(`Du hast bereits für diesen Track abgestimmt. Warte noch ${remaining} Minute${remaining !== 1 ? 'n' : ''}.`);
      return;
    }

    currentTrack = track;
    selectedMoodCurrent = null;
    selectedMoodNext = null;
    activeTab = 'current';

    // Update track display
    trackInfo.innerHTML = `
      <div class="mood-dialog__track-title">${track.title || 'Unknown Title'}</div>
      <div class="mood-dialog__track-artist">${track.artist || 'Unknown Artist'}</div>
    `;

    // Reset UI
    moodFeedback.textContent = '';
    moodSubmit.disabled = true;
    selectionCurrent.textContent = '';
    selectionNext.textContent = '';

    // Reset selections
    moodOverlay.querySelectorAll('.mood-btn').forEach(btn => {
      btn.classList.remove('selected');
      btn.setAttribute('aria-checked', 'false');
    });

    // Reset to first tab
    moodOverlay.querySelector('.mood-tab[data-tab="current"]').click();

    moodOverlay.classList.add('active');
    moodOverlay.querySelector('.mood-dialog').focus();
  };

  // ========== Close Dialog ==========

  const closeMoodDialog = () => {
    moodOverlay.classList.remove('active');
  };

  // ========== Mood Selection ==========

  moodOverlay.addEventListener('click', (e) => {
    const btn = e.target.closest('.mood-btn');
    if (!btn) return;

    const target = btn.dataset.target; // 'current' or 'next'
    const value = btn.dataset.value;

    // Deselect others in same panel
    moodOverlay.querySelectorAll(`.mood-btn[data-target="${target}"]`).forEach(b => {
      b.classList.remove('selected');
      b.setAttribute('aria-checked', 'false');
    });

    // Select clicked
    btn.classList.add('selected');
    btn.setAttribute('aria-checked', 'true');

    // Update state
    const mood = MOODS.find(m => m.id === value);
    if (target === 'current') {
      selectedMoodCurrent = value;
      selectionCurrent.textContent = mood ? `Aktuell: ${mood.emoji} ${mood.label}` : '';
    } else {
      selectedMoodNext = value;
      selectionNext.textContent = mood ? `Nächster: ${mood.emoji} ${mood.label}` : '';
    }

    // Enable submit if at least one is selected
    moodSubmit.disabled = (!selectedMoodCurrent && !selectedMoodNext);
  });

  // ========== Submit Vote ==========

  async function submitVoteToServer(payload) {
    const response = await fetch('/wp-json/yourparty/v1/vote-mood', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  moodSubmit.addEventListener('click', async () => {
    if ((!selectedMoodCurrent && !selectedMoodNext) || !currentTrack?.id) return;

    moodSubmit.disabled = true;
    moodFeedback.textContent = 'Wird gesendet...';

    const payload = {
      song_id: currentTrack.id,
      mood_current: selectedMoodCurrent || '',
      mood_next: selectedMoodNext || '',
      title: currentTrack.title,
      artist: currentTrack.artist
    };

    try {
      if (!navigator.onLine) {
        // Queue for later
        addPendingVote(payload);
        moodFeedback.textContent = '📡 Offline - Vote wird später gesendet';
        setLastVoteTime(currentTrack.id);
        setTimeout(closeMoodDialog, 2000);
        return;
      }

      await submitVoteToServer(payload);

      moodFeedback.textContent = '✅ Danke für dein Vote!';
      setLastVoteTime(currentTrack.id);
      setTimeout(closeMoodDialog, 1500);

    } catch (e) {
      console.error('[MoodDialog] Submit error:', e);

      // Queue for retry
      addPendingVote(payload);
      moodFeedback.textContent = '⚠️ Netzwerkfehler - Vote wird später gesendet';
      setLastVoteTime(currentTrack.id);
      setTimeout(closeMoodDialog, 2000);
    }
  });

  // ========== Event Handlers ==========

  moodCancel.addEventListener('click', closeMoodDialog);

  moodOverlay.addEventListener('click', (e) => {
    if (e.target === moodOverlay) closeMoodDialog();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && moodOverlay.classList.contains('active')) {
      closeMoodDialog();
    }
  });

  // ========== Init & Sync ==========

  document.addEventListener('DOMContentLoaded', () => {
    // Attach to trigger button
    const triggerBtn = document.getElementById('mood-tag-button');
    if (triggerBtn) {
      triggerBtn.addEventListener('click', () => {
        const title = document.getElementById('track-title')?.textContent;
        const artist = document.getElementById('track-artist')?.textContent;

        window.openMoodDialog({
          id: window.currentSongId,
          title: title,
          artist: artist
        });
      });
    }

    // Sync pending votes when online
    window.addEventListener('online', syncPendingVotes);
    if (navigator.onLine) {
      syncPendingVotes();
    }
  });

})();
