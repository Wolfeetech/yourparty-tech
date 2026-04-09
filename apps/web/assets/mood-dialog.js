// QUICK VIBE REACTIONS - Professional Auto-Submit System
(function () {
  'use strict';

  // Core 4 Vibes (reduced from 10)
  const VIBES = [
    { id: 'energy', label: 'Energy', icon: '⚡' },
    { id: 'chill', label: 'Chill', icon: '🌊' },
    { id: 'dark', label: 'Dark', icon: '🌑' },
    { id: 'euphoric', label: 'Euphoric', icon: '✨' }
  ];

  // Configuration
  const COOLDOWN_MS = 5 * 60 * 1000; // 5 minutes
  const STORAGE_KEY = 'yp_vibe_cooldown';

  let currentTrack = null;
  let panelElement = null;

  // ========== Cooldown Management ==========

  function getLastVote(songId) {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return data[songId] || 0;
    } catch { return 0; }
  }

  function setLastVote(songId) {
    try {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      data[songId] = Date.now();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) { console.warn('[Vibe] Storage error:', e); }
  }

  function isOnCooldown(songId) {
    return (Date.now() - getLastVote(songId)) < COOLDOWN_MS;
  }

  // ========== Create Panel ==========

  function createVibePanel() {
    const panel = document.createElement('div');
    panel.className = 'vibe-panel';
    panel.id = 'vibe-panel';
    panel.setAttribute('role', 'group');
    panel.setAttribute('aria-label', 'Quick Vibe Reactions');

    const vibeButtonsHTML = VIBES.map(v => `
      <button class="vibe-btn" data-vibe="${v.id}" aria-label="${v.label}">
        <span class="vibe-btn__icon">${v.icon}</span>
        <span class="vibe-btn__label">${v.label}</span>
      </button>
    `).join('');

    panel.innerHTML = `
      <div class="vibe-panel__header">
        <span class="vibe-panel__prompt">What's the vibe?</span>
        <button class="vibe-panel__close" aria-label="Close">&times;</button>
      </div>
      <div class="vibe-panel__track">
        <span class="vibe-panel__title">—</span>
        <span class="vibe-panel__artist">—</span>
      </div>
      <div class="vibe-panel__buttons">
        ${vibeButtonsHTML}
      </div>
      <div class="vibe-panel__feedback"></div>
    `;

    document.body.appendChild(panel);
    return panel;
  }

  // ========== Show/Hide Panel ==========

  function showVibePanel(track) {
    if (!track) {
      track = {
        id: window.currentSongId,
        title: document.getElementById('track-title')?.textContent || 'Unknown',
        artist: document.getElementById('track-artist')?.textContent || 'Unknown'
      };
    }

    if (!track.id) {
      console.warn('[Vibe] No track info available');
      return;
    }

    if (isOnCooldown(track.id)) {
      showFeedback('Already voted for this track', 'info');
      return;
    }

    currentTrack = track;

    // Update track display
    panelElement.querySelector('.vibe-panel__title').textContent = track.title;
    panelElement.querySelector('.vibe-panel__artist').textContent = track.artist;

    // Reset buttons
    panelElement.querySelectorAll('.vibe-btn').forEach(btn => {
      btn.classList.remove('selected', 'submitting');
      btn.disabled = false;
    });

    // Clear feedback
    panelElement.querySelector('.vibe-panel__feedback').textContent = '';
    panelElement.querySelector('.vibe-panel__feedback').className = 'vibe-panel__feedback';

    // Show panel
    panelElement.classList.add('active');
  }

  function hideVibePanel() {
    panelElement.classList.remove('active');
    currentTrack = null;
  }

  function showFeedback(message, type = 'success') {
    const feedback = panelElement.querySelector('.vibe-panel__feedback');
    feedback.textContent = message;
    feedback.className = `vibe-panel__feedback vibe-panel__feedback--${type}`;
  }

  // ========== Submit Vote ==========

  async function submitVibe(vibeId, button) {
    if (!currentTrack?.id) return;

    // Visual feedback
    button.classList.add('submitting');
    panelElement.querySelectorAll('.vibe-btn').forEach(b => b.disabled = true);

    const payload = {
      song_id: currentTrack.id,
      mood_current: vibeId,
      title: currentTrack.title,
      artist: currentTrack.artist
    };

    try {
      const response = await fetch('/wp-json/yourparty/v1/vote-mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      // Success
      button.classList.remove('submitting');
      button.classList.add('selected');
      setLastVote(currentTrack.id);
      showFeedback('✓ Vibe recorded', 'success');

      // Auto-close after short delay
      setTimeout(hideVibePanel, 1200);

    } catch (e) {
      console.error('[Vibe] Submit error:', e);
      button.classList.remove('submitting');
      showFeedback('Network error', 'error');
      panelElement.querySelectorAll('.vibe-btn').forEach(b => b.disabled = false);
    }
  }

  // ========== Event Handlers ==========

  function setupEventListeners() {
    // Close button
    panelElement.querySelector('.vibe-panel__close').addEventListener('click', hideVibePanel);

    // Click outside to close
    panelElement.addEventListener('click', (e) => {
      if (e.target === panelElement) hideVibePanel();
    });

    // Vibe buttons - auto submit on click
    panelElement.querySelectorAll('.vibe-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const vibeId = btn.dataset.vibe;
        submitVibe(vibeId, btn);
      });
    });

    // ESC to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panelElement.classList.contains('active')) {
        hideVibePanel();
      }
    });
  }

  // ========== Initialize ==========

  function init() {
    // Don't initialize on Control Panel page where ControlPanel.js handles tagging
    if (window.location.pathname.includes('/control')) {
      console.log('[Vibe] Skipped on Control Panel page');
      return;
    }

    panelElement = createVibePanel();
    setupEventListeners();

    // Global function for TAG VIBE button
    window.openMoodDialog = showVibePanel;

    // Attach to trigger button (but not on Control Panel where ControlPanel.js handles it)
    const triggerBtn = document.getElementById('mood-tag-button');
    if (triggerBtn) {
      triggerBtn.addEventListener('click', () => {
        // Skip if ControlPanel is managing the tag button
        if (window.controlPanel || document.body.classList.contains('page-template-page-control')) {
          return;
        }
        showVibePanel();
      });
    }

    console.log('[Vibe] Quick Reactions initialized');
  }

  // Start when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
