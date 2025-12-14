<?php
/**
 * Contact Section Template Part
 *
 * @package YourPartyTech
 */

$requests_url = $args['requests_url'] ?? '#';
?>
<section id="kontakt" class="section section--dark">
    <div class="container">
        <div class="contact-grid">
            <div class="contact-form">
                <header>
                    <p class="section__eyebrow"><?php echo esc_html(yourparty_get_content('contact_eyebrow')); ?></p>
                    <h2><?php echo esc_html(yourparty_get_content('contact_title')); ?></h2>
                    <p><?php echo esc_html(yourparty_get_content('contact_lead')); ?></p>
                </header>

                <form action="#" method="post" class="form-grid" id="contact-form">
                    <!-- Honeypot for Spam Bots -->
                    <div style="display:none; visibility:hidden;">
                        <input type="text" name="_honeypot" value="" tabindex="-1" autocomplete="off">
                    </div>

                    <div class="form-row form-row--inline">
                        <div class="form-field">
                            <label for="name" class="sr-only">Name</label>
                            <input type="text" id="name" name="name" placeholder="Dein Name" required>
                        </div>
                        <div class="form-field">
                            <label for="email" class="sr-only">E-Mail</label>
                            <input type="email" id="email" name="email" placeholder="Deine E-Mail" required>
                        </div>
                    </div>
                    <div class="form-field">
                        <label for="message" class="sr-only">Nachricht</label>
                        <textarea id="message" name="message" placeholder="Erzähl uns von deinem Event..."
                            required></textarea>
                    </div>
                    
                    <div id="contact-status" class="form-status" role="status" aria-live="polite"></div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn--primary" id="contact-submit">Nachricht senden</button>
                    </div>
                    <p class="form-privacy">
                        Mit dem Absenden stimmst du der <a
                            href="<?php echo esc_url(home_url('/datenschutz')); ?>">Datenschutzerklärung</a> zu.
                    </p>
                </form>
            </div>

            <div class="contact-details">
                <div class="contact-card">
                    <h3>Kontakt</h3>
                    <p><strong>E-Mail:</strong> <a
                            href="mailto:<?php echo esc_attr(yourparty_get_content('contact_email')); ?>"><?php echo esc_html(yourparty_get_content('contact_email')); ?></a>
                    </p>
                    <p><strong>Telefon:</strong> <a
                            href="tel:<?php echo esc_attr(str_replace(' ', '', yourparty_get_content('contact_phone'))); ?>"><?php echo esc_html(yourparty_get_content('contact_phone')); ?></a>
                    </p>
                </div>

                <div class="contact-card">
                    <h3>Musikwünsche?</h3>
                    <p>Du willst den Sound mitbestimmen? Schick uns deine Wünsche direkt ins Studio.</p>
                    <a href="<?php echo esc_url($requests_url); ?>" class="btn btn--ghost btn--small"
                        target="_blank">Zum Wunsch-Formular</a>
                </div>

                <div class="contact-card">
                    <h3>Social Media</h3>
                    <ul class="social-links">
                        <li><a href="#">Instagram</a></li>
                        <li><a href="#">SoundCloud</a></li>
                        <li><a href="#">LinkedIn</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</section>