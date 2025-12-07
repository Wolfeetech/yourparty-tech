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
        'about_title' => 'Handwerk trifft Veranstaltungstechnik',
        'about_lead' => 'Wir sind ein  2-Mann-Team aus dem Bodenseeraum mit Expertise in Bühnenbau und Veranstaltungstechnik.',
        'about_text' => 'Unsere Stärke liegt in der Kombination aus handwerklichem Können und technischem Verständnis. Wir realisieren Bühnenbau-Projekte, entwickeln maßgeschneiderte Audio-Lösungen für private Musikzimmer, Proberäume, kleine Events und DJ-Setups. B2B und B2C.',

        // Contact Section
        'contact_eyebrow' => 'Kontakt',
        'contact_title' => 'Projekt besprechen?',
        'contact_lead' => 'Erzähl uns von deiner Idee – egal ob Bühnenbau, Proberaum-Akustik, DJ-Setup oder individuelles Stage-Design.',
        'contact_email' => 'hello@yourparty.tech',
        'contact_phone' => '+49 1515 5243164',

        // Services Section
        'services_eyebrow' => 'Services',
        'services_title' => 'Was wir umsetzen',
        'service_1_title' => 'Bühnenbau & Stage Construction',
        'service_1_desc' => 'Professioneller Bühnenbau für Events jeder Größe. Von mobilen Bühnen bis zu fest installierten Konstruktionen.',
        'service_2_title' => 'FOH & Lichttechnik',
        'service_2_desc' => 'Front-of-House Audio-Engineering und professionelle Lichttechnik für kleine bis mittlere Veranstaltungen. B2B Festival-Support.',
        'service_3_title' => 'Custom Audio Builds',
        'service_3_desc' => 'Individuelle Lautsprechersysteme und Akustik-Lösungen für Proberäume, DJ-Setups und private Räume. B2B & B2C.',

        // References Section
        'references_eyebrow' => 'Projekte',
        'references_title' => 'Was wir bisher realisiert haben',
        'reference_1' => 'Bühnenbau-Projekte',
        'reference_2' => 'Festival Support (FOH)',
        'reference_3' => 'Private DJ-Studios',
        'reference_4' => 'Proberaum-Akustik',
        'reference_5' => 'Event-Tech (lokal)',

        // Footer
        'footer_tagline' => 'YourParty Tech – Bühnenbau, Custom Audio & Event Solutions',
        'footer_copyright' => '© 2025 YourParty Tech. Stockenweiler 3, 88138 Hergensweiler.',
    ];
}
