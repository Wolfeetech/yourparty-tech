const REST_BASE = (
  window.YourPartyConfig && window.YourPartyConfig.restBase
    ? window.YourPartyConfig.restBase
    : "/wp-json/yourparty/v1"
).replace(/\/$/, "");
const PUBLIC_BASE =
  window.YourPartyConfig && window.YourPartyConfig.publicBase
    ? window.YourPartyConfig.publicBase.replace(/\/$/, "")
    : "";
const STREAM_URL =
  window.YourPartyConfig && window.YourPartyConfig.streamUrl
    ? window.YourPartyConfig.streamUrl
    : "";
let PUBLIC_URL = null;
try {
  PUBLIC_URL = PUBLIC_BASE ? new URL(PUBLIC_BASE) : null;
} catch (error) {
  PUBLIC_URL = null;
}
const normaliseUrl = (value) => {
  if (!value || !PUBLIC_URL) return value;
  try {
    const candidate = new URL(value, PUBLIC_URL.href);
    const isInternalIp = candidate.hostname === "192.168.178.210";
    const isRadioHost = candidate.hostname === PUBLIC_URL.hostname;
    if (isInternalIp || isRadioHost) {
      candidate.protocol = PUBLIC_URL.protocol;
      candidate.hostname = PUBLIC_URL.hostname;
      candidate.port = PUBLIC_URL.port;
    }
    return candidate.toString();
  } catch (error) {
    return value;
  }
};
const buildEndpoint = (slug) => `${REST_BASE}/${slug.replace(/^\//, "")}`;

document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.getElementById("nav-toggle");
  const mobileMenu = document.getElementById("mobile-menu");

  // Audio Context Variables (Lifted Scope)
  let audioContext, analyser, dataArray, source;
  let visualizerMode = 'waveform'; // 'waveform', 'spectrum', 'circular', 'shockwave'

  // Fix for Safari Audio Context State
  document.addEventListener('click', () => {
    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume();
    }
  }, { passive: true });

  if (navToggle && mobileMenu) {
    navToggle.addEventListener("click", () => {
      const isOpen = mobileMenu.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
      navToggle.innerHTML = isOpen ? "&times;" : "&#9776;";
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.remove("open");
        navToggle.innerHTML = "&#9776;";
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      const targetId = anchor.getAttribute("href");
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        event.preventDefault();
        targetElement.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  // Mood Tag Button
  const moodTagButton = document.getElementById("mood-tag-button");
  if (moodTagButton) {
    moodTagButton.addEventListener("click", () => {
      const titleEl = document.getElementById("track-title");
      const artistEl = document.getElementById("track-artist");
      const coverEl = document.getElementById("player-cover");

      if (typeof window.openMoodDialog === "function") {
        window.openMoodDialog({
          id: window.currentSongId || null,
          title: titleEl ? titleEl.textContent : "Unknown Title",
          artist: artistEl ? artistEl.textContent : "Unknown Artist"
        });
      }
    });
  }

  const contactForm = document.getElementById("contact-form");
  const contactFeedback = document.getElementById("contact-feedback");
  if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
      const formData = new FormData(contactForm);
      const hasEmptyField = Array.from(formData.values()).some(
        (value) => String(value).trim() === ""
      );
      if (hasEmptyField) {
        event.preventDefault();
        if (contactFeedback) {
          contactFeedback.textContent =
            "Bitte alle Felder ausfüllen, bevor du sendest.";
        }
        return;
      }

      if (contactFeedback) {
        contactFeedback.textContent =
          "Vielen Dank! Wir melden uns innerhalb von 24 Stunden.";
      }
    });
  }

  const audioPlayer = document.getElementById("radio-player");
  if (audioPlayer) {
    audioPlayer.crossOrigin = "anonymous";
  }

  const resolvedStreamUrl = STREAM_URL ? normaliseUrl(STREAM_URL) : "";
  if (audioPlayer && resolvedStreamUrl) {
    let shouldReload = false;
    const sourceEl = audioPlayer.querySelector("source");
    if (sourceEl) {
      if (sourceEl.src !== resolvedStreamUrl) {
        sourceEl.src = resolvedStreamUrl;
        shouldReload = true;
      }
    } else if (audioPlayer.src !== resolvedStreamUrl) {
      audioPlayer.src = resolvedStreamUrl;
      shouldReload = true;
    }
    if (shouldReload) {
      audioPlayer.load();
    }
  }

  // SCROLL ANIMATION (Focus Effect)
  const radioCard = document.querySelector('.radio-card');
  if (radioCard) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('focused');
        } else {
          entry.target.classList.remove('focused');
        }
      });
    }, { threshold: 0.6 });
    observer.observe(radioCard);
  }
  const playToggle = document.getElementById("play-toggle");
  const miniPlayer = document.getElementById("mini-player");
  const miniPlayToggle = document.getElementById("mini-play-toggle");
  const miniTrackTitle = document.getElementById("mini-track-title");
  const miniTrackArtist = document.getElementById("mini-track-artist");
  const miniListenerCount = document.getElementById("mini-listener-count");
  if (audioPlayer && playToggle) {
    const playToggleIcon = playToggle.querySelector("[aria-hidden]");

    // Visualizer Setup
    // Variables lifted to top scope
    const initAudioContext = () => {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.88;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        try {
          source = audioContext.createMediaElementSource(audioPlayer);
          source.connect(analyser);
          analyser.connect(audioContext.destination);
        } catch (e) {
          console.warn("MediaElementSource already connected or CORS issue", e);
        }
      } else if (audioContext.state === 'suspended') {
        audioContext.resume();
      }
    };

    const updateIcon = () => {
      const isPaused = audioPlayer.paused;
      const icon = isPaused ? "▶" : "❚❚";
      const label = isPaused ? "Stream starten" : "Stream pausieren";

      // Main Player
      if (playToggleIcon) {
        playToggleIcon.textContent = icon;
      } else {
        playToggle.textContent = icon;
      }
      playToggle.setAttribute("aria-label", label);

      // Mini Player
      if (miniPlayToggle) {
        const miniIcon = miniPlayToggle.querySelector("span");
        if (miniIcon) miniIcon.textContent = icon;
        miniPlayToggle.setAttribute("aria-label", label);
        miniPlayToggle.classList.toggle("playing", !isPaused);

        // Reset scale when paused
        if (isPaused) {
          miniPlayToggle.style.transform = 'scale(1)';
          miniPlayToggle.style.boxShadow = '';
        }
      }
    };

    const togglePlay = async () => {
      try {
        initAudioContext();
        if (audioPlayer.paused) {
          // LIVESTREAM FIX: Reload source to resync with live position
          // This prevents playing stale cached audio after pause
          const sourceEl = audioPlayer.querySelector("source");
          const currentSrc = sourceEl ? sourceEl.src : audioPlayer.src;
          if (currentSrc) {
            // Add cache-buster to force reload
            const cleanSrc = currentSrc.split('?')[0];
            const newSrc = `${cleanSrc}?_=${Date.now()}`;
            if (sourceEl) {
              sourceEl.src = newSrc;
            } else {
              audioPlayer.src = newSrc;
            }
            audioPlayer.load();
          }
          await audioPlayer.play();
          // Fetch latest status immediately after resume
          fetchStatus();
        } else {
          audioPlayer.pause();
        }
        updateIcon();
        const mediaContainer = document.querySelector('.radio-card__media');
        if (mediaContainer) mediaContainer.classList.toggle('playing', !audioPlayer.paused);
      } catch (error) {
        console.error("Audio playback error:", error);
      }
    };

    playToggle.addEventListener("click", togglePlay);
    if (miniPlayToggle) {
      miniPlayToggle.addEventListener("click", togglePlay);
    }

    if ('mediaSession' in navigator) {
      navigator.mediaSession.setActionHandler('play', togglePlay);
      navigator.mediaSession.setActionHandler('pause', togglePlay);
    }

    audioPlayer.addEventListener("play", updateIcon);
    audioPlayer.addEventListener("pause", updateIcon);
  }

  const titleElement = document.getElementById("track-title");
  const artistElement = document.getElementById("track-artist");
  const albumElement = document.getElementById("track-album");
  const statusElement = document.getElementById("track-status");
  const listenersElement = document.getElementById("listener-count");
  const coverElement = document.getElementById("cover-art");
  const ratingStars = Array.from(
    document.querySelectorAll(".rating-star[data-value]")
  );
  const ratingAverageElement = document.getElementById("rating-average");
  const ratingTotalElement = document.getElementById("rating-total");
  const voteFeedback = document.getElementById("vote-feedback");
  const historyList = document.getElementById("history-list");
  const historyRefresh = document.getElementById("refresh-history");
  const scheduleList = document.getElementById("schedule-list");

  const PLACEHOLDER_COVER =
    "https://placehold.co/480x480/2e8b57/ffffff?text=YourParty+Radio";

  let currentSongId = null;
  let isSendingVote = false;
  let lastServerAverage = 0;
  let pendingSelection = 0;

  const fallback = (value, alt) =>
    value === undefined || value === null || value === "" ? alt : value;

  const detectOnlineState = (data) => {
    if (typeof data?.is_online === "boolean") return data.is_online;
    if (typeof data?.stream_online === "boolean")
      return data.stream_online === true;
    if (typeof data?.stream_is_online === "boolean")
      return data.stream_is_online === true;
    if (typeof data?.now_playing?.is_playing === "boolean")
      return data.now_playing.is_playing === true;
    if (typeof data?.now_playing?.is_live === "boolean")
      return data.now_playing.is_live === true;
    if (data?.now_playing?.live?.is_live) return true;
    return true;
  };

  const computeAverageFromRating = (rating = {}) => {
    if (typeof rating.average === "number") return rating.average;

    if (rating.distribution && typeof rating.distribution === "object") {
      let totalVotes = 0;
      let weighted = 0;
      Object.entries(rating.distribution).forEach(([key, value]) => {
        const votes = Number(value) || 0;
        const star = Number(key);
        if (star >= 1 && star <= 5) {
          totalVotes += votes;
          weighted += votes * star;
        }
      });
      return totalVotes ? weighted / totalVotes : 0;
    }

    const like = Number(rating.like ?? rating.likes ?? 0);
    const dislike = Number(rating.dislike ?? rating.dislikes ?? 0);
    const total = like + dislike;
    return total ? (like / total) * 5 : 0;
  };

  const computeTotalVotes = (rating = {}) => {
    if (typeof rating.total === "number") return rating.total;
    if (typeof rating.count === "number") return rating.count;
    if (typeof rating.votes === "number") return rating.votes;
    if (rating.distribution && typeof rating.distribution === "object") {
      return Object.values(rating.distribution).reduce(
        (sum, value) => sum + (Number(value) || 0),
        0
      );
    }
    const like = Number(rating.like ?? rating.likes ?? 0);
    const dislike = Number(rating.dislike ?? rating.dislikes ?? 0);
    return like + dislike;
  };

  const buildStarRow = (average = 0) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const threshold = i - 0.25;
      const filled = average >= threshold;
      stars.push(
        `<span class="history-star${filled ? " filled" : ""}" aria-hidden="true">&#9733;</span>`
      );
    }
    return stars.join("");
  };

  const setStarHighlight = (value) => {
    const numericValue = Number(value);
    const hasSelection = Number.isFinite(numericValue) && numericValue > 0;
    const focusValue = hasSelection ? numericValue : 1;

    ratingStars.forEach((star) => {
      const starValue = Number(star.dataset.value);
      const isActive = hasSelection && starValue <= numericValue;
      const isChecked = hasSelection && starValue === numericValue;

      star.classList.toggle("active", isActive);
      star.setAttribute("aria-checked", isChecked ? "true" : "false");
      star.setAttribute("tabindex", starValue === focusValue ? "0" : "-1");
    });
  };

  const resetStarHighlight = () => {
    const base = pendingSelection || Math.round(lastServerAverage || 0);
    setStarHighlight(base);
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "--:--";
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleTimeString("de-DE", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return "--:--";
    }
  };

  const updateStatus = (data) => {
    const nowPlaying = data?.now_playing ?? {};
    const song = nowPlaying.song ?? {};
    const listeners = data?.listeners?.current ?? 0;

    const isOnline = detectOnlineState(data);
    currentSongId = song.id ?? null;
    const trackTitle = fallback(song.title, "Titel unbekannt");
    const trackArtist = fallback(song.artist, "Künstler unbekannt");
    const trackAlbum = fallback(song.album, "Album unbekannt");
    let cover = fallback(normaliseUrl(song.art), PLACEHOLDER_COVER);

    const isLive = Boolean(nowPlaying.live?.is_live);
    const statusLabel = isOnline ? (isLive ? "Live DJ" : "On Air") : "Offline";

    if (isLive) {
      const liveArt = normaliseUrl(nowPlaying.live?.art);
      if (liveArt) {
        cover = liveArt;
      }
    }

    // Update Main Player (Always update, even if not live DJ)
    if (titleElement) titleElement.textContent = trackTitle;
    if (artistElement) artistElement.textContent = trackArtist;
    if (albumElement) albumElement.textContent = trackAlbum;
    if (listenersElement) listenersElement.textContent = listeners;

    // Update Mini Player
    if (miniTrackTitle) miniTrackTitle.textContent = trackTitle;
    if (miniTrackArtist) miniTrackArtist.textContent = trackArtist;
    if (miniListenerCount) miniListenerCount.textContent = listeners;

    // Update Pro Visualizer Elements
    const nextSong = data?.playing_next?.song ?? {};
    const nextTitle = fallback(nextSong.title, "Non-Stop Music");
    const nextArtist = fallback(nextSong.artist, "YourParty Selection");

    const proTitle = document.getElementById('pro-title');
    const proArtist = document.getElementById('pro-artist');
    const proCover = document.getElementById('pro-cover');
    const proListeners = document.getElementById('pro-listeners');
    const proNextTitle = document.getElementById('pro-next-title');
    const proNextArtist = document.getElementById('pro-next-artist');

    if (proTitle) proTitle.textContent = trackTitle;
    if (proArtist) proArtist.textContent = trackArtist;
    if (proCover && proCover.src !== cover) proCover.src = cover;
    if (proListeners) proListeners.textContent = listeners;
    if (proNextTitle) proNextTitle.textContent = nextTitle;
    if (proNextArtist) proNextArtist.textContent = nextArtist;

    if (statusElement) {
      statusElement.textContent = statusLabel;
      statusElement.classList.toggle("status-online", isOnline);
      statusElement.classList.toggle("status-offline", !isOnline);
    }

    if (coverElement) {
      coverElement.onerror = () => {
        if (coverElement.src !== PLACEHOLDER_COVER) {
          coverElement.src = PLACEHOLDER_COVER;
        }
      };
      const cacheSafeCover =
        isLive && cover
          ? `${cover}${cover.includes("?") ? "&" : "?"}_=${Date.now()}`
          : cover;
      coverElement.src = cacheSafeCover;
      coverElement.alt = `Cover zu ${trackTitle} von ${trackArtist}`;
    }

    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: trackTitle,
        artist: trackArtist,
        album: trackAlbum,
        artwork: [
          { src: cover, sizes: '96x96', type: 'image/png' },
          { src: cover, sizes: '128x128', type: 'image/png' },
          { src: cover, sizes: '192x192', type: 'image/png' },
          { src: cover, sizes: '256x256', type: 'image/png' },
          { src: cover, sizes: '384x384', type: 'image/png' },
          { src: cover, sizes: '512x512', type: 'image/png' },
        ]
      });
    }

    const rating = song.rating ?? {};
    const average = computeAverageFromRating(rating);
    const votes = computeTotalVotes(rating);
    lastServerAverage = average || 0;
    pendingSelection = 0;
    resetStarHighlight();

    if (ratingAverageElement) {
      ratingAverageElement.textContent = average
        ? average.toFixed(1).replace(".", ",")
        : "--";
    }

    if (ratingTotalElement) {
      ratingTotalElement.textContent = votes
        ? `${votes} ${votes === 1 ? "Bewertung" : "Bewertungen"}`
        : "Noch keine Bewertungen";
    }

    // Display Mood Tags if available
    const moodTagDisplay = document.getElementById('current-mood-tags');
    const topMood = song.top_mood;
    const moods = song.moods || {};

    if (moodTagDisplay) {
      const moodEmojis = {
        'energetic': '🔥', 'chill': '😌', 'dark': '🌑', 'euphoric': '✨',
        'melancholic': '💙', 'groovy': '🎵', 'hypnotic': '🌀',
        'aggressive': '😤', 'trippy': '🍄', 'warm': '☀️',
        'uplifting': '🌈', 'deep': '🌊', 'funky': '🕺'
      };

      if (topMood) {
        const emoji = moodEmojis[topMood] || '🎵';
        const moodLabel = topMood.charAt(0).toUpperCase() + topMood.slice(1);
        const voteCount = moods[topMood] || 0;
        moodTagDisplay.innerHTML = `<span class="mood-badge">${emoji} ${moodLabel}${voteCount > 1 ? ` (${voteCount})` : ''}</span>`;
      } else {
        moodTagDisplay.innerHTML = '<span class="mood-badge mood-empty">+ Tag hinzufügen</span>';
      }
    }

    if (voteFeedback) {
      voteFeedback.textContent = "";
    }
  };

  const renderHistory = (items = []) => {
    if (!historyList) return;
    historyList.innerHTML = "";

    if (!items.length) {
      historyList.innerHTML = '<div style="padding:20px; text-align:center; color:#666; font-size:12px;">Noch keine History verfügbar</div>';
      return;
    }

    const table = document.createElement("table");
    table.className = "history-table";

    items.slice(0, 10).forEach((entry) => {
      const song = entry.song ?? {};
      const art = fallback(normaliseUrl(song.art), "https://placehold.co/40x40/1f1f2b/ffffff?text=?");

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="history-cover">
            <img src="${art}" alt="Cover" loading="lazy">
        </td>
        <td class="history-info">
            <span class="history-title">${fallback(song.title, "Unbekannt")}</span>
            <span class="history-artist">${fallback(song.artist, "Unbekannt")}</span>
        </td>
        <td class="history-rating">
            <div class="history-stars" data-song-id="${song.id}">
                ${[1, 2, 3, 4, 5].map(i => `
                    <span class="history-star" data-value="${i}" title="${i} Sterne">★</span>
                `).join('')}
            </div>
            <div class="history-time">${timeAgo(entry.played_at)}</div>
        </td>
      `;
      table.appendChild(tr);
    });

    historyList.appendChild(table);
  };

  const formatDateTime = (value) => {
    if (!value) return "--:--";
    try {
      const date =
        typeof value === "number"
          ? new Date(value * 1000)
          : new Date(String(value));
      return date.toLocaleTimeString("de-DE", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return "--:--";
    }
  };

  const timeAgo = (timestamp) => {
    if (!timestamp) return "";
    const seconds = Math.floor((new Date() - new Date(timestamp * 1000)) / 1000);
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " J.";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " Mon.";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " T.";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " Std.";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " Min.";
    return "Gerade eben";
  };

  const renderSchedule = (items = []) => {
    if (!scheduleList) return;
    scheduleList.innerHTML = "";

    if (!items.length) {
      const empty = document.createElement("li");
      empty.className = "schedule-item";
      empty.innerHTML =
        "<strong>Keine Einträge</strong><small>Der Programmplan wird geladen.</small>";
      scheduleList.appendChild(empty);
      return;
    }

    const now = Date.now() / 1000;

    items.slice(0, 5).forEach((entry) => {
      const li = document.createElement("li");
      const startTs = entry.start_timestamp ?? entry.start ?? entry.timestamp;
      const endTs = entry.end_timestamp ?? entry.end;

      const isActive = now >= startTs && now < endTs;
      li.className = `schedule-item ${isActive ? "schedule-item--active" : ""}`;

      const title = fallback(entry.name ?? entry.title, "Show");
      const start = formatDateTime(startTs);
      const end = formatDateTime(endTs);
      const description = fallback(entry.description, "");

      // Calculate progress if active
      let progressHtml = "";
      if (isActive && startTs && endTs) {
        const duration = endTs - startTs;
        const elapsed = now - startTs;
        const percent = Math.min(100, Math.max(0, (elapsed / duration) * 100));
        progressHtml = `<div class="schedule-progress"><div class="schedule-progress-bar" style="width: ${percent}%"></div></div>`;
      }

      li.innerHTML = `
        <div class="schedule-time">
            <span>${start}</span>
        </div>
        <div class="schedule-content">
            <strong>${title}</strong>
            <small>${end !== "--:--" ? `Bis ${end}` : ""}</small>
            ${description ? `<span class="schedule-desc">${description}</span>` : ""}
            ${isActive ? '<span class="status-pill status-pill--online">Live</span>' : ""}
            ${progressHtml}
        </div>
      `;
      scheduleList.appendChild(li);
    });
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch(buildEndpoint("status"));
      if (!response.ok) throw new Error(`Status HTTP ${response.status}`);
      const data = await response.json();
      updateStatus(data);
    } catch (error) {
      console.error("Status fetch failed:", error);
      if (statusElement) {
        statusElement.textContent = "Offline";
        statusElement.classList.remove("status-online");
        statusElement.classList.add("status-offline");
      }
      if (titleElement) titleElement.textContent = "Stream offline";
      if (artistElement)
        artistElement.textContent = "Bitte AzuraCast pruefen";
      if (albumElement) albumElement.textContent = "-";
      if (voteFeedback) {
        voteFeedback.textContent =
          "Livestatus konnte nicht geladen werden. Bitte neu laden.";
      }
    }
  };

  const fetchHistory = async () => {
    if (historyList) {
      historyList.innerHTML = `
        <li class="history-item skeleton"></li>
        <li class="history-item skeleton"></li>
        <li class="history-item skeleton"></li>
      `;
    }
    try {
      const response = await fetch(buildEndpoint("history"));
      if (!response.ok) throw new Error(`History HTTP ${response.status}`);
      const data = await response.json();
      const items = Array.isArray(data) ? data : data.history ?? [];
      renderHistory(items);
    } catch (error) {
      console.error("History fetch failed:", error);
      renderHistory([]);
    }
  };

  const setScheduleSkeleton = () => {
    if (!scheduleList) return;
    scheduleList.innerHTML = `
      <li class="schedule-item schedule-item--loading"></li>
      <li class="schedule-item schedule-item--loading"></li>
      <li class="schedule-item schedule-item--loading"></li>
    `;
  };

  const fetchSchedule = async () => {
    if (scheduleList) {
      setScheduleSkeleton();
    }
    try {
      const response = await fetch(buildEndpoint("schedule"));
      if (!response.ok) throw new Error(`Schedule HTTP ${response.status}`);
      const data = await response.json();
      const items = Array.isArray(data) ? data : data.schedule ?? [];
      renderSchedule(items);
    } catch (error) {
      console.error("Schedule fetch failed:", error);
      renderSchedule([]);
    }
  };

  const submitRating = async (value) => {
    const ratingValue = Number(value);
    if (!ratingValue || ratingValue < 1 || ratingValue > 5) return;

    if (!currentSongId) {
      if (voteFeedback) {
        voteFeedback.textContent =
          "Keine aktive Wiedergabe. Bitte warte auf den nächsten Track.";
      }
      return;
    }

    if (isSendingVote) return;

    isSendingVote = true;
    pendingSelection = ratingValue;
    setStarHighlight(ratingValue);
    if (voteFeedback) {
      voteFeedback.textContent = "Bewertung wird übertragen …";
    }

    try {
      const response = await fetch(buildEndpoint("rate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          song_id: currentSongId,
          rating: ratingValue,
          vote:
            ratingValue >= 4
              ? "like"
              : ratingValue <= 2
                ? "dislike"
                : "neutral",
        }),
      });
      if (!response.ok) throw new Error(`Vote HTTP ${response.status}`);
      const result = await response.json();
      const counts = result.ratings ?? {};

      const average = computeAverageFromRating(counts) || ratingValue;
      const votes = computeTotalVotes(counts);
      lastServerAverage = average;
      pendingSelection = 0;
      resetStarHighlight();

      if (ratingAverageElement) {
        ratingAverageElement.textContent = average
          ? average.toFixed(1).replace(".", ",")
          : ratingValue.toFixed(1).replace(".", ",");
      }
      if (ratingTotalElement) {
        const totalVotes = votes || Number(counts.total) || 0;
        ratingTotalElement.textContent = totalVotes
          ? `${totalVotes} ${totalVotes === 1 ? "Bewertung" : "Bewertungen"
          }`
          : "Deine Bewertung ist eingegangen";
      }

      if (voteFeedback) {
        voteFeedback.textContent =
          "Danke! Deine Bewertung beeinflusst das Programm.";
      }
    } catch (error) {
      console.error("Vote failed:", error);
      if (voteFeedback) {
        voteFeedback.textContent =
          "Bewertung nicht möglich. Bitte später erneut versuchen.";
      }
    } finally {
      isSendingVote = false;
    }
  };

  ratingStars.forEach((star) => {
    const value = Number(star.dataset.value);
    star.addEventListener("mouseenter", () => setStarHighlight(value));
    star.addEventListener("focus", () => setStarHighlight(value));
    star.addEventListener("mouseleave", resetStarHighlight);
    star.addEventListener("blur", resetStarHighlight);
    star.addEventListener("click", () => submitRating(value));
    star.addEventListener("keydown", (event) => {
      const key = event.key;
      if (key === "Enter" || key === " ") {
        event.preventDefault();
        submitRating(value);
      }
      if (key === "ArrowLeft" || key === "ArrowDown") {
        event.preventDefault();
        const prev = Math.max(1, value - 1);
        const prevStar = ratingStars.find(
          (item) => Number(item.dataset.value) === prev
        );
        if (prevStar) prevStar.focus();
      }
      if (key === "ArrowRight" || key === "ArrowUp") {
        event.preventDefault();
        const next = Math.min(5, value + 1);
        const nextStar = ratingStars.find(
          (item) => Number(item.dataset.value) === next
        );
        if (nextStar) nextStar.focus();
      }
    });
  });

  if (historyRefresh) {
    historyRefresh.addEventListener("click", fetchHistory);
  }

  fetchStatus();
  fetchHistory();
  fetchSchedule();
  setInterval(fetchStatus, 10000);
  setInterval(fetchHistory, 30000);
  setInterval(fetchSchedule, 60000);
  // History Rating Listener (Delegation)
  if (historyList) {
    historyList.addEventListener('click', async (e) => {
      if (e.target.classList.contains('history-star')) {
        const star = e.target;
        const container = star.closest('.history-stars');
        const songId = container.dataset.songId;
        const value = parseInt(star.dataset.value);

        // Visual Feedback
        const stars = container.querySelectorAll('.history-star');
        stars.forEach((s, i) => {
          if (i < value) {
            s.classList.add('filled');
            s.style.color = 'var(--emerald)';
          } else {
            s.classList.remove('filled');
            s.style.color = '#444';
          }
        });

        // API Call
        try {
          await fetch('/wp-json/yourparty/v1/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              song_id: songId,
              rating: value,
              vote: value >= 4 ? 'like' : value <= 2 ? 'dislike' : 'neutral'
            })
          });
        } catch (err) {
          console.error('Rating failed', err);
        }
      }
    });
  }

  // Modal Logic
  const modal = document.getElementById('page-modal');
  const modalBody = document.getElementById('modal-body');
  const modalClose = document.querySelector('.modal-close');

  if (modal && modalBody) {
    const openModal = async (url) => {
      modal.classList.add('active');
      modal.setAttribute('aria-hidden', 'false');
      modalBody.innerHTML = '<div style="text-align:center; padding:40px; color: #fff;">Lade Inhalte...</div>';

      try {
        const response = await fetch(url);
        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        // Try to find the main content area
        const content = doc.querySelector('main') || doc.querySelector('#content') || doc.querySelector('.entry-content') || doc.body;

        // Remove hero if present in content (optional)
        const hero = content.querySelector('#hero');
        if (hero) hero.remove();

        modalBody.innerHTML = content.innerHTML;
      } catch (e) {
        modalBody.innerHTML = '<p style="color: #fff;">Fehler beim Laden der Seite.</p>';
      }
    };

    const closeModal = () => {
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
      modalBody.innerHTML = '';
    };

    if (modalClose) modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });

    // Attach to footer links
    document.querySelectorAll('.site-footer a, .site-footer__legal a').forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        // Only intercept internal links that are not anchors
        if (href && href.startsWith('http') && href.includes(window.location.hostname) && !href.includes('#')) {
          e.preventDefault();
          openModal(href);
        }
      });
    });
  }

  // Mini Player Visibility
  // Mini Player Visibility
  if (!radioCard && miniPlayer) {
    miniPlayer.style.display = 'flex';
  }

  // FULLSCREEN VISUALIZER LOGIC
  const visualizerToggle = document.getElementById('visualizer-toggle');
  let isFullscreenVisualizer = false;
  let fullscreenCanvas = null;
  let fullscreenCtx = null;
  let animationFrameId = null;

  if (visualizerToggle) {
    visualizerToggle.addEventListener('click', () => {
      toggleFullscreenVisualizer();
    });
  }

  // PROFESSIONAL FULLSCREEN VISUALIZER
  let proWaveformHistory = [];

  const toggleFullscreenVisualizer = () => {
    isFullscreenVisualizer = !isFullscreenVisualizer;

    if (isFullscreenVisualizer) {
      // Create Overlay
      const overlay = document.createElement('div');
      overlay.className = 'visualizer-fullscreen pro-mode';

      const ratingHtml = document.querySelector('.rating-container')?.innerHTML || '';
      const coverSrc = coverElement ? coverElement.src : '';
      const title = titleElement ? titleElement.textContent : 'Unknown Track';
      const artist = artistElement ? artistElement.textContent : 'Unknown Artist';
      const time = new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });

      overlay.innerHTML = `
        <div class="pro-header">
            <div class="pro-brand">
                <span>YOURPARTY RADIO</span>
                <span class="pro-live-indicator">LIVE</span>
            </div>
            <div class="pro-clock">${time}</div>
        </div>
        
        <div class="pro-main">
            <div class="pro-cover-art">
                <img src="${coverSrc}" id="pro-cover">
            </div>
            <div class="pro-track-info">
                <h1 id="pro-title" class="pro-title">${title}</h1>
                <h2 id="pro-artist" class="pro-artist">${artist}</h2>
                <div class="pro-meta">
                    <div class="pro-badge">ELECTRONIC</div>
                    <div class="pro-badge">HQ AUDIO</div>
                    <div class="rating-container">${ratingHtml}</div>
                </div>
            </div>
            <div class="pro-sidebar">
                <h3>Up Next</h3>
                <div class="pro-next-track">
                    <div id="pro-next-title" class="pro-next-title">Loading...</div>
                    <div id="pro-next-artist" class="pro-next-artist">...</div>
                </div>
                <h3>Listeners</h3>
                <div class="pro-badge" style="justify-content:center; margin-top:10px;">
                    <span id="pro-listeners">${listenersElement ? listenersElement.textContent : '0'}</span>
                </div>
            </div>
        </div>

        <div class="pro-visualizer-area">
            <canvas id="pro-canvas"></canvas>
            <div class="pro-vis-controls" style="position:absolute; bottom:20px; right:20px; display:flex; gap:10px; z-index:10;">
                <button class="vis-btn" data-mode="waveform">WAVE</button>
                <button class="vis-btn" data-mode="spectrum">SPEC</button>
                <button class="vis-btn" data-mode="circular">CIRC</button>
                <button class="vis-btn" data-mode="shockwave">BASS</button>
            </div>
            <button class="pro-close">×</button>
        </div>
      `;

      document.body.appendChild(overlay);
      document.body.classList.add('visualizer-active');

      fullscreenCanvas = overlay.querySelector('canvas');
      fullscreenCtx = fullscreenCanvas.getContext('2d');

      // Close handler
      overlay.querySelector('.pro-close').addEventListener('click', toggleFullscreenVisualizer);

      // Mode Handlers
      overlay.querySelectorAll('.vis-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          visualizerMode = e.target.dataset.mode;
          overlay.querySelectorAll('.vis-btn').forEach(b => b.classList.remove('active'));
          e.target.classList.add('active');
        });
      });

      // Clock Update
      const clockInterval = setInterval(() => {
        const t = new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
        const clock = overlay.querySelector('.pro-clock');
        if (clock) clock.textContent = t;
        else clearInterval(clockInterval);
      }, 1000);

      resizeFullscreenCanvas();
      window.addEventListener('resize', resizeFullscreenCanvas);
      drawFullscreenVisualizer();

    } else {
      const overlay = document.querySelector('.visualizer-fullscreen');
      if (overlay) overlay.remove();
      document.body.classList.remove('visualizer-active');
      window.removeEventListener('resize', resizeFullscreenCanvas);
      cancelAnimationFrame(animationFrameId);
    }
  };

  const resizeFullscreenCanvas = () => {
    if (fullscreenCanvas) {
      fullscreenCanvas.width = fullscreenCanvas.parentElement.clientWidth;
      fullscreenCanvas.height = fullscreenCanvas.parentElement.clientHeight;
    }
  };

  const drawFullscreenVisualizer = () => {
    if (!isFullscreenVisualizer) return;
    animationFrameId = requestAnimationFrame(drawFullscreenVisualizer);

    const width = fullscreenCanvas.width;
    const height = fullscreenCanvas.height;
    const ctx = fullscreenCtx;

    // Fade effect for trails
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    if (!analyser || (audioContext && audioContext.state === 'suspended')) {
      ctx.fillStyle = '#666';
      ctx.font = '20px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('Click Play to Start Visualizer', width / 2, height / 2);
      return;
    }

    analyser.getByteFrequencyData(dataArray);

    if (visualizerMode === 'circular') {
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) / 4;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = '#333';
      ctx.stroke();

      for (let i = 0; i < dataArray.length; i++) {
        const barHeight = (dataArray[i] / 255) * 100;
        const angle = (i / dataArray.length) * 2 * Math.PI;

        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        const x2 = centerX + Math.cos(angle) * (radius + barHeight);
        const y2 = centerY + Math.sin(angle) * (radius + barHeight);

        ctx.strokeStyle = `hsl(${i / dataArray.length * 360}, 100%, 50%)`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    } else if (visualizerMode === 'shockwave') {
      // Bass detection
      let bass = 0;
      for (let i = 0; i < 10; i++) bass += dataArray[i];
      bass /= 10;

      const centerX = width / 2;
      const centerY = height / 2;
      const radius = (bass / 255) * (Math.min(width, height) / 2);

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = `hsl(${bass}, 100%, 50%)`;
      ctx.lineWidth = 5;
      ctx.stroke();

      if (bass > 200) {
        ctx.fillStyle = `rgba(255, 255, 255, ${bass / 500})`;
        ctx.fillRect(0, 0, width, height);
      }
    } else if (visualizerMode === 'spectrum') {
      // Existing Spectrum
      const barWidth = (width / dataArray.length) * 2.5;
      let x = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const barHeight = (dataArray[i] / 255) * height;
        const hue = i / dataArray.length * 360;
        ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
        ctx.fillRect(x, height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
        if (x > width) break;
      }
    } else {
      // Existing Waveform
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
      let average = sum / dataArray.length;

      proWaveformHistory.push(average);
      if (proWaveformHistory.length > width / 2) proWaveformHistory.shift();

      const centerY = height / 2;
      const playheadX = width;

      for (let i = 0; i < proWaveformHistory.length; i++) {
        const vol = proWaveformHistory[proWaveformHistory.length - 1 - i];
        const x = playheadX - (i * 2);
        if (x < 0) break;
        const h = (vol / 255) * height * 0.9;
        const hue = 190 + (vol / 255) * 60;
        ctx.fillStyle = `hsl(${hue}, 100%, 60%)`;
        ctx.fillRect(x, centerY - h / 2, 2, h);
      }
    }
  };

  // INLINE VISUALIZER LOGIC
  const inlineCanvas = document.getElementById('inline-visualizer');
  let visualizerCtx = null;
  let visualizerAnimationFrame = null;
  let inlineWaveformHistory = [];


  // Mode Switcher Logic
  document.querySelectorAll('.vis-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.vis-btn').forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      visualizerMode = e.currentTarget.dataset.mode;
    });
  });

  if (inlineCanvas) {
    visualizerCtx = inlineCanvas.getContext('2d');

    const resizeVisualizer = () => {
      inlineCanvas.width = inlineCanvas.parentElement.clientWidth;
      inlineCanvas.height = inlineCanvas.parentElement.clientHeight;
    };

    window.addEventListener('resize', resizeVisualizer);
    resizeVisualizer();

    // Start loop
    drawInlineVisualizer();
  }

  function drawInlineVisualizer() {
    visualizerAnimationFrame = requestAnimationFrame(drawInlineVisualizer);

    if (!inlineCanvas || !visualizerCtx) return;

    const width = inlineCanvas.width;
    const height = inlineCanvas.height;
    const ctx = visualizerCtx;

    // Clear Canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, width, height);

    // Draw Grid
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x < width; x += 50) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    ctx.stroke();

    if (!analyser || (audioContext && audioContext.state === 'suspended')) {
      // Draw idle line
      ctx.strokeStyle = '#333';
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();
      return;
    }

    analyser.getByteFrequencyData(dataArray);

    if (visualizerMode === 'circular') {
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) / 4;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = '#333';
      ctx.stroke();

      for (let i = 0; i < dataArray.length; i++) {
        const barHeight = (dataArray[i] / 255) * 60;
        const angle = (i / dataArray.length) * 2 * Math.PI;

        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        const x2 = centerX + Math.cos(angle) * (radius + barHeight);
        const y2 = centerY + Math.sin(angle) * (radius + barHeight);

        ctx.strokeStyle = `hsl(${i / dataArray.length * 360}, 100%, 50%)`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    } else if (visualizerMode === 'shockwave') {
      // Bass detection
      let bass = 0;
      for (let i = 0; i < 10; i++) bass += dataArray[i];
      bass /= 10;

      const centerX = width / 2;
      const centerY = height / 2;
      const radius = (bass / 255) * (Math.min(width, height) / 2);

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.strokeStyle = `hsl(${bass}, 100%, 50%)`;
      ctx.lineWidth = 3;
      ctx.stroke();
    } else if (visualizerMode === 'spectrum') {
      // SPECTRUM MODE
      const barWidth = (width / dataArray.length) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < dataArray.length; i++) {
        barHeight = (dataArray[i] / 255) * height;

        const hue = i / dataArray.length * 360;
        ctx.fillStyle = 'hsl(' + hue + ', 100%, 50%)';
        ctx.fillRect(x, height - barHeight, barWidth, barHeight);

        x += barWidth + 1;
        if (x > width) break;
      }
    } else {
      // WAVEFORM MODE (Scrolling)

      // Calculate average volume
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
      let average = sum / dataArray.length;

      inlineWaveformHistory.push(average);
      if (inlineWaveformHistory.length > width / 2) inlineWaveformHistory.shift();

      const centerY = height / 2;
      const playheadX = width;

      for (let i = 0; i < inlineWaveformHistory.length; i++) {
        const vol = inlineWaveformHistory[inlineWaveformHistory.length - 1 - i];
        const x = playheadX - (i * 2);

        if (x < 0) break;

        const h = (vol / 255) * height * 0.8;
        const hue = 190 + (vol / 255) * 40;
        ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
        ctx.fillRect(x, centerY - h / 2, 2, h);
      }
    }
  }

});
