import React, { useState } from 'react';
import axios from 'axios';
import { Database, Star, TrendingUp } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function MongoIntegration() {
    const [mongoConnected, setMongoConnected] = useState(false);
    const [ratedTracks, setRatedTracks] = useState([]);
    const [loading, setLoading] = useState(false);

    const [mongoConfig, setMongoConfig] = useState({
        connection_string: 'mongodb://localhost:27017/',
        database_name: 'radio_ratings'
    });

    const [azuraConfig, setAzuraConfig] = useState({
        base_url: 'http://192.168.178.210',
        api_key: '9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c',
        station_id: 1
    });

    const connectMongo = async () => {
        try {
            setLoading(true);
            const res = await axios.post(`${API_URL}/mongo/connect`, mongoConfig);
            if (res.data.success) {
                setMongoConnected(true);
                alert('MongoDB verbunden!');
            }
        } catch (error) {
            alert('MongoDB Verbindung fehlgeschlagen: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchRatedTracks = async () => {
        if (!mongoConnected) {
            alert('Bitte zuerst MongoDB verbinden!');
            return;
        }

        try {
            setLoading(true);
            const res = await axios.get(`${API_URL}/mongo/tracks/rated?min_rating=0`);
            setRatedTracks(res.data.tracks || []);
        } catch (error) {
            alert('Fehler beim Laden: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const syncMetadata = async () => {
        if (!mongoConnected) {
            alert('Bitte zuerst MongoDB verbinden!');
            return;
        }

        try {
            setLoading(true);
            const res = await axios.post(`${API_URL}/mongo/sync/metadata`);
            alert(`${res.data.synced} Tracks synchronisiert!`);
        } catch (error) {
            alert('Sync fehlgeschlagen: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const syncAzuraCast = async () => {
        if (!azuraConfig.api_key) {
            alert('Bitte AzuraCast API Key eingeben!');
            return;
        }

        try {
            setLoading(true);
            const res = await axios.post(`${API_URL}/azuracast/sync`, azuraConfig);
            alert(res.data.message || 'AzuraCast Sync erfolgreich!');
        } catch (error) {
            alert('AzuraCast Sync fehlgeschlagen: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-col" style={{ gap: '1.5rem' }}>
            <div className="glass-card">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Database size={24} />
                    MongoDB Integration
                </h2>

                <div className="flex-col" style={{ gap: '1rem', marginTop: '1.5rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Connection String
                        </label>
                        <input
                            type="text"
                            value={mongoConfig.connection_string}
                            onChange={(e) => setMongoConfig({ ...mongoConfig, connection_string: e.target.value })}
                            placeholder="mongodb://localhost:27017/"
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Database Name
                        </label>
                        <input
                            type="text"
                            value={mongoConfig.database_name}
                            onChange={(e) => setMongoConfig({ ...mongoConfig, database_name: e.target.value })}
                            placeholder="radio_ratings"
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            className="btn"
                            onClick={connectMongo}
                            disabled={loading || mongoConnected}
                        >
                            {mongoConnected ? '✅ Verbunden' : 'Verbinden'}
                        </button>

                        {mongoConnected && (
                            <>
                                <button className="btn btn-secondary" onClick={syncMetadata} disabled={loading}>
                                    Metadata Sync
                                </button>
                                <button className="btn btn-secondary" onClick={fetchRatedTracks} disabled={loading}>
                                    <Star size={16} /> Ratings laden
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>

            <div className="glass-card">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <TrendingUp size={20} />
                    AzuraCast Sync
                </h3>

                <div className="flex-col" style={{ gap: '1rem', marginTop: '1rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                        <input
                            type="text"
                            value={azuraConfig.base_url}
                            onChange={(e) => setAzuraConfig({ ...azuraConfig, base_url: e.target.value })}
                            placeholder="API URL"
                        />
                        <input
                            type="text"
                            value={azuraConfig.api_key}
                            onChange={(e) => setAzuraConfig({ ...azuraConfig, api_key: e.target.value })}
                            placeholder="API Key"
                        />
                        <input
                            type="number"
                            value={azuraConfig.station_id}
                            onChange={(e) => setAzuraConfig({ ...azuraConfig, station_id: parseInt(e.target.value) })}
                            placeholder="Station ID"
                        />
                    </div>
                    <button className="btn" onClick={syncAzuraCast} disabled={loading}>
                        AzuraCast Sync
                    </button>
                </div>
            </div>

            {ratedTracks.length > 0 && (
                <div className="glass-card">
                    <h3>Bewertete Tracks ({ratedTracks.length})</h3>
                    <div style={{ maxHeight: '400px', overflowY: 'auto', marginTop: '1rem' }}>
                        {ratedTracks.map((track, idx) => (
                            <div
                                key={idx}
                                style={{
                                    padding: '1rem',
                                    borderBottom: '1px solid var(--border)',
                                    display: 'flex',
                                    justifyContent: 'space-between'
                                }}
                            >
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>
                                        {track.metadata?.title || 'Unknown Title'}
                                    </div>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                        {track.metadata?.artist || 'Unknown Artist'} - {track.metadata?.album || 'Unknown Album'}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                        {track.metadata?.genre}
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <Star size={16} fill="var(--accent)" color="var(--accent)" />
                                        <span style={{ fontWeight: 'bold' }}>{track.rating.average.toFixed(1)}</span>
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        {track.rating.total} Bewertung{track.rating.total !== 1 ? 'en' : ''}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
