<?php
/**
 * Front page template for YourParty Tech.
 *
 * @package YourPartyTech
 */

get_header();

$stream_url = apply_filters('yourparty_stream_url', YOURPARTY_STREAM_URL);
$schedule_url = apply_filters(
    'yourparty_schedule_url',
    yourparty_public_url('/public/' . YOURPARTY_STATION_SLUG . '/schedule')
);
$requests_url = apply_filters(
    'yourparty_requests_url',
    yourparty_public_url('/public/' . YOURPARTY_STATION_SLUG . '/embed-requests')
);
?>

<main id="main" class="site-main">
    <?php
    $hero_background = yourparty_get_hero_background_url();
    // Note: Background is now handled via CSS/Global styles, but we keep this if needed for inline overrides
    ?>
    <section id="hero" class="hero">
        <div class="container">
            <p class="hero__eyebrow" data-aos="fade-down"><?php echo esc_html(yourparty_get_content('hero_eyebrow')); ?>
            </p>
            <h1 class="hero__headline" data-aos="fade-up" data-aos-delay="100">
                <?php echo esc_html(yourparty_get_content('hero_headline')); ?>
            </h1>
            <p class="hero__lead" data-aos="fade-up" data-aos-delay="200">
                <?php echo esc_html(yourparty_get_content('hero_lead')); ?>
            </p>
            <div class="hero__actions" data-aos="fade-up" data-aos-delay="300">
                <a class="btn btn--primary"
                    href="#kontakt"><?php echo esc_html(yourparty_get_content('hero_cta_primary')); ?></a>
                <a class="btn btn--ghost"
                    href="#radio-live"><?php echo esc_html(yourparty_get_content('hero_cta_secondary')); ?></a>
            </div>
        </div>
    </section>

    <section id="usp" class="section section--muted">
        <div class="container">
            <div class="usp-grid">
                <article class="usp-card" data-aos="fade-up" data-aos-delay="100">
                    <h2><?php echo esc_html(yourparty_get_content('usp_title_1')); ?></h2>
                    <p><?php echo esc_html(yourparty_get_content('usp_desc_1')); ?></p>
                </article>
                <article class="usp-card" data-aos="fade-up" data-aos-delay="200">
                    <h2><?php echo esc_html(yourparty_get_content('usp_title_2')); ?></h2>
                    <p><?php echo esc_html(yourparty_get_content('usp_desc_2')); ?></p>
                </article>
                <article class="usp-card" data-aos="fade-up" data-aos-delay="300">
                    <h2><?php echo esc_html(yourparty_get_content('usp_title_3')); ?></h2>
                    <p><?php echo esc_html(yourparty_get_content('usp_desc_3')); ?></p>
                </article>
            </div>
        </div>
    </section>

    <section id="radio-live" class="section" aria-labelledby="radio-live-title">
        <div class="container">
            <header class="section__intro" style="text-align: center; margin-bottom: 3rem;" data-aos="fade-up">
                <p class="section__eyebrow"
                    style="color: var(--color-emerald); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    <?php echo esc_html(yourparty_get_content('radio_eyebrow')); ?>
                </p>
                <h2 id="radio-live-title" style="font-size: 2.5rem; margin-bottom: 1rem;">
                    <?php echo esc_html(yourparty_get_content('radio_title')); ?>
                </h2>
                <p style="color: var(--color-text-muted); max-width: 60ch; margin: 0 auto;">
                    <?php echo esc_html(yourparty_get_content('radio_lead')); ?>
                </p>
            </header>

            <div class="radio-card radio-card--integrated" aria-live="polite" data-aos="zoom-in"
                data-aos-duration="1000">
                <div class="radio-card__header">
                    <div class="radio-card__cover-wrapper">
                        <img id="cover-art" src="https://placehold.co/600x600/10b981/ffffff?text=YourParty+Radio"
                            alt="<?php esc_attr_e('Cover-Art des laufenden Tracks', 'yourparty-tech'); ?>"
                            loading="lazy">
                    </div>
                    <div class="radio-card__info">
                        <div class="radio-card__title-row">
                            <h3 id="track-title"><?php esc_html_e('Lade Titel...', 'yourparty-tech'); ?></h3>
                        </div>
                        <div class="radio-card__artist-row">
                            <p id="track-artist"><?php esc_html_e('Lade Künstler...', 'yourparty-tech'); ?></p>
                        </div>

                        <!-- NEW: Next Track Marquee -->
                        <div class="radio-card__next-row"
                            style="opacity: 0; transition: opacity 0.5s; margin-top: 0.5rem;">
                            <p id="next-track-marquee"
                                style="font-size: 0.85rem; color: var(--color-emerald); font-weight: 500;">
                                <!-- JS Injects Coming Up -->
                            </p>
                        </div>

                        <div class="radio-card__meta-row">
                            <div class="meta-left">
                                <span id="track-status"
                                    class="status-badge"><?php esc_html_e('LIVE', 'yourparty-tech'); ?></span>
                                <span class="listener-badge">
                                    <strong id="listener-count">--</strong>
                                    <?php esc_html_e('Zuhörer', 'yourparty-tech'); ?>
                                </span>
                            </div>
                            <div class="meta-center">
                                <div class="rating-container">
                                    <div class="rating-stars" id="rating-stars" role="radiogroup"
                                        aria-label="Bewertung">
                                        <button type="button" class="rating-star" data-value="1"
                                            aria-label="1 Stern">★</button>
                                        <button type="button" class="rating-star" data-value="2"
                                            aria-label="2 Sterne">★</button>
                                        <button type="button" class="rating-star" data-value="3"
                                            aria-label="3 Sterne">★</button>
                                        <button type="button" class="rating-star" data-value="4"
                                            aria-label="4 Sterne">★</button>
                                        <button type="button" class="rating-star" data-value="5"
                                            aria-label="5 Sterne">★</button>
                                    </div>
                                    <span id="rating-average" class="rating-average">--</span>
                                    <span id="rating-total" class="rating-total"></span>
                                </div>
                                <div id="current-mood-tags" class="current-mood-tags"></div>
                            </div>
                            <div class="meta-right">
                                <button id="mood-tag-button" class="mood-tag-btn" title="Mood Tagging">🏷️</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="radio-card__visualizer-container">
                    <canvas id="inline-visualizer"></canvas>
                    <div class="visualizer-controls"
                        style="position: absolute; top: 10px; right: 10px; display: flex; gap: 5px; z-index: 10;">
                        <button class="vis-btn active" data-mode="waveform" title="Waveform">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M2 12h3l2-9 4 18 4-18 2 9h3" />
                            </svg>
                        </button>
                        <button class="vis-btn" data-mode="spectrum" title="Spectrum">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M12 20V10M6 20V16M18 20V4" />
                            </svg>
                        </button>
                        <button class="vis-btn" data-mode="rgb_waveform" title="GFX Mode">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M4 4h16v16H4zM8 8v8M12 8v8M16 8v8" />
                            </svg>
                        </button>
                        <button id="visualizer-toggle" class="vis-btn" title="Fullscreen">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Immersive Fullscreen Overlay -->
                <div id="immersive-overlay" class="immersive-overlay">
                    <div class="immersive-bg"></div>

                    <!-- Close Button -->
                    <button id="exit-fullscreen" class="immersive-close-btn" title="Exit Fullscreen">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"></path>
                        </svg>
                    </button>

                    <!-- Main Visualizer Area -->
                    <div class="immersive-visualizer-container">
                        <canvas id="immersive-canvas"></canvas>
                    </div>

                    <!-- Track Info & Controls -->
                    <div class="immersive-footer">
                        <div class="immersive-track-row">
                            <img id="immersive-cover-img" src="" alt="Cover" class="immersive-cover">
                            <div class="immersive-meta">
                                <h1 id="immersive-title">Waiting for Signal...</h1>
                                <h2 id="immersive-artist">YourParty Radio</h2>

                                <!-- Immersive Rating System -->
                                <div class="rating-container immersive-rating">
                                    <div class="rating-stars" role="radiogroup" aria-label="Bewertung">
                                        <button type="button" class="rating-star" data-value="1">★</button>
                                        <button type="button" class="rating-star" data-value="2">★</button>
                                        <button type="button" class="rating-star" data-value="3">★</button>
                                        <button type="button" class="rating-star" data-value="4">★</button>
                                        <button type="button" class="rating-star" data-value="5">★</button>
                                    </div>
                                    <!-- Optional: Mood Tags Display -->
                                    <div id="immersive-mood-tags" class="current-mood-tags" style="margin-top: 10px;">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="immersive-controls-row">
                            <!-- Cloned Play Button via JS or separate instance -->
                            <button id="immersive-play-btn" class="immersive-play-btn">
                                <span class="icon-play">▶</span>
                                <span class="icon-pause" style="display:none;">⏸</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="radio-card__controls-row">
                    <button id="play-toggle" class="play-btn-large"
                        aria-label="<?php esc_attr_e('Stream starten', 'yourparty-tech'); ?>">
                        <span aria-hidden="true">▶</span>
                    </button>
                    <div id="vote-feedback" class="vote-feedback"></div>
                </div>
            </div>

            <div
                style="margin-top: 3rem; display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                <aside class="radio-history"
                    style="background: var(--color-glass); padding: 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border);">
                    <header
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="font-size: 1.25rem; margin: 0;">
                            <?php echo esc_html(yourparty_get_content('radio_history_title')); ?>
                        </h3>
                        <button class="btn btn--ghost btn--small" id="refresh-history"
                            style="font-size: 0.75rem; padding: 0.25rem 0.75rem;">
                            <?php esc_html_e('Aktualisieren', 'yourparty-tech'); ?>
                        </button>
                    </header>
                    <ul id="history-list" class="history-list" aria-live="polite"
                        style="list-style: none; padding: 0; margin: 0;">
                        <li class="history-item"
                            style="padding: 0.75rem 0; border-bottom: 1px solid var(--color-glass-border); color: var(--color-text-muted);">
                            Lade Verlauf...</li>
                    </ul>
                </aside>

                <div
                    style="display: flex; flex-direction: column; justify-content: center; align-items: flex-start; gap: 1rem; padding: 1.5rem; background: var(--color-glass); border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border);">
                    <h3 style="font-size: 1.25rem; margin: 0;">Musikwünsche?</h3>
                    <p style="color: var(--color-text-muted); margin: 0;">Wünsche dir deine Lieblingstracks direkt in
                        den Stream.</p>
                    <a class="btn btn--primary" href="<?php echo esc_url($requests_url); ?>" target="_blank"
                        rel="noopener">
                        <?php echo esc_html(yourparty_get_content('radio_cta_request')); ?>
                    </a>
                </div>
            </div>
        </div>

        <!-- MTV STYLE VOTE NEXT -->
        <div class="container" style="margin-top: 2rem;" data-aos="fade-up">
            <div class="vibe-vote-container">
                <header class="vibe-vote-header">
                    <h3>📢 VOTE NEXT VIBE</h3>
                    <p>Bestimme, was als nächstes läuft! (Community Vote)</p>
                </header>
                <div class="vibe-options">
                    <button class="vibe-btn" data-vote="energetic">
                        <span class="emoji">🔥</span>
                        <span class="label">ENERGETIC</span>
                    </button>
                    <button class="vibe-btn" data-vote="chill">
                        <span class="emoji">😎</span>
                        <span class="label">CHILL</span>
                    </button>
                    <button class="vibe-btn" data-vote="groovy">
                        <span class="emoji">🕺</span>
                        <span class="label">GROOVY</span>
                    </button>
                    <button class="vibe-btn" data-vote="dark">
                        <span class="emoji">🌑</span>
                        <span class="label">DARK</span>
                    </button>
                </div>
                <div id="vibe-feedback" class="vibe-feedback"></div>
            </div>
        </div>
    </section>



    <?php get_template_part('template-parts/sections/references'); ?>
    <?php get_template_part('template-parts/sections/services'); ?>
    <?php get_template_part('template-parts/sections/about'); ?>
    <?php
    get_template_part(
        'template-parts/sections/contact',
        null,
        [
            'requests_url' => $requests_url,
        ]
    );
    ?>
    <!-- Audio Source (Hidden) -->
    <audio id="radio-audio" crossorigin="anonymous" preload="none" style="display:none;">
        <source src="<?php echo esc_url(YOURPARTY_STREAM_URL); ?>" type="audio/mpeg">
    </audio>
</main>

<?php
get_footer();
