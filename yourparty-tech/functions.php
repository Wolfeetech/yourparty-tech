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

    // BUNDLED FRONTEND ASSETS
    $dist_path = get_template_directory_uri() . '/assets/dist/main.js';
    $dist_ver = file_exists(get_template_directory() . '/assets/dist/main.js') 
        ? filemtime(get_template_directory() . '/assets/dist/main.js') 
        : YOURPARTY_VERSION;

    // Load Main Application Bundle (Vite Build)
    wp_enqueue_script(
        'yourparty-app-bundle',
        $dist_path,
        [], // No dependencies, everything is bundled
        $dist_ver,
        true
    );

    // Load CSS (if any was extracted by Vite, usually style.css handles it, but check dist)
    if (file_exists(get_template_directory() . '/assets/dist/style.css')) {
         wp_enqueue_style(
            'yourparty-app-style',
            get_template_directory_uri() . '/assets/dist/style.css',
            [],
            $dist_ver
        );
    }
    
    // We still need the Mood Dialog CSS if not imported in JS (it's not imported in main.js yet)
    // Actually, I should import it in JS, but for now keep it separate to be safe
    wp_enqueue_style(
        'yourparty-mood-dialog',
        get_template_directory_uri() . '/assets/mood-dialog.css',
        [],
        YOURPARTY_VERSION
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
        // Point to WP REST API (Unified Gateway via inc/api.php)
        'restBase' => esc_url_raw(rest_url('yourparty/v1')), 
        'wpRestBase' => esc_url_raw(rest_url('yourparty/v1')),
        'publicBase' => esc_url_raw(yourparty_public_url()),
        'streamUrl' => esc_url_raw($stream_url),
        'publicSchedule' => esc_url_raw($schedule_url),
        'publicRequests' => esc_url_raw($requests_url),
        'stationSlug' => YOURPARTY_STATION_SLUG,
        'nonce' => $nonce
    ];

    wp_localize_script('yourparty-app-bundle', 'YourPartyConfig', $config);
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