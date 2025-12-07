<?php
/**
 * REST API proxy endpoints for YourParty Tech.
 */

if (!defined('ABSPATH')) {
    exit;
}

const YOURPARTY_RATINGS_OPTION = 'yourparty_track_ratings';

function yourparty_azuracast_base_url(): string
{
    if (defined('YOURPARTY_AZURACAST_URL') && YOURPARTY_AZURACAST_URL) {
        return rtrim(YOURPARTY_AZURACAST_URL, '/');
    }

    // Use internal IP to bypass DNS/NAT issues on local network
    return 'https://192.168.178.210';
}

function yourparty_http_defaults(): array
{
    $headers = [
        'Accept' => 'application/json',
        'Host' => 'radio.yourparty.tech', // Ensure correct vhost routing
    ];

    if (defined('YOURPARTY_AZURACAST_API_KEY') && YOURPARTY_AZURACAST_API_KEY) {
        $headers['Authorization'] = 'Bearer ' . YOURPARTY_AZURACAST_API_KEY;
    }

    return [
        'timeout' => 10,
        'headers' => $headers,
        'sslverify' => false,
    ];
}

function yourparty_public_base_url(): string
{
    if (function_exists('yourparty_public_url')) {
        return yourparty_public_url();
    }

    if (defined('YOURPARTY_AZURACAST_PUBLIC_URL') && YOURPARTY_AZURACAST_PUBLIC_URL) {
        return untrailingslashit(set_url_scheme(YOURPARTY_AZURACAST_PUBLIC_URL, 'https'));
    }

    return 'https://radio.yourparty.tech';
}

function yourparty_build_url(array $parts): string
{
    if (empty($parts['host'])) {
        return '';
    }

    $scheme = $parts['scheme'] ?? 'https';
    $host = $parts['host'];
    $port = isset($parts['port']) ? ':' . $parts['port'] : '';
    $path = $parts['path'] ?? '';
    $query = isset($parts['query']) && '' !== $parts['query'] ? '?' . $parts['query'] : '';
    $fragment = isset($parts['fragment']) && '' !== $parts['fragment'] ? '#' . $parts['fragment'] : '';

    return $scheme . '://' . $host . $port . $path . $query . $fragment;
}

function yourparty_normalize_public_asset_url(string $url): string
{
    $trimmed = trim($url);

    if ('' === $trimmed || str_starts_with($trimmed, 'data:')) {
        return $trimmed;
    }

    $public_base = yourparty_public_base_url();
    $public_parts = wp_parse_url($public_base);

    if (false === $public_parts || empty($public_parts['host'])) {
        return $trimmed;
    }

    $parsed = wp_parse_url($trimmed);

    if (false === $parsed) {
        return $trimmed;
    }

    if (!isset($parsed['host'])) {
        if (str_starts_with($trimmed, '//')) {
            $parsed = wp_parse_url('https:' . $trimmed);
        } elseif (str_starts_with($trimmed, '/')) {
            return $public_base . $trimmed;
        } else {
            return $trimmed;
        }
    }

    if (!isset($parsed['host']) || '' === $parsed['host']) {
        return $trimmed;
    }

    $host = $parsed['host'];

    if (filter_var($host, FILTER_VALIDATE_IP) || 'radio.yourparty.tech' === $host) {
        $parsed['scheme'] = 'https';
        $parsed['host'] = $public_parts['host'];

        if (isset($public_parts['port'])) {
            $parsed['port'] = $public_parts['port'];
        } else {
            unset($parsed['port']);
        }

        $rewritten = yourparty_build_url($parsed);

        return '' !== $rewritten ? $rewritten : $trimmed;
    }

    if ($host === $public_parts['host'] && ($parsed['scheme'] ?? 'https') !== 'https') {
        $parsed['scheme'] = 'https';
        $rewritten = yourparty_build_url($parsed);

        return '' !== $rewritten ? $rewritten : $trimmed;
    }

    return $trimmed;
}

function yourparty_normalize_public_response($value)
{
    if (is_array($value)) {
        foreach ($value as $key => $item) {
            $value[$key] = yourparty_normalize_public_response($item);
        }

        return $value;
    }

    if (is_string($value)) {
        return yourparty_normalize_public_asset_url($value);
    }

    return $value;
}

function yourparty_fetch_azuracast(string $endpoint)
{
    $url = yourparty_azuracast_base_url() . '/' . ltrim($endpoint, '/');

    $response = wp_remote_get($url, yourparty_http_defaults());

    if (is_wp_error($response)) {
        return $response;
    }

    $code = (int) wp_remote_retrieve_response_code($response);

    if ($code < 200 || $code >= 300) {
        error_log('YourParty AzuraCast Error: ' . $url . ' returned ' . $code);
        error_log('Response Body: ' . wp_remote_retrieve_body($response));
        error_log('Response Headers: ' . print_r(wp_remote_retrieve_headers($response), true));
        return new WP_Error(
            'yourparty_azuracast_error',
            sprintf('AzuraCast request failed with status %d', $code),
            ['status' => $code]
        );
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        return new WP_Error('yourparty_azuracast_json_error', 'Konnte API-Antwort nicht parsen.');
    }

    if (is_array($data)) {
        $data = yourparty_normalize_public_response($data);
    }

    return $data;
}

function yourparty_get_ratings(): array
{
    $stored = get_option(YOURPARTY_RATINGS_OPTION, []);

    if (!is_array($stored)) {
        $stored = [];
    }

    return $stored;
}

function yourparty_set_ratings(array $ratings): void
{
    update_option(YOURPARTY_RATINGS_OPTION, $ratings, false);
}

function yourparty_default_rating_bucket(): array
{
    return [
        'like' => 0,
        'dislike' => 0,
        'neutral' => 0,
        'distribution' => [
            1 => 0,
            2 => 0,
            3 => 0,
            4 => 0,
            5 => 0,
        ],
        'total' => 0,
        'average' => 0,
        'updated_at' => 0,
    ];
}

function yourparty_recalculate_rating_entry(array $entry): array
{
    $defaults = yourparty_default_rating_bucket();

    $entry['distribution'] = array_replace(
        $defaults['distribution'],
        isset($entry['distribution']) && is_array($entry['distribution'])
        ? array_map('intval', $entry['distribution'])
        : []
    );

    $entry['like'] = isset($entry['like']) ? max(0, (int) $entry['like']) : 0;
    $entry['dislike'] = isset($entry['dislike']) ? max(0, (int) $entry['dislike']) : 0;
    $entry['neutral'] = isset($entry['neutral']) ? max(0, (int) $entry['neutral']) : 0;

    $entry['total'] = array_sum($entry['distribution']);

    if ($entry['total'] > 0) {
        $weighted = 0;
        foreach ($entry['distribution'] as $stars => $count) {
            $weighted += (int) $stars * (int) $count;
        }
        $entry['average'] = round($weighted / $entry['total'], 2);
    } else {
        $entry['average'] = 0;
    }

    if (isset($entry['updated_at'])) {
        $entry['updated_at'] = (int) $entry['updated_at'];
    } else {
        $entry['updated_at'] = 0;
    }

    return $entry;
}

function yourparty_normalize_rating_entry($entry): array
{
    $normalized = yourparty_default_rating_bucket();

    if (!is_array($entry)) {
        return $normalized;
    }

    foreach (['like', 'dislike', 'neutral'] as $key) {
        if (isset($entry[$key])) {
            $normalized[$key] = max(0, (int) $entry[$key]);
        }
    }

    if (isset($entry['distribution']) && is_array($entry['distribution'])) {
        $normalized['distribution'] = array_replace(
            $normalized['distribution'],
            array_map('intval', $entry['distribution'])
        );
    }

    if (isset($entry['updated_at'])) {
        $normalized['updated_at'] = (int) $entry['updated_at'];
    }

    return yourparty_recalculate_rating_entry($normalized);
}

function yourparty_prepare_rating_for_song(string $song_id, array $ratings): array
{
    $entry = $ratings[$song_id] ?? null;

    return yourparty_normalize_rating_entry($entry);
}

function yourparty_forward_rating_to_backend(string $song_id, string $vote, ?int $rating_value): bool
{
    if (!defined('YOURPARTY_API_RATE_URL') || empty(YOURPARTY_API_RATE_URL)) {
        return false;
    }

    if (!in_array($vote, ['like', 'dislike'], true)) {
        return false;
    }

    $payload = [
        'song_id' => $song_id,
        'vote' => $vote,
    ];

    if (null !== $rating_value) {
        $payload['rating'] = $rating_value;
    }

    $timeout = defined('YOURPARTY_API_TIMEOUT') ? (int) YOURPARTY_API_TIMEOUT : 8;
    if ($timeout <= 0) {
        $timeout = 8;
    }

    $args = [
        'timeout' => $timeout,
        'headers' => [
            'Content-Type' => 'application/json',
        ],
        'body' => wp_json_encode($payload),
    ];

    if (defined('YOURPARTY_API_TOKEN') && YOURPARTY_API_TOKEN) {
        $args['headers']['Authorization'] = 'Bearer ' . YOURPARTY_API_TOKEN;
    }

    $max_attempts = defined('YOURPARTY_API_RETRY') ? max(1, (int) YOURPARTY_API_RETRY) : 3;
    $delay_ms = defined('YOURPARTY_API_RETRY_DELAY_MS') ? max(0, (int) YOURPARTY_API_RETRY_DELAY_MS) : 250;

    for ($attempt = 1; $attempt <= $max_attempts; $attempt++) {
        $response = wp_remote_post(YOURPARTY_API_RATE_URL, $args);

        if (is_wp_error($response)) {
            error_log(
                sprintf(
                    '[YourParty REST] Forward rating attempt %d failed for %s: %s',
                    $attempt,
                    $song_id,
                    $response->get_error_message()
                )
            );
        } else {
            $code = (int) wp_remote_retrieve_response_code($response);
            if ($code >= 200 && $code < 300) {
                return true;
            }

            error_log(
                sprintf(
                    '[YourParty REST] Forward rating attempt %d HTTP %d for %s (body: %s)',
                    $attempt,
                    $code,
                    $song_id,
                    wp_remote_retrieve_body($response)
                )
            );
        }

        if ($attempt < $max_attempts && $delay_ms > 0) {
            if (function_exists('wp_sleep')) {
                wp_sleep($delay_ms / 1000);
            } else {
                usleep($delay_ms * 1000);
            }
        }
    }

    return false;
}

function yourparty_attach_rating_to_now_playing(array $data): array
{
    if (empty($data['now_playing']['song']['id'])) {
        return $data;
    }

    $ratings = yourparty_get_ratings();
    $song_id = $data['now_playing']['song']['id'];
    $data['now_playing']['song']['rating'] = yourparty_prepare_rating_for_song($song_id, $ratings);

    return $data;
}

function yourparty_rest_get_status(WP_REST_Request $request)
{
    $data = yourparty_fetch_azuracast('/api/nowplaying/1');

    if (is_wp_error($data)) {
        return $data;
    }

    $data = yourparty_attach_rating_to_now_playing($data);

    return rest_ensure_response($data);
}

function yourparty_rest_get_history(WP_REST_Request $request)
{
    // Use public endpoint instead of protected station endpoint
    $data = yourparty_fetch_azuracast('/api/nowplaying/1');

    if (is_wp_error($data)) {
        return $data;
    }

    $history = $data['song_history'] ?? [];
    $ratings = yourparty_get_ratings();

    foreach ($history as &$entry) {
        if (empty($entry['song']['id'])) {
            continue;
        }

        $song_id = $entry['song']['id'];
        $entry['song']['rating'] = yourparty_prepare_rating_for_song($song_id, $ratings);
    }
    unset($entry);

    return rest_ensure_response(['history' => $history]);
}

function yourparty_check_rate_limit(string $ip): bool
{
    $transient_key = 'yourparty_rate_limit_' . md5($ip);
    $count = get_transient($transient_key);

    if (false === $count) {
        set_transient($transient_key, 1, 60); // 1 minute window
        return true;
    }

    if ($count > 10) { // Max 10 votes per minute per IP
        return false;
    }

    set_transient($transient_key, $count + 1, 60);
    return true;
}

function yourparty_rest_post_rate(WP_REST_Request $request)
{
    // Security: Rate Limiting
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    if (!yourparty_check_rate_limit($ip)) {
        return new WP_Error('yourparty_rate_limit', 'Zu viele Anfragen. Bitte warten.', ['status' => 429]);
    }

    // Security: Strict Sanitization
    $song_id = preg_replace('/[^a-zA-Z0-9]/', '', (string) $request->get_param('song_id'));
    $vote = sanitize_text_field((string) $request->get_param('vote'));
    $rating = $request->get_param('rating');

    if (empty($song_id)) {
        return new WP_Error('yourparty_invalid_payload', 'Ungültige Song ID.', ['status' => 400]);
    }

    $rating_value = null;

    if (null !== $rating) {
        $rating_value = (int) $rating;
        if ($rating_value < 1 || $rating_value > 5) {
            $rating_value = null;
        }
    }

    if ('' === $vote && null === $rating_value) {
        return new WP_Error('yourparty_invalid_payload', 'Vote oder Rating ist erforderlich.', ['status' => 400]);
    }

    if ('' === $vote && null !== $rating_value) {
        if ($rating_value >= 4) {
            $vote = 'like';
        } elseif ($rating_value <= 2) {
            $vote = 'dislike';
        } else {
            $vote = 'neutral';
        }
    }

    if ('' !== $vote && !in_array($vote, ['like', 'dislike', 'neutral'], true)) {
        return new WP_Error('yourparty_invalid_vote', 'Ungueltiger Vote-Wert.', ['status' => 400]);
    }

    $ratings = yourparty_get_ratings();

    $entry = yourparty_normalize_rating_entry($ratings[$song_id] ?? null);

    if ('like' === $vote) {
        $entry['like']++;
    } elseif ('dislike' === $vote) {
        $entry['dislike']++;
    } elseif ('neutral' === $vote) {
        $entry['neutral']++;
    }

    if (null !== $rating_value) {
        $entry['distribution'][$rating_value]++;
    }

    $entry['updated_at'] = time();
    $entry = yourparty_recalculate_rating_entry($entry);

    $ratings[$song_id] = $entry;
    yourparty_set_ratings($ratings);

    $forwarded = yourparty_forward_rating_to_backend($song_id, $vote, $rating_value);

    return rest_ensure_response(
        [
            'status' => 'ok',
            'song_id' => $song_id,
            'vote' => $vote,
            'ratings' => $entry,
            'forwarded' => $forwarded,
        ]
    );
}

function yourparty_rest_post_mood_tag(WP_REST_Request $request)
{
    $song_id = preg_replace('/[^a-zA-Z0-9]/', '', (string) $request->get_param('song_id'));
    $mood = sanitize_text_field((string) $request->get_param('mood'));
    $genre = sanitize_text_field((string) $request->get_param('genre'));

    // Expanded mood list to match frontend
    $valid_moods = [
        'energetic',
        'chill',
        'dark',
        'euphoric',
        'melancholic',
        'groovy',
        'hypnotic',
        'aggressive',
        'trippy',
        'warm',
        'uplifting',
        'deep',
        'funky'
    ];

    if (empty($song_id)) {
        return new WP_Error('yourparty_invalid_payload', 'Ungültige Song ID.', ['status' => 400]);
    }

    // Validate Mood if present
    if (!empty($mood) && !in_array($mood, $valid_moods, true)) {
        return new WP_Error('yourparty_invalid_mood', 'Ungültiger Mood: ' . $mood, ['status' => 400]);
    }

    $title = sanitize_text_field((string) $request->get_param('title'));
    $artist = sanitize_text_field((string) $request->get_param('artist'));

    // Proxy to FastAPI backend (MongoDB storage)
    // Using PVE Host IP (.25) via NAT because direct container access (.211) is bridged/isolated
    $api_url = 'http://192.168.178.25:8080/mood-tag';

    $body_args = [
        'song_id' => $song_id,
        'title' => $title,
        'artist' => $artist
    ];
    if (!empty($mood))
        $body_args['mood'] = $mood;
    if (!empty($genre))
        $body_args['genre'] = $genre;

    $response = wp_remote_post($api_url, [
        'headers' => ['Content-Type' => 'application/json'],
        'body' => json_encode($body_args),
        'timeout' => 5
    ]);

    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Failed to contact backend API: ' . $response->get_error_message(), ['status' => 500]);
    }

    $code = wp_remote_retrieve_response_code($response);
    if ($code !== 200) {
        $body = wp_remote_retrieve_body($response);
        return new WP_Error('api_error', 'Backend API returned error: ' . $body, ['status' => $code]);
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    return rest_ensure_response($data ?: [
        'status' => 'ok',
        'song_id' => $song_id,
        'mood' => $mood,
    ]);
}

add_action('rest_api_init', function () {
    register_rest_route(
        'yourparty/v1',
        '/status',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => 'yourparty_rest_get_status',
            'permission_callback' => '__return_true',
        ]
    );

    register_rest_route(
        'yourparty/v1',
        '/history',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => 'yourparty_rest_get_history',
            'permission_callback' => '__return_true',
        ]
    );

    register_rest_route(
        'yourparty/v1',
        '/rate',
        [
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => 'yourparty_rest_post_rate',
            'permission_callback' => '__return_true',
            'args' => [
                'song_id' => [
                    'required' => true,
                    'type' => 'string',
                ],
                'vote' => [
                    'required' => true,
                    'type' => 'string',
                ],
            ],
        ]
    );

    // VOTE NEXT PROXY
    register_rest_route(
        'yourparty/v1',
        '/vote-next',
        [
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => function (WP_REST_Request $request) {
                $vote = sanitize_text_field($request->get_param('vote'));

                // Proxy to FastAPI
                $api_url = 'http://192.168.178.211:8080/control/vote-next';

                $response = wp_remote_post($api_url, [
                    'headers' => ['Content-Type' => 'application/json'],
                    'body' => json_encode(['vote' => $vote]),
                    'timeout' => 5
                ]);

                if (is_wp_error($response)) {
                    return new WP_Error('api_error', 'Service unavailable', ['status' => 503]);
                }

                $body = json_decode(wp_remote_retrieve_body($response), true);
                return rest_ensure_response($body);
            },
            'permission_callback' => '__return_true',
        ]
    );

    register_rest_route(
        'yourparty/v1',
        '/schedule',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function () {
                $data = yourparty_fetch_azuracast('/api/station/1/schedule');
                if (is_wp_error($data)) {
                    return $data;
                }
                return rest_ensure_response($data);
            },
            'permission_callback' => '__return_true',
        ]
    );

    register_rest_route(
        'yourparty/v1',
        '/requests',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function () {
                $data = yourparty_fetch_azuracast('/api/station/1/requests');
                if (is_wp_error($data)) {
                    return $data;
                }
                return rest_ensure_response($data);
            },
            'permission_callback' => '__return_true',
        ]
    );
    register_rest_route(
        'yourparty/v1',
        '/content',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function () {
                return rest_ensure_response([
                    'hero' => [
                        'eyebrow' => yourparty_get_content('hero_eyebrow'),
                        'headline' => yourparty_get_content('hero_headline'),
                        'lead' => yourparty_get_content('hero_lead'),
                        'cta_primary' => yourparty_get_content('hero_cta_primary'),
                        'cta_secondary' => yourparty_get_content('hero_cta_secondary'),
                        'caption' => yourparty_get_content('hero_caption'),
                    ],
                    'usp' => [
                        [
                            'title' => yourparty_get_content('usp_title_1'),
                            'desc' => yourparty_get_content('usp_desc_1'),
                        ],
                        [
                            'title' => yourparty_get_content('usp_title_2'),
                            'desc' => yourparty_get_content('usp_desc_2'),
                        ],
                        [
                            'title' => yourparty_get_content('usp_title_3'),
                            'desc' => yourparty_get_content('usp_desc_3'),
                        ],
                    ],
                    'radio' => [
                        'eyebrow' => yourparty_get_content('radio_eyebrow'),
                        'title' => yourparty_get_content('radio_title'),
                        'lead' => yourparty_get_content('radio_lead'),
                    ]
                ]);
            },
            'permission_callback' => '__return_true',
        ]
    );
    register_rest_route(
        'yourparty/v1',
        '/control/skip',
        [
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => function (WP_REST_Request $request) {
                if (!current_user_can('manage_options')) {
                    return new WP_Error('rest_forbidden', 'Nur für Admins.', ['status' => 403]);
                }

                // AzuraCast API: POST /api/station/{id}/backend/skip
                $response = wp_remote_post(
                    yourparty_azuracast_base_url() . '/api/station/1/backend/skip',
                    yourparty_http_defaults()
                );

                if (is_wp_error($response)) {
                    return $response;
                }

                return rest_ensure_response(['status' => 'skipped']);
            },
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
        ]
    );

    register_rest_route(
        'yourparty/v1',
        '/control/ratings',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function () {
                if (!current_user_can('manage_options')) {
                    return new WP_Error('rest_forbidden', 'Nur für Admins.', ['status' => 403]);
                }
                return rest_ensure_response(yourparty_get_ratings());
            },
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
        ]
    );

    // Mood Tagging Endpoint
    register_rest_route(
        'yourparty/v1',
        '/mood-tag',
        [
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => 'yourparty_rest_post_mood_tag',
            'permission_callback' => '__return_true',
            'args' => [
                'song_id' => [
                    'required' => true,
                    'type' => 'string',
                ],
                'mood' => [
                    'required' => true,
                    'type' => 'string',
                ],
            ],
        ]
    );

    // Get all mood tags (Admin only)
    register_rest_route(
        'yourparty/v1',
        '/control/moods',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function () {
                if (!current_user_can('manage_options')) {
                    return new WP_Error('rest_forbidden', 'Nur für Admins.', ['status' => 403]);
                }
                $moods = get_option('yourparty_mood_tags', []);
                return rest_ensure_response($moods);
            },
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
        ]
    );

    // Generate playlist by mood (Admin only)
    register_rest_route(
        'yourparty/v1',
        '/control/playlist-by-mood',
        [
            'methods' => WP_REST_Server::READABLE,
            'callback' => function (WP_REST_Request $request) {
                if (!current_user_can('manage_options')) {
                    return new WP_Error('rest_forbidden', 'Nur für Admins.', ['status' => 403]);
                }

                $mood = sanitize_text_field($request->get_param('mood'));
                $min_votes = max(1, (int) $request->get_param('min_votes') ?: 2);

                $moods = get_option('yourparty_mood_tags', []);
                $playlist = [];

                foreach ($moods as $song_id => $data) {
                    if (!isset($data['moods'][$mood]))
                        continue;
                    if ($data['moods'][$mood] < $min_votes)
                        continue;

                    $playlist[] = [
                        'song_id' => $song_id,
                        'mood' => $mood,
                        'votes' => $data['moods'][$mood],
                        'total_votes' => array_sum($data['moods']),
                    ];
                }

                // Sort by votes descending
                usort($playlist, function ($a, $b) {
                    return $b['votes'] - $a['votes'];
                });

                return rest_ensure_response([
                    'mood' => $mood,
                    'min_votes' => $min_votes,
                    'tracks' => $playlist,
                    'count' => count($playlist),
                ]);
            },
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
        ]
    );
});
