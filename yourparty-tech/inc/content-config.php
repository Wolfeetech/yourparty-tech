<?php
/**
 * YourParty Tech - Content Configuration (Marketing SSOT)
 * 
 * Zentrale Verwaltung aller Texte und Inhalte.
 * Diese Datei ist die Single Source of Truth für alle Marketing-Texte.
 * 
 * @package YourPartyTech
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get default content for a specific key.
 *
 * @param string $key Content key (e.g., 'hero_eyebrow', 'hero_headline').
 * @return string Default content.
 */
function yourparty_get_default_content(string $key): string
{
    $defaults = yourparty_content_defaults();
    return $defaults[$key] ?? '';
}

/**
 * Get content from theme mod or fallback to default.
 *
 * @param string $key Content key.
 * @return string Content value.
 */
function yourparty_get_content(string $key): string
{
    $default = yourparty_get_default_content($key);
    return get_theme_mod("yourparty_content_{$key}", $default);
}

/**
 * Content defaults - Marketing SSOT.
 *
 * @return array<string, string> Content defaults.
 */
function yourparty_content_defaults(): array
{
    return [
        // Hero Section
        'hero_eyebrow' => 'Custom Audio · Bühnenbau · Bodensee',
        'hero_headline' => 'AUTHENTIC. QUALITY. SOUND.',
        'hero_lead' => 'Maßgeschneiderte Veranstaltungstechnik, Bühnenbau & Akustiklösungen für private und gewerbliche Räume.',
        'hero_cta_primary' => 'Anfrage stellen',
        'hero_cta_secondary' => 'Radio Stream',
        'hero_caption' => 'Planung · Sonderanfertigung · Realisation',

        // USP Section
        'usp_title_1' => 'B2B & B2C Custom Builds',
        'usp_desc_1' => 'Von Proberäumen über DJ-Setups bis zu kleinen Veranstaltungen – wir planen und realisieren individuelle Lösungen.',
        'usp_title_2' => 'Bühnenbau & Stage Design',
        'usp_desc_2' => 'Professioneller Bühnenbau und Sonderfertigungen für Bühnen-Designs. Handwerklich präzise, technisch durchdacht.',
        'usp_title_3' => '24/7 Radio Stream',
        'usp_desc_3' => 'Unser eigener Internet-Radiosender mit elektronischer Musik – zur Inspiration und als technische Referenz.',

        // Radio Section
        'radio_eyebrow' => '24/7 ELECTRONIC MUSIC',
        'radio_title' => 'ON AIR: YOURPARTY LIVE',
        'radio_lead' => 'Elektronische Musik rund um die Uhr. Kein Geschwätz, nur Tracks.',
        'radio_history_title' => 'Playlist History',
        'radio_cta_request' => 'Song wünschen',

        // About Section
        'about_eyebrow' => 'Über uns',
        'reference_3' => 'Private DJ-Studios',
        'reference_4' => 'Proberaum-Akustik',
        'reference_5' => 'Event-Tech (lokal)',

        // Footer
        'footer_tagline' => 'YourParty Tech – Bühnenbau, Custom Audio & Event Solutions',
        'footer_copyright' => '© 2025 YourParty Tech. Stockenweiler 3, 88138 Hergensweiler.',
    ];
}
