<?php
/**
 * Social Proof / Google Reviews Section
 *
 * @package YourPartyTech
 */

// Google API Configuration (key must be set in WP options)
$google_api_key = get_option('yourparty_google_api_key', '');
$google_place_id = get_theme_mod('yourparty_google_places_id', '');

// Fetch reviews server-side
$reviews_data = false;
if (!empty($google_place_id) && !empty($google_api_key)) {
    $cache_key = 'yourparty_google_reviews_' . md5($google_place_id);
    $reviews_data = get_transient($cache_key);

    if (false === $reviews_data) {
        $api_url = sprintf(
            'https://maps.googleapis.com/maps/api/place/details/json?place_id=%s&fields=name,rating,user_ratings_total,reviews&key=%s',
            urlencode($google_place_id),
            urlencode($google_api_key)
        );

        $response = wp_remote_get($api_url);

        if (!is_wp_error($response)) {
            $body = wp_remote_retrieve_body($response);
            $data = json_decode($body, true);

            if (isset($data['result'])) {
                $reviews_data = $data['result'];
                // Cache for 1 hour
                set_transient($cache_key, $reviews_data, HOUR_IN_SECONDS);
            }
        }
    }
}
?>
<section id="references" class="section section--muted">
    <div class="container">

        <!-- Reference Image -->
        <div
            style="margin-bottom: 3rem; border-radius: 24px; overflow: hidden; height: 400px; position: relative; box-shadow: 0 20px 40px rgba(0,0,0,0.3);">
            <img src="<?php echo get_template_directory_uri(); ?>/assets/images/reference-event.jpg"
                alt="Event Atmosphere" style="width: 100%; height: 100%; object-fit: cover; object-position: center;">
            <div
                style="position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);">
            </div>
            <div
                style="position: absolute; bottom: 2rem; left: 2rem; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                <h3 style="margin: 0; font-size: 1.5rem;">Live Experience</h3>
                <p style="margin: 0; opacity: 0.9;">Echte Emotionen, perfekter Sound.</p>
            </div>
        </div>

        <div style="text-align: center; margin-bottom: 3rem;">
            <p class="section__eyebrow"
                style="color: var(--emerald); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">
                SOCIAL PROOF
            </p>
            <h3 style="font-size: 2rem; margin-top: 0.5rem;">
                Google Reviews
            </h3>
        </div>

        <?php if ($reviews_data && isset($reviews_data['reviews'])): ?>
            <!-- Google Reviews -->
            <div
                style="display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); max-width: 1000px; margin: 0 auto;">
                <?php
                $top_reviews = array_slice($reviews_data['reviews'], 0, 3);
                foreach ($top_reviews as $review):
                    $stars = str_repeat('★', $review['rating']) . str_repeat('☆', 5 - $review['rating']);
                    $initial = substr($review['author_name'], 0, 1);
                    $date = date('d.m.Y', $review['time']);
                    ?>
                    <article
                        style="background: var(--bg-card); padding: 2rem; border-radius: 12px; border: 1px solid var(--border);">
                        <div
                            style="display: flex; gap: 0.5rem; margin-bottom: 1rem; color: var(--emerald); font-size: 1.25rem;">
                            <?php echo $stars; ?>
                        </div>
                        <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem; color: var(--text);">
                            "<?php echo esc_html($review['text']); ?>"
                        </p>
                        <footer
                            style="display: flex; align-items: center; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                            <div
                                style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--emerald), var(--purple)); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">
                                <?php echo esc_html($initial); ?>
                            </div>
                            <div>
                                <div style="font-weight: 600;"><?php echo esc_html($review['author_name']); ?></div>
                                <div style="font-size: 0.875rem; color: var(--text-muted);"><?php echo esc_html($date); ?></div>
                            </div>
                        </footer>
                    </article>
                <?php endforeach; ?>
            </div>

            <!-- Overall Rating -->
            <div
                style="text-align: center; margin-top: 2rem; padding: 2rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); max-width: 600px; margin-left: auto; margin-right: auto;">
                <div style="font-size: 2.5rem; color: var(--emerald); margin-bottom: 0.5rem;">
                    <?php echo number_format($reviews_data['rating'], 1, ',', '.'); ?> ★
                </div>
                <div style="color: var(--text-muted);">
                    Basierend auf <?php echo number_format($reviews_data['user_ratings_total'], 0, ',', '.'); ?> Google
                    Bewertungen
                </div>
                <a href="https://search.google.com/local/writereview?placeid=<?php echo urlencode($google_place_id); ?>"
                    target="_blank" rel="noopener"
                    style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, var(--emerald), #1a6d41); color: white; border-radius: 24px; text-decoration: none; font-weight: 600;">
                    Bewertung schreiben
                </a>
            </div>
        <?php else: ?>
            <!-- Static Testimonials Fallback -->
            <div
                style="display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); max-width: 1000px; margin: 0 auto;">
                
                <!-- Testimonial 1 -->
                <article
                    style="background: var(--bg-card, rgba(20,20,20,0.8)); padding: 2rem; border-radius: 12px; border: 1px solid var(--border, rgba(255,255,255,0.1));">
                    <div
                        style="display: flex; gap: 0.5rem; margin-bottom: 1rem; color: var(--emerald, #00ff88); font-size: 1.25rem;">
                        ★★★★★
                    </div>
                    <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem; color: var(--text, #fff);">
                        "Wolf hat unsere Hochzeit mit perfektem Sound und toller Musikauswahl unvergesslich gemacht. Absolut empfehlenswert!"
                    </p>
                    <footer
                        style="display: flex; align-items: center; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border, rgba(255,255,255,0.1));">
                        <div
                            style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--emerald, #00ff88), #6366f1); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">
                            M
                        </div>
                        <div>
                            <div style="font-weight: 600;">Martina K.</div>
                            <div style="font-size: 0.875rem; color: var(--text-muted, #888);">Hochzeit 2024</div>
                        </div>
                    </footer>
                </article>

                <!-- Testimonial 2 -->
                <article
                    style="background: var(--bg-card, rgba(20,20,20,0.8)); padding: 2rem; border-radius: 12px; border: 1px solid var(--border, rgba(255,255,255,0.1));">
                    <div
                        style="display: flex; gap: 0.5rem; margin-bottom: 1rem; color: var(--emerald, #00ff88); font-size: 1.25rem;">
                        ★★★★★
                    </div>
                    <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem; color: var(--text, #fff);">
                        "Super professionelle Abwicklung, tolle Lichttechnik und die Musik war genau das, was wir wollten. Gerne wieder!"
                    </p>
                    <footer
                        style="display: flex; align-items: center; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border, rgba(255,255,255,0.1));">
                        <div
                            style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--emerald, #00ff88), #6366f1); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">
                            T
                        </div>
                        <div>
                            <div style="font-weight: 600;">Thomas S.</div>
                            <div style="font-size: 0.875rem; color: var(--text-muted, #888);">Firmenfeier 2024</div>
                        </div>
                    </footer>
                </article>

                <!-- Testimonial 3 -->
                <article
                    style="background: var(--bg-card, rgba(20,20,20,0.8)); padding: 2rem; border-radius: 12px; border: 1px solid var(--border, rgba(255,255,255,0.1));">
                    <div
                        style="display: flex; gap: 0.5rem; margin-bottom: 1rem; color: var(--emerald, #00ff88); font-size: 1.25rem;">
                        ★★★★★
                    </div>
                    <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem; color: var(--text, #fff);">
                        "Der Radio-Stream läuft bei uns im Büro permanent. Beste Musikauswahl, keine nervige Werbung. Top!"
                    </p>
                    <footer
                        style="display: flex; align-items: center; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border, rgba(255,255,255,0.1));">
                        <div
                            style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--emerald, #00ff88), #6366f1); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">
                            L
                        </div>
                        <div>
                            <div style="font-weight: 600;">Lisa M.</div>
                            <div style="font-size: 0.875rem; color: var(--text-muted, #888);">Radio-Hörer</div>
                        </div>
                    </footer>
                </article>
            </div>
            
            <!-- CTA for real reviews -->
            <div style="text-align: center; margin-top: 2rem;">
                <p style="color: var(--text-muted, #888); font-size: 0.9rem;">
                    Du warst bei einem meiner Events? Ich freue mich über dein Feedback!
                </p>
                <a href="mailto:wolf@yourparty.tech?subject=Feedback"
                    style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, var(--emerald, #00ff88), #1a6d41); color: white; border-radius: 24px; text-decoration: none; font-weight: 600; transition: transform 0.2s;">
                    Feedback senden
                </a>
            </div>
        <?php endif; ?>
    </div>
</section>
