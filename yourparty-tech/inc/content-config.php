<?php
/**
 * YourParty Tech - Content Configuration (Marketing SSOT)
 * 
 * Zentrale Verwaltung aller Texte und Inhalte.
 * Diese Datei ist die Single Source of Truth fr alle Marketing-Texte.
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
        'hero_eyebrow' => 'Custom Audio  Bhnenbau  Bodensee',
        'hero_headline' => 'AUTHENTIC. QUALITY. SOUND.',
        'hero_lead' => 'Mageschneiderte Veranstaltungstechnik, Bhnenbau & Akustiklsungen fr private und gewerbliche Rume.',
        'hero_cta_primary' => 'Anfrage stellen',
        'hero_cta_secondary' => 'Radio Stream',
        'hero_caption' => 'Planung  Sonderanfertigung  Realisation',

        // USP Section
        'usp_title_1' => 'B2B & B2C Custom Builds',
        'usp_desc_1' => 'Von Proberumen ber DJ-Setups bis zu kleinen Veranstaltungen  wir planen und realisieren individuelle Lsungen.',
        'usp_title_2' => 'Bhnenbau & Stage Design',
        'usp_desc_2' => 'Professioneller Bhnenbau und Sonderfertigungen fr Bhnen-Designs. Handwerklich przise, technisch durchdacht.',
        'usp_title_3' => 'Smart Home & Installation',
        'usp_desc_3' => 'Netzwerktechnik, Multi-Room Audio und intelligente Steuerungssysteme fr private und gewerbliche Kunden.',

        // Services Section (Fixed)
        'services_eyebrow' => 'Leistungen',
        'services_title' => 'Technische Realisation',
        'service_1_title' => 'Bhnenbau & Rigging',
        'service_1_desc' => 'Sicherer Bau von Bhnen, Traversenkonstruktionen und Hngepunkten nach aktuellen SQ-Standards.',
        'service_2_title' => 'Event Production',
        'service_2_desc' => 'Vollumfngliche technische Planung und Durchfhrung von Events. Licht, Ton, Video  alles aus einer Hand.',
        'service_3_title' => 'Festinstallation',
        'service_3_desc' => 'Dauerhafte Installation von Licht- und Tontechnik in Clubs, Bars und Konferenzrumen.',

        // Radio Section
        'radio_eyebrow' => '24/7 ELECTRONIC MUSIC',
        'radio_title' => 'ON AIR: YOURPARTY LIVE',
        'radio_lead' => 'Elektronische Musik rund um die Uhr. Kein Geschwtz, nur Tracks.',
        'radio_history_title' => 'Playlist History',
        'radio_cta_request' => 'Song wnschen',

        // About Section
        'about_eyebrow' => 'ber uns',
        'reference_3' => 'Private DJ-Studios',
        'reference_4' => 'Proberaum-Akustik',
        'reference_5' => 'Event-Tech (lokal)',

        // Footer
        'footer_tagline' => 'YourParty Tech  Bhnenbau, Custom Audio & Event Solutions',
        'footer_copyright' => ' 2025 YourParty Tech. Stockenweiler 3, 88138 Hergensweiler.',
    ];
}
