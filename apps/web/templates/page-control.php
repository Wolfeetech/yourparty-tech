<?php
/**
 * Template Name: Radio Control Dashboard
 * 
 * Frontend dashboard for managing radio content.
 * DESIGN: DEEP SPACE / CLUB MIX (Unified with Front Page)
 */

if (!is_user_logged_in()) {
    get_header(); /* Ensure header loads CSS */
    ?>
    <div class="control-login-wrapper">
        <div class="glass-panel login-box">
            <h1 class="neon-text glow">SYSTEM ACCESS</h1>
            <p class="subtitle">IDENTITY_VERIFICATION_REQUIRED</p>
            
            <?php if (isset($_GET['login']) && $_GET['login'] == 'failed'): ?>
            <div class="login-error" style="background: rgba(255,68,68,0.1); border: 1px solid #ff4444; color: #ff4444; padding: 10px; border-radius: 8px; font-size: 11px; margin-bottom: 20px; text-align: center; text-transform: uppercase; letter-spacing: 0.1em;">
                Access Denied: Invalid Credentials
            </div>
            <?php endif; ?>
            
            <form name="loginform" id="loginform" action="<?php echo esc_url(site_url('wp-login.php', 'login_post')); ?>" method="post">
                <div class="input-group">
                    <input type="text" name="log" placeholder="CODENAME" class="cyber-input" autofocus required>
                </div>
                <div class="input-group">
                    <input type="password" name="pwd" placeholder="PASSKEY" class="cyber-input" required>
                </div>
                <button type="submit" name="wp-submit" class="cyber-btn primary full-width">INITIALIZE UPLINK</button>
                <input type="hidden" name="redirect_to" value="<?php echo esc_url($_SERVER['REQUEST_URI']); ?>">
            </form>
        </div>
    </div>
    
    <style>
        /* INLINE CRITICAL CSS FOR LOGIN ONLY */
        body { background: #000; color: #fff; margin: 0; font-family: 'Outfit', sans-serif; }
        .control-login-wrapper { display: flex; align-items: center; justify-content: center; height: 100vh; background: radial-gradient(circle at center, #1a1a1a 0%, #000 100%); }
        .glass-panel { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); width: 100%; max-width: 400px; }
        .neon-text { color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.5); text-align: center; margin-bottom: 5px; font-weight: 800; letter-spacing: -0.02em; }
        .subtitle { text-align: center; color: var(--emerald, #00ff88); font-size: 10px; letter-spacing: 0.2em; margin-bottom: 30px; opacity: 0.8; }
        .cyber-input { width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 15px; margin-bottom: 15px; border-radius: 8px; font-family: 'Inter', monospace; box-sizing: border-box; transition: all 0.3s ease; }
        .cyber-input:focus { border-color: var(--emerald, #00ff88); outline: none; box-shadow: 0 0 15px rgba(0,255,136,0.2); }
        .cyber-btn { background: var(--emerald, #00ff88); color: #000; border: none; padding: 15px; border-radius: 8px; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 0.1em; transition: all 0.3s ease; }
        .cyber-btn:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(0,255,136,0.4); }
        .full-width { width: 100%; }
    </style>
    <?php
    get_footer();
    exit;
}

// === AUTHENTICATED LOGIC & DATA FETCHING ===
$current_user = wp_get_current_user();
$is_admin = current_user_can('manage_options');

// --- ACTIONS (Skip, Sync, Steer) ---
// Handle Skip
if ($is_admin && isset($_POST['skip_track']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    if (defined('YOURPARTY_AZURACAST_API_KEY')) {
        $api_url = rtrim(yourparty_azuracast_base_url(), '/') . "/api/station/1/backend/skip";
        wp_remote_post($api_url, array_merge(yourparty_http_defaults(), ['timeout' => 5]));
    }
    wp_redirect(add_query_arg('skip_result', 'success', remove_query_arg('skip_result'))); exit;
}

// Handle Steer
if ($is_admin && isset($_POST['set_steering']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    $payload = ['mode' => $_POST['steering_mode'], 'target' => $_POST['steering_target'] ?: null];
    wp_remote_post("https://api.yourparty.tech/control/steer", ['body' => json_encode($payload), 'headers' => ['Content-Type' => 'application/json']]);
    wp_redirect(add_query_arg('steering_updated', '1')); exit;
    wp_redirect(add_query_arg('steering_updated', '1')); exit;
}

// Handle Queue Removal (Admin)
if ($is_admin && isset($_POST['remove_queue_item']) && wp_verify_nonce($_POST['_wpnonce'], 'yourparty_control_action')) {
    if (defined('YOURPARTY_AZURACAST_BASE_URL') && defined('YOURPARTY_AZURACAST_API_KEY')) {
        $station_id = 1;
        $queue_id = intval($_POST['queue_item_id']); // AzuraCast unique ID
        $api_url = rtrim(YOURPARTY_AZURACAST_BASE_URL, '/') . "/api/station/$station_id/queue/$queue_id";
        
        // DELETE Request
        wp_remote_request($api_url, array_merge(yourparty_http_defaults(), [
            'method' => 'DELETE',
            'timeout' => 5
        ]));
    }
    wp_redirect(add_query_arg('queue_removed', '1')); exit;
}

// --- DATA FETCH ---
// Use centralized API URL function (Single Source of Truth)
$api_internal = function_exists('yourparty_api_base_url') ? yourparty_api_base_url() : 'https://api.yourparty.tech';
$api_public = 'https://api.yourparty.tech'; // Client-side accessible

// PHP Fetches use Internal
$api_base = $api_internal; 

$ratings_body = wp_remote_retrieve_body(wp_remote_get("$api_base/ratings", ['sslverify' => true, 'timeout' => 5]));
$ratings_data = json_decode($ratings_body, true);
if (!is_array($ratings_data)) $ratings_data = [];

$moods_body = wp_remote_retrieve_body(wp_remote_get("$api_base/moods", ['sslverify' => true, 'timeout' => 5]));
$moods_data = json_decode($moods_body, true);
if (!is_array($moods_data)) $moods_data = [];

$steer_body = wp_remote_retrieve_body(wp_remote_get("$api_base/control/steer", ['sslverify' => true, 'timeout' => 5]));
$steering_status = json_decode($steer_body, true);
if (!is_array($steering_status)) $steering_status = ['mode' => 'auto', 'target' => null];

// Fetch AzuraCast Queue
$azura_base = yourparty_azuracast_base_url();
$queue_response = wp_remote_get("$azura_base/api/station/1/queue", array_merge(yourparty_http_defaults(), ['timeout' => 5]));
$queue_data = json_decode(wp_remote_retrieve_body($queue_response), true);
if (!is_array($queue_data)) $queue_data = [];

// Fetch Now Playing
$np_response = wp_remote_get("$azura_base/api/nowplaying_static/radio.yourparty.json", array_merge(yourparty_http_defaults(), ['timeout' => 5]));
$np_data = json_decode(wp_remote_retrieve_body($np_response), true);
$now_playing = $np_data['now_playing']['song'] ?? null;
$listeners = $np_data['listeners']['current'] ?? 0;

// Calculate Voting Stats
$top_rated = null;
$most_votes = null;
$low_rated = null;
$total_votes = 0;

foreach ($ratings_data as $id => $data) {
    if (!is_array($data)) continue;
    $avg = $data['average'] ?? 0;
    $total = $data['total'] ?? 0;
    $total_votes += $total;
    
    if ($total >= 3) { // Minimum threshold for stats
        if (!$top_rated || $avg > ($top_rated['average'] ?? 0)) {
            $top_rated = array_merge($data, ['id' => $id]);
        }
        if (!$most_votes || $total > ($most_votes['total'] ?? 0)) {
            $most_votes = array_merge($data, ['id' => $id]);
        }
        if ($avg < 3 && (!$low_rated || $avg < ($low_rated['average'] ?? 5))) {
            $low_rated = array_merge($data, ['id' => $id]);
        }
    }
}


// Combine Data
$combined_data = [];
// Use ratings as base
if (isset($ratings_data) && is_array($ratings_data)) {
    foreach ($ratings_data as $id => $data) {
        if (!$id) continue;
        
        $title = $data['title'] ?? '';
        $artist = $data['artist'] ?? '';
        
        // Use song_id hash as fallback display name if no metadata
        $display_title = $title && $title !== 'Unknown' ? $title : substr($id, 0, 8) . '...';
        $display_artist = $artist && $artist !== 'Unknown' ? $artist : 'Unbekannt';

        $combined_data[$id] = [
            'title' => $display_title,
            'artist' => $display_artist,
            'path' => $data['path'] ?? '',
            'rating_avg' => $data['average'] ?? 0,
            'rating_total' => $data['total'] ?? 0,
            'top_mood' => $moods_data[$id]['top_mood'] ?? '-',
            'votes' => ($data['total'] ?? 0) + ($moods_data[$id]['total_votes'] ?? 0)
        ];
    }
}

// Sort by Votes (Rating * Total roughly, or just Avg)
uasort($combined_data, function ($a, $b) { 
    return $b['rating_avg'] <=> $a['rating_avg']; 
});


get_header(); 
?>

<!-- HIDE GLOBAL FOOTER/PLAYER ON THIS PAGE -->
<style>
    .site-footer, #mini-player { display: none !important; }
    /* Ensure no padding bump from global styles */
    body { padding-bottom: 0 !important; }
</style>

<!-- MAIN DASHBOARD UI -->
<div class="control-dashboard-v2">
    
    <!-- HEADER -->
    <header class="dashboard-header">
        <div class="header-content">
            <h1 class="brand-title">MISSION<span class="highlight">CONTROL</span></h1>
            <div class="user-badge">
                <span class="status-dot online"></span>
                CMDR <?php echo strtoupper(esc_html($current_user->display_name)); ?>
            </div>
        </div>
    </header>

    <!-- COMMUNITY VIBE DASHBOARD -->
    <section class="deck-panel vibe-overview">
        <div class="panel-head">
            <h3> COMMUNITY VIBE</h3>
            <span class="live-tag">LIVE</span>
        </div>
        <div class="vibe-content">
            <div class="dominant-mood" id="dominant-mood-display">
                <span class="label">DOMINANT</span>
                <span class="mood-name" id="dominant-mood-name">--</span>
                <span class="mood-icon" id="dominant-mood-icon"></span>
            </div>
            <div class="mood-bars" id="mood-bars">
                <!-- Populated by JavaScript -->
                <div class="mood-bar-item" style="opacity:0.5;">
                    <span class="mood-label">Loading...</span>
                    <div class="bar-container"><div class="bar-fill" style="width:0%;"></div></div>
                    <span class="vote-count">--</span>
                </div>
            </div>
            <div class="vibe-stats">
                <div class="stat">
                    <span class="stat-value"><?php echo number_format($total_votes); ?></span>
                    <span class="stat-label">TOTAL VOTES</span>
                </div>
                <div class="stat">
                    <span class="stat-value"><?php echo $listeners; ?></span>
                    <span class="stat-label">LISTENERS</span>
                </div>
                <div class="stat">
                    <span class="stat-value"><?php echo count($ratings_data); ?></span>
                    <span class="stat-label">TRACKS RATED</span>
                </div>
            </div>
            
            <!-- Voting Highlights -->
            <div class="voting-highlights">
                <?php if ($top_rated): ?>
                <div class="highlight-card top">
                    <span class="highlight-label"> TOP RATED</span>
                    <span class="highlight-title"><?php echo esc_html($top_rated['title'] ?? 'Unknown'); ?></span>
                    <span class="highlight-value"><?php echo number_format($top_rated['average'] ?? 0, 1); ?> </span>
                </div>
                <?php endif; ?>
                <?php if ($most_votes): ?>
                <div class="highlight-card votes">
                    <span class="highlight-label"> MOST VOTES</span>
                    <span class="highlight-title"><?php echo esc_html($most_votes['title'] ?? 'Unknown'); ?></span>
                    <span class="highlight-value"><?php echo $most_votes['total'] ?? 0; ?> votes</span>
                </div>
                <?php endif; ?>
                <?php if ($low_rated): ?>
                <div class="highlight-card low">
                    <span class="highlight-label"> LOW RATED</span>
                    <span class="highlight-title"><?php echo esc_html($low_rated['title'] ?? 'Unknown'); ?></span>
                    <span class="highlight-value"><?php echo number_format($low_rated['average'] ?? 0, 1); ?>  (<?php echo $low_rated['total'] ?? 0; ?>)</span>
                </div>
                <?php endif; ?>
            </div>
        </div>
    </section>
    
    <!-- RADIO QUEUE SECTION -->
    <section class="deck-panel queue-panel">
        <div class="panel-head">
            <h3> RADIO QUEUE</h3>
            <div style="display:flex; gap:10px; align-items:center;">
                <button id="open-library-btn" class="cyber-btn small" style="padding:5px 10px; font-size:10px; background:#222; border:1px solid #444; color:#fff; cursor:pointer;"> BROWSE</button>
                <span class="live-tag">LIVE</span>
            </div>
        </div>
        <div class="queue-content">
            <?php if ($now_playing): ?>
            <div class="now-playing-card">
                <span class="np-label">NOW PLAYING</span>
                <div class="np-info">
                    <span class="np-title"><?php echo esc_html($now_playing['title'] ?? 'Unknown'); ?></span>
                    <span class="np-artist"><?php echo esc_html($now_playing['artist'] ?? 'Unknown Artist'); ?></span>
                </div>
            </div>
            <?php endif; ?>
            
            <div class="queue-list">
                <?php if (empty($queue_data)): ?>
                <p class="no-queue">Queue empty or AutoDJ active</p>
                <?php else: ?>
                <?php foreach (array_slice(array_values($queue_data), 0, 8) as $i => $item): ?>
                <div class="queue-item" data-id="<?php echo esc_attr($item['id'] ?? $i); ?>">
                    <span class="queue-pos"><?php echo $i + 1; ?></span>
                    <div class="queue-track">
                        <span class="queue-title"><?php echo esc_html($item['song']['title'] ?? 'Unknown'); ?></span>
                        <span class="queue-artist"><?php echo esc_html($item['song']['artist'] ?? ''); ?></span>
                    </div>
                    <?php if ($is_admin): ?>
                    <div class="queue-actions">
                        <button class="queue-btn move-up" title="Move Up (Coming Soon)" disabled style="opacity:0.3; cursor:not-allowed;"></button>
                        <button class="queue-btn move-down" title="Move Down (Coming Soon)" disabled style="opacity:0.3; cursor:not-allowed;"></button>
                        
                        <form method="post" style="display:inline;" onsubmit="return confirm('Remove track from queue?');">
                            <?php wp_nonce_field('yourparty_control_action'); ?>
                            <input type="hidden" name="remove_queue_item" value="1">
                            <input type="hidden" name="queue_item_id" value="<?php echo esc_attr($item['id']); ?>">
                            <button type="submit" class="queue-btn remove" title="Remove Track"></button>
                        </form>
                    </div>
                    <?php endif; ?>
                </div>
                <?php endforeach; ?>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <div class="dashboard-grid">
        
        <!-- LEFT: INTELLIGENCE DECK -->
        <section class="deck-panel intelligence-deck">
            <div class="panel-head">
                <h3>LIBRARY INTEL</h3>
                <span class="live-tag">LIVE</span>
            </div>
            
            <div class="scrollable-table">
                <table class="cyber-table control-table">
                    <thead>
                        <tr>
                            <th>TRACK</th>
                            <th>MOOD</th>
                            <th>RATING</th>
                            <th>FILE</th>
                            <th>TREND</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach (array_slice($combined_data, 0, 50) as $id => $row): 
                            $score = $row['rating_avg'];
                            $color = $score >= 4.5 ? '#00ff88' : ($score >= 3 ? '#ffffff' : '#ff4444');
                            $path = $row['path'] ?? '';
                            $filename = basename($path);
                            // Clean path for display (hide internal structure)
                            $display_path = str_replace('/var/radio/music', 'M:', $path);
                        ?>
                        <tr>
                            <td>
                                <div class="track-info">
                                    <span class="track-title"><?php echo esc_html($row['title'] ?: $filename); ?></span>
                                    <span class="track-artist"><?php echo esc_html($row['artist']); ?></span>
                                </div>
                            </td>
                            <td><span class="badge-mood"><?php echo esc_html($row['top_mood']); ?></span></td>
                            <td style="color: <?php echo $color; ?>; font-weight:800;"><?php echo number_format($score, 1); ?></td>
                            <td>
                                <?php if ($path): ?>
                                <button class="cyber-btn small copy-btn" onclick="navigator.clipboard.writeText('<?php echo esc_js(str_replace('/', '\\', $display_path)); ?>'); alert('Copied Path: <?php echo esc_js($filename); ?>');">
                                     LINK
                                </button>
                                <?php endif; ?>
                            </td>
                            <td>
                                <!-- Sparkline simulated -->
                                <div class="mini-bar" style="width: <?php echo min(100, $row['votes'] * 5); ?>px;"></div>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                        <?php if (empty($combined_data)): ?>
                            <tr><td colspan="5" style="text-align:center; padding:20px; color:#666;">NO DATA AVAILABLE (Wait for Votes)</td></tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- MY PLAYLISTS (NTS-Lite Curator Feature) -->
        <section class="deck-panel playlist-deck">
            <div class="panel-head">
                <h3> MY PLAYLISTS</h3>
                <button id="create-playlist-btn" class="cyber-btn small" style="padding:5px 10px; font-size:10px; background:var(--emerald); color:#000; border:none; cursor:pointer;">+ NEW</button>
            </div>
            
            <div class="playlist-grid" id="playlist-grid">
                <div class="loading-state" style="text-align:center; padding:30px; color:#666;">
                    Loading playlists...
                </div>
            </div>
            
            <!-- Schedule Overview -->
            <div class="schedule-overview" style="margin-top:20px; border-top:1px solid #222; padding-top:15px;">
                <h4 style="font-size:11px; color:#888; margin-bottom:10px; letter-spacing:0.1em;"> UPCOMING SCHEDULE</h4>
                <div id="schedule-list" style="font-size:12px; color:#aaa;">
                    <div class="loading-state">Loading schedule...</div>
                </div>
            </div>
        </section>

        <!-- RIGHT: COMMAND DECK (Admin Only) -->
        <?php if ($is_admin): ?>
        <aside class="deck-panel command-deck">
            
            <!-- STEERING MODULE -->
            <div class="module steering-module">
                <div class="module-head">
                    <h3>VIBE STEERING</h3>
                    <div class="mode-indicator <?php echo $steering_status['mode'] === 'auto' ? 'auto' : 'manual'; ?>">
                        <?php echo strtoupper($steering_status['mode']); ?>
                    </div>
                </div>
                
                <form method="post" class="steering-grid">
                    <?php wp_nonce_field('yourparty_control_action'); ?>
                    <input type="hidden" name="set_steering" value="1">
                    <input type="hidden" name="steering_mode" id="steer_mode_input" value="<?php echo esc_attr($steering_status['mode']); ?>">
                    
                    <!-- Auto Button -->
                    <button type="submit" onclick="document.getElementById('steer_mode_input').value='auto'" 
                            class="steer-btn auto <?php echo $steering_status['mode'] === 'auto' ? 'active' : ''; ?>">
                         AUTO PILOT
                    </button>
                    
                    <!-- Manual Moods -->
                    <?php 
                    $moods = ['energetic'=>'', 'chill'=>'', 'dark'=>'', 'groovy'=>'', 'hypnotic'=>'', 'euphoric'=>''];
                    foreach($moods as $key => $icon): 
                        $isActive = $steering_status['mode'] === 'mood' && ($steering_status['target'] ?? '') === $key;
                    ?>
                    <button type="submit" name="steering_target" value="<?php echo $key; ?>" 
                            onclick="document.getElementById('steer_mode_input').value='mood'"
                            class="steer-btn mood <?php echo $isActive ? 'active' : ''; ?>">
                        <span class="icon"><?php echo $icon; ?></span>
                        <span class="label"><?php echo strtoupper($key); ?></span>
                    </button>
                    <?php endforeach; ?>
                </form>
            </div>

            <!-- EMERGENCY ACTIONS -->
            <div class="module action-module">
                <h3>EMERGENCY OVERRIDE</h3>
                <form method="post">
                    <?php wp_nonce_field('yourparty_control_action'); ?>
                    <button type="submit" name="skip_track" class="cyber-btn danger full-width">
                         FORCE SKIP TRACK
                    </button>
                </form>
            </div>
            
        </aside>
        <?php endif; ?>
        
    </div>
</div>

    <!-- VIBE TAGGING MODAL -->
    <dialog id="vibe-tag-modal" class="glass-modal">
        <div class="modal-head">
            <h3> TAG CURRENT VIBE</h3>
            <button onclick="document.getElementById('vibe-tag-modal').close()" class="close-btn"></button>
        </div>
        <div class="modal-body">
            <p class="track-preview">
                Target: <span id="modal-track-title" class="highlight">Unknown Track</span>
                <div id="modal-track-genre" style="display:none;"></div>
            </p>
            <div class="mood-grid">
                <!-- Row 1 -->
                <button class="mood-option energy" onclick="window.controlPanel.submitTag('Energy')">
                    <span class="icon"></span>
                    <span class="label">ENERGY</span>
                </button>
                <button class="mood-option chill" onclick="window.controlPanel.submitTag('Chill')">
                    <span class="icon"></span>
                    <span class="label">CHILL</span>
                </button>
                <button class="mood-option euphoric" onclick="window.controlPanel.submitTag('Euphoric')">
                    <span class="icon"></span>
                    <span class="label">EUPHORIC</span>
                </button>
                
                <!-- Row 2 -->
                <button class="mood-option dark" onclick="window.controlPanel.submitTag('Dark')">
                    <span class="icon"></span>
                    <span class="label">DARK</span>
                </button>
                <button class="mood-option groovy" onclick="window.controlPanel.submitTag('Groovy')">
                    <span class="icon"></span>
                    <span class="label">GROOVY</span>
                </button>
                <button class="mood-option hypnotic" onclick="window.controlPanel.submitTag('Hypnotic')">
                    <span class="icon"></span>
                    <span class="label">HYPNOTIC</span>
                </button>
            </div>
            <div id="tag-status" class="status-msg"></div>
        </div>
    </dialog>

    <!-- LIBRARY BROWSER MODAL -->
    <dialog id="library-modal" class="glass-modal library-modal">
        <div class="modal-head">
            <h3> LIBRARY BROWSER</h3>
            <button onclick="document.getElementById('library-modal').close()" class="close-btn"></button>
        </div>
        <div class="modal-body" style="text-align:left;">
            <div class="search-box" style="margin-bottom:20px;">
                <input type="text" id="lib-search-input" placeholder="Search Title or Artist..." class="cyber-input" style="width:100%; border-color:#333;">
            </div>
            <div id="lib-search-results" class="results-grid" style="max-height:400px; overflow-y:auto; display:flex; flex-direction:column; gap:5px;">
                <!-- Results go here -->
                <div style="text-align:center; color:#666; font-size:11px; padding:20px;">Type query to search tracks...</div>
            </div>
        </div>
    </dialog>

</div>

<style>
/* MODAL CSS */
.glass-modal {
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 0;
    width: 90%;
    max-width: 500px; /* Slight increase for better grid */
    color: #fff;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    position: fixed; 
    inset: 0; margin: auto; 
    z-index: 2000;
}
.glass-modal::backdrop { background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); }
.modal-head {
    padding: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.modal-head h3 { margin: 0; font-size: 14px; letter-spacing: 0.1em; color: var(--emerald); }
.close-btn { background: none; border: none; color: #666; cursor: pointer; font-size: 18px; }
.close-btn:hover { color: #fff; }

.modal-body { padding: 30px 20px; text-align: center; }
.track-preview { margin-bottom: 30px; font-size: 13px; color: #888; }
.track-preview .highlight { color: #fff; font-weight: bold; display: block; margin-top: 5px; font-size: 16px; }

.mood-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
.mood-option {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 15px 10px;
    cursor: pointer;
    transition: all 0.2s;
    color: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}
.mood-option:hover { transform: translateY(-5px); background: rgba(255,255,255,0.1); }
.mood-option .icon { font-size: 24px; }
.mood-option .label { font-size: 10px; font-weight: bold; letter-spacing: 0.1em; }

/* Colors */
.mood-option.energy:hover { border-color: #ffaa00; box-shadow: 0 0 20px rgba(255,170,0,0.3); }
.mood-option.chill:hover { border-color: #00aaff; box-shadow: 0 0 20px rgba(0,170,255,0.3); }
.mood-option.euphoric:hover { border-color: #ff00ff; box-shadow: 0 0 20px rgba(255,0,255,0.3); }
.mood-option.dark:hover { border-color: #555; box-shadow: 0 0 20px rgba(100,100,100,0.3); }
.mood-option.groovy:hover { border-color: #00ffaa; box-shadow: 0 0 20px rgba(0,255,170,0.3); }
.mood-option.hypnotic:hover { border-color: #4400ff; box-shadow: 0 0 20px rgba(68,0,255,0.3); }

.status-msg { margin-top: 20px; font-size: 12px; height: 15px; color: var(--emerald); }
</style>

<!-- STICKY MONITOR FOOTER (GLOBAL) -->

<!-- REFACTORED TO MATCH USER CSS CLASS NAMES -->
<div class="control-footer">
    <div class="footer-left">
        <div class="now-playing-monitor">
             <canvas id="inline-visualizer" style="width:40px; height:20px; margin-right:5px; opacity:0.7;"></canvas>
             <div class="monitor-info">
                 <span style="font-size:9px; color:var(--emerald); letter-spacing:1px; font-weight:bold;">ON AIR</span>
                 <span id="track-title" class="skeleton">WAITING FOR SIGNAL...</span>
                 <span id="track-artist" style="display:none;">Artist</span>
             </div>
             <button id="mood-tag-button" class="footer-btn" style="margin-left: 10px; border-color: var(--emerald); color: var(--emerald);" title="Tag Current Vibe">
                 &#127991; TAG
             </button>
        </div>
    </div>

    <div class="footer-center">
        <button id="mini-play-toggle" class="footer-btn">
            <span class="play-state-icon"></span> MONITOR
        </button>
    </div>

    <div class="footer-right">
        <div class="volume-control">
            VOL <input type="range" id="monitor-volume" min="0" max="100" value="80">
        </div>
        <div class="status-metric">
            <span class="label">DB</span>
            <span class="value">OK</span>
        </div>
        <div class="status-metric">
            <span class="label">API</span>
            <span class="value">LINKED</span>
        </div>
    </div>
</div>

<style>
/* DASHBOARD CSS (Scoped) */
:root {
    --bg-dark: #050505;
    --glass: rgba(20,20,20,0.7);
    --border: rgba(255,255,255,0.08);
    --primary: #00ff88;
    --danger: #ff4444;
    --emerald: #00ff88;
}

body { background: var(--bg-dark); }

.control-dashboard-v2 {
    padding: 100px 20px 120px; /* Pad for Fixed Header/Footer */
    max-width: 1400px;
    margin: 0 auto;
}

/* Header */
.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}
.brand-title { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; margin: 0; }
.brand-title .highlight { color: var(--primary); }
.user-badge { display: flex; align-items: center; font-size: 12px; letter-spacing: 0.1em; color: #888; }
.status-dot { width: 8px; height: 8px; background: var(--primary); border-radius: 50%; margin-right: 8px; box-shadow: 0 0 10px var(--primary); }

/* Grid */
.dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}
@media(max-width: 900px) { .dashboard-grid { grid-template-columns: 1fr; } }

/* Panels */
.deck-panel {
    background: var(--glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 0;
    overflow: hidden;
}
.panel-head {
    padding: 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.panel-head h3 { margin: 0; font-size: 14px; letter-spacing: 0.1em; color: #aaa; }
.live-tag { background: #ff0000; color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 2px; font-weight: bold; animation: pulse 2s infinite; }

/* Table */
.scrollable-table { height: 600px; overflow-y: auto; }
.cyber-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cyber-table th { text-align: left; padding: 15px 20px; color: #666; font-size: 10px; letter-spacing: 0.1em; position: sticky; top: 0; background: #0a0a0a; z-index: 10; }
.cyber-table td { padding: 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.02); }
.cyber-table tr:hover { background: rgba(255,255,255,0.03); }
.track-title { display: block; font-weight: 600; color: #fff; }
.track-artist { display: block; font-size: 11px; color: var(--primary); opacity: 0.8; }
.badge-mood { font-size: 10px; background: #222; padding: 2px 6px; border-radius: 4px; color: #aaa; border: 1px solid #333; }
.mini-bar { height: 4px; background: #333; border-radius: 2px; position: relative; }
.mini-bar::after { content: ''; position: absolute; left: 0; top: 0; height: 100%; width: 100%; background: var(--primary); border-radius: 2px; opacity: 0.5; }

/* Modules */
.module { padding: 20px; border-bottom: 1px solid var(--border); }
.module:last-child { border-bottom: none; }
.module-head { display: flex; justify-content: space-between; margin-bottom: 15px; }
.module-head h3 { margin: 0; font-size: 12px; color: #888; letter-spacing: 0.1em; }

/* Steering Grid */
.steering-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.steer-btn { 
    background: #111; border: 1px solid #333; color: #888; 
    padding: 15px; border-radius: 8px; cursor: pointer; 
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px;
    transition: all 0.2s;
}
.steer-btn.auto { grid-column: span 2; background: #1a1a1a; color: #fff; }
.steer-btn:hover { border-color: #555; background: #181818; }
.steer-btn.active { 
    background: var(--primary); color: #000; border-color: var(--primary); 
    box-shadow: 0 0 20px rgba(0,255,136,0.3); 
}
.steer-btn.active .icon { color: #000; }
.steer-btn .label { font-size: 10px; font-weight: bold; letter-spacing: 0.1em; }

/* Action Btn */
.cyber-btn.danger { background: rgba(255,68,68,0.1); color: #ff4444; border: 1px solid #ff4444; }
.cyber-btn.danger:hover { background: #ff4444; color: #fff; box-shadow: 0 0 20px rgba(255,68,68,0.4); }


@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

/* USER CSS (Injected) */
.mood-btn { background: #1a1a1a; border: 1px solid #333; color: #ccc; padding: 8px; font-size: 11px; cursor: pointer; border-radius: 4px; text-align: left; } 
.mood-btn:hover { border-color: #666; } 
.nav-tabs { display: flex; gap: 2px; background: #111; padding: 4px; border-radius: 4px; } 
.tab-btn { background: transparent; border: none; color: #666; padding: 6px 12px; font-family: var(--font-display); font-size: 10px; font-weight: bold; cursor: pointer; border-radius: 2px; } 
.tab-btn.active { background: #222; color: #fff; } 
.tab-btn:hover:not(.active) { color: #999; } 
.data-table-wrapper { display: none; } 
.data-table-wrapper.active { display: block; } 
.mood-btn.active { border-color: var(--emerald); color: var(--emerald); background: rgba(16, 185, 129, 0.1); } 
.control-footer { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background: rgba(10, 10, 10, 0.95); border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center; padding: 0 20px; z-index: 1000; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); } 
.footer-left, .footer-center, .footer-right { display: flex; align-items: center; gap: 20px; } 
.footer-btn { background: #222; border: 1px solid #333; color: #fff; padding: 6px 12px; font-family: var(--font-display); font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; border-radius: 2px; transition: all 0.2s; } 
.footer-btn:hover { background: #333; border-color: #555; } 
.footer-btn.danger { border-color: #aa0000; color: #ff4444; } 
.footer-btn.danger:hover { background: #330000; } 
.footer-btn.warning { border-color: #aa5500; color: #ffaa00; } 
.now-playing-monitor { display: flex; align-items: center; gap: 10px; background: rgba(0, 0, 0, 0.5); padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05); } 
.monitor-info { display: flex; flex-direction: column; line-height: 1.1; width: 150px; } 
#monitor-title { font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } 
.volume-control { display: flex; align-items: center; gap: 8px; font-size: 10px; color: #666; } 
input[type=range] { height: 4px; -webkit-appearance: none; background: #333; border-radius: 2px; width: 80px; } 
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 10px; height: 10px; background: var(--emerald); border-radius: 50%; cursor: pointer; } 
.status-metric { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.1; } 
.status-metric .label { font-size: 9px; color: #666; } 
.status-metric .value { font-size: 12px; color: var(--emerald); font-family: monospace; }

/* VIBE OVERVIEW DASHBOARD */
.vibe-overview { margin-bottom: 20px; }
.vibe-content { padding: 20px; display: grid; grid-template-columns: 200px 1fr 200px; gap: 30px; align-items: center; }
@media(max-width: 900px) { .vibe-content { grid-template-columns: 1fr; gap: 20px; } }

.dominant-mood { 
    text-align: center; 
    padding: 20px; 
    background: rgba(0,255,136,0.05); 
    border: 1px solid rgba(0,255,136,0.2); 
    border-radius: 12px; 
}
.dominant-mood .label { 
    display: block; 
    font-size: 10px; 
    color: #666; 
    letter-spacing: 0.1em; 
    margin-bottom: 8px; 
}
.dominant-mood .mood-name { 
    display: block; 
    font-size: 18px; 
    font-weight: 800; 
    color: var(--emerald); 
    text-transform: uppercase; 
    letter-spacing: 0.05em; 
}
.dominant-mood .mood-icon { 
    font-size: 32px; 
    margin-top: 10px; 
    display: block; 
}

.mood-bars { display: flex; flex-direction: column; gap: 8px; }
.mood-bar-item { 
    display: grid; 
    grid-template-columns: 100px 1fr 40px; 
    gap: 10px; 
    align-items: center; 
}
.mood-label { 
    font-size: 11px; 
    color: #888; 
    text-transform: uppercase; 
    letter-spacing: 0.05em; 
}
.bar-container { 
    height: 12px; 
    background: rgba(255,255,255,0.05); 
    border-radius: 6px; 
    overflow: hidden; 
}
.bar-fill { 
    height: 100%; 
    background: linear-gradient(90deg, var(--emerald), #00ccaa); 
    border-radius: 6px; 
    transition: width 0.5s ease; 
}
.vote-count { 
    font-size: 12px; 
    font-weight: bold; 
    color: #fff; 
    text-align: right; 
    font-family: monospace; 
}

.vibe-stats { 
    display: flex; 
    flex-direction: column; 
    gap: 15px; 
}
.vibe-stats .stat { 
    text-align: center; 
    padding: 10px; 
    background: rgba(255,255,255,0.02); 
    border-radius: 8px; 
}
.vibe-stats .stat-value { 
    display: block; 
    font-size: 20px; 
    font-weight: 800; 
    color: #fff; 
}
.vibe-stats .stat-label { 
    font-size: 10px; 
    color: #666; 
    letter-spacing: 0.1em; 
}

/* VOTING HIGHLIGHTS */
.voting-highlights {
    display: flex;
    gap: 15px;
    margin-top: 20px;
    padding: 0 20px 20px;
}
.highlight-card {
    flex: 1;
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
}
.highlight-card.top { border-color: rgba(0,255,136,0.3); }
.highlight-card.votes { border-color: rgba(255,165,0,0.3); }
.highlight-card.low { border-color: rgba(255,68,68,0.3); }
.highlight-label { display: block; font-size: 10px; color: #666; margin-bottom: 8px; }
.highlight-title { display: block; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.highlight-value { display: block; font-size: 16px; font-weight: 800; margin-top: 5px; }
.highlight-card.top .highlight-value { color: var(--emerald); }
.highlight-card.votes .highlight-value { color: #ffa500; }
.highlight-card.low .highlight-value { color: var(--danger); }

/* QUEUE PANEL */
.queue-panel { margin-bottom: 20px; }
.queue-content { padding: 20px; }
.now-playing-card {
    background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,200,100,0.05));
    border: 1px solid rgba(0,255,136,0.2);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 20px;
}
.np-label { display: block; font-size: 10px; color: var(--emerald); letter-spacing: 0.1em; margin-bottom: 8px; }
.np-info { display: flex; flex-direction: column; }
.np-title { font-size: 16px; font-weight: 700; }
.np-artist { font-size: 13px; color: #888; }

.queue-list { display: flex; flex-direction: column; gap: 8px; }
.no-queue { color: #666; text-align: center; padding: 30px; font-style: italic; }
.queue-item {
    display: flex;
    align-items: center;
    gap: 15px;
    background: rgba(0,0,0,0.2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 15px;
    transition: all 0.2s;
}
.queue-item:hover { background: rgba(255,255,255,0.03); border-color: rgba(255,255,255,0.15); }
.queue-pos { width: 24px; height: 24px; background: #222; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: #888; }
.queue-track { flex: 1; overflow: hidden; }
.queue-title { display: block; font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.queue-artist { display: block; font-size: 12px; color: #888; }
.queue-actions { display: flex; gap: 5px; }
.queue-btn { width: 28px; height: 28px; background: #222; border: 1px solid #333; color: #888; font-size: 12px; cursor: pointer; border-radius: 4px; transition: all 0.2s; }
.queue-btn:hover { background: #333; color: #fff; }
.queue-btn.remove:hover { background: #330000; border-color: var(--danger); color: var(--danger); }

@media(max-width: 600px) {
    .voting-highlights { flex-direction: column; }
    .queue-actions { display: none; }
}

/* iPhone X / Mobile Optimization */
@media(max-width: 480px) {
    .control-dashboard-v2 {
        padding: 80px 15px 140px; /* Optimized bottom padding */
    }
    .brand-title { font-size: 18px; }
    .user-badge { display: none; }
    
    /* Tiles / Panels */
    .vibe-overview, .queue-panel, .deck-panel {
        margin-bottom: 15px; /* Consistent smaller gap on mobile */
    }
    .dashboard-grid { display: flex; flex-direction: column; gap: 15px; }

    /* Vibe Dashboard Compact */
    .vibe-content { 
        display: flex; 
        flex-direction: column; 
        gap: 15px; 
        padding: 15px; 
    }
    
    .dominant-mood { padding: 15px; }
    
    .vibe-stats {
        flex-direction: row;
        justify-content: space-between;
        gap: 10px;
    }
    .vibe-stats .stat { flex: 1; padding: 10px 5px; } /* Better touch padding */
    .vibe-stats .stat-value { font-size: 16px; }

    /* Table: Hide complex columns */
    .cyber-table th:nth-child(4), .cyber-table td:nth-child(4), /* File */
    .cyber-table th:nth-child(5), .cyber-table td:nth-child(5)  /* Trend */
    { display: none; }
    
    .track-title { font-size: 13px; max-width: 140px; }
    .track-artist { font-size: 10px; }

    /* Footer: Stacked "Mission Control" Layout */
    .control-footer {
        flex-direction: column;
        height: auto;
        padding: 15px 20px 25px; /* More bottom padding for Safe Area (Home Indicator) */
        gap: 15px;
        background: rgba(10, 10, 10, 0.98);
        border-top: 1px solid rgba(255,255,255,0.15);
    }

    /* Footer Row 1: Player Monitor */
    .footer-left { 
        width: 100%; 
        justify-content: center;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 15px;
    }
    .now-playing-monitor { 
        width: 100%; 
        max-width: none; 
        justify-content: space-between;
        background: transparent;
        border: none;
        padding: 0;
    }
    .monitor-info { width: auto; flex: 1; text-align: left; }

    /* Footer Row 2: Controls */
    .footer-center {
        display: flex;
        width: 100%;
        justify-content: space-between;
        gap: 10px;
    }
    .footer-right { display: none !important; } /* Hard hide volume on mobile */

    /* Big Touch Buttons */
    .footer-btn {
        flex: 1;
        padding: 14px 0;
        font-size: 11px; /* Slightly smaller text */
        border-radius: 6px;
        white-space: nowrap;
    }
    
    /* Queue: Simplified */
    .queue-item { padding: 10px; }
    .queue-actions { display: none; }
    
    /* Footer Monitor Fixes */
    .now-playing-monitor { padding: 5px 0; }
    #monitor-title { max-width: 180px; } /* Force truncate */
}
</style>

<!-- MONITOR AUDIO ENGINE -->
<audio id="monitor-stream" preload="none">
    <source src="<?php echo esc_url($stream_url); ?>" type="audio/mpeg">
</audio>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // === MONITOR BUTTON LOGIC ===
    const monitorBtn = document.getElementById('mini-play-toggle');
    const audio = document.getElementById('monitor-stream');
    const volSlider = document.getElementById('monitor-volume');
    const icon = monitorBtn.querySelector('.play-state-icon');
    
    if(monitorBtn && audio) {
        monitorBtn.addEventListener('click', function() {
            if (audio.paused) {
                audio.play().then(() => {
                    icon.textContent = '';
                    monitorBtn.classList.add('active');
                    monitorBtn.style.borderColor = 'var(--emerald)';
                }).catch(e => console.error("Stream Error:", e));
            } else {
                audio.pause();
                icon.textContent = '';
                monitorBtn.classList.remove('active');
                monitorBtn.style.borderColor = '';
            }
        });
        
        // Volume
        if(volSlider) {
            volSlider.addEventListener('input', (e) => audio.volume = e.target.value / 100);
            audio.volume = volSlider.value / 100;
        }
    }
});
</script>

<?php get_footer(); ?>

<script>
document.addEventListener('DOMContentLoaded', function () {
    const tableBody=document.querySelector('.control-table tbody');
    const wpNonce='<?php echo wp_create_nonce('wp_rest'); ?>';
    
    // API Endpoints
    // API Endpoints
    const apiGeneric = '<?php echo esc_url(rest_url('yourparty/v1')); ?>';
    const apiLib = apiGeneric + '/library';
    const apiStatus = apiGeneric + '/status';

    // --- LIBRARY TABLE ---
    function updateLibrary() {
        fetch(apiLib, {
            credentials: 'same-origin',
            headers: { 'X-WP-Nonce': wpNonce }
        })
        .then(r => r.json())
        .then(tracks => {
            if (!Array.isArray(tracks) || tracks.length === 0) {
                 if (!tableBody.querySelector('.empty-state')) {
                    tableBody.innerHTML='<tr><td colspan="5" class="empty-state">NO DATA YET</td></tr>';
                 }
                 return;
            }

            // Map & Sort
            const rows = tracks.map(t => {
                const meta = t.metadata || {};
                const rating = t.rating || {};
                const moods = t.moods || {};

                return {
                    id: t.song_id || t._id,
                    title: meta.title || 'Unknown',
                    artist: meta.artist || 'Unknown',
                    top: moods.top_mood || '-',
                    avg: parseFloat(rating.average || 0),
                    votes: parseInt(rating.total || 0), // Rating count
                    path: t.file_path,
                    combinedScore: (rating.total || 0) // Sort by popularity
                };
            });

            // Sort by most rated/popular
            rows.sort((a, b) => b.combinedScore - a.combinedScore);

            const e=str=> str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';

            const html = rows.map(row => {
                 const color = row.avg >= 4 ? 'var(--emerald)' : (row.avg <= 2 && row.votes > 0 ? '#ff4444' : '#888');
                 // Ensure we escape ID for button
                 const safeId = e(row.id);
                 return `<tr>
                    <td class="mono-font" title="${e(row.path)}">${e(row.artist)} - ${e(row.title)}</td>
                    <td><span class="mood-badge">${e(row.top)}</span></td>
                    <td><span style="color: ${color}; font-weight: bold;"> ${row.avg.toFixed(1)}</span></td>
                    <td><button class="cyber-btn small" onclick="openMoodDialog('${safeId}', '${e(row.title.replace(/'/g, "\\'"))}', '${e(row.artist.replace(/'/g, "\\'"))}')">TAG</button></td>
                    <td><div class="mini-bar" style="width: ${Math.min(100, row.votes * 10)}px;"></div></td>
                </tr>`;
            }).join('');

            tableBody.innerHTML = html;
        })
        .catch(err => {
            console.warn('Library Fetch Failed:', err);
        });
    }

    // Update Library occasionally (every 30s is enough, it's big)
    updateLibrary();
    setInterval(updateLibrary, 30000);

    // --- MONITOR / FOOTER ---
    const monitorTitle = document.getElementById('monitor-title');
    const monitorStatus = document.querySelector('.status-indicator span');
    
    function updateMonitor() {
        // console.log("Polling Status...");
        fetch(apiStatus, { credentials: 'same-origin' })
            .then(r => r.json())
            .then(data => {
                const np = data.now_playing?.song || {};
                if (monitorTitle) {
                    if (np.title && np.artist) {
                        monitorTitle.textContent = `${np.artist} - ${np.title}`;
                        monitorTitle.classList.add('active');
                    } else {
                        monitorTitle.textContent = "WAITING FOR SIGNAL...";
                        monitorTitle.classList.remove('active');
                    }
                }
                
                if (monitorStatus) {
                    // Update ON AIR / OFF AIR
                    if (data.is_online || (data.listeners && data.listeners.total !== undefined)) {
                        monitorStatus.textContent = "ON AIR";
                        monitorStatus.style.color = "var(--emerald)";
                         // Trigger visualizer loop if not running? handled by StreamController usually
                    } else {
                         monitorStatus.textContent = "OFFLINE";
                         monitorStatus.style.color = "red";
                    }
                }
            })
            .catch(e => console.error("Monitor Poll Error", e));
    }
    
    // Poll Monitor frequently (2s)
    setInterval(updateMonitor, 2000);
    updateMonitor();

    // --- VIBE OVERVIEW UPDATES ---
    // (Existing Vibe logic remains mostly same, just ensuring fetch works)
    const moodIcons = {
        'energetic': '', 'chill': '', 'euphoric': '', 'dark': '',
        'groovy': '', 'melodic': '', 'hypnotic': '', 'uplifting': '',
        'atmospheric': '', 'driving': '', 'trashey': '',
        'dislike': ''
    };

    function updateVibeOverview() {
        // Use the public mood-stats endpoint (same as frontend)
        fetch('/wp-json/yourparty/v1/mood-stats')
            .then(r => r.json())
            .then(data => {
                // Backend returns: { votes: { energy: 0, ... }, total: 0, dominant: '...' }
                const votes = data.votes || {};
                
                // Convert votes object to array for sorting
                const sortedMoods = Object.entries(votes)
                    .map(([tag, count]) => ({ tag, count }))
                    .sort((a, b) => b.count - a.count);

                if (sortedMoods.length > 0) {
                    const dominant = sortedMoods[0];
                    const nameEl = document.getElementById('dominant-mood-name');
                    const iconEl = document.getElementById('dominant-mood-icon');
                    
                    if (nameEl) nameEl.textContent = dominant.count > 0 ? dominant.tag.toUpperCase() : 'NEUTRAL';
                    if (iconEl) iconEl.textContent = dominant.count > 0 ? (moodIcons[dominant.tag] || '') : '';
                    
                    const barsContainer = document.getElementById('mood-bars');
                    if (barsContainer) {
                        const maxCount = dominant.count > 0 ? dominant.count : 1;
                        
                        const barsHtml = sortedMoods.slice(0, 6).map(m => {
                           const pct = Math.round((m.count / maxCount) * 100);
                           const icon = moodIcons[m.tag] || '';
                           const isDislike = m.tag === 'dislike';
                           const barColor = isDislike ? 'var(--danger)' : 'linear-gradient(90deg, var(--emerald), #00ccaa)';
                           const labelColor = isDislike ? 'var(--danger)' : '#888';
                           
                           return `
                               <div class="mood-bar-item">
                                   <span class="mood-label" style="color:${labelColor}">${icon} ${m.tag}</span>
                                   <div class="bar-container"><div class="bar-fill" style="width:${pct}%; background:${barColor}"></div></div>
                                   <span class="vote-count">${m.count}</span>
                               </div>`;
                        }).join('');
                        
                        barsContainer.innerHTML = barsHtml;
                    }
                }
            })
            .catch(err => console.warn('Vibe fetch failed:', err));
    }
    setInterval(updateVibeOverview, 3000);
    updateVibeOverview();

    // --- GLOBAL HELPERS (for button clicks) ---
    window.openMoodDialog = function(id, title, artist) {
        // Dispatch event for Main App to handle if loaded
        const event = new CustomEvent('open-mood-tagger', { 
            detail: { id, title, artist } 
        });
        window.dispatchEvent(event);
        
        // Fallback: If no listener, alert user (or implement dialog here if missing)
        // Usually YourPartyAppInstance handles this.
        // console.log("Requesting Mood Tag for", id);
    };
});
</script>