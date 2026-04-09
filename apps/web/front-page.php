<?php
/**
 * Front page template for YourParty Tech.
 * DESIGN: IMMERSIVE RADIO (Premium/Club)
 * 
 * @package YourPartyTech
 */

get_header();

$stream_url = apply_filters('yourparty_stream_url', YOURPARTY_STREAM_URL);
?>

<main id="main" class="site-main immersive-mode">
    
    <!-- FULLSCREEN HERO / PLAYER -->
    <section id="hero-player" class="hero-fullscreen">
        
        <!-- BACKGROUND VISUALIZER -->
        <div class="vis-bg-container">
            <!-- ID must match app.js VisualizerController -->
            <canvas id="inline-visualizer"></canvas>
            <div class="vis-overlay-gradient"></div>
        </div>

        <div class="container hero-container">
            
            <!-- TOP BRANDING -->
            <div class="hero-branding" data-aos="fade-down">
                <h1 class="hero-logo">YOURPARTY<span class="highlight">RADIO</span></h1>
                <div class="live-indicator">
                    <span class="pulse-dot"></span> ON AIR
                </div>
                
                <!-- STATION SWITCHER -->
                <!-- STATION SWITCHER (DISABLED FOR SAFE MODE)
                <div class="station-switcher" role="tablist" aria-label="Select Radio Station">
                    <button class="station-btn active" data-station="1" role="tab" aria-selected="true" aria-controls="player-panel">
                        <span class="station-btn__icon"></span>
                        <span class="station-btn__label">Radio</span>
                    </button>
                    <button class="station-btn" data-station="2" role="tab" aria-selected="false" aria-controls="player-panel">
                        <span class="station-btn__icon"></span>
                        <span class="station-btn__label">Mixtapes</span>
                    </button>
                </div>
                -->
            </div>

            <!-- CENTER: THE GLASS PLAYER -->
            <div class="glass-player-wrapper" data-aos="zoom-in" data-aos-duration="1000">
                <div class="glass-player">
                    
                    <!-- Cover Art (Floating) -->
                    <div class="player-cover">
                        <img id="cover-art" src="https://placehold.co/600x600/10b981/ffffff?text=YourParty" alt="Cover" loading="eager" fetchpriority="high">
                        <div class="cover-glow"></div>
                    </div>

                    <!-- Track Info -->
                    <div class="player-info">
                        <!-- Dynamic Vibe Badge -->
                        <div id="vibe-badge-container" style="height: 24px; margin-bottom: 12px; display: flex; justify-content: center; align-items: center; gap: 8px;"></div>

                        <h2 id="track-title" class="track-title skeleton">Loading Station...</h2> 
                        <p id="track-artist" class="track-artist skeleton">Please wait</p>
                        
                        <!-- Rating Structure must match rating-module.js -->
                        <!-- Rating Structure must match rating-module.js (DISABLED FOR SAFE MODE)
                        <div class="rating-strip rating-container">
                            <div class="rating-stars" id="rating-stars" role="radiogroup" aria-label="Rate this track">
                                <button class="rating-star" data-value="1" aria-label="1 star"></button>
                                <button class="rating-star" data-value="2" aria-label="2 stars"></button>
                                <button class="rating-star" data-value="3" aria-label="3 stars"></button>
                                <button class="rating-star" data-value="4" aria-label="4 stars"></button>
                                <button class="rating-star" data-value="5" aria-label="5 stars"></button>
                            </div>
                            <span id="rating-average" class="rating-score rating-average" aria-label="Average Rating">--</span>
                        </div>
                        -->
                    </div>

                    <!-- Mood/Rating Actions - LARGER BUTTONS FOR VISIBILITY -->
                    <!-- Mood/Rating Actions - LARGER BUTTONS FOR VISIBILITY (DISABLED FOR SAFE MODE)
                    <div class="player-actions" style="margin: 25px 0; display: flex; gap: 20px; justify-content: center; position: relative; z-index: 9999; pointer-events: auto;">
                         <button id="like-button" class="btn-reaction btn-reaction--like" title="Gefllt mir" aria-label="Like this track">
                            <span class="btn-reaction__icon"></span>
                            <span class="btn-reaction__label">LIKE</span>
                         </button>
                         <button id="dislike-button" class="btn-reaction btn-reaction--dislike" title="Gefllt mir nicht" aria-label="Dislike this track">
                            <span class="btn-reaction__icon"></span>
                            <span class="btn-reaction__label">SKIP</span>
                         </button>
                    </div>
                    -->

                    <!-- Vibe Tag Trigger -->
                    <!-- Vibe Tag Trigger (DISABLED FOR SAFE MODE)
                    <div style="margin-top: 1rem; display: flex; justify-content: center;">
                        <button id="mood-tag-button" class="btn-glass-small" style="display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 20px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);">
                            <span style="font-size: 1.2em; line-height: 1;"></span>
                            <span style="text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; opacity: 0.8; font-weight: 600;">Vibe</span>
                        </button>
                    </div>
                    -->

                    <!-- Controls -->
                    <div class="player-controls">
                        <button id="play-toggle" class="mini-player__button" aria-label="<?php esc_attr_e('Stream starten', 'yourparty-tech'); ?>">
        <span class="icon-play" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </span>
        <span class="icon-pause" style="display:none;" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </span>
    </button>
                    </div>

                    <!-- Queue / Next Tracks -->
                    <div class="next-track-queue" aria-live="polite" style="margin-top: 20px; text-align: left; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                        <span class="label" style="display:block; margin-bottom: 5px; color: var(--neon-green); font-size: 0.7rem;">COMING UP</span>
                        <div id="queue-list" style="font-size: 0.85rem; color: #ccc;">
                            <div class="queue-item skeleton" style="margin-bottom: 4px;">--</div>
                            <div class="queue-item skeleton" style="opacity: 0.7;">--</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- BOTTOM: VIBE CONTROL DECK -->
            <!-- BOTTOM: VIBE CONTROL DECK (DISABLED FOR SAFE MODE)
            <div class="vibe-deck" data-aos="fade-up" style="display: none;">
                <div class="vibe-deck-glass">
                    <div class="deck-header">
                        <div class="deck-icon"></div>
                        <div class="deck-title-group">
                            <h3>STEER THE MUSIC</h3>
                            <p class="deck-subtitle">Your vote influences what plays next</p>
                        </div>
                    </div>
                    
                    <div class="live-voting-widget"></div>
                    
                    <div class="vibe-buttons-grid">
                        <button class="vibe-btn vibe-btn--energy" data-vote="energetic">
                            <span class="vibe-btn__icon"></span>
                            <span class="vibe-btn__label">ENERGY</span>
                            <span class="vibe-btn__hint">High tempo bangers</span>
                        </button>
                        <button class="vibe-btn vibe-btn--chill" data-vote="chill">
                            <span class="vibe-btn__icon"></span>
                            <span class="vibe-btn__label">CHILL</span>
                            <span class="vibe-btn__hint">Smooth & relaxed</span>
                        </button>
                        <button class="vibe-btn vibe-btn--groove" data-vote="groovy">
                            <span class="vibe-btn__icon"></span>
                            <span class="vibe-btn__label">GROOVE</span>
                            <span class="vibe-btn__hint">Funky rhythms</span>
                        </button>
                        <button class="vibe-btn vibe-btn--dark" data-vote="dark">
                            <span class="vibe-btn__icon"></span>
                            <span class="vibe-btn__label">DARK</span>
                            <span class="vibe-btn__hint">Deep & intense</span>
                        </button>
                    </div>
                    
                    <div id="vibe-feedback" class="vibe-feedback" aria-live="assertive"></div>
                    <div id="vibe-status" class="vibe-status" aria-live="polite">
                        <span class="status-dot"></span>
                        <span class="status-text">AUTO MODE</span>
                    </div>
                </div>
            </div>
            -->

        </div>
    </section>

    <!-- AUDIO ELEMENT REMOVED (Located in footer.php) -->

    <!-- SCROLL INDICATOR -->
    <div class="scroll-indicator" data-aos="fade-up" data-aos-delay="1000">
        <span class="mouse-icon"></span>
        <span class="text">DETAILS</span>
    </div>

        <!-- SECONDARY SECTIONS (Revealed on Scroll) -->
    <div id="more-content" class="content-below">
        <div class="container section-spacer">
             <!-- SERVICES / FEATURES -->
             <?php get_template_part('template-parts/sections/services'); ?>
        </div>
        
        <div class="container section-spacer">
             <!-- REFERENCES / TRACK RECORD -->
             <?php get_template_part('template-parts/sections/references'); ?>
        </div>

        <div class="container section-spacer">
             <!-- ABOUT -->
             <?php get_template_part('template-parts/sections/about'); ?>
        </div>

        <div class="container section-spacer">
             <!-- CONTACT -->
             <?php 
             $requests_url = apply_filters(
                 'yourparty_requests_url',
                 yourparty_public_url('/public/' . YOURPARTY_STATION_SLUG . '/embed-requests')
             );
             get_template_part('template-parts/sections/contact', null, ['requests_url' => $requests_url]); 
             ?>
        </div>
    </div>

</main>

<style>
/* CRITICAL INLINE CSS FOR HERO LAYOUT */
:root {
    --neon-green: #00ff88;
    --neon-blue: #00ccff;
    --glass-bg: rgba(20, 20, 20, 0.65);
    --glass-border: rgba(255, 255, 255, 0.1);
}

body { background: #000; margin: 0; overflow-x: hidden; font-family: 'Inter', sans-serif; color: #eee; }

/* Hero Fullscreen */
.hero-fullscreen {
    position: relative;
    min-height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
}

/* Scroll Indicator */
.scroll-indicator {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    opacity: 0.7;
    animation: bounce 2s infinite;
    cursor: pointer;
    z-index: 20;
}
.scroll-indicator .mouse-icon {
    width: 20px; height: 32px; border: 2px solid rgba(255,255,255,0.5); border-radius: 12px; position: relative;
}
.scroll-indicator .mouse-icon::before {
    content: ''; position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 4px; height: 4px; background: #fff; border-radius: 50%;
}
.scroll-indicator .text { font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; }

@keyframes bounce { 0%, 20%, 50%, 80%, 100% {transform: translateX(-50%) translateY(0);} 40% {transform: translateX(-50%) translateY(-10px);} 60% {transform: translateX(-50%) translateY(-5px);} }


/* Background Visualizer */
.vis-bg-container {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: 1;
}
#inline-visualizer { width: 100%; height: 100%; opacity: 0.4; }
.vis-overlay-gradient {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle at center, transparent 0%, #000 90%);
    pointer-events: none;
}

/* Container - Professional Spacing System */
.hero-container {
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 48px; /* 8px grid: 6 units */
    height: auto;
    min-height: 90vh;
    width: 100%;
    max-width: 1200px;
    padding: 80px 24px 80px 24px; /* 8px grid */
}

/* Branding - Refined Typography */
.hero-branding { 
    text-align: center; 
    margin-bottom: 0; 
    z-index: 20; 
    position: relative; 
}

.hero-logo { 
    font-size: 2.5rem; /* 40px - professional scale */
    font-weight: 800; 
    letter-spacing: -0.02em; 
    margin: 0; 
    color: #fff; 
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
    font-family: 'Inter', sans-serif;
    line-height: 1.1;
}

.hero-logo .highlight { 
    color: var(--neon-green); 
}

.live-indicator { 
    font-size: 0.75rem; /* 12px */
    letter-spacing: 0.2em; 
    color: var(--neon-green); 
    font-weight: 600; 
    margin-top: 12px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 8px;
}

.pulse-dot { 
    width: 6px; 
    height: 6px; 
    background: var(--neon-green); 
    border-radius: 50%; 
    box-shadow: 0 0 8px var(--neon-green); 
    animation: pulse 2s infinite; 
}

/* Glass Player - Balanced Proportions */
.glass-player-wrapper { 
    width: 100%; 
    max-width: 380px; /* Reduced from 500px */
    perspective: 1000px; 
}

.glass-player {
    background: var(--glass-bg);
    backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    border: 1px solid var(--glass-border);
    border-radius: 24px; /* Consistent with vibe deck */
    padding: 32px; /* 8px grid: 4 units */
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    position: relative;
    transition: transform 0.3s ease;
}

/* Album Art - Proportional to Player */
.player-cover {
    width: 200px; /* Reduced from 250px */
    height: 200px; 
    margin: 0 auto 24px; /* 8px grid: 3 units */
    position: relative;
}

.player-cover img {
    width: 100%; 
    height: 100%; 
    object-fit: cover; 
    border-radius: 16px; /* Slightly smaller radius */
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
    position: relative; 
    z-index: 2;
}

.cover-glow { 
    position: absolute; 
    top: 10%; 
    left: 10%; 
    width: 80%; 
    height: 80%; 
    background: var(--neon-green); 
    filter: blur(40px); 
    opacity: 0.3; 
    z-index: 1;
    animation: glow-breathe 4s infinite alternate;
}

/* Track Info - Professional Type Scale */
.track-title { 
    font-size: 1.5rem; /* 24px */
    margin: 0 0 8px 0; /* 8px grid: 1 unit */
    font-weight: 700; 
    letter-spacing: -0.01em; 
    line-height: 1.2; 
    color: #fff; 
}

.track-artist { 
    font-size: 1rem; /* 16px */
    color: rgba(255, 255, 255, 0.6); 
    margin: 0 0 24px 0; /* 8px grid: 3 units */
    font-weight: 500; 
}

/* Controls - 8px Grid System */
.play-fab {
    width: 64px; /* 8px grid: 8 units */
    height: 64px; 
    border-radius: 50%; 
    border: none;
    background: linear-gradient(135deg, var(--neon-green), #00ccaa);
    color: #000; 
    font-size: 24px; /* 8px grid: 3 units */
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(0,255,136,0.3);
    transition: all 0.2s; 
    display: flex; 
    align-items: center; 
    justify-content: center;
    margin: 0 auto 16px; /* 8px grid: 2 units */
    z-index: 100;
    position: relative;
}

.play-fab:hover { 
    transform: scale(1.05); 
    box-shadow: 0 12px 32px rgba(0,255,136,0.4); 
}

.btn-glass-small {
    background: rgba(255,255,255,0.08); 
    border: 1px solid rgba(255,255,255,0.15);
    color: #fff; 
    padding: 8px 16px; /* 8px grid */
    border-radius: 12px; 
    font-size: 0.75rem; /* 12px */
    cursor: pointer; 
    transition: all 0.2s; 
    font-weight: 600; 
    letter-spacing: 0.05em;
}

.btn-glass-small:hover { 
    background: rgba(255,255,255,0.15); 
    border-color: rgba(255,255,255,0.3); 
}

/* Reaction Buttons - Refined */
.btn-reaction {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 12px 24px; /* 8px grid */
    border-radius: 12px;
    border: 1.5px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.05);
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    z-index: 10000;
}

.btn-reaction__icon {
    font-size: 1.75rem; /* 28px - slightly smaller */
    line-height: 1;
}

.btn-reaction__label {
    font-size: 0.625rem; /* 10px */
    font-weight: 700;
    letter-spacing: 0.15em;
    color: rgba(255,255,255,0.7);
    text-transform: uppercase;
}

.btn-reaction--like {
    border-color: rgba(0, 255, 136, 0.3);
    background: rgba(0, 255, 136, 0.08);
}

.btn-reaction--like:hover {
    border-color: var(--neon-green);
    background: rgba(0, 255, 136, 0.2);
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0, 255, 136, 0.25);
}

.btn-reaction--like:active {
    transform: scale(0.98);
}

.btn-reaction--dislike:hover {
    border-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.12);
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.2);
}

.btn-reaction--dislike:active {
    transform: scale(0.98);
}

/* Vibe Deck - Premium Glassmorphism */
.vibe-deck { 
    width: 100%; 
    max-width: 700px; 
    margin-top: 20px;
}

.vibe-deck-glass {
    background: rgba(20, 20, 30, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.deck-header { 
    display: flex; 
    align-items: center; 
    gap: 15px; 
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.deck-icon {
    font-size: 2rem;
    line-height: 1;
    filter: drop-shadow(0 0 10px rgba(0, 255, 136, 0.3));
}

.deck-title-group {
    flex: 1;
}

.deck-header h3 { 
    font-size: 1.1rem; 
    color: #fff; 
    letter-spacing: 0.15em; 
    margin: 0 0 5px 0;
    font-weight: 800;
    text-transform: uppercase;
}

.deck-subtitle {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
    font-weight: 400;
}

.vibe-buttons-grid { 
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.vibe-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1.5px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    padding: 20px 16px;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    position: relative;
    overflow: hidden;
}

.vibe-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.05) 100%);
    opacity: 0;
    transition: opacity 0.3s;
}

.vibe-btn:hover::before {
    opacity: 1;
}

.vibe-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

.vibe-btn:active {
    transform: translateY(-2px);
}

.vibe-btn__icon {
    font-size: 2.5rem;
    line-height: 1;
    filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
}

.vibe-btn__label {
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.vibe-btn__hint {
    font-size: 0.65rem;
    color: rgba(255, 255, 255, 0.4);
    font-weight: 400;
    text-align: center;
}

/* Individual Button Themes */
.vibe-btn--energy:hover {
    border-color: #ff6b35;
    background: rgba(255, 107, 53, 0.15);
    box-shadow: 0 12px 30px rgba(255, 107, 53, 0.3);
}

.vibe-btn--chill:hover {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.15);
    box-shadow: 0 12px 30px rgba(78, 205, 196, 0.3);
}

.vibe-btn--groove:hover {
    border-color: #ff6bff;
    background: rgba(255, 107, 255, 0.15);
    box-shadow: 0 12px 30px rgba(255, 107, 255, 0.3);
}

.vibe-btn--dark:hover {
    border-color: #9b59b6;
    background: rgba(155, 89, 182, 0.15);
    box-shadow: 0 12px 30px rgba(155, 89, 182, 0.3);
}

.vibe-btn.selected {
    border-width: 2px;
}

.vibe-btn--energy.selected {
    border-color: #ff6b35;
    background: rgba(255, 107, 53, 0.2);
    box-shadow: 0 0 20px rgba(255, 107, 53, 0.4);
}

.vibe-btn--chill.selected {
    border-color: #4ecdc4;
    background: rgba(78, 205, 196, 0.2);
    box-shadow: 0 0 20px rgba(78, 205, 196, 0.4);
}

.vibe-btn--groove.selected {
    border-color: #ff6bff;
    background: rgba(255, 107, 255, 0.2);
    box-shadow: 0 0 20px rgba(255, 107, 255, 0.4);
}

.vibe-btn--dark.selected {
    border-color: #9b59b6;
    background: rgba(155, 89, 182, 0.2);
    box-shadow: 0 0 20px rgba(155, 89, 182, 0.4);
}

.vibe-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 0.7rem;
    color: var(--neon-green);
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 10px;
    background: rgba(0, 255, 136, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(0, 255, 136, 0.2);
}

.status-dot {
    width: 6px;
    height: 6px;
    background: var(--neon-green);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

.vibe-feedback {
    text-align: center;
    font-size: 0.8rem;
    padding: 10px;
    margin: 10px 0;
    border-radius: 8px;
    font-weight: 600;
}

.vibe-feedback.success {
    background: rgba(0, 255, 136, 0.1);
    color: var(--neon-green);
    border: 1px solid rgba(0, 255, 136, 0.3);
}

.vibe-feedback.warning {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
    border: 1px solid rgba(255, 193, 7, 0.3);
}

@keyframes glow-breathe { 0% { opacity: 0.3; transform: scale(0.9); } 100% { opacity: 0.6; transform: scale(1.1); } }

/* Next Track Preview */
.next-track-preview {
    margin-top: 15px;
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: #888;
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    white-space: nowrap;
    border: 1px solid rgba(255,255,255,0.05);
}
.next-track-preview .label {
    color: var(--neon-green);
    font-weight: bold;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
}

/* Rating Stars - Balanced Size */
.rating-strip { 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 12px; /* 8px grid: 1.5 units */
    margin-bottom: 16px; /* 8px grid: 2 units */
}

.rating-stars button { 
    background: none; 
    border: none; 
    color: #444; 
    font-size: 20px; /* Reduced from 24px */
    cursor: pointer; 
    transition: color 0.15s; 
    padding: 0 2px; 
}

.rating-stars button:hover, 
.rating-stars button.active { 
    color: #ffbb00; 
}

.rating-score { 
    font-size: 1rem; /* 16px */
    font-weight: 600; 
    color: #fff; 
}

/* Next Track Queue - Refined */
.next-track-queue {
    margin-top: 16px; /* 8px grid: 2 units */
    text-align: left; 
    padding: 12px; /* 8px grid: 1.5 units */
    background: rgba(0,0,0,0.2); 
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
}

.next-track-queue .label {
    display: block; 
    margin-bottom: 8px; /* 8px grid: 1 unit */
    color: var(--neon-green); 
    font-size: 0.625rem; /* 10px */
    font-weight: 700;
    letter-spacing: 0.15em;
}

.next-track-queue #queue-list {
    font-size: 0.875rem; /* 14px */
    color: rgba(255, 255, 255, 0.7);
}

.queue-item {
    margin-bottom: 4px;
}

/* Next Track Preview */
.next-track-preview {
    margin-top: 12px; /* 8px grid: 1.5 units */
    background: rgba(0,0,0,0.25);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.875rem; /* 14px */
    color: rgba(255, 255, 255, 0.6);
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    white-space: nowrap;
    border: 1px solid rgba(255,255,255,0.05);
}

.next-track-preview .label {
    color: var(--neon-green);
    font-weight: 600;
    font-size: 0.625rem; /* 10px */
    letter-spacing: 0.1em;
}

/* Content Below Styling */
.content-below {
    position: relative;
    z-index: 10;
    background: #050505;
    background: linear-gradient(to bottom, #000 0%, #0a0a0a 100%);
    padding-top: 50px;
}

.section-spacer { 
    padding: 40px 20px; 
    border-bottom: 1px solid rgba(255,255,255,0.05); 
}

/* Mobile Responsive */
@media(max-width: 600px) {
    .glass-player { padding: 20px; }
    .player-cover { width: 180px; height: 180px; }
    .track-title { font-size: 1.5rem; }
    .track-artist { font-size: 0.9rem; color: #ccc; }
    
    .vibe-deck-glass {
        padding: 20px;
    }
    
    .deck-header h3 {
        font-size: 0.9rem;
    }
    
    .deck-subtitle {
        font-size: 0.65rem;
    }
    
    .vibe-buttons-grid { 
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    
    .vibe-btn {
        padding: 16px 12px;
    }
    
    .vibe-btn__icon {
        font-size: 2rem;
    }
    
    .vibe-btn__label {
        font-size: 0.75rem;
    }
    
    .vibe-btn__hint {
        font-size: 0.6rem;
    }
    
    .hero-container { 
        padding-top: 100px; 
        padding-bottom: 120px;
        justify-content: flex-start;
        gap: 20px;
    } 
    
    .hero-logo { font-size: 2rem; }
    .live-indicator { font-size: 0.7rem; }
    
    .play-fab { width: 70px; height: 70px; font-size: 24px; }
}

/* ===== STATION SWITCHER ===== */
.station-switcher {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    padding: 4px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.station-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.25s ease;
}

.station-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.08);
}

.station-btn.active {
    background: rgba(0, 255, 136, 0.15);
    border-color: var(--neon-green);
    color: var(--neon-green);
    box-shadow: 0 0 12px rgba(0, 255, 136, 0.2);
}

.station-btn__icon {
    font-size: 1rem;
    line-height: 1;
}

.station-btn__label {
    text-transform: uppercase;
}

@media (max-width: 600px) {
    .station-switcher {
        margin-top: 12px;
    }
    
    .station-btn {
        padding: 6px 12px;
        font-size: 0.65rem;
    }
    
    .station-btn__icon {
        font-size: 0.9rem;
    }
}

/* === MOOD DIALOG STYLES MOVED TO assets/mood-dialog.css === */
</style>

<!-- MOOD DIALOG: Created dynamically by assets/mood-dialog.js -->
<!-- Do NOT add inline dialog HTML here - mood-dialog.js handles it -->

<!-- Inline script removed. Logic handled by assets/mood-dialog.js -->


<?php get_footer(); ?>
