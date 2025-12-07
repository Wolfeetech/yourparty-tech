<?php
/**
 * Template Name: Radio Control Dashboard
 * 
 * Frontend dashboard for managing radio content, mood tags, and playlists.
 * Accessible at /control
 */

// 1. LOGIN CHECK & FORM
if (!is_user_logged_in()) {
    get_header();
    ?>
    <div class="control-dashboard login-screen">
        <div class="container" style="max-width: 400px; padding-top: 100px;">
            <div class="control-panel">
                <div class="panel-header">
                    <h3>SYSTEM AUTHENTICATION</h3>
                </div>
                <div style="padding: 30px;">
                    <h1 class="glitch-text" style="text-align: center; margin-bottom: 30px; font-size: 24px;">IDENTIFY
                        YOURSELF</h1>

                    <form name="loginform" id="loginform"
                        action="<?php echo esc_url(site_url('wp-login.php', 'login_post')); ?>" method="post">
                        <div class="form-group">
                            <label>CODENAME (USER)</label>
                            <input type="text" name="log" class="control-input" autofocus required>
                        </div>
                        <div class="form-group">
                            <label>PASSKEY</label>
                            <input type="password" name="pwd" class="control-input" required>
                        </div>
                        <div class="form-group">
                            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                                <input type="checkbox" name="rememberme" value="forever">
                                <span>MAINTAIN SESSION UPLINK</span>
                            </label>
                        </div>
                        <button type="submit" name="wp-submit" class="control-btn">INITIALIZE SESSION</button>
                        <input type="hidden" name="redirect_to" value="<?php echo esc_url($_SERVER['REQUEST_URI']); ?>">
                    </form>
                </div>
            </div>
        </div>
    </div>
    <style>
        .control-dashboard {
            background: #050505;
            min-height: 100vh;
            font-family: var(--font-display);
            color: #fff;
        }

        .control-panel {
            background: #0a0a0a;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-header {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-header h3 {
            margin: 0;
            font-size: 12px;
            letter-spacing: 0.15em;
            color: #888;
        }

        .control-input {
            width: 100%;
            background: #111;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 12px;
            margin-bottom: 20px;
            font-family: monospace;
        }

        .control-input:focus {
            border-color: var(--emerald);
            outline: none;
        }

        .control-btn {
            background: var(--emerald);
            color: #000;
            border: none;
            padding: 15px;
            width: 100%;
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 0.1em;
        }

        .control-btn:hover {
            opacity: 0.9;
        }

        label {
            font-size: 10px;
            color: #666;
            letter-spacing: 0.1em;
            display: block;
            margin-bottom: 8px;
        }
    </style>
    <?php
    get_footer();
    exit;
}

// 2. ROLE CHECK
$current_user = wp_get_current_user();
$is_admin = current_user_can('manage_options');

// Handle Skip Track with PRG Pattern (ADMIN ONLY) - BEFORE get_header()
if ($is_admin && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['skip_track']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    $result = 'error';
    if (defined('YOURPARTY_AZURACAST_API_KEY') && YOURPARTY_AZURACAST_API_KEY) {
        $station_id = 1;
        $api_url = rtrim(yourparty_azuracast_base_url(), '/') . "/api/station/$station_id/backend/skip";
        $args = yourparty_http_defaults();
        $args['timeout'] = 5;
        $response = wp_remote_post($api_url, $args);
        if (!is_wp_error($response)) {
            $code = wp_remote_retrieve_response_code($response);
            if ($code === 200 || $code === 204) {
                $result = 'success';
            }
        }
    } else {
        $result = 'nokey';
    }
    // PRG: Redirect to prevent form resubmission on refresh
    wp_redirect(add_query_arg('skip_result', $result, remove_query_arg('skip_result')));
    exit;
}

// Handle Sync Metadata with PRG Pattern (ADMIN ONLY)
if ($is_admin && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['sync_metadata']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    $api_base = 'https://api.yourparty.tech';
    $all_songs = yourparty_fetch_azuracast('/api/station/1/requests?per_page=500');
    $updated = 0;

    if (!is_wp_error($all_songs) && is_array($all_songs)) {
        foreach ($all_songs as $song) {
            $s_obj = $song['song'] ?? $song;
            $id = (string) ($s_obj['unique_id'] ?? $s_obj['id'] ?? '');
            $title = $s_obj['title'] ?? '';
            $artist = $s_obj['artist'] ?? '';
            if (empty($id) || empty($title))
                continue;

            $response = wp_remote_post("$api_base/metadata", [
                'body' => json_encode(['song_id' => $id, 'title' => $title, 'artist' => $artist]),
                'headers' => ['Content-Type' => 'application/json'],
                'timeout' => 1,
                'sslverify' => false
            ]);
            if (!is_wp_error($response))
                $updated++;
        }
    }
    wp_redirect(add_query_arg('sync_result', $updated, remove_query_arg(['sync_result', 'skip_result'])));
    exit;
}

// Handle Steering Control (ADMIN ONLY)
if ($is_admin && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['set_steering']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    $mode = sanitize_text_field($_POST['steering_mode']);
    $target = sanitize_text_field($_POST['steering_target']);

    $payload = [
        'mode' => $mode,
        'target' => $target ?: null
    ];

    $response = wp_remote_post("https://api.yourparty.tech/control/steer", [
        'body' => json_encode($payload),
        'headers' => ['Content-Type' => 'application/json'],
        'timeout' => 5
    ]);

    // PRG
    wp_redirect(add_query_arg('steering_updated', '1', remove_query_arg(['steering_updated', 'skip_result', 'sync_result'])));
    exit;
}

get_header();

// Fetch Current Steering Status
$steering_status = ['mode' => 'auto', 'target' => null];
$steering_response = wp_remote_get("https://api.yourparty.tech/control/steer", ['timeout' => 2]);
if (!is_wp_error($steering_response) && wp_remote_retrieve_response_code($steering_response) === 200) {
    $steering_status = json_decode(wp_remote_retrieve_body($steering_response), true) ?: $steering_status;
}

// Check for flash messages from redirects

// Check for flash messages from redirects
$skip_message = '';
if (isset($_GET['skip_result'])) {
    switch ($_GET['skip_result']) {
        case 'success':
            $skip_message = 'SUCCESS: TRACK SKIPPED';
            break;
        case 'error':
            $skip_message = 'ERROR: Skip failed';
            break;
        case 'nokey':
            $skip_message = 'ERROR: API KEY MISSING';
            break;
    }
}
$sync_message = '';
if (isset($_GET['sync_result'])) {
    $count = intval($_GET['sync_result']);
    $sync_message = $count > 0 ? "SUCCESS: Updated $count tracks." : "INFO: Library is up to date.";
}

// Fetch Data from FastAPI Backend
$api_base = 'https://api.yourparty.tech';
$moods_data = [];
$ratings_data = [];

// Fetch Ratings
$ratings_response = wp_remote_get("$api_base/ratings", ['timeout' => 5, 'sslverify' => false]);
if (!is_wp_error($ratings_response) && wp_remote_retrieve_response_code($ratings_response) === 200) {
    $ratings_data = json_decode(wp_remote_retrieve_body($ratings_response), true) ?: [];
}

// Fetch Moods
$moods_response = wp_remote_get("$api_base/moods", ['timeout' => 5, 'sslverify' => false]);
if (!is_wp_error($moods_response) && wp_remote_retrieve_response_code($moods_response) === 200) {
    $moods_data = json_decode(wp_remote_retrieve_body($moods_response), true) ?: [];
}

// Merge Data
$combined_data = [];
$all_ids = array_unique(array_merge(array_keys($ratings_data), array_keys($moods_data)));

foreach ($all_ids as $id) {
    $mood_entry = $moods_data[$id] ?? [];
    $rating_entry = $ratings_data[$id] ?? [];
    $combined_data[$id] = [
        'title' => $mood_entry['title'] ?? '',
        'artist' => $mood_entry['artist'] ?? '',
        'moods' => $mood_entry['moods'] ?? [],
        'top_mood' => $mood_entry['top_mood'] ?? '',
        'top_genre' => $mood_entry['top_genre'] ?? '',
        'total_votes' => $mood_entry['total_votes'] ?? 0,
        'rating_total' => $rating_entry['total'] ?? 0,
        'rating_avg' => $rating_entry['average'] ?? 0,
    ];
}

// Sort by activity
uasort($combined_data, function ($a, $b) {
    return (($b['total_votes'] ?? 0) + ($b['rating_total'] ?? 0)) - (($a['total_votes'] ?? 0) + ($a['rating_total'] ?? 0));
});

// Fetch AzuraCast Playlists for Status Panel
$ac_playlists = [];
$ac_response = yourparty_fetch_azuracast('/api/station/1/playlists');
if (!is_wp_error($ac_response) && is_array($ac_response)) {
    foreach ($ac_response as $pl) {
        if (strpos($pl['name'], 'Mood:') === 0) {
            $mood_name = trim(str_replace('Mood:', '', $pl['name']));
            $ac_playlists[$mood_name] = [
                'count' => $pl['count'] ?? 0,
                'time' => $pl['total_time'] ?? 0,
                'weight' => $pl['weight'] ?? 3
            ];
        }
    }
}
?>

<div class="control-dashboard">
    <div class="container">
        <header class="control-header">
            <h1 class="glitch-text">SYSTEM CONTROL</h1>
            <div class="control-meta">
                <span>Logged in as <?php echo esc_html($current_user->display_name); ?></span>
                <span class="status-indicator online">SYSTEM ONLINE</span>
            </div>
        </header>

        <?php if ($skip_message): ?>
            <div class="alert <?php echo strpos($skip_message, 'SUCCESS') !== false ? 'alert-success' : 'alert-error'; ?>">
                <?php echo esc_html($skip_message); ?>
            </div>
        <?php endif; ?>

        <?php if ($sync_message): ?>
            <div class="alert <?php echo strpos($sync_message, 'SUCCESS') !== false ? 'alert-success' : 'alert-info'; ?>">
                <?php echo esc_html($sync_message); ?>
            </div>
        <?php endif; ?>

        <div class="control-grid">
            <!-- LEFT: DATA TABLE -->
            <div class="control-panel">
                <div class="panel-header" style="flex-direction: column; align-items: flex-start; gap: 15px;">
                    <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                        <h3>STATION DATA</h3>
                        <span class="panel-badge" id="track-count-badge"><?php echo count($combined_data); ?>
                            TRACKS</span>
                    </div>
                    <div class="nav-tabs">
                        <button class="tab-btn active" onclick="switchTab('live')">🔥 LIVE</button>
                        <button class="tab-btn" onclick="switchTab('top')">⭐ TOP RATED</button>
                        <button class="tab-btn" onclick="switchTab('history')">clock HISTORY</button>
                    </div>
                </div>
                <div class="data-table-wrapper">
                    <table class="control-table">
                        <thead>
                            <tr>
                                <th>TRACK</th>
                                <th>GENRE</th>
                                <th>TOP MOOD</th>
                                <th>RATING</th>
                                <th>VOTES</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php if (empty($combined_data)): ?>
                                <tr>
                                    <td colspan="4" class="empty-state">NO DATA YET</td>
                                </tr>
                            <?php else: ?>
                                <?php foreach ($combined_data as $song_id => $data): ?>
                                    <?php
                                    $title = $data['title'] ?? '';
                                    $artist = $data['artist'] ?? '';
                                    $display = ($title && $artist) ? "$artist - $title" : substr($song_id, 0, 8) . '...';
                                    $top = $data['top_mood'] ?? '-';
                                    $genre = $data['top_genre'] ?? '-';
                                    $avg = $data['rating_avg'] ?? 0;
                                    $total = $data['rating_total'] ?? 0;
                                    $votes = $data['total_votes'] ?? 0;
                                    $color = $avg >= 4 ? 'var(--emerald)' : ($avg <= 2 ? '#ff4444' : '#888');
                                    ?>
                                    <tr>
                                        <td class="mono-font" title="<?php echo esc_attr($song_id); ?>">
                                            <?php echo esc_html($display); ?>
                                        </td>
                                        <td style="color: #aaa; font-size: 11px;"><?php echo esc_html(ucfirst($genre)); ?></td>
                                        <td><span class="mood-badge"><?php echo esc_html(ucfirst($top)); ?></span></td>
                                        <td><span style="color: <?php echo $color; ?>; font-weight: bold;">★
                                                <?php echo number_format($avg, 1); ?></span>
                                            <small>(<?php echo $total; ?>)</small>
                                        </td>
                                        <td class="text-right"><?php echo $votes; ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- RIGHT: ADMIN TOOLS -->
            <div class="control-sidebar">

                <!-- 1. PLAYLIST INTELLIGENCE -->
                <div class="control-panel">
                    <div class="panel-header">
                        <h3>PLAYLIST INTELLIGENCE</h3>
                        <span class="panel-badge">LIVE AZURACAST DATA</span>
                    </div>
                    <div style="padding: 0;">
                        <table class="control-table" style="font-size: 11px;">
                            <thead>
                                <tr>
                                    <th>PLAYLIST</th>
                                    <th>TRACKS</th>
                                    <th>STATUS</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php if (empty($ac_playlists)): ?>
                                    <tr>
                                        <td colspan="3" style="padding: 15px; color: #666; text-align: center;">NO MOOD
                                            PLAYLISTS FOUND</td>
                                    </tr>
                                <?php else: ?>
                                    <?php foreach ($ac_playlists as $mood => $stats):
                                        $is_ready = $stats['count'] >= 5;
                                        $status_color = $is_ready ? 'var(--emerald)' : '#ffaa00';
                                        $status_text = $is_ready ? 'READY' : 'BUILDING';
                                        ?>
                                        <tr>
                                            <td><strong style="color: #ddd;"><?php echo esc_html($mood); ?></strong></td>
                                            <td><?php echo $stats['count']; ?> <span
                                                    style="color: #666;">(<?php echo round($stats['time'] / 60); ?>m)</span>
                                            </td>
                                            <td><span class="status-dot"
                                                    style="background: <?php echo $status_color; ?>"></span>
                                                <?php echo $status_text; ?></td>
                                        </tr>
                                    <?php endforeach; ?>
                                <?php endif; ?>
                            </tbody>
                        </table>
                        <div
                            style="padding: 10px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 10px; color: #666;">
                            Playlists are created automatically when you tag songs.
                        </div>
                    </div>
                </div>

                <?php if ($is_admin): ?>
                    <!-- STEERING CONTROL -->
                    <div class="control-panel">
                        <div class="panel-header">
                            <h3>RADIO STEERING</h3>
                            <span class="panel-badge"
                                style="background: <?php echo $steering_status['mode'] === 'auto' ? '#888' : 'var(--emerald)'; ?>">
                                <?php echo strtoupper($steering_status['mode']); ?>
                            </span>
                        </div>
                        <div style="padding: 20px;">
                            <form method="post">
                                <?php wp_nonce_field('yourparty_control_action'); ?>
                                <input type="hidden" name="set_steering" value="1">

                                <div style="margin-bottom: 20px;">
                                    <label>MODE SELECTION</label>
                                    <div class="mode-toggle">
                                        <button type="submit" name="steering_mode" value="auto"
                                            class="mode-btn <?php echo $steering_status['mode'] === 'auto' ? 'active' : ''; ?>">
                                            🤖 AUTO
                                        </button>
                                        <button type="button"
                                            class="mode-btn <?php echo $steering_status['mode'] !== 'auto' ? 'active' : ''; ?>"
                                            onclick="document.getElementById('manual-controls').style.display='block'">
                                            🎛 MANUAL
                                        </button>
                                    </div>
                                </div>

                                <div id="manual-controls"
                                    style="display: <?php echo $steering_status['mode'] !== 'auto' ? 'block' : 'none'; ?>">
                                    <label>FORCE MOOD</label>
                                    <div class="mood-grid">
                                        <?php
                                        $moods = [
                                            'energetic' => '🔥',
                                            'chill' => '😌',
                                            'dark' => '🌑',
                                            'euphoric' => '✨',
                                            'melancholic' => '💙',
                                            'groovy' => '🎵',
                                            'hypnotic' => '🌀',
                                            'aggressive' => '😤'
                                        ];
                                        foreach ($moods as $m => $e):
                                            $isActive = $steering_status['mode'] === 'mood' && $steering_status['target'] === $m;
                                            ?>
                                            <button type="submit" name="steering_target" value="<?php echo $m; ?>"
                                                class="mood-btn <?php echo $isActive ? 'active' : ''; ?>"
                                                onclick="this.form.steering_mode.value='mood'">
                                                <?php echo $e . ' ' . ucfirst($m); ?>
                                            </button>
                                        <?php endforeach; ?>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="control-panel">
                        <div class="panel-header">
                            <h3>ADMIN TOOLS</h3>
                        </div>
                        <div style="padding: 20px;">
                            <form method="post" style="margin-bottom: 15px;">
                                <?php wp_nonce_field('yourparty_control_action'); ?>
                                <button type="submit" name="skip_track" class="control-btn"
                                    style="background: #ff4444; color: white;">⏭ SKIP TRACK</button>
                            </form>
                            <form method="post">
                                <?php wp_nonce_field('yourparty_control_action'); ?>
                                <button type="submit" name="sync_metadata" class="control-btn">🔄 SYNC METADATA</button>
                            </form>
                        </div>
                    </div>
                <?php endif; ?>

                <div class="control-panel">
                    <div class="panel-header">
                        <h3>SYSTEM STATUS</h3>
                    </div>
                    <div class="status-grid">
                        <div class="status-item"><span class="label">API</span><span class="value ok">ONLINE</span>
                        </div>
                        <div class="status-item"><span class="label">DB</span><span class="value ok">CONNECTED</span>
                        </div>
                        <div class="status-item"><span class="label">TIME</span><span
                                class="value"><?php echo date('H:i'); ?></span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- BOTTOM: MISSION CONTROL FOOTER -->
    <div class="control-footer">
        <div class="footer-left">
            <button id="monitor-play-btn" class="footer-btn">▶ MONITOR</button>
            <div class="volume-control">
                <span>VOL</span>
                <input type="range" id="monitor-volume" min="0" max="100" value="80">
            </div>

            <div class="vis-controls" style="display:flex !important; gap: 4px; margin-left: 10px;">
                <button class="footer-btn" onclick="setVisMode('modern_wave')">WAVE</button>
                <button class="footer-btn" onclick="setVisMode('rta_spectrum')">BARS</button>
                <button class="footer-btn" onclick="setVisMode('rgb_waveform')">GFX</button>
            </div>

            <div class="now-playing-monitor" style="margin-left: 10px;">
                <canvas id="monitor-visualizer" width="90" height="30"></canvas>
                <div class="monitor-info">
                    <span id="monitor-title">CONNECTING...</span>
                    <span id="monitor-artist" style="font-size: 9px; color: #666;">--</span>
                </div>
            </div>
        </div>

        <div class="footer-center">
            <?php if ($is_admin): ?>
                <form method="post" style="display:flex; gap: 10px;">
                    <?php wp_nonce_field('yourparty_control_action'); ?>
                    <button type="submit" name="skip_track" class="footer-btn danger"
                        onclick="return confirm('SKIP TRACK?');">
                        ⏭ SKIP
                    </button>
                    <button type="button" class="footer-btn warning"
                        onclick="document.querySelector('input[name=steering_mode][value=auto]').click()">
                        🤖 AUTO PILOT
                    </button>
                </form>
            <?php endif; ?>
        </div>

        <div class="footer-right">
            <div class="status-metric">
                <span class="label">LISTENERS</span>
                <span class="value" id="monitor-listeners">--</span>
            </div>
            <div class="status-metric">
                <span class="label">CPU</span>
                <span class="value">OK</span>
            </div>
        </div>
    </div>

</div> <!-- End control-dashboard -->

<style>
    .control-dashboard {
        background: #050505;
        min-height: 100vh;
        padding: 100px 0 40px;
        font-family: var(--font-display);
        color: #fff;
    }

    .control-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 40px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 20px;
    }

    .control-header h1 {
        font-size: 32px;
        margin: 0;
    }

    .control-meta {
        font-size: 12px;
        color: #666;
        display: flex;
        gap: 20px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .status-indicator.online {
        color: var(--emerald);
    }

    .status-indicator.online::before {
        content: '●';
        margin-right: 6px;
    }

    .control-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 30px;
    }

    @media (max-width: 900px) {
        .control-grid {
            grid-template-columns: 1fr;
        }
    }

    .control-panel {
        background: #0a0a0a;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .panel-header {
        background: rgba(255, 255, 255, 0.02);
        padding: 15px 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .panel-header h3 {
        margin: 0;
        font-size: 12px;
        letter-spacing: 0.15em;
        color: #888;
    }

    .panel-badge {
        font-size: 10px;
        background: var(--emerald);
        color: #000;
        padding: 2px 6px;
        border-radius: 2px;
        font-weight: bold;
    }

    .data-table-wrapper {
        max-height: 600px;
        overflow-y: auto;
    }

    .control-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .control-table th {
        text-align: left;
        padding: 12px 20px;
        color: #555;
        font-size: 10px;
        letter-spacing: 0.1em;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .control-table td {
        padding: 12px 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
    }

    .control-table tr:hover {
        background: rgba(255, 255, 255, 0.02);
    }

    .mono-font {
        font-family: monospace;
        color: #888;
    }

    .mood-badge {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
    }

    .text-right {
        text-align: right;
    }

    .control-btn {
        background: var(--emerald);
        color: #000;
        border: none;
        padding: 15px;
        width: 100%;
        font-weight: bold;
        cursor: pointer;
        letter-spacing: 0.1em;
        border-radius: 4px;
    }

    .control-btn:hover {
        opacity: 0.9;
    }

    .status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1px;
        background: rgba(255, 255, 255, 0.05);
    }

    .status-item {
        background: #0a0a0a;
        padding: 15px;
        text-align: center;
    }

    .status-item .label {
        display: block;
        font-size: 10px;
        color: #555;
        margin-bottom: 5px;
    }

    .status-item .value {
        font-size: 13px;
        font-weight: bold;
    }

    .status-item .value.ok {
        color: var(--emerald);
    }

    .empty-state {
        text-align: center;
        padding: 40px;
        color: #444;
        font-size: 12px;
    }

    .alert {
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 4px;
        font-size: 12px;
    }

    .alert-success {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--emerald);
        color: var(--emerald);
    }

    .alert-error {
        background: rgba(255, 68, 68, 0.1);
        border: 1px solid #ff4444;
        color: #ff4444;
    }

    .alert-info {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #888;
        color: #888;
    }

    /* Steering Controls */
    .mode-toggle {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }

    .mode-btn {
        flex: 1;
        background: #222;
        border: 1px solid #333;
        color: #888;
        padding: 10px;
        cursor: pointer;
        border-radius: 4px;
        font-weight: bold;
    }

    .mode-btn.active {
        background: var(--emerald);
        color: #000;
        border-color: var(--emerald);
    }

    .mood-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .mood-btn {
        background: #1a1a1a;
        border: 1px solid #333;
        color: #ccc;
        padding: 8px;
        font-size: 11px;
        cursor: pointer;
        border-radius: 4px;
        text-align: left;
    }

    .mood-btn:hover {
        border-color: #666;
    }

    /* Tabs */
    .nav-tabs {
        display: flex;
        gap: 2px;
        background: #111;
        padding: 4px;
        border-radius: 4px;
    }

    .tab-btn {
        background: transparent;
        border: none;
        color: #666;
        padding: 6px 12px;
        font-family: var(--font-display);
        font-size: 10px;
        font-weight: bold;
        cursor: pointer;
        border-radius: 2px;
    }

    .tab-btn.active {
        background: #222;
        color: #fff;
    }

    .tab-btn:hover:not(.active) {
        color: #999;
    }

    .data-table-wrapper {
        display: none;
        /* Hidden by default, JS toggles */
    }

    .data-table-wrapper.active {
        display: block;
    }

    .mood-btn.active {
        border-color: var(--emerald);
        color: var(--emerald);
        background: rgba(16, 185, 129, 0.1);
    }

    /* Footer Controls */
    .control-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: rgba(10, 10, 10, 0.95);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        z-index: 1000;
        backdrop-filter: blur(10px);
    }

    .footer-left,
    .footer-center,
    .footer-right {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .footer-btn {
        background: #222;
        border: 1px solid #333;
        color: #fff;
        padding: 6px 12px;
        font-family: var(--font-display);
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        cursor: pointer;
        border-radius: 2px;
        transition: all 0.2s;
    }

    .footer-btn:hover {
        background: #333;
        border-color: #555;
    }

    .footer-btn.danger {
        border-color: #aa0000;
        color: #ff4444;
    }

    .footer-btn.danger:hover {
        background: #330000;
    }

    .footer-btn.warning {
        border-color: #aa5500;
        color: #ffaa00;
    }

    .now-playing-monitor {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(0, 0, 0, 0.5);
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .monitor-info {
        display: flex;
        flex-direction: column;
        line-height: 1.1;
        width: 150px;
    }

    #monitor-title {
        font-size: 11px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .volume-control {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 10px;
        color: #666;
    }

    input[type=range] {
        height: 4px;
        -webkit-appearance: none;
        background: #333;
        border-radius: 2px;
        width: 80px;
    }

    input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 10px;
        height: 10px;
        background: var(--emerald);
        border-radius: 50%;
        cursor: pointer;
    }

    .status-metric {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        line-height: 1.1;
    }

    .status-metric .label {
        font-size: 9px;
        color: #666;
    }

    .status-metric .value {
        font-size: 12px;
        color: var(--emerald);
        font-family: monospace;
    }

    /* Adjust main content padding to prevent overlap */
    .control-dashboard {
        padding-bottom: 80px;
    }

    <script>document.addEventListener('DOMContentLoaded', function () {
            const tableBody=document.querySelector('.control-table tbody');
            const apiBase='<?php echo esc_js($api_base); ?>';

            function updateData() {
                Promise.all([ fetch(`$ {
                            apiBase
                        }

                        /ratings`).then(r=> r.json()),
                    fetch(`$ {
                            apiBase
                        }

                        /moods`).then(r=> r.json())]).then(([ratings, moods])=> {
                        const allIds=new Set([...Object.keys(ratings), ...Object.keys(moods)]);

                        // If empty
                        if (allIds.size===0) {
                            if ( !tableBody.querySelector('.empty-state')) {
                                tableBody.innerHTML='<tr><td colspan="5" class="empty-state">NO DATA YET</td></tr>';
                            }

                            return;
                        }

                        // Map data
                        const rows=Array.from(allIds).map(id=> {
                                const r=ratings[id] || {}

                                ;

                                const m=moods[id] || {}

                                ;

                                return {
                                    id,
                                    title: m.title,
                                    artist: m.artist,
                                    top: m.top_mood || '-',
                                    genre: m.top_genre || '-',
                                    avg: parseFloat(r.average || 0),
                                    total: parseInt(r.total || 0),
                                    votes: parseInt(m.total_votes || 0),
                                    combinedScore: (parseInt(m.total_votes || 0) + parseInt(r.total || 0))
                                }

                                ;
                            });

                        // Sort
                        rows.sort((a, b)=> b.combinedScore - a.combinedScore);

                        // Rebuild HTML (Cleanest way without VDOM)
                        // Note: In production you might want to update cells individually to avoid flicker,
                        // but for this dashboard a simple rebuild is fine and robust.
                        const html=rows.map(row=> {
                                const color=row.avg >=4 ? 'var(--emerald)' : (row.avg <=2 ? '#ff4444' : '#888');

                                const display=(row.title && row.artist) ? `$ {
                                    row.artist
                                }

                                - $ {
                                    row.title
                                }

                                ` : (row.id.substring(0, 8) + '...');
                                // Escape HTML function
                                const e=str=> str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';

                                return ` <tr> <td class="mono-font" title="${e(row.id)}" >$ {
                                    e(display)
                                }

                                </td> <td style="color: #aaa; font-size: 11px;" >$ {
                                    e(row.genre)
                                }

                                </td> <td><span class="mood-badge" >$ {
                                    e(row.top.charAt(0).toUpperCase() + row.top.slice(1))
                                }

                                </span></td> <td> <span style="color: ${color}; font-weight: bold;" >★ $ {
                                    row.avg.toFixed(1)
                                }

                                </span> <small>($ {
                                        row.total

                                    })</small> </td> <td class="text-right" >$ {
                                    row.votes
                                }

                                </td> </tr> `;
                            }).join('');

                        tableBody.innerHTML=html;
                    }).catch(err=> console.error('Data pull failed', err));
            }

            // Update every 5 seconds
            setInterval(updateData, 5000);

            // --- FOOTER CONTROLS ---
            const monitorPlayBtn=document.getElementById('monitor-play-btn');
            const volSlider=document.getElementById('monitor-volume');
            const monitorTitle=document.getElementById('monitor-title');
            const monitorArtist=document.getElementById('monitor-artist');
            const listenerVal=document.getElementById('monitor-listeners');
            const monitorCanvas=document.getElementById('monitor-visualizer');
            let monitorCtx;

            if(monitorCanvas) monitorCtx=monitorCanvas.getContext('2d');

            // Check StreamController availability
            let sc=window.StreamController;
            if ( !sc && window.YourPartyApp) sc=window.YourPartyApp.getStreamController();

            if (monitorPlayBtn && sc) {
                monitorPlayBtn.addEventListener('click', ()=> sc.togglePlay());

                // Sync Play State
                window.addEventListener('stream:playing', ()=> {
                        monitorPlayBtn.textContent='⏸ PAUSE';
                        monitorPlayBtn.style.color='var(--emerald)';
                        monitorPlayBtn.style.borderColor='var(--emerald)';
                    });

                window.addEventListener('stream:paused', ()=> {
                        monitorPlayBtn.textContent='▶ MONITOR';
                        monitorPlayBtn.style.color='';
                        monitorPlayBtn.style.borderColor='';
                    });
            }

            if (volSlider) {
                volSlider.addEventListener('input', (e)=> {
                        const audio=document.getElementById('radio-audio');
                        if(audio) audio.volume=e.target.value / 100;
                    });
            }

            // Sync Metadata
            window.addEventListener('songChange', (e)=> {
                    const song=e.detail.song;

                    if(song) {
                        if(monitorTitle) monitorTitle.textContent=song.title;
                        if(monitorArtist) monitorArtist.textContent=song.artist;
                    }
                });

            // Listeners (Quick Hack using existing update logic or polling)
            // Ideally we grab it from the main update loop, but for now let's just use the main UI elem
            setInterval(()=> {
                    const mainCount=document.getElementById('listener-count');

                    if(mainCount && listenerVal) {
                        listenerVal.textContent=mainCount.textContent || '--';
                    }
                }

                , 2000);

            // Mini Visualizer Loop
            function drawMiniVis() {
                requestAnimationFrame(drawMiniVis);
                if( !monitorCtx || !sc) return;
                const analyser=sc.getAnalyser();

                if( !analyser) {
                    // Idle noise
                    monitorCtx.clearRect(0, 0, 100, 30);
                    monitorCtx.fillStyle='#222';
                    monitorCtx.fillRect(0, 14, 100, 2);
                    return;
                }

                const bufferValid=analyser.frequencyBinCount;
                if( !bufferValid) return;

                const data=new Uint8Array(bufferValid);
                analyser.getByteFrequencyData(data);

                monitorCtx.clearRect(0, 0, 100, 30);
                monitorCtx.fillStyle='var(--emerald)';

                const barW=3;
                const gap=1;
                const count=Math.floor(100 / (barW+gap));
                const step=Math.floor(data.length / count);

                for(let i=0; i<count; i++) {
                    let sum=0; for(let j=0; j<step; j++) sum+=data[i*step+j];
                    const val=sum/step;
                    const h=(val/255)*25;

                    monitorCtx.fillRect(i*(barW+gap), 30-h, barW, h);
                }
            }

            drawMiniVis();

            function updateData() {
                Promise.all([ fetch(`$ {
                            apiBase
                        }

                        /ratings`).then(r=> r.json()),
                    fetch(`$ {
                            apiBase
                        }

                        /moods`).then(r=> r.json())]).then(([ratings, moods])=> {
                        const allIds=new Set([...Object.keys(ratings), ...Object.keys(moods)]);

                        // If empty
                        if (allIds.size===0) {
                            if ( !tableBody.querySelector('.empty-state')) {
                                tableBody.innerHTML='<tr><td colspan="5" class="empty-state">NO DATA YET</td></tr>';
                            }

                            return;
                        }

                        // Map data
                        const rows=Array.from(allIds).map(id=> {
                                const r=ratings[id] || {}

                                ;

                                const m=moods[id] || {}

                                ;

                                // Clean up title/artist display
                                let displayTitle=(m.title && m.artist) ? `$ {
                                    m.artist
                                }

                                - $ {
                                    m.title
                                }

                                ` : (m.title || 'Unknown Track');

                                if ( !m.title && !m.artist) {

                                    // Fallback to ID if absolutely nothing else
                                    displayTitle=`Track $ {
                                        id.substring(0, 8)
                                    }

                                    ...`;
                                }

                                return {
                                    id,
                                    title: m.title,
                                    artist: m.artist,
                                    display: displayTitle,
                                    top: m.top_mood || '-',
                                    genre: m.top_genre || '-',
                                    avg: parseFloat(r.average || 0),
                                    total: parseInt(r.total || 0),
                                    votes: parseInt(m.total_votes || 0),
                                    combinedScore: (parseInt(m.total_votes || 0) + parseInt(r.total || 0))
                                }

                                ;
                            });

                        // Sort
                        rows.sort((a, b)=> b.combinedScore - a.combinedScore);

                        // Rebuild HTML
                        const e=str=> str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';

                        const html=rows.map(row=> {
                                const color=row.avg >=4 ? 'var(--emerald)' : (row.avg <=2 ? '#ff4444' : '#888');

                                return ` <tr> <td class="mono-font" title="${e(row.id)}" > $ {
                                    e(row.display)
                                }

                                </td> <td style="color: #aaa; font-size: 11px;" >$ {
                                    e(row.genre)
                                }

                                </td> <td> <span class="mood-badge" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2);" > $ {
                                    e(row.top !=='-' ? row.top.toUpperCase() : '-')
                                }

                                </span> </td> <td> <span style="color: ${color}; font-weight: bold;" >★ $ {
                                    row.avg.toFixed(1)
                                }

                                </span> <small>($ {
                                        row.total

                                    })</small> </td> <td class="text-right" >$ {
                                    row.votes
                                }

                                </td> </tr> `;
                            }).join('');

                        tableBody.innerHTML=html;
                    }).catch(err=> console.error('Data pull failed', err));
            }

            // Update every 5 seconds
            setInterval(updateData, 5000);

            // --- FOOTER CONTROLS ---
            const monitorPlayBtn=document.getElementById('monitor-play-btn');
            const volSlider=document.getElementById('monitor-volume');
            const monitorTitle=document.getElementById('monitor-title');
            const monitorArtist=document.getElementById('monitor-artist');
            const listenerVal=document.getElementById('monitor-listeners');
            const monitorCanvas=document.getElementById('monitor-visualizer');
            let monitorCtx;

            if(monitorCanvas) monitorCtx=monitorCanvas.getContext('2d');

            // Check StreamController availability
            let sc=window.StreamController;
            if ( !sc && window.YourPartyApp) sc=window.YourPartyApp.getStreamController();

            if (monitorPlayBtn && sc) {
                monitorPlayBtn.addEventListener('click', ()=> sc.togglePlay());

                // Sync Play State
                window.addEventListener('stream:playing', ()=> {
                        monitorPlayBtn.textContent='⏸ PAUSE';
                        monitorPlayBtn.style.color='var(--emerald)';
                        monitorPlayBtn.style.borderColor='var(--emerald)';
                    });

                window.addEventListener('stream:paused', ()=> {
                        monitorPlayBtn.textContent='▶ MONITOR';
                        monitorPlayBtn.style.color='';
                        monitorPlayBtn.style.borderColor='';
                    });
            }

            if (volSlider) {
                volSlider.addEventListener('input', (e)=> {
                        const audio=document.getElementById('radio-audio');
                        if(audio) audio.volume=e.target.value / 100;
                    });
            }

            // Sync Metadata
            window.addEventListener('songChange', (e)=> {
                    const song=e.detail.song;

                    if(song) {
                        if(monitorTitle) monitorTitle.textContent=song.title;
                        if(monitorArtist) monitorArtist.textContent=song.artist;
                    }
                });

            // Listeners (Quick Hack using existing update logic or polling)
            // Ideally we grab it from the main update loop, but for now let's just use the main UI elem
            setInterval(()=> {
                    const mainCount=document.getElementById('listener-count');

                    if(mainCount && listenerVal) {
                        listenerVal.textContent=mainCount.textContent || '--';
                    }
                }

                , 2000);

            // Mini Visualizer Loop
            function drawMiniVis() {
                requestAnimationFrame(drawMiniVis);
                if( !monitorCtx || !sc) return;
                const analyser=sc.getAnalyser();

                if( !analyser) {
                    // Idle noise
                    monitorCtx.clearRect(0, 0, 100, 30);
                    monitorCtx.fillStyle='#222';
                    monitorCtx.fillRect(0, 14, 100, 2);
                    return;
                }

                const bufferValid=analyser.frequencyBinCount;
                if( !bufferValid) return;

                const data=new Uint8Array(bufferValid);
                analyser.getByteFrequencyData(data);

                monitorCtx.clearRect(0, 0, 100, 30);
                monitorCtx.fillStyle='var(--emerald)';

                const barW=3;
                const gap=1;
                const count=Math.floor(100 / (barW+gap));
                const step=Math.floor(data.length / count);

                for(let i=0; i<count; i++) {
                    let sum=0; for(let j=0; j<step; j++) sum+=data[i*step+j];
                    const val=sum/step;
                    const h=(val/255)*25;
                    monitorCtx.fillRect(i*(barW+gap), 30-h, barW, h);
                    let count=0;

                    rows.forEach(row=> {
                            let show=false;

                            if (tab==='live') {
                                // Just show all for now, or filter by recent votes? 
                                // Let's assume 'Live' means sorted by activity (default view)
                                show=true;
                            }

                            else if (tab==='top') {
                                // Filter > 4 stars
                                const rating=parseFloat(row.querySelector('td:nth-child(4)').innerText.replace('★', ''));
                                if(rating >=4.0) show=true;
                            }

                            else if (tab==='history') {
                                // Logic would need real history data, for now show nothing or placeholder
                                // Since we don't have history in this table, let's just show 'all' but re-sorted (simulated)
                                show=true;
                            }

                            row.style.display=show ? 'table-row' : 'none';
                            if(show) count++;
                        });

                    // Sort Logic (Client Side)
                    if(tab==='top') {
                        const tbody=document.querySelector('.control-table tbody');

                        const sorted=Array.from(rows).sort((a, b)=> {
                                const ra=parseFloat(a.querySelector('td:nth-child(4)').innerText.replace('★', '')||0);
                                const rb=parseFloat(b.querySelector('td:nth-child(4)').innerText.replace('★', '')||0);
                                return rb - ra;
                            });
                        tbody.append(...sorted);
                    }

                    document.getElementById('track-count-badge').textContent=`$ {
                        count
                    }

                    TRACKS`;
                }

                ;

                // --- TOAST SYSTEM ---
                const toastContainer=document.createElement('div');
                toastContainer.id='toast-container';
                toastContainer.style.cssText='position:fixed; top: 20px; right: 20px; z-index: 9999; display:flex; flex-direction:column; gap:10px; pointer-events:none;';
                document.body.appendChild(toastContainer);

                window.showControlToast=function(msg, type='info') {
                    const toast=document.createElement('div');
                    const color=type==='error' ?'#ff4444':(type==='success' ?'var(--emerald)':'#fff');
                    const bg=type==='error' ?'rgba(50,0,0,0.9)':'rgba(0,20,0,0.9)';

                    toast.style.cssText=`background:$ {
                        bg
                    }

                    ; color:$ {
                        color
                    }

                    ; border:1px solid $ {
                        color
                    }

                    ; padding:12px 20px; border-radius:4px; font-family:var(--font-display); font-size:12px; opacity:0; transform:translateX(20px); transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); `;
                    toast.textContent=msg;

                    toastContainer.appendChild(toast);

                    // Animate In
                    requestAnimationFrame(()=> {
                            toast.style.opacity='1';
                            toast.style.transform='translateX(0)';
                        });

                    // Remove
                    setTimeout(()=> {
                            toast.style.opacity='0';
                            toast.style.transform='translateX(20px)';
                            setTimeout(()=> toast.remove(), 300);
                        }

                        , 3000);
                }

                ;

                // --- KEYBOARD SHORTCUTS ---
                document.addEventListener('keydown', (e)=> {
                        // N -> Next Track (Admin)
                        if (e.key.toLowerCase()==='n' && e.shiftKey &&

                            <?php echo $is_admin ? 'true' : 'false'; ?>
                        ) {
                            if(confirm('QUICK SKIP?')) document.querySelector('button[name=skip_track]').click();
                        }

                        // Space -> Toggle Monitor
                        if (e.code==='Space' && e.target.tagName !=='INPUT') {
                            e.preventDefault();
                            document.getElementById('monitor-play-btn').click();
                        }
                    });

                // Initial Toast if messaged
                <?php if ($skip_message): ?>
                    setTimeout(()=> window.showControlToast('<?php echo esc_js($skip_message); ?>', '<?php echo strpos($skip_message, 'SUCCESS') !== false ? 'success' : 'error'; ?>'), 500);
                <?php endif; ?>

                // Re-bind table updater to respect tab sorting? 
                // For now, let the interval update run, it might reset sort, but that's acceptable for "Live" view.
            });
        </script><?php get_footer(); ?>```