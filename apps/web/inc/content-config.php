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
        'hero_lead'     => 'Authentic Quality. Wir liefern den Soundtrack fr dein Leben direkt vom Bodensee.',
        'hero_cta_primary' => 'Listen Live',
        'hero_cta_secondary' => 'Unsere Services',
        'hero_caption'  => 'Live aus dem Studio Allgu/Bodensee',

        // USP
        'usp_title_1' => 'Authentic Quality',
        'usp_desc_1'  => 'Kein Bullshit. Professionelle Eventtechnik und DJing ohne Kompromisse.',
        'usp_title_2' => 'Pro Audio',
        'usp_desc_2'  => 'High-End Systeme fr maximalen Druck und absolute Klarheit.',
        'usp_title_3' => 'Live Vibe',
        'usp_desc_3'  => 'Interaktives Radio  Bestimme den Sound des Abends mit.',

        // Radio
        'radio_eyebrow' => '24/7 Stream',
        'radio_title'   => 'Live on Air',
        'radio_lead'    => 'Deep House, Tech House und elektronische Klassiker. Non-stop im Mix.',
        'radio_history_title' => 'Zuletzt gespielt',
        'radio_cta_request' => 'Wnsch dir was',

        // Services
        'services_eyebrow' => 'Engineering Services',
        'services_title'   => 'Was wir tun',
        
        'service_1_title' => 'Stage Management',
        'service_1_desc'  => 'Koordination hinter den Kulissen. Damit auf der Bhne alles glatt luft.',
        
        'service_2_title' => 'FOH & Licht Design',
        'service_2_desc'  => 'Perfekter Sound, perfekte Atmosphre. Wir setzen dein Event ins richtige Licht.',
        
        'service_3_title' => '4K Luftaufnahmen',
        'service_3_desc'  => 'Cinematische Drohnenaufnahmen fr einzigartige Perspektiven.',

        // About
        'about_eyebrow' => 'Die Mission',
        'about_title'   => 'Sound ist Energie.',
        'about_lead'    => 'Veranstaltungstechniker und DJs mit einer Obsession fr Perfektion.',
        'about_text'    => 'Was als Leidenschaft fr elektronische Musik begann, ist heute ein Standard fr professionelle Event-Technik. Wir glauben, dass Qualitt hrbar ist.',

        // Contact
        'contact_eyebrow' => 'Kontakt',
        'contact_title'   => 'Start a Project',
        'contact_lead'    => 'Planst du einen Club, ein Festival oder suchst du das perfekte System?',
        'contact_email'   => 'wolf@yourparty.tech',
        'contact_phone'   => '', 

        // Footer
        'footer_tagline'  => 'Wir machen Events legendr.',
        'footer_copyright' => ' ' . date('Y') . ' YourParty Tech. Authentic Quality.',
    ];
}

function yourparty_get_content($key)
{
    $defaults = yourparty_content_defaults();
    $default_value = $defaults[$key] ?? '';

    // Get from Customizer (with default fallback)
    return get_theme_mod("yourparty_content_{$key}", $default_value);
}
