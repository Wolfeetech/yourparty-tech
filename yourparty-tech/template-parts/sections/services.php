<?php
/**
 * Services Section Template Part
 *
 * @package YourPartyTech
 */
?>
<section id="services" class="section">
    <div class="container">
        <div style="text-align: center; margin-bottom: 4rem;">
            <p class="section__eyebrow"
                style="color: var(--color-emerald); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">
                <?php echo esc_html(yourparty_get_content('services_eyebrow')); ?>
            </p>
            <h2 style="font-size: clamp(2rem, 4vw, 3rem); margin-top: 0.5rem;">
                <?php echo esc_html(yourparty_get_content('services_title')); ?>
            </h2>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;">

            <!-- Service 1 -->
            <div style="background: var(--color-glass); padding: 2rem; border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border); transition: transform 0.3s;"
                onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; height: 200px;">
                    <img src="<?php echo get_template_directory_uri(); ?>/assets/images/service-stage.jpg"
                        alt="Bühnenbau" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <h3 style="margin-top: 0; font-size: 1.5rem;">
                    <?php echo esc_html(yourparty_get_content('service_1_title')); ?>
                </h3>
                <p style="color: var(--color-text-muted);">
                    <?php echo esc_html(yourparty_get_content('service_1_desc')); ?>
                </p>
            </div>

            <!-- Service 2 -->
            <div style="background: var(--color-glass); padding: 2rem; border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border); transition: transform 0.3s;"
                onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; height: 200px;">
                    <img src="<?php echo get_template_directory_uri(); ?>/assets/images/reference-event.jpg"
                        alt="FOH & Licht" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <h3 style="margin-top: 0; font-size: 1.5rem;">
                    <?php echo esc_html(yourparty_get_content('service_2_title')); ?>
                </h3>
                <p style="color: var(--color-text-muted);">
                    <?php echo esc_html(yourparty_get_content('service_2_desc')); ?>
                </p>
            </div>

            <!-- Service 3 -->
            <div style="background: var(--color-glass); padding: 2rem; border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border); transition: transform 0.3s;"
                onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; height: 200px;">
                    <img src="<?php echo get_template_directory_uri(); ?>/assets/images/service-audio.jpg"
                        alt="Custom Audio" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <h3 style="margin-top: 0; font-size: 1.5rem;">
                    <?php echo esc_html(yourparty_get_content('service_3_title')); ?>
                </h3>
                <p style="color: var(--color-text-muted);">
                    <?php echo esc_html(yourparty_get_content('service_3_desc')); ?>
                </p>
            </div>

        </div>
    </div>
</section>