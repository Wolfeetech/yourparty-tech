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
            </div>

            <!-- CENTER: THE GLASS PLAYER -->
            <div class="glass-player-wrapper" data-aos="zoom-in" data-aos-duration="1000">
                <div class="glass-player">
                    
                    <!-- Cover Art (Floating) -->
                    <div class="player-cover">
                        <img id="cover-art" src="https://placehold.co/600x600/10b981/ffffff?text=YourParty" alt="Cover" loading="eager">
                        <div class="cover-glow"></div>
                    </div>

                    <!-- Track Info -->
                    <div class="player-info">
                        <h2 id="track-title" class="track-title">STATION LOADING...</h2> <!-- Updated fallback -->
                        <p id="track-artist" class="track-artist">YourParty Tech</p>
                        
                        <!-- Rating Structure must match rating-module.js -->
                        <div class="rating-strip rating-container">
                            <div class="rating-stars" id="rating-stars" role="radiogroup">
                                <button class="rating-star" data-value="1">★</button>
                                <button class="rating-star" data-value="2">★</button>
                                <button class="rating-star" data-value="3">★</button>
                                <button class="rating-star" data-value="4">★</button>
                                <button class="rating-star" data-value="5">★</button>
                            </div>
                            <span id="rating-average" class="rating-score rating-average">--</span>
                        </div>
                    </div>

                    <!-- Mood/Rating Actions -->
                    <div class="player-actions" style="margin: 20px 0; display: flex; gap: 10px; justify-content: center; position: relative; z-index: 5;">
                         <button id="mood-tag-button" class="btn-glass-small" style="background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.3);" title="Set Vibe & Genre">
                            <span style="font-size: 1.2em; vertical-align: middle; margin-right: 5px;">🏷️</span> TAG VIBE
                         </button>
                    </div>

                    <!-- Controls -->
                    <div class="player-controls">
                        <button id="play-toggle" class="play-fab" aria-label="Play">
                            <span class="icon-play">
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                            </span>
                            <span class="icon-pause" style="display:none;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                            </span>
                        </button>
                    </div>

                    <!-- Next Track Preview (Marquee) -->
                    <div class="next-track-preview">
                        <span class="label">NEXT:</span>
                        <span id="next-track-marquee">--</span>
                    </div>
                </div>
            </div>

            <!-- BOTTOM: VIBE CONTROL DECK -->
            <div class="vibe-deck" data-aos="fade-up">
                <div class="deck-header">
                    <h3>CONTROL THE VIBE</h3>
                    <div class="deck-line"></div>
                    <!-- VOTE STATUS INDICATOR -->
                    <div id="vibe-status" style="font-size: 0.7rem; color: var(--neon-green); font-weight: bold; white-space: nowrap;">AUTO MODE</div>
                </div>
                <div class="vibe-buttons">
                    <button class="vibe-btn" data-vote="energetic" title="More Energy"><span class="emoji">🔥</span> <span class="lbl">ENERGY</span></button>
                    <button class="vibe-btn" data-vote="chill" title="Chill Out"><span class="emoji">🧊</span> <span class="lbl">CHILL</span></button>
                    <button class="vibe-btn" data-vote="groovy" title="Groove"><span class="emoji">🕺</span> <span class="lbl">GROOVE</span></button>
                    <button class="vibe-btn" data-vote="dark" title="Dark Mode"><span class="emoji">🌑</span> <span class="lbl">DARK</span></button>
                </div>
                <div id="vibe-feedback" class="vibe-feedback"></div>
            </div>

        </div>
    </section>

    <!-- HIDDEN AUDIO -->
    <audio id="radio-audio" crossorigin="anonymous" preload="none" style="display:none;">
        <source src="<?php echo esc_url($stream_url); ?>" type="audio/mpeg">
    </audio>

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
             <?php get_template_part('template-parts/sections/contact'); ?>
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
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
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

/* Container */
.hero-container {
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    height: 90vh; /* Keep it constrained so scroll indicator fits */
    width: 100%;
    max-width: 1200px;
    padding: 20px 20px 80px 20px; /* More bottom padding for scroll indicator */
}

/* Branding */
.hero-branding { text-align: center; margin-bottom: 20px; z-index: 20; position: relative; }
.hero-logo { 
    font-size: 3rem; font-weight: 800; letter-spacing: -0.05em; margin: 0; color: #fff; text-shadow: 0 0 30px rgba(255,255,255,0.2); 
    font-family: 'Outfit', sans-serif;
}
.hero-logo .highlight { color: var(--neon-green); }
.live-indicator { 
    font-size: 0.8rem; letter-spacing: 0.3em; color: var(--neon-green); font-weight: bold; margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.pulse-dot { width: 8px; height: 8px; background: var(--neon-green); border-radius: 50%; box-shadow: 0 0 10px var(--neon-green); animation: pulse 2s infinite; }

/* Glass Player (Centerpiece) */
.glass-player-wrapper { width: 100%; max-width: 500px; perspective: 1000px; margin-top: -20px; }
.glass-player {
    background: var(--glass-bg);
    backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    border: 1px solid var(--glass-border);
    border-radius: 30px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 30px 60px rgba(0,0,0,0.8);
    position: relative;
    transition: transform 0.3s ease;
}
/* Album Art */
.player-cover {
    width: 250px; height: 250px; margin: 0 auto 30px; position: relative;
}
.player-cover img {
    width: 100%; height: 100%; object-fit: cover; border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    position: relative; z-index: 2;
}
.cover-glow { 
    position: absolute; top: 10%; left: 10%; width: 80%; height: 80%; 
    background: var(--neon-green); filter: blur(50px); opacity: 0.4; z-index: 1;
    animation: glow-breathe 4s infinite alternate;
}

/* Info */
.track-title { font-size: 2rem; margin: 0; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; color: #fff; }
.track-artist { font-size: 1.1rem; color: #aaa; margin: 5px 0 20px; font-weight: 500; }

/* Controls */
.play-fab {
    width: 80px; height: 80px; border-radius: 50%; border: none;
    background: linear-gradient(135deg, var(--neon-green), #00ccaa);
    color: #000; font-size: 30px; cursor: pointer;
    box-shadow: 0 10px 30px rgba(0,255,136,0.3);
    transition: all 0.2s; display: flex; align-items: center; justify-content: center;
    margin: 0 auto 20px;
    z-index: 100;
    position: relative;
}
.play-fab:hover { transform: scale(1.1); box-shadow: 0 0 50px rgba(0,255,136,0.6); }

.btn-glass-small {
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
    color: #fff; padding: 8px 16px; border-radius: 20px; font-size: 0.75rem;
    cursor: pointer; transition: all 0.2s; font-weight: bold; letter-spacing: 0.05em;
}
.btn-glass-small:hover { background: rgba(255,255,255,0.2); border-color: #fff; }

/* Vibe Deck */
.vibe-deck { width: 100%; max-width: 600px; text-align: center; }
.deck-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
.deck-header h3 { font-size: 0.8rem; color: #666; letter-spacing: 0.2em; margin: 0; white-space: nowrap; }
.deck-line { width: 100%; height: 1px; background: rgba(255,255,255,0.1); }
.vibe-buttons { display: flex; justify-content: space-between; gap: 10px; }
.vibe-btn {
    flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    color: #fff; padding: 15px 0; border-radius: 12px; cursor: pointer; transition: all 0.2s;
    display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.vibe-btn:hover { background: rgba(255,255,255,0.1); transform: translateY(-3px); border-color: #fff; }
.vibe-btn .emoji { font-size: 1.5rem; }
.vibe-btn .lbl { font-size: 0.6rem; font-weight: bold; letter-spacing: 0.1em; opacity: 0.7; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@keyframes glow-breathe { 0% { opacity: 0.3; transform: scale(0.9); } 100% { opacity: 0.6; transform: scale(1.1); } }

/* Rating Stars */
.rating-strip { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
.rating-stars button { background: none; border: none; color: #444; font-size: 24px; cursor: pointer; transition: color 0.1s; padding: 0 2px; }
.rating-stars button:hover, .rating-stars button.active { color: #ffbb00; }
.rating-score { font-size: 1.2rem; font-weight: bold; color: #fff; }

/* Content Below Styling */
.content-below {
    position: relative;
    z-index: 10;
    background: #050505;
    background: linear-gradient(to bottom, #000 0%, #0a0a0a 100%);
    padding-top: 50px;
}
.section-spacer { padding: 40px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); }

/* Mobile */
@media(max-width: 600px) {
    .glass-player { padding: 20px; }
    .player-cover { width: 180px; height: 180px; }
    .track-title { font-size: 1.5rem; }
    .vibe-buttons { display: grid; grid-template-columns: 1fr 1fr; }
    .hero-container { padding-bottom: 100px; } 
}

/* === MOOD DIALOG / MODAL === */
.mood-dialog {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    z-index: 10000;
    display: none; align-items: center; justify-content: center;
}
.mood-dialog.active { display: flex; }

.mood-dialog-backdrop {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.8);
    backdrop-filter: blur(10px);
    z-index: 1;
}

.mood-dialog-content {
    position: relative; z-index: 10;
    background: rgba(20,20,20,0.9);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 50px rgba(0,0,0,0.8);
    border-radius: 20px;
    padding: 30px;
    width: 90%; max-width: 500px;
    text-align: center;
    color: #fff;
    animation: zoomIn 0.3s ease;
}

@keyframes zoomIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.mood-dialog h3 { font-size: 1.5rem; margin-bottom: 5px; }
.track-info { color: #888; margin-bottom: 20px; font-size: 0.9rem; }

.tag-section { margin-bottom: 20px; }
.tag-section h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--neon-green); margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }

.mood-grid, .genre-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px;
}

.mood-btn {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    padding: 10px; border-radius: 10px; cursor: pointer; color: #fff;
    transition: all 0.2s; display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.mood-btn:hover { background: rgba(255,255,255,0.1); transform: translateY(-2px); border-color: #fff; }
.mood-btn .emoji { font-size: 1.5rem; }
.mood-btn .label { font-size: 0.8rem; font-weight: bold; }

.genre-grid .mood-btn { padding: 8px; }

.status-msg { margin-top: 15px; font-weight: bold; min-height: 20px; }
.status-msg.success { color: #00ff88; }
.status-msg.error { color: #ff4444; }

.close-btn {
    position: absolute; top: 15px; right: 15px; background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer; opacity: 0.7;
}
.close-btn:hover { opacity: 1; color: var(--neon-green); }
</style>

<?php get_footer(); ?>
