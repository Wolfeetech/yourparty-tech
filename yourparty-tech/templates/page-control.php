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
        .glass-panel { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); width: 100%; max-width: 400px; }
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
}

// --- DATA FETCH ---
// Internal IP for PHP Server-Side Requests (Docker Network / Localhost)
$api_base_internal = 'http://192.168.178.211:8000'; 

// Public URL for Client-Side JS Requests (Proxied via WordPress)
$api_base_public = rest_url('yourparty/v1/control');

$ratings_body = wp_remote_retrieve_body(wp_remote_get("$api_base_internal/ratings", ['sslverify' => false, 'timeout' => 5]));
$ratings_data = json_decode($ratings_body, true);
if (!is_array($ratings_data)) $ratings_data = [];

$moods_body = wp_remote_retrieve_body(wp_remote_get("$api_base_internal/moods", ['sslverify' => false, 'timeout' => 5]));
$moods_data = json_decode($moods_body, true);
if (!is_array($moods_data)) $moods_data = [];

$steer_body = wp_remote_retrieve_body(wp_remote_get("$api_base_internal/control/steer", ['sslverify' => false, 'timeout' => 5]));
$steering_status = json_decode($steer_body, true);
if (!is_array($steering_status)) $steering_status = ['mode' => 'auto', 'target' => null];


// Combine Data
$combined_data = [];
// Use ratings as base
if (isset($ratings_data) && is_array($ratings_data)) {
// ... (rest of logic same) ...
}

// ... lines 112-421 unchanged ...

<script>
document.addEventListener('DOMContentLoaded', function () {
    const tableBody=document.querySelector('.control-table tbody');
    // CRITICAL FIX: Use Public WP REST Endpoint for Client JS
    const apiBase='<?php echo esc_js($api_base_public); ?>';
    
    console.log('[Control] API Base:', apiBase);

    function updateData() {
    foreach ($ratings_data as $id => $data) {
        if (!$id) continue;
        
        $title = $data['title'] ?? 'Unknown';
        $artist = $data['artist'] ?? 'Unknown';
        
        // FILTER: Skip useless data (User Request)
        if ($title === 'Unknown' && $artist === 'Unknown') continue;
        if ($title === 'Unknown Track' && $artist === 'Unknown Artist') continue;

        $combined_data[$id] = [
            'title' => $title,
            'artist' => $artist,
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
                                    📂 LINK
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
                        🤖 AUTO PILOT
                    </button>
                    
                    <!-- Manual Moods -->
                    <?php 
                    $moods = ['energetic'=>'🔥', 'chill'=>'🧊', 'dark'=>'🌑', 'groovy'=>'🌊', 'hypnotic'=>'🌀', 'euphoric'=>'✨'];
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
                        ⏭ FORCE SKIP TRACK
                    </button>
                </form>
            </div>
            
        </aside>
        <?php endif; ?>
        
    </div>
</div>

<!-- STICKY MONITOR FOOTER (GLOBAL) -->
<!-- REFACTORED TO MATCH USER CSS CLASS NAMES -->
<div class="control-footer">
    <div class="footer-left">
        <div class="now-playing-monitor">
             <canvas id="monitor-visualizer" style="width:40px; height:20px; margin-right:5px; opacity:0.7;"></canvas>
             <div class="monitor-info">
                 <span style="font-size:9px; color:var(--emerald); letter-spacing:1px; font-weight:bold;">ON AIR</span>
                 <span id="monitor-title">WAITING FOR SIGNAL...</span>
             </div>
        </div>
    </div>

    <div class="footer-center">
        <button id="monitor-play-btn" class="footer-btn">▶ MONITOR</button>
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
.control-footer { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background: rgba(10, 10, 10, 0.95); border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center; padding: 0 20px; z-index: 1000; backdrop-filter: blur(10px); } 
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
</style>

<?php get_footer(); ?>

<script>
document.addEventListener('DOMContentLoaded', function () {
    const tableBody=document.querySelector('.control-table tbody');
    const apiBase='<?php echo esc_js($api_base_public); ?>';

    function updateData() {
        Promise.all([ 
            fetch(`${apiBase}/ratings`).then(r=> r.json()),
            fetch(`${apiBase}/moods`).then(r=> r.json())
        ]).then(([ratings, moods])=> {
            const allIds=new Set([...Object.keys(ratings), ...Object.keys(moods)]);

            // If empty
            if (allIds.size===0) {
                if (!tableBody.querySelector('.empty-state')) {
                    tableBody.innerHTML='<tr><td colspan="5" class="empty-state">NO DATA YET</td></tr>';
                }
                return;
            }

            // Map data
            const rows=Array.from(allIds).map(id=> {
                const r=ratings[id] || {};
                const m=moods[id] || {};

                // Client Side Filter for noise
                if ( (!r.title || r.title==='Unknown') && (!m.title) ) return null;

                return {
                    id,
                    title: m.title || r.title || 'Unknown',
                    artist: m.artist || r.artist || 'Unknown',
                    top: m.top_mood || '-',
                    genre: m.top_genre || '-',
                    avg: parseFloat(r.average || 0),
                    total: parseInt(r.total || 0),
                    votes: parseInt(m.total_votes || 0),
                    combinedScore: (parseInt(m.total_votes || 0) + parseInt(r.total || 0))
                };
            }).filter(Boolean);

            // Sort
            rows.sort((a, b)=> b.combinedScore - a.combinedScore);

            // Rebuild HTML
            const e=str=> str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';

            const html=rows.map(row=> {
                const color=row.avg >=4 ? 'var(--emerald)' : (row.avg <=2 ? '#ff4444' : '#888');
                const display = `${row.artist} - ${row.title}`;

                return `<tr>
                    <td class="mono-font" title="${e(row.id)}">${e(display)}</td>
                    <td><span class="mood-badge">${e(row.top)}</span></td>
                    <td><span style="color: ${color}; font-weight: bold;">★ ${row.avg.toFixed(1)}</span></td>
                    <td><button class="cyber-btn small">FILES</button></td>
                    <td><div class="mini-bar" style="width: ${Math.min(100, row.votes * 5)}px;"></div></td>
                </tr>`;
            }).join('');

            tableBody.innerHTML=html;
        }).catch(err=> console.error('Data pull failed', err));
    }

    // Update every 5 seconds
    setInterval(updateData, 5000);
    updateData(); // Initial call

    // --- FOOTER CONTROLS ---
    const monitorPlayBtn=document.getElementById('monitor-play-btn');
    const volSlider=document.getElementById('monitor-volume');
    const monitorTitle=document.getElementById('monitor-title');
    const monitorCanvas=document.getElementById('monitor-visualizer');
    let monitorCtx;

    if(monitorCanvas) monitorCtx=monitorCanvas.getContext('2d');

    // Check StreamController availability
    let sc = null;
    if (window.YourPartyAppInstance && window.YourPartyAppInstance.modules.stream) {
        sc = window.YourPartyAppInstance.modules.stream;
    } else if (window.StreamController) {
        sc = window.StreamController;
    }

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
        if(song && monitorTitle) {
            monitorTitle.textContent=song.title;
        }
    });

    // Mini Visualizer Loop
    function drawMiniVis() {
        requestAnimationFrame(drawMiniVis);
        if( !monitorCtx || !sc) return;
        const analyser=sc.getAnalyser();

        if( !analyser) {
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
});
</script>