<?php

/**
 * About Section Template Part
 *
 * @package YourPartyTech
 */
?>
<section id="about" class="section">
    <div class="container">
        <div class="about-grid"
            style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 4rem; align-items: center;">
            <div class="about-content">
                <p class="section__eyebrow"
                    style="color: var(--color-emerald); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">
                    <?php echo esc_html(yourparty_get_content('about_eyebrow')); ?>
                </p>
                <h2 style="font-size: clamp(2rem, 4vw, 3rem); margin-bottom: 1.5rem; line-height: 1.1;">
                    <?php echo esc_html(yourparty_get_content('about_title')); ?>
                </h2>
                <p class="lead" style="font-size: 1.25rem; color: var(--color-text-muted); margin-bottom: 2rem;">
                    <?php echo esc_html(yourparty_get_content('about_lead')); ?>
                </p>
                <p style="margin-bottom: 2rem; line-height: 1.8;">
                    <?php echo esc_html(yourparty_get_content('about_text')); ?>
                </p>

                <div class="about-values" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="color: var(--color-emerald); font-size: 1.25rem;">✓</span>
                        <span>Pro Eventtechnik</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="color: var(--color-emerald); font-size: 1.25rem;">✓</span>
                        <span>Erfahrene DJs</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="color: var(--color-emerald); font-size: 1.25rem;">✓</span>
                        <span>Lichtkonzepte</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="color: var(--color-emerald); font-size: 1.25rem;">✓</span>
                        <span>Planung</span>
                    </div>
                </div>
            </div>

            <div class="about-image" style="position: relative;">
                <div
                    style="border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.3); transform: rotate(2deg);">
                    <img src="<?php echo get_template_directory_uri(); ?>/assets/images/about-console.jpg"
                        alt="Mixing Console" style="width: 100%; height: auto; display: block;">
                </div>
                <!-- Decorative Elements -->
                <div
                    style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: var(--gradient-primary); filter: blur(40px); opacity: 0.4; border-radius: 50%; z-index: -1;">
                </div>

                <!-- Stats Overlay -->
                <div
                    style="position: absolute; bottom: -20px; left: -20px; background: var(--color-glass); padding: 1.5rem; border-radius: 16px; border: 1px solid var(--color-glass-border); backdrop-filter: blur(10px);">
                    <div style="font-weight: 700; font-size: 1.5rem; color: var(--color-emerald);">100%</div>
                    <div style="font-size: 0.875rem; color: var(--color-text-muted);">Passion & Quality</div>
                </div>
            </div>
        </div>
    </div>
</section>