<?php
/**
 * Template Name: Legal Page (Rechtstexte)
 *
 * @package YourPartyTech
 */

get_header();
?>

<main id="main" class="site-main">
    <section class="section">
        <div class="container">
            <header class="page-header" style="text-align: center; margin-bottom: 4rem;">
                <h1 class="page-title"
                    style="font-size: clamp(2.5rem, 5vw, 4rem); background: linear-gradient(to right, #fff, #cbd5e1); -webkit-background-clip: text; background-clip: text; color: transparent;">
                    <?php the_title(); ?>
                </h1>
            </header>

            <div class="page-content"
                style="max-width: 800px; margin: 0 auto; background: var(--color-glass); padding: 3rem; border-radius: var(--radius-lg); border: 1px solid var(--color-glass-border);">
                <?php
                while (have_posts()):
                    the_post();
                    the_content();
                endwhile;
                ?>
            </div>
        </div>
    </section>
</main>

<?php
get_footer();
