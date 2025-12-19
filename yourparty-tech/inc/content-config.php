<?php
/**
 * Content Configuration (SSOT)
 * Defines default content for the theme.
 */

if (!defined('ABSPATH')) {
    exit;
}

function yourparty_content_defaults(): array
{
    return [
        // Hero
        'hero_eyebrow' => 'Official Radio Stream',
        'hero_headline' => 'YOURPARTY RADIO',
        'hero_lead'     => 'Authentic Quality. Wir liefern den Soundtrack für dein Leben direkt vom Bodensee.',
        'hero_cta_primary' => 'Listen Live',
        'hero_cta_secondary' => 'Unsere Services',
        'hero_caption'  => 'Live aus dem Studio Allgäu/Bodensee',

        // USP
        'usp_title_1' => 'Authentic Quality',
        'usp_desc_1'  => 'Kein Bullshit. Wir liefern professionelle Eventtechnik und DJing ohne Kompromisse.',
        'usp_title_2' => 'Pro Audio',
        'usp_desc_2'  => 'Unsere Systeme sind auf maximalen Druck und Klarheit ausgelegt.',
        'usp_title_3' => 'Live Vibe',
        'usp_desc_3'  => 'Interaktives Radio - Bestimme den Sound des Abends mit.',

        // Radio
        'radio_eyebrow' => '24/7 Stream',
        'radio_title'   => 'Live on Air',
        'radio_lead'    => 'Deep House, Tech House und elektronische Klassiker. Non-stop gemixt.',
        'radio_history_title' => 'Zuletzt gespielt',
        'radio_cta_request' => 'Wünsch dir was',

        // Services
        'services_eyebrow' => 'Engineering Services',
        'services_title'   => 'Was wir tun',
        
        'service_1_title' => 'Stage Management',
        'service_1_desc'  => 'Wir koordinieren den Ablauf hinter den Kulissen, damit auf der Bühne alles glatt läuft.',
        
        'service_2_title' => 'Licht & Ton Design',
        'service_2_desc'  => 'Perfekter Sound und Atmosphäre. Wir setzen dein Event ins richtige Licht.',
        
        'service_3_title' => 'Drohnenaufnahmen',
        'service_3_desc'  => '4K Luftaufnahmen für einzigartige Perspektiven deines Events.',

        // About
        'about_eyebrow' => 'Die Mission',
        'about_title'   => 'Sound als physische Erfahrung',
        'about_lead'    => 'Wir sind Ingenieure und DJs mit einer Obsession für perfekten Klang.',
        'about_text'    => 'Was als Leidenschaft für elektronische Musik begann, ist heute eine Manufaktur für professionelle Audiotechnik. Wir glauben, dass Musik mehr ist als Schallwellen – sie ist Energie.',

        // Contact
        'contact_eyebrow' => 'Kontakt',
        'contact_title'   => 'Start a Project',
        'contact_lead'    => 'Planst du einen Club, ein Festival oder suchst du das perfekte System?',
        'contact_email'   => 'engineering@yourparty.tech',
        'contact_phone'   => '+49 151 12345678', // Placeholder

        // Footer
        'footer_tagline'  => 'Events mit Charakter & Herz am Bodensee.',
        'footer_copyright' => '© 2026 YourParty Tech. Alle Rechte vorbehalten.',
    ];
}

function yourparty_get_content($key)
{
    $defaults = yourparty_content_defaults();
    $default_value = $defaults[$key] ?? '';

    // Get from Customizer (with default fallback)
    return get_theme_mod("yourparty_content_{$key}", $default_value);
}
