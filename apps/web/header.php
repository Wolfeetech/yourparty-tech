<?php
/**
 * Theme header template.
 *
 * @package YourPartyTech
 */

?><!DOCTYPE html>
<html <?php language_attributes(); ?>>

<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php
    $yourparty_description = __(
        'YourParty Tech liefert Veranstaltungstechnik, DJ-Sets und Eventproduktionen – vom Clubfloor bis zur Konferenz, inklusive 24/7-Radiostream vom Bodensee.',
        'yourparty-tech'
    );
    $yourparty_url = home_url('/');
    $yourparty_title = __('YourParty Tech – Eventtechnik & DJ', 'yourparty-tech');
    $yourparty_og = trailingslashit(get_template_directory_uri()) . 'assets/og-default.png';
    ?>
    <meta name="description" content="<?php echo esc_attr($yourparty_description); ?>">
    <meta property="og:locale" content="de_DE">
    <meta property="og:type" content="website">
    <meta property="og:title" content="<?php echo esc_attr($yourparty_title); ?>">
    <meta property="og:description" content="<?php echo esc_attr($yourparty_description); ?>">
    <meta property="og:url" content="<?php echo esc_url($yourparty_url); ?>">
    <meta property="og:site_name" content="<?php echo esc_attr($yourparty_title); ?>">
    <meta property="og:image" content="<?php echo esc_url($yourparty_og); ?>">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="<?php echo esc_attr($yourparty_title); ?>">
    <meta name="twitter:description" content="<?php echo esc_attr($yourparty_description); ?>">
    <meta name="twitter:image" content="<?php echo esc_url($yourparty_og); ?>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <?php
    $yourparty_public = function_exists('yourparty_public_url') ? yourparty_public_url() : '';
    if ($yourparty_public):
        ?>
        <link rel="preconnect" href="<?php echo esc_url($yourparty_public); ?>" crossorigin>
        <link rel="dns-prefetch" href="<?php echo esc_url($yourparty_public); ?>">
    <?php endif; ?>
    <?php
    if (function_exists('has_site_icon') && !has_site_icon()):
        $yourparty_fallback_icon = 'data:image/svg+xml,' . rawurlencode('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" rx="3" ry="3" fill="#08363c"/><text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" font-size="9" fill="#ffffff">YP</text></svg>');
        ?>
        <link rel="icon" href="<?php echo esc_attr($yourparty_fallback_icon); ?>" sizes="any">
    <?php endif; ?>
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
    <?php wp_body_open(); ?>
    <div id="page" class="site">
        <header class="site-header">
            <div class="container">
                <div class="brand">
                    <span class="brand-glow"><?php esc_html_e('YourParty', 'yourparty-tech'); ?></span>
                    <span class="brand-sub"><?php esc_html_e('Eventtechnik & DJ', 'yourparty-tech'); ?></span>
                </div>
                <nav class="site-nav" aria-label="<?php esc_attr_e('Hauptnavigation', 'yourparty-tech'); ?>">
                    <?php $link_prefix = is_front_page() ? '' : home_url('/'); ?>
                    <a href="<?php echo esc_url($link_prefix . '#hero'); ?>">Start</a>
                    <a href="<?php echo esc_url($link_prefix . '#radio-live'); ?>">Radio</a>
                    <a href="<?php echo esc_url($link_prefix . '#services'); ?>">Tech</a>
                    <a href="<?php echo esc_url($link_prefix . '#references'); ?>">Social Proof</a>
                    <a href="<?php echo esc_url($link_prefix . '#about'); ?>">About</a>
                    <a href="<?php echo esc_url($link_prefix . '#kontakt'); ?>">Kontakt</a>
                </nav>
                <button class="nav-toggle" id="nav-toggle"
                    aria-label="<?php esc_attr_e('Navigation oeffnen', 'yourparty-tech'); ?>" aria-expanded="false">
                    &#9776;
                </button>
            </div>
        </header>

        <nav id="mobile-menu" class="mobile-menu"
            aria-label="<?php esc_attr_e('Mobile Navigation', 'yourparty-tech'); ?>">
            <a href="<?php echo esc_url($link_prefix . '#hero'); ?>">Start</a>
            <a href="<?php echo esc_url($link_prefix . '#radio-live'); ?>">Radio</a>
            <a href="<?php echo esc_url($link_prefix . '#services'); ?>">Tech</a>
            <a href="<?php echo esc_url($link_prefix . '#references'); ?>">Social Proof</a>
            <a href="<?php echo esc_url($link_prefix . '#about'); ?>">About</a>
            <a href="<?php echo esc_url($link_prefix . '#kontakt'); ?>">Kontakt</a>
        </nav>