<?php
/**
 * Theme footer template.
 *
 * @package YourPartyTech
 */

?>
</div><!-- #page -->
<footer class="site-footer">
    <div class="container"
        style="display: grid; gap: 3rem; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); padding-bottom: 3rem; border-bottom: 1px solid var(--color-glass-border);">
        <div class="footer-brand">
            <span class="footer-eyebrow"
                style="color: var(--color-emerald); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.5rem;"><?php esc_html_e('YourParty Tech', 'yourparty-tech'); ?></span>
            <h2 style="font-size: 1.5rem; margin: 0 0 1rem;">
                <?php esc_html_e('Events mit Charakter & Herz am Bodensee', 'yourparty-tech'); ?>
            </h2>
            <p style="color: var(--color-text-muted);">
                <?php esc_html_e('Veranstaltungstechnik, Musik und knstlerische Leitung  von Clubs bis Festivals, vom Bodensee bis international.', 'yourparty-tech'); ?>
            </p>
        </div>
        <div class="footer-links">
            <h3 style="font-size: 1.1rem; margin-bottom: 1rem;"><?php esc_html_e('Links', 'yourparty-tech'); ?></h3>
            <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem;">
                <li><a href="<?php echo esc_url(home_url('/impressum/')); ?>"
                        style="color: var(--color-text-muted);"><?php esc_html_e('Impressum', 'yourparty-tech'); ?></a>
                </li>
                <li><a href="<?php echo esc_url(home_url('/datenschutz/')); ?>"
                        style="color: var(--color-text-muted);"><?php esc_html_e('Datenschutz', 'yourparty-tech'); ?></a>
                </li>
                <li><a href="<?php echo esc_url(home_url('/agb/')); ?>"
                        style="color: var(--color-text-muted);"><?php esc_html_e('AVB', 'yourparty-tech'); ?></a></li>
                <li><a href="<?php echo esc_url((is_front_page() ? '' : home_url('/')) . '#kontakt'); ?>"
                        style="color: var(--color-text-muted);"><?php esc_html_e('Kontakt', 'yourparty-tech'); ?></a>
                </li>
            </ul>
        </div>
        <div class="footer-social">
            <h3 style="font-size: 1.1rem; margin-bottom: 1rem;"><?php esc_html_e('Social', 'yourparty-tech'); ?></h3>
            <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem;">
                <li><a href="#" aria-label="<?php esc_attr_e('Instagram ffnen', 'yourparty-tech'); ?>"
                        style="color: var(--color-text-muted);">Instagram</a></li>
                <li><a href="#" aria-label="<?php esc_attr_e('YouTube ffnen', 'yourparty-tech'); ?>"
                        style="color: var(--color-text-muted);">YouTube</a></li>
                <li><a href="#" aria-label="<?php esc_attr_e('Discord ffnen', 'yourparty-tech'); ?>"
                        style="color: var(--color-text-muted);">Discord</a></li>
            </ul>
        </div>
    </div>
    <div class="site-footer__bottom"
        style="padding-top: 2rem; text-align: center; color: var(--color-text-muted); font-size: 0.875rem;">
        <div class="container" style="display: flex; flex-direction: column; gap: 1rem; align-items: center;">
            <p class="site-footer__copyright" style="margin: 0;">
                &copy; <?php echo date('Y'); ?> YourParty Tech.
                <?php esc_html_e('Alle Rechte vorbehalten.', 'yourparty-tech'); ?>
            </p>
            <div class="site-footer__player">
                <audio id="radio-player" preload="none" crossorigin="anonymous">
                    <source src="<?php echo esc_url(apply_filters('yourparty_stream_url', YOURPARTY_STREAM_URL)); ?>"
                        type="audio/mpeg">
                    <?php esc_html_e('Dein Browser untersttzt keine HTML5 Audio-Wiedergabe.', 'yourparty-tech'); ?>
                </audio>
            </div>
            <nav class="site-footer__legal" style="display: flex; gap: 1.5rem;">
                <a
                    href="<?php echo esc_url(home_url('/impressum/')); ?>"><?php esc_html_e('Impressum', 'yourparty-tech'); ?></a>
                <a
                    href="<?php echo esc_url(home_url('/datenschutzerklaerung/')); ?>"><?php esc_html_e('Datenschutz', 'yourparty-tech'); ?></a>
            </nav>
        </div>
    </div>
</footer>
<div id="mini-player" class="mini-player" aria-live="polite" style="display: none;">
    <button id="mini-play-toggle" class="mini-player__button" aria-label="<?php esc_attr_e('Stream starten', 'yourparty-tech'); ?>">
        <span class="icon-play" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        </span>
        <span class="icon-pause" style="display:none;" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </span>
    </button>
    <div class="mini-player__meta">
        <span id="mini-track-title"
            style="display: block; font-weight: 600;"><?php esc_html_e('YourParty Radio', 'yourparty-tech'); ?></span>
        <small id="mini-track-artist"
            style="color: var(--color-text-muted);"><?php esc_html_e('Live Stream', 'yourparty-tech'); ?></small>
    </div>
</div>

<div id="page-modal" class="modal-overlay" aria-hidden="true">
    <div class="modal-content">
        <button class="modal-close" aria-label="Schlieen">&times;</button>
        <div id="modal-body"></div>
    </div>
</div>

<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function () {
        AOS.init({
            duration: 800,
            once: true,
            offset: 50
        });
    });
</script>
</script>

<div id="shoutout-dialog" class="shoutout-dialog" aria-hidden="true">
    <div class="shoutout-content">
        <button id="close-shoutout-btn" class="close-btn">&times;</button>
        <h3><?php esc_html_e('Send Shoutout', 'yourparty-tech'); ?></h3>
        <p class="shoutout-desc"><?php esc_html_e('Schick eine Nachricht direkt ins Studio!', 'yourparty-tech'); ?></p>
        <form id="shoutout-form">
            <input type="text" name="sender" placeholder="<?php esc_attr_e('Dein Name (Optional)', 'yourparty-tech'); ?>" maxlength="30">
            <textarea name="message" placeholder="<?php esc_attr_e('Deine Nachricht...', 'yourparty-tech'); ?>" required maxlength="280"></textarea>
            <button type="submit" class="button-primary"><?php esc_html_e('Absenden', 'yourparty-tech'); ?></button>
            <div id="shoutout-feedback" class="shoutout-feedback" style="display:none;"></div>
        </form>
    </div>
</div>

<?php wp_footer(); ?>
</body>

</html>