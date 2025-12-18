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
        'hero_eyebrow' => 'DJ · Eventtechnik · Bodensee',
        'hero_headline' => 'YOURPARTY.TECH',
        'hero_lead' => 'Professionelle Event-Technik, DJ-Services und Sound am Bodensee. Persönlich. Leidenschaftlich. Zuverlässig.',
        'hero_cta_primary' => 'Anfrage starten',
        'hero_cta_secondary' => 'Live Stream',
        'hero_caption' => 'DJ · Beschallung · Lichttechnik',

        // USP Section
        'usp_title_1' => 'DJ & Musik',
        'usp_desc_1' => 'Erfahrener DJ für Hochzeiten, Firmenfeiern und private Events. Von House über Charts bis zu den Classics – immer passend zur Stimmung.',
        'usp_title_2' => 'Sound & Licht',
        'usp_desc_2' => 'Professionelle PA-Systeme und Lichtkonzepte für jede Location. Von der intimen Feier bis zum Open-Air.',
        'usp_title_3' => '24/7 Radio',
        'usp_desc_3' => 'Unser kuratierter Stream mit Deep House, Melodic Techno und relaxten Vibes – jederzeit verfügbar.',

        // Radio Section
        'radio_eyebrow' => 'LIVE RADIO',
        'radio_title' => 'YOURPARTY RADIO',
        'radio_lead' => 'Hand-picked Tracks aus der Tiefe des Sounds. Kein Mainstream, reiner Vibe.',
        'radio_history_title' => 'Zuletzt gespielt',
        'radio_cta_request' => 'Track Request',

        // About Section
        'about_eyebrow' => 'Über mich',
        'about_title' => 'Musik aus Leidenschaft',
        'about_lead' => 'Hey, ich bin Wolf – DJ und Eventtech aus der Bodenseeregion.',
        'about_text' => 'Was als Hobby mit einem kleinen Mischpult begann, ist heute mein Beruf und meine Berufung. Ich bringe die Technik und die Musik für dein Event – von der Hochzeit im Schloss bis zur Gartenparty mit Freunden. Persönliche Betreuung und ein Auge (und Ohr) für Details sind für mich selbstverständlich.',

        // Contact Section
        'contact_eyebrow' => 'Kontakt',
        'contact_title' => 'Dein Event, mein Sound',
        'contact_lead' => 'Du planst ein Event und suchst jemanden für DJ, Technik oder beides? Schreib mir!',
        'contact_email' => 'wolf@yourparty.tech',
        'contact_phone' => '',

        // Services Section
        'services_eyebrow' => 'Leistungen',
        'services_title' => 'Was ich anbiete',
        'service_1_title' => 'DJ für dein Event',
        'service_1_desc' => 'Von Hochzeiten über Geburtstage bis zu Firmenfeiern – ich liefere den perfekten Soundtrack für deinen besonderen Anlass.',
        'service_2_title' => 'Sound & PA',
        'service_2_desc' => 'Professionelle Beschallungstechnik für jede Größe. Sauberer, kraftvoller Sound für drinnen und draußen.',
        'service_3_title' => 'Licht & Ambiente',
        'service_3_desc' => 'Stimmungsvolles Lichtdesign, das dein Event visuell unterstreicht. Von dezent bis spektakulär.',

        // References Section
        'references_eyebrow' => 'Referenzen',
        'references_title' => 'Events & Projekte',
        'reference_1' => 'Hochzeiten am Bodensee',
        'reference_2' => 'Firmenfeiern & Jubiläen',
        'reference_3' => 'Private Partys',
        'reference_4' => 'Open-Air Events',
        'reference_5' => '24/7 Radio Stream',

        // Footer
        'footer_tagline' => 'YourParty Tech – Events mit Leidenschaft',
        'footer_copyright' => '© 2025 YourParty Tech. Wolfgang Prinz, Bodensee.',
    ];
}
