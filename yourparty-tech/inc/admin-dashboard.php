<?php
/**
 * YourParty Tech - Radio Control Dashboard
 * 
 * Verwaltung der Mood-Tags und Playlist-Generierung.
 */

if (!defined('ABSPATH')) {
    exit;
}

// Register Menu Page
add_action('admin_menu', function () {
    add_menu_page(
        'Radio Control',
        'Radio Control',
        'manage_options',
        'yourparty-radio-control',
        'yourparty_render_admin_page',
        'dashicons-playlist-audio',
        6
    );
});

// Render Page
function yourparty_render_admin_page()
{
    $moods_data = get_option('yourparty_mood_tags', []);

    // Sort by total votes desc
    uasort($moods_data, function ($a, $b) {
        return ($b['total_votes'] ?? 0) - ($a['total_votes'] ?? 0);
    });

    // Handle Playlist Generation
    $generated_playlist = '';
    if (isset($_POST['generate_playlist']) && check_admin_referer('yourparty_generate_playlist')) {
        $target_mood = sanitize_text_field($_POST['target_mood']);
        $min_votes = intval($_POST['min_votes']);

        $playlist_lines = ["#EXTM3U"];
        foreach ($moods_data as $song_id => $data) {
            $votes = $data['moods'][$target_mood] ?? 0;
            if ($votes >= $min_votes) {
                // Note: We only have ID here. In a real scenario, we'd need the filename/path.
                // Assuming ID maps to something usable or we just list IDs for now.
                $playlist_lines[] = "#EXTINF:-1,Song ID: $song_id (Votes: $votes)";
                $playlist_lines[] = "song_id_$song_id.mp3";
            }
        }
        $generated_playlist = implode("\n", $playlist_lines);
    }

    ?>
    <div class="wrap">
        <h1>📻 Radio Control Dashboard</h1>

        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 20px;">

            <!-- LEFT: Song List -->
            <div class="card" style="padding: 20px; max-width: 100%;">
                <h2>🎵 Getaggte Songs (<?php echo count($moods_data); ?>)</h2>
                <table class="wp-list-table widefat fixed striped">
                    <thead>
                        <tr>
                            <th>Song ID</th>
                            <th>Top Mood</th>
                            <th>Total Votes</th>
                            <th>Verteilung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (empty($moods_data)): ?>
                            <tr>
                                <td colspan="4">Noch keine Daten vorhanden.</td>
                            </tr>
                        <?php else: ?>
                            <?php foreach ($moods_data as $song_id => $data): ?>
                                <tr>
                                    <td><strong><?php echo esc_html($song_id); ?></strong></td>
                                    <td>
                                        <?php
                                        $top = $data['top_mood'] ?? '-';
                                        $emoji = '';
                                        switch ($top) {
                                            case 'energetic':
                                                $emoji = '🔥';
                                                break;
                                            case 'chill':
                                                $emoji = '😌';
                                                break;
                                            case 'dark':
                                                $emoji = '🌑';
                                                break;
                                            case 'euphoric':
                                                $emoji = '✨';
                                                break;
                                            case 'melancholic':
                                                $emoji = '💙';
                                                break;
                                            case 'groovy':
                                                $emoji = '🎵';
                                                break;
                                        }
                                        echo $emoji . ' ' . ucfirst($top);
                                        ?>
                                    </td>
                                    <td><?php echo intval($data['total_votes']); ?></td>
                                    <td>
                                        <div style="display: flex; gap: 5px; font-size: 10px;">
                                            <?php foreach (($data['moods'] ?? []) as $m => $c): ?>
                                                <?php if ($c > 0): ?>
                                                    <span style="background: #eee; padding: 2px 5px; border-radius: 3px;">
                                                        <?php echo ucfirst($m) . ': ' . $c; ?>
                                                    </span>
                                                <?php endif; ?>
                                            <?php endforeach; ?>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>

            <!-- RIGHT: Actions -->
            <div>
                <div class="card" style="padding: 20px;">
                    <h2>⚡ Playlist Generator</h2>
                    <form method="post">
                        <?php wp_nonce_field('yourparty_generate_playlist'); ?>
                        <p>
                            <label><strong>Mood:</strong></label><br>
                            <select name="target_mood" style="width: 100%;">
                                <option value="energetic">🔥 Energetic</option>
                                <option value="chill">😌 Chill</option>
                                <option value="dark">🌑 Dark</option>
                                <option value="euphoric">✨ Euphoric</option>
                                <option value="melancholic">💙 Melancholic</option>
                                <option value="groovy">🎵 Groovy</option>
                            </select>
                        </p>
                        <p>
                            <label><strong>Min. Votes:</strong></label><br>
                            <input type="number" name="min_votes" value="1" min="1" style="width: 100%;">
                        </p>
                        <p>
                            <button type="submit" name="generate_playlist" class="button button-primary button-large"
                                style="width: 100%;">Playlist generieren</button>
                        </p>
                    </form>

                    <?php if ($generated_playlist): ?>
                        <div style="margin-top: 20px;">
                            <h3>Ergebnis (M3U):</h3>
                            <textarea style="width: 100%; height: 200px; font-family: monospace; background: #f0f0f0;"
                                readonly><?php echo esc_textarea($generated_playlist); ?></textarea>
                            <p class="description">Kopiere dies in eine .m3u Datei für AzuraCast.</p>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
    <?php
}
