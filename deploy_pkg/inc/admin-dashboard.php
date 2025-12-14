<?php
/**
 * YourParty Tech - Radio Control Dashboard
 * 
 * Powered by Python API & MongoDB
 */

if (!defined('ABSPATH')) {
    exit;
}

// Configuration
define('YOURPARTY_API_BASE', 'http://192.168.178.211:8000');

// Register Menu Page
add_action('admin_menu', function () {
    add_menu_page(
        'Mission Control', // Renamed per user language
        'Mission Control',
        'manage_options',
        'yourparty-radio-control',
        'yourparty_render_admin_page',
        'dashicons-chart-bar',
        6
    );
});

// Add Dashboard Styles (User Requested)
add_action('admin_head', function() {
    echo '<style>
    .mood-btn { background: #1a1a1a; border: 1px solid #333; color: #ccc; padding: 8px; font-size: 11px; cursor: pointer; border-radius: 4px; text-align: left; } 
    .mood-btn:hover { border-color: #666; } 
    
    /* Tabs */ 
    .nav-tabs { display: flex; gap: 2px; background: #111; padding: 4px; border-radius: 4px; margin-bottom: 20px; } 
    .tab-btn { background: transparent; border: none; color: #666; padding: 6px 12px; font-family: monospace; font-size: 10px; font-weight: bold; cursor: pointer; border-radius: 2px; } 
    .tab-btn.active { background: #222; color: #fff; } 
    .tab-btn:hover:not(.active) { color: #999; } 
    
    .data-table-wrapper { display: none; margin-top: 15px; } 
    .data-table-wrapper.active { display: block; } 
    
    .mood-btn.active { border-color: #10b981; color: #10b981; background: rgba(16, 185, 129, 0.1); } 
    
    /* Footer Controls */ 
    .control-footer { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background: rgba(10, 10, 10, 0.95); border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center; padding: 0 20px; z-index: 1000; backdrop-filter: blur(10px); } 
    .footer-left, .footer-center, .footer-right { display: flex; align-items: center; gap: 20px; } 
    .footer-btn { background: #222; border: 1px solid #333; color: #fff; padding: 6px 12px; font-family: monospace; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; border-radius: 2px; transition: all 0.2s; } 
    .footer-btn:hover { background: #333; border-color: #555; } 
    .footer-btn.danger { border-color: #aa0000; color: #ff4444; } 
    .footer-btn.danger:hover { background: #330000; } 
    .footer-btn.warning { border-color: #aa5500; color: #ffaa00; } 
    
    .now-playing-monitor { display: flex; align-items: center; gap: 10px; background: rgba(0, 0, 0, 0.5); padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05); } 
    .monitor-info { display: flex; flex-direction: column; line-height: 1.1; width: 150px; } 
    #monitor-title { font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; } 
    
    .volume-control { display: flex; align-items: center; gap: 8px; font-size: 10px; color: #666; } 
    input[type=range] { height: 4px; -webkit-appearance: none; background: #333; border-radius: 2px; width: 80px; } 
    input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 10px; height: 10px; background: #10b981; border-radius: 50%; cursor: pointer; } 
    
    .status-metric { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.1; } 
    .status-metric .label { font-size: 9px; color: #666; } 
    .status-metric .value { font-size: 12px; color: #10b981; font-family: monospace; } 
    
    /* Adjust main content padding to prevent overlap */ 
    .control-dashboard { padding-bottom: 80px; }
    
    /* Responsive tweaks for admin */
    #wpadminbar { z-index: 999; }
    </style>';
});

// Helper: Fetch API Data
function yourparty_api_get($endpoint) {
    $url = YOURPARTY_API_BASE . '/' . ltrim($endpoint, '/');
    $response = wp_remote_get($url, ['timeout' => 5]);
    
    if (is_wp_error($response)) {
        return [];
    }
    
    $body = wp_remote_retrieve_body($response);
    return json_decode($body, true);
}

// Helper: Render Mood Badge
function yourparty_render_mood_badge($mood, $count = 0) {
    $moods = [
        'hypnotic' => ['label' => 'Hypnotic', 'bg' => '#8b5cf6', 'icon' => '🌀'],
        'driving' => ['label' => 'Driving', 'bg' => '#ef4444', 'icon' => '🏎️'],
        'euphoric' => ['label' => 'Euphoric', 'bg' => '#fbbf24', 'icon' => '🤩'],
        'groovy' => ['label' => 'Groovy', 'bg' => '#f59e0b', 'icon' => '🕺'],
        'chill' => ['label' => 'Chill', 'bg' => '#10b981', 'icon' => '🌴'],
        'dark' => ['label' => 'Dark', 'bg' => '#6b7280', 'icon' => '🌑'],
        'atmospheric' => ['label' => 'Atmospheric', 'bg' => '#3b82f6', 'icon' => '🌫️'],
        'raw' => ['label' => 'Raw', 'bg' => '#78716c', 'icon' => '🏗️'],
    ];

    $data = $moods[$mood] ?? ['label' =>ucfirst($mood), 'bg' => '#888', 'icon' => '❓'];
    
    $style = "background: {$data['bg']}; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-flex; align-items: center; gap: 4px; border: 1px solid rgba(255,255,255,0.2); margin-right: 4px; margin-bottom: 4px;";
    
    echo sprintf('<span style="%s">%s %s%s</span>', 
        $style, 
        $data['icon'], 
        $data['label'],
        $count > 1 ? " ($count)" : ""
    );
}

// Render Page
function yourparty_render_admin_page()
{
    // Fetch Data from Python API
    $api_moods = yourparty_api_get('moods');
    
    // Sort logic (if API returns object, converting to array of items might be needed)
    // Structure expected: { "song_id": { "top_mood": "x", "moods": {...}, "total_votes": n } }
    
    $generated_playlist = '';
    
    // Handle Actions
    if (isset($_POST['sync_library'])) {
         // Trigger Python Sync
         wp_remote_post(YOURPARTY_API_BASE . '/library/sync?directory=/var/radio/music/radio_library');
         echo '<div class="notice notice-success"><p>Library Sync Triggered!</p></div>';
    }

    // Handle Playlist Gen
    if (isset($_POST['generate_playlist'])) {
        $target_mood = sanitize_text_field($_POST['target_mood']);
        $lines = ["#EXTM3U"];
        $count = 0;
        
        if ($api_moods) {
            foreach ($api_moods as $id => $data) {
                $moods = $data['moods'] ?? [];
                if (isset($moods[$target_mood]) && $moods[$target_mood] > 0) {
                    $lines[] = "#EXTINF:-1,Song $id (Vote: " . $moods[$target_mood] . ")";
                    $lines[] = "song_id_$id.mp3"; // Placeholder until we have paths
                    $count++;
                }
            }
        }
        $generated_playlist = implode("\n", $lines);
    }

    ?>
    <div class="wrap">
        <h1 style="font-weight: 800; letter-spacing: -0.02em;">🚀 Mission Control</h1>
        <p class="description">Live Data from Python Backend (Container 211)</p>

        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 20px;">

            <!-- LEFT: Song Intelligence -->
            <div class="card" style="padding: 20px;">
                <h2 style="margin-top:0;">📡 Song Intelligence (<?php echo is_array($api_moods) ? count($api_moods) : 0; ?>)</h2>
                
                <table class="wp-list-table widefat fixed striped">
                    <thead>
                        <tr>
                            <th style="font-weight: bold;">Global Vibe Tag</th>
                            <th style="font-weight: bold;">Vote Count</th>
                            <th style="font-weight: bold;">Trend Indicator</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (empty($api_moods) || empty($api_moods['top_moods'])): ?>
                            <tr><td colspan="3">Connecting to Neural Core... (If persistent: Check Container 211 / API Status)</td></tr>
                        <?php else: ?>
                            <?php foreach ($api_moods['top_moods'] as $m): ?>
                                <tr>
                                    <td>
                                        <?php yourparty_render_mood_badge($m['tag']); ?>
                                    </td>
                                    <td>
                                        <div style="background: #e5e7eb; border-radius: 999px; width: 100%; height: 8px; position: relative; max-width: 100px;">
                                            <div style="background: #3b82f6; height: 100%; border-radius: 999px; width: <?php echo min(100, $m['count'] * 10); ?>%;"></div>
                                        </div>
                                        <small style="margin-left: 5px;"><?php echo $m['count']; ?> Votes</small>
                                    </td>
                                    <td>
                                        <!-- Trend logic placeholder -->
                                        <span style="color: green;">▲ Rising</span>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
                </table>
            </div>

            <!-- QUEUE HORIZON -->
            <?php 
                $queue_data = yourparty_api_get('queue'); // Fetches from /queue
                $status_data = yourparty_api_get('status'); // Fetches steering info
                $steering = $status_data['steering'] ?? ['mode' => 'auto', 'target' => 'neutral'];
            ?>
            <div class="card" style="padding: 20px; grid-column: span 1;">
                 <h2 style="margin-top:0;">🔮 Queue Horizon</h2>
                 <div style="background: #111; color: #fff; padding: 15px; border-radius: 6px; font-family: monospace;">
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px;">
                        <span>CURRENT MODE:</span>
                        <strong style="color: <?php echo $steering['mode'] === 'manual' ? '#ef4444' : '#10b981'; ?>"><?php echo strtoupper($steering['mode']); ?></strong>
                    </div>
                    <?php if(!empty($steering['target'])): ?>
                    <div style="display:flex; justify-content:space-between; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px;">
                        <span>TARGET VIBE:</span>
                        <strong style="color: #f59e0b;"><?php echo strtoupper($steering['target']); ?></strong>
                    </div>
                    <?php endif; ?>

                    <?php if (empty($queue_data)): ?>
                        <p style="color: #666;">-- No upcoming tracks queued (Random Rotation Active) --</p>
                    <?php else: ?>
                        <ul style="margin:0; padding:0; list-style:none;">
                            <?php foreach($queue_data as $idx => $q_item): 
                                $song = $q_item['song'] ?? [];
                                $title = $song['title'] ?? 'Unknown Track';
                                $artist = $song['artist'] ?? 'Unknown Artist';
                            ?>
                            <li style="display: flex; gap: 10px; margin-bottom: 8px; align-items: center;">
                                <span style="color: #666;">+<?php echo ($idx+1); ?></span>
                                <img src="<?php echo esc_url($song['art'] ?? ''); ?>" style="width: 30px; height: 30px; border-radius: 3px; background: #333;">
                                <div>
                                    <div style="color: #fff; font-weight: bold; font-size: 12px;"><?php echo esc_html($title); ?></div>
                                    <div style="color: #888; font-size: 11px;"><?php echo esc_html($artist); ?></div>
                                </div>
                            </li>
                            <?php endforeach; ?>
                        </ul>
                    <?php endif; ?>
                 </div>
            </div>

            <!-- RIGHT: Actions -->
            <div style="display: flex; flex-direction: column; gap: 20px;">
                
                <!-- Live Stream Control -->
                <div class="card" style="padding: 20px; border-left: 4px solid #ef4444; background: #fff1f2;">
                    <h2 style="margin-top:0;">📡 Live Stream Control</h2>
                    <p class="description">Directly intervene in the playback algorithm.</p>
                    
                    <strong style="display:block; margin-bottom: 5px;">Steering Mode:</strong>
                    <form method="post" style="display: flex; gap: 5px; margin-bottom: 15px;">
                        <button type="submit" name="steer_mode" value="auto" class="button button-secondary">🤖 Auto</button>
                        <button type="submit" name="steer_mode" value="manual" class="button button-primary" style="background: #ef4444; border-color: #b91c1c;">✋ Manual Override</button>
                    </form>

                    <?php if(isset($_POST['steer_mode'])): 
                        $mode = sanitize_text_field($_POST['steer_mode']);
                        wp_remote_post(YOURPARTY_API_BASE . '/control/steer', [
                            'headers' => ['Content-Type' => 'application/json'],
                            'body' => json_encode(['mode' => $mode])
                        ]);
                        echo "<div class='updated inline'><p>Steering set to: <strong>$mode</strong></p></div>";
                    endif; ?>

                    <strong style="display:block; margin-bottom: 5px;">Force Vibe Injection:</strong>
                    <form method="post" style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                        <button type="submit" name="vote_next" value="energetic" class="button">🔥 High Energy</button>
                        <button type="submit" name="vote_next" value="chill" class="button">🌴 Chill / Deep</button>
                        <button type="submit" name="vote_next" value="dark" class="button">🌑 Dark</button>
                        <button type="submit" name="vote_next" value="groovy" class="button">🕺 Groovy</button>
                    </form>
                    <?php if(isset($_POST['vote_next'])): 
                         $vote = sanitize_text_field($_POST['vote_next']);
                         wp_remote_post(YOURPARTY_API_BASE . '/vote-next', [
                             'headers' => ['Content-Type' => 'application/json'],
                             'body' => json_encode(['vote' => $vote])
                         ]);
                         echo "<div class='updated inline'><p>Vibe injected: <strong>$vote</strong></p></div>";
                    endif; ?>
                </div>

                <!-- Sync Control -->
                <div class="card" style="padding: 20px; border-left: 4px solid #0073aa;">
                    <h2 style="margin-top:0;">🔄 Sync & Playlist Logic</h2>
                    <p>Trigger complex logic loops.</p>
                    
                    <form method="post" style="margin-bottom: 10px;">
                        <button type="submit" name="sync_playlist_now" class="button button-primary">⚡ Update 'Top Rated' on AzuraCast</button>
                    </form>
                    <?php if(isset($_POST['sync_playlist_now'])): 
                         wp_remote_post(YOURPARTY_API_BASE . '/tasks/recalc-playlists', ['timeout'=>1]); 
                         // Check API logs for result, timeout low as it is async
                         echo "<div class='notice notice-info'><p>Task sent to background queue. AzuraCast should update shortly.</p></div>";
                    endif; ?>

                    <form method="post">
                        <small>Library Scan (ID3 Tags)</small><br>
                        <button type="submit" name="sync_library" class="button button-secondary button-small">Run Library Scan</button>
                    </form>
                </div>

                <!-- Playlist Generator -->
                <div class="card" style="padding: 20px; border-left: 4px solid #10b981;">
                    <h2 style="margin-top:0;">⚡ Vibe Generator</h2>
                    <form method="post">
                        <label><strong>Target Vibe:</strong></label>
                        <select name="target_mood" style="width: 100%; margin-top: 5px; margin-bottom: 10px;">
                            <?php 
                            $options = ['hypnotic', 'driving', 'euphoric', 'groovy', 'chill', 'dark', 'atmospheric', 'raw'];
                            foreach($options as $opt) {
                                echo "<option value='$opt'>" . ucfirst($opt) . "</option>";
                            }
                            ?>
                        </select>
                        <button type="submit" name="generate_playlist" class="button button-primary" style="width: 100%;">Create Playlist</button>
                    </form>

                    <?php if ($generated_playlist): ?>
                        <div style="margin-top: 15px;">
                            <textarea style="width: 100%; height: 150px; font-family: monospace; font-size: 11px;" readonly><?php echo esc_textarea($generated_playlist); ?></textarea>
                        </div>
                    <?php endif; ?>
                </div>

            </div>
        </div>
    </div>
    <?php
}
