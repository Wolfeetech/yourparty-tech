import React, { useState } from 'react';
import { useStore } from '../store';
import { Music, Folder, Tag, RefreshCw } from 'lucide-react';
import axios from 'axios';

const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="glass-card flex-between">
        <div>
            <h3 className="text-muted" style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>{label}</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{value}</div>
        </div>
        <div style={{
            padding: '1rem',
            borderRadius: '12px',
            background: `rgba(${color}, 0.2)`,
            color: `rgb(${color})`
        }}>
            <Icon size={24} />
        </div>
    </div>
);

export default function Dashboard() {
    const { stats, scanPath, setScanPath, scanLibrary, isLoading, organizeLibrary } = useStore();
    const [organizeResult, setOrganizeResult] = useState(null);

    const handleOrganize = async (outputPath) => {
        if (confirm(`This will move files into genre folders${outputPath ? ' at ' + outputPath : ''}. Are you sure?`)) {
            const res = await organizeLibrary(false, outputPath);
            setOrganizeResult(res);
        }
    };

    return (
        <div className="flex-col">
            <div className="glass-card">
                <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
                    <h2>Library Scanner</h2>
                    {isLoading && <span className="badge animate-pulse">Processing...</span>}
                </div>

                <div className="flex-between" style={{ gap: '1rem' }}>
                    <input
                        type="text"
                        value={scanPath}
                        onChange={(e) => setScanPath(e.target.value)}
                        placeholder="Path to music folder (e.g. C:/Music; D:/Archive)..."
                    />
                    <button className="btn" onClick={scanLibrary} disabled={isLoading}>
                        <RefreshCw size={18} className={isLoading ? 'animate-spin' : ''} />
                        Scan
                    </button>
                    <button className="btn btn-secondary" onClick={useStore.getState().improveAllUntagged} disabled={isLoading || stats.totalTracks === 0}>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                            <span>🪄</span>
                            <span>Auto-Tag All</span>
                        </div>
                    </button>
                </div>
            </div>

            <div className="grid-cols-3">
                <StatCard
                    icon={Music}
                    label="Total Tracks"
                    value={stats.totalTracks}
                    color="139, 92, 246"
                />
                <StatCard
                    icon={Tag}
                    label="Genres"
                    value={stats.genres}
                    color="236, 72, 153"
                />
                <StatCard
                    icon={Folder}
                    label="Untagged"
                    value={stats.untagged}
                    color="245, 158, 11"
                />
            </div>

            <div className="glass-card">
                <h3>Quick Actions</h3>
                <div className="flex-col" style={{ marginTop: '1rem' }}>

                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <input
                            type="text"
                            placeholder="Optional: Output Path (SMB/Network Share)..."
                            style={{ flex: 1 }}
                            id="outputPath"
                        />
                        <button className="btn btn-secondary" onClick={() => {
                            const outPath = document.getElementById('outputPath').value;
                            handleOrganize(outPath);
                        }} disabled={isLoading || stats.totalTracks === 0}>
                            <Folder size={18} />
                            Organize & Move
                        </button>
                    </div>

                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                        <h4>AzuraCast Integration</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '0.5rem' }}>
                            <input type="text" id="azUrl" placeholder="API URL" />
                            <input type="text" id="azKey" placeholder="API Key" />
                            <input type="text" id="azStation" placeholder="Station ID" />
                            <button className="btn btn-secondary" onClick={async () => {
                                const url = document.getElementById('azUrl').value;
                                const key = document.getElementById('azKey').value;
                                const id = document.getElementById('azStation').value;
                                if (!url || !key || !id) return alert("Please fill all AzuraCast fields");

                                try {
                                    const res = await axios.post('http://localhost:8000/azuracast/sync', {
                                        base_url: url,
                                        api_key: key,
                                        station_id: parseInt(id)
                                    });
                                    alert(res.data.message || "Sync triggered!");
                                } catch (e) {
                                    alert("Sync failed: " + e.message);
                                }
                            }}>
                                Sync
                            </button>
                        </div>
                    </div>

                </div>

                {organizeResult && (
                    <div style={{ marginTop: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
                        <h4>Last Organization Result:</h4>
                        <pre style={{ fontSize: '0.8rem' }}>{JSON.stringify(organizeResult, null, 2)}</pre>
                    </div>
                )}
            </div>
        </div>
    );
}
