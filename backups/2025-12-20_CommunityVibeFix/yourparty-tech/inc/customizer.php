<?php
/**
 * YourParty Tech - WordPress Customizer Integration
 * 
 * Registriert alle Content-Felder im WordPress Customizer.
 * 
 * @package YourPartyTech
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Register Customizer settings and controls.
 *
 * @param WP_Customize_Manager $wp_customize Customizer manager instance.
 */
function yourparty_register_customizer($wp_customize)
{
    $defaults = yourparty_content_defaults();

    // ========================================
    // Panel: YourParty Content
    // ========================================
    $wp_customize->add_panel(
        'yourparty_content',
        [
            'title' => __('YourParty Content (Marketing SSOT)', 'yourparty-tech'),
            'description' => __('Zentrale Verwaltung aller Texte und Inhalte.', 'yourparty-tech'),
            'priority' => 30,
        ]
    );

    // ========================================
    // Section: Hero
    // ========================================
    $wp_customize->add_section(
        'yourparty_hero_content',
        [
            'title' => __('Hero-Bereich', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 10,
        ]
    );

    yourparty_add_text_setting($wp_customize, 'hero_eyebrow', 'Hero Eyebrow', 'yourparty_hero_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'hero_headline', 'Hero Headline', 'yourparty_hero_content', $defaults);
    yourparty_add_textarea_setting($wp_customize, 'hero_lead', 'Hero Lead Text', 'yourparty_hero_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'hero_cta_primary', 'Primärer CTA', 'yourparty_hero_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'hero_cta_secondary', 'Sekundärer CTA', 'yourparty_hero_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'hero_caption', 'Bild-Beschriftung', 'yourparty_hero_content', $defaults);

    // ========================================
    // Section: USPs
    // ========================================
    $wp_customize->add_section(
        'yourparty_usp_content',
        [
            'title' => __('USPs (Unique Selling Points)', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 20,
        ]
    );

    for ($i = 1; $i <= 3; $i++) {
        yourparty_add_text_setting($wp_customize, "usp_title_{$i}", "USP {$i} Titel", 'yourparty_usp_content', $defaults);
        yourparty_add_textarea_setting($wp_customize, "usp_desc_{$i}", "USP {$i} Beschreibung", 'yourparty_usp_content', $defaults);
    }

    // ========================================
    // Section: Radio
    // ========================================
    $wp_customize->add_section(
        'yourparty_radio_content',
        [
            'title' => __('Radio-Bereich', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 30,
        ]
    );

    yourparty_add_text_setting($wp_customize, 'radio_eyebrow', 'Radio Eyebrow', 'yourparty_radio_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'radio_title', 'Radio Titel', 'yourparty_radio_content', $defaults);
    yourparty_add_textarea_setting($wp_customize, 'radio_lead', 'Radio Lead Text', 'yourparty_radio_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'radio_history_title', 'History Titel', 'yourparty_radio_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'radio_cta_request', 'Song Request CTA', 'yourparty_radio_content', $defaults);

    // ========================================
    // Section: About
    // ========================================
    $wp_customize->add_section(
        'yourparty_about_content',
        [
            'title' => __('Über uns', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 40,
        ]
    );

    yourparty_add_text_setting($wp_customize, 'about_eyebrow', 'About Eyebrow', 'yourparty_about_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'about_title', 'About Titel', 'yourparty_about_content', $defaults);
    yourparty_add_textarea_setting($wp_customize, 'about_lead', 'About Lead Text', 'yourparty_about_content', $defaults);
    yourparty_add_textarea_setting($wp_customize, 'about_text', 'About Text', 'yourparty_about_content', $defaults);

    // ========================================
    // Section: Contact
    // ========================================
    $wp_customize->add_section(
        'yourparty_contact_content',
        [
            'title' => __('Kontakt', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 50,
        ]
    );

    yourparty_add_text_setting($wp_customize, 'contact_eyebrow', 'Kontakt Eyebrow', 'yourparty_contact_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'contact_title', 'Kontakt Titel', 'yourparty_contact_content', $defaults);
    yourparty_add_textarea_setting($wp_customize, 'contact_lead', 'Kontakt Lead Text', 'yourparty_contact_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'contact_email', 'E-Mail', 'yourparty_contact_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'contact_phone', 'Telefon', 'yourparty_contact_content', $defaults);

    // ========================================
    // Section: Footer
    // ========================================
    $wp_customize->add_section(
        'yourparty_footer_content',
        [
            'title' => __('Footer', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 60,
        ]
    );

    yourparty_add_text_setting($wp_customize, 'footer_tagline', 'Footer Tagline', 'yourparty_footer_content', $defaults);
    yourparty_add_text_setting($wp_customize, 'footer_copyright', 'Copyright', 'yourparty_footer_content', $defaults);

    // ========================================
    // Section: Google Reviews
    // ========================================
    $wp_customize->add_section(
        'yourparty_reviews',
        [
            'title' => __('Google Reviews', 'yourparty-tech'),
            'description' => __('Trage deine Google Places ID oder Elfsight Widget-ID ein, um echte Bewertungen anzuzeigen.', 'yourparty-tech'),
            'panel' => 'yourparty_content',
            'priority' => 55,
        ]
    );

    $wp_customize->add_setting(
        'yourparty_google_places_id',
        [
            'default' => '',
            'sanitize_callback' => 'sanitize_text_field',
            'transport' => 'refresh',
        ]
    );

    $wp_customize->add_control(
        'yourparty_google_places_id',
        [
            'label' => __('Google Places ID / Elfsight Widget ID', 'yourparty-tech'),
            'description' => __('Z.B. "ChIJN1t_tDeuEmsRUsoyG83frY4" für Google Places oder "12345678-1234-1234-1234-123456789abc" für Elfsight', 'yourparty-tech'),
            'section' => 'yourparty_reviews',
            'type' => 'text',
        ]
    );
}
add_action('customize_register', 'yourparty_register_customizer');

/**
 * Helper: Add text setting to customizer.
 *
 * @param WP_Customize_Manager $wp_customize Customizer manager.
 * @param string               $key          Setting key.
 * @param string               $label        Control label.
 * @param string               $section      Section ID.
 * @param array                $defaults     Default values.
 */
function yourparty_add_text_setting($wp_customize, $key, $label, $section, $defaults)
{
    $setting_id = "yourparty_content_{$key}";

    $wp_customize->add_setting(
        $setting_id,
        [
            'default' => $defaults[$key] ?? '',
            'sanitize_callback' => 'sanitize_text_field',
            'transport' => 'refresh',
        ]
    );

    $wp_customize->add_control(
        $setting_id,
        [
            'label' => $label,
            'section' => $section,
            'type' => 'text',
        ]
    );
}

/**
 * Helper: Add textarea setting to customizer.
 *
 * @param WP_Customize_Manager $wp_customize Customizer manager.
 * @param string               $key          Setting key.
 * @param string               $label        Control label.
 * @param string               $section      Section ID.
 * @param array                $defaults     Default values.
 */
function yourparty_add_textarea_setting($wp_customize, $key, $label, $section, $defaults)
{
    $setting_id = "yourparty_content_{$key}";

    $wp_customize->add_setting(
        $setting_id,
        [
            'default' => $defaults[$key] ?? '',
            'sanitize_callback' => 'sanitize_textarea_field',
            'transport' => 'refresh',
        ]
    );

    $wp_customize->add_control(
        $setting_id,
        [
            'label' => $label,
            'section' => $section,
            'type' => 'textarea',
        ]
    );
}
