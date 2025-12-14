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
        'hero_eyebrow' => 'Pro Audio · Event Engineering · Ravensburg',
        'hero_headline' => 'SONAY AUDIO ENGINEERING.',
        'hero_lead' => 'High-Fidelity Beschallungslösungen für anspruchsvolle Club-Installationen, Festivals und private Listening Rooms. Handgefertigt im Bodenseekreis.',
        'hero_cta_primary' => 'Engineering anfragen',
        'hero_cta_secondary' => 'Live Stream',
        'hero_caption' => 'Akustik · Systemdesign · Installation',

        // USP Section
        'usp_title_1' => 'Custom Sound Systems',
        'usp_desc_1' => 'Entwicklung und Fertigung von Hochleistungslautsprechern für elektronische Musik. Fokus auf Phasentreue und Impulsverhalten.',
        'usp_title_2' => 'Stage & Light Design',
        'usp_desc_2' => 'Ganzheitliche Konzepte für immersive Dancefloors. Wir bauen Bühnenbilder, die den Sound visuell greifbar machen.',
        'usp_title_3' => '24/7 Radio Stream',
        'usp_desc_3' => 'Unsere musikalische DNA. Ein kuratierter Stream mit Deep House, Melodic Techno und Minimal – ohne Moderation, purer Vibe.',

        // Radio Section
        'radio_eyebrow' => 'UNDERGROUND FREQUENCIES',
        'radio_title' => 'SIGNAL: LIVE',
        'radio_lead' => 'Hand-picked Tracks aus der Tiefe des Raums. Kein Mainstream, kein algorithmischer Noise.',
        'radio_history_title' => 'Zuletzt gespielt',
        'radio_cta_request' => 'Track Request',

        // About Section
        'about_eyebrow' => 'Die Mission',
        'about_title' => 'Sound als physische Erfahrung',
        'about_lead' => 'Wir sind Ingenieure und DJs mit einer Obsession für perfekten Klang.',
        'about_text' => 'Was als Leidenschaft für elektronische Musik begann, ist heute eine Manufaktur für professionelle Audiotechnik. Wir glauben, dass Musik mehr ist als Schallwellen – sie ist Energie. Unsere Systeme sind darauf ausgelegt, diese Energie verlustfrei auf den Dancefloor zu bringen.',

        // Contact Section
        'contact_eyebrow' => 'Kontakt',
        'contact_title' => 'Start a Project',
        'contact_lead' => 'Planst du einen Club, ein Festival oder suchst du das perfekte System für dein Studio?',
        'contact_email' => 'engineering@yourparty.tech',
        'contact_phone' => '+49 751 12345678',

        // Services Section
        'services_eyebrow' => 'Expertise',
        'services_title' => 'Engineering Services',
        'service_1_title' => 'System Calibration',
        'service_1_desc' => 'Einmessen von PA-Systemen mit modernster Messtechnik (Smaart/Systune) für linearen Frequenzgang und perfekte Phase.',
        'service_2_title' => 'Installation',
        'service_2_desc' => 'Festinstallation von Ton- und Lichttechnik in Clubs, Bars und Lounges. Kabelführung, Rigging und Sicherheit.',
        'service_3_title' => 'Custom Fabrication',
        'service_3_desc' => 'CNC-Fertigung von Lautsprechergehäusen, DJ-Booths und akustischen Elementen nach Maß.',

        // References Section
        'references_eyebrow' => 'Track Record',
        'references_title' => 'Selected Works',
        'reference_1' => 'Club "TechnoDrom" - Main Floor',
        'reference_2' => 'OpenAir Festival 2024 - FOH',
        'reference_3' => 'Private Listening Studio, Lindau',
        'reference_4' => 'Bar "Deep End" - System Design',
        'reference_5' => 'Mobile DJ Setup Custom Build',

        // Footer
        'footer_tagline' => 'YourParty Tech – Precision Audio Engineering',
        'footer_copyright' => '© 2025 YourParty Tech. Engineering made in Germany.',
    ];
}
