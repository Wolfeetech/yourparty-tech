<?php
/**
 * YourParty Tech theme functions.
 */

if (!defined('YOURPARTY_VERSION')) {
    define('YOURPARTY_VERSION', '3.3.34');
}

if (!defined('YOURPARTY_AZURACAST_API_KEY')) {
    // SECURITY: Keys must be defined in wp-config.php
    // define('YOURPARTY_AZURACAST_API_KEY', 'Get-Key-From-Admin-Panel');
    if (defined('WP_DEBUG') && WP_DEBUG) {
        error_log('YOURPARTY SECURITY WARNING: AzuraCast API Key not defined in wp-config.php');
    }
}

if (!defined('YOURPARTY_DEFAULT_HERO_IMAGE')) {
    define(
        'YOURPARTY_DEFAULT_HERO_IMAGE',
        'https://images.unsplash.com/photo-1529665253569-6d01c0eaf7b6?auto=format&fit=crop&w=1920&q=80'
    );
}

if (!defined('YOURPARTY_AZURACAST_PUBLIC_URL')) {
    $public_base = 'https://radio.yourparty.tech';

    if (defined('YOURPARTY_AZURACAST_URL') && YOURPARTY_AZURACAST_URL) {
        $parsed = wp_parse_url(YOURPARTY_AZURACAST_URL);
        if (false !== $parsed && isset($parsed['host']) && !filter_var($parsed['host'], FILTER_VALIDATE_IP)) {
            $public_base = set_url_scheme(YOURPARTY_AZURACAST_URL, 'https');
        }
    }

    define('YOURPARTY_AZURACAST_PUBLIC_URL', $public_base);
}

if (!function_exists('yourparty_public_url')) {
    function yourparty_public_url(string $path = ''): string
    {
        $base = YOURPARTY_AZURACAST_PUBLIC_URL ?: 'https://radio.yourparty.tech';
        $base = untrailingslashit(set_url_scheme($base, 'https'));

        if ('' === $path) {
            return $base;
        }

        return $base . '/' . ltrim($path, '/');
    }
}

if (!defined('YOURPARTY_STATION_SLUG')) {
    define('YOURPARTY_STATION_SLUG', 'radio.yourparty');
}

if (!defined('YOURPARTY_STREAM_URL')) {
    $stream_url_option = get_option('yourparty_stream_url');
    define(
        'YOURPARTY_STREAM_URL',
        $stream_url_option ?: 'https://radio.yourparty.tech/listen/radio.yourparty/radio.mp3'
    );
}

if (!function_exists('yourparty_get_hero_background_url')) {
    function yourparty_get_hero_background_url(): string
    {
        $default = YOURPARTY_DEFAULT_HERO_IMAGE;
        $url = get_theme_mod('yourparty_hero_background', $default);

        if (!is_string($url) || '' === trim($url)) {
            return $default;
        }

        return esc_url_raw($url);
    }
}

if (file_exists(__DIR__ . '/inc/content-config.php')) {
    require_once __DIR__ . '/inc/content-config.php';
} else {
    // Fallback if file is missing (prevents fatal error)
    if (!function_exists('yourparty_get_content')) {
        function yourparty_get_content($key)
        {
            return '';
        }
    }
}
require_once __DIR__ . '/inc/customizer.php';
require_once __DIR__ . '/inc/api.php';
require_once __DIR__ . '/inc/admin-dashboard.php';

add_action('wp_enqueue_scripts', function () {
    // Fonts
    wp_enqueue_style(
        'yourparty-tech-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap',
        [],
        null
    );

    // Core Styles
    wp_enqueue_style('yourparty-tech-style', get_stylesheet_uri(), [], YOURPARTY_VERSION);

    // Core Modules (JS) - CORRECT PATHS
    wp_enqueue_script(
        'yourparty-stream-controller',
        get_template_directory_uri() . '/assets/js/stream-controller.js',
        [],
        YOURPARTY_VERSION,
        true
    );
    wp_enqueue_script(
        'yourparty-rating-module',
        get_template_directory_uri() . '/assets/js/rating-module.js',
        [],
        YOURPARTY_VERSION,
        true
    );
    wp_enqueue_script(
        'yourparty-mood-module',
        get_template_directory_uri() . '/assets/js/mood-module.js',
        [],
        YOURPARTY_VERSION,
        true
    );

    // Mood Dialog (Tag Window)
    wp_enqueue_style(
        'yourparty-mood-dialog',
        get_template_directory_uri() . '/assets/mood-dialog.css',
        [],
        time() // Cache bust
    );
    wp_enqueue_script(
        'yourparty-mood-dialog',
        get_template_directory_uri() . '/assets/mood-dialog.js',
        [],
        time(), // Cache bust
        true
    );

    // Visual System - NEW
    wp_enqueue_style(
        'yourparty-visual-player',
        get_template_directory_uri() . '/assets/css/visual-player.css',
        [],
        YOURPARTY_VERSION
    );
    wp_enqueue_script(
        'yourparty-visual-engine',
        get_template_directory_uri() . '/assets/js/visual-engine.js',
        ['yourparty-stream-controller'],
        YOURPARTY_VERSION,
        true
    );
    wp_enqueue_script(
        'yourparty-fullscreen-visual',
        get_template_directory_uri() . '/assets/js/fullscreen-visual-player.js',
        ['yourparty-visual-engine'],
        YOURPARTY_VERSION,
        true
    );

    // Main App (depends on modules)
    wp_enqueue_script(
        'yourparty-tech-app',
        get_template_directory_uri() . '/assets/js/app.js',
        ['yourparty-stream-controller', 'yourparty-rating-module', 'yourparty-mood-module'],
        time(), // FORCE CACHE BUST
        true
    );

    // Community Steering
    wp_enqueue_style(
        'yourparty-steering',
        get_template_directory_uri() . '/assets/css/community-steering.css',
        [],
        YOURPARTY_VERSION
    );
    wp_enqueue_script(
        'yourparty-steering',
        get_template_directory_uri() . '/assets/js/community-steering.js',
        ['yourparty-tech-app'],
        YOURPARTY_VERSION,
        true
    );

    // Config & URLs
    $stream_url = apply_filters('yourparty_stream_url', YOURPARTY_STREAM_URL);
    $schedule_url = apply_filters(
        'yourparty_schedule_url',
        yourparty_public_url('/public/' . YOURPARTY_STATION_SLUG . '/schedule')
    );
    $requests_url = apply_filters(
        'yourparty_requests_url',
        yourparty_public_url('/public/' . YOURPARTY_STATION_SLUG . '/embed-requests')
    );
    $nonce = wp_create_nonce('wp_rest');

    $config = [
        // Point to Python Backend API
        // We now have a ProxyPass in Apache on Container 207 (yourparty.tech)
        // mapping /api/ -> http://192.168.178.211:8000/
        // This solves HTTPS/CORS issues by serving it from the same domain.
        'restBase' => 'https://yourparty.tech/api', 
        'wpRestBase' => esc_url_raw(rest_url('yourparty/v1')), // Keep WP separate
        'publicBase' => esc_url_raw(yourparty_public_url()),
        'streamUrl' => esc_url_raw($stream_url),
        'publicSchedule' => esc_url_raw($schedule_url),
        'publicRequests' => esc_url_raw($requests_url),
        'stationSlug' => YOURPARTY_STATION_SLUG,
        'nonce' => $nonce
    ];

    wp_localize_script('yourparty-tech-app', 'YourPartyConfig', $config);
    wp_localize_script('yourparty-steering', 'yourpartySettings', ['nonce' => $nonce]);
});

add_action(
    'customize_register',
    function ($wp_customize) {
        $wp_customize->add_section(
            'yourparty_hero',
            [
                'title' => __('Hero-Bereich', 'yourparty-tech'),
                'description' => __('Passe das Hintergrundfoto der Startseite an.', 'yourparty-tech'),
                'priority' => 30,
            ]
        );

        $wp_customize->add_setting(
            'yourparty_hero_background',
            [
                'default' => YOURPARTY_DEFAULT_HERO_IMAGE,
                'sanitize_callback' => 'esc_url_raw',
            ]
        );

        $wp_customize->add_control(
            new WP_Customize_Image_Control(
                $wp_customize,
                'yourparty_hero_background_control',
                [
                    'label' => __('Hero-Bild', 'yourparty-tech'),
                    'section' => 'yourparty_hero',
                    'settings' => 'yourparty_hero_background',
                ]
            )
        );
    }
);

function yourparty_force_https_asset_src($src)
{
    if (is_admin() || !is_string($src) || '' === $src) {
        return $src;
    }

    foreach (['http://', 'https://', '//'] as $prefix) {
        if (0 === strpos($src, $prefix)) {
            return set_url_scheme($src, 'https');
        }
    }

    return $src;
}

add_filter('script_loader_src', 'yourparty_force_https_asset_src', 20);
add_filter('style_loader_src', 'yourparty_force_https_asset_src', 20);

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    register_nav_menus(
        [
            'primary' => __('Primary Menu', 'yourparty-tech'),
        ]
    );
});

add_filter(
    'language_attributes',
    function ($output) {
        if (false === stripos($output, 'lang=')) {
            $output .= ' lang="de"';
        }
        if (false === stripos($output, 'dir=')) {
            $output .= ' dir="ltr"';
        }
        return trim($output);
    },
    20
);

// Register Control Page Route
add_action('init', function () {
    add_rewrite_rule('^control/?$', 'index.php?yourparty_control=1', 'top');
});

add_filter('query_vars', function ($vars) {
    $vars[] = 'yourparty_control';
    return $vars;
});

add_action('template_include', function ($template) {
    if (get_query_var('yourparty_control')) {
        return get_template_directory() . '/templates/page-control.php';
    }
    return $template;
});