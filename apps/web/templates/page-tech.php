<?php
/**
 * Template for the /tech page (Services/Features).
 *
 * @package YourPartyTech
 */

get_header();
?>

<main id="main" class="site-main">
    <div class="page-content" style="padding-top: 100px;"> <!-- Padding for fixed header -->
        <?php get_template_part('template-parts/sections/services'); ?>
    </div>
</main>

<?php
get_footer();
