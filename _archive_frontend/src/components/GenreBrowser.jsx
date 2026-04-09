import React from 'react';
import { useStore } from '../store';
import { ChevronDown, ChevronRight, Wand2, Music } from 'lucide-react';

export default function GenreBrowser() {
    const { library, improveTags } = useStore();

    // Group tracks by genre
    const genreGroups = library.reduce((acc, file) => {
        const genre = file.metadata.genre || 'Unknown Genre';
        if (!acc[genre]) acc[genre] = [];
        acc[genre].push(file);
        return acc;
    }, {});

    // ALL genres expanded by default
    const [expandedGenres, setExpandedGenres] = React.useState(() => {
        const initial = {};
        Object.keys(genreGroups).forEach(genre => {
            initial[genre] = true; // Auto-expand all
        });
        return initial;
    });

    const toggleGenre = (genre) => {
        setExpandedGenres(prev => ({ ...prev, [genre]: !prev[genre] }));
    };

    const handleImprove = async (filePath) => {
        await improveTags(filePath);
    };

    if (library.length === 0) {
        return (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
                <Music size={48} className="text-muted" style={{ marginBottom: '1rem' }} />
                <h3>Library is empty</h3>
                <p className="text-muted">Scan a folder to see your music here.</p>
            </div>
        );
    }

    return (
        <div className="flex-col">
            {Object.entries(genreGroups).map(([genre, tracks]) => {
                const isExpanded = expandedGenres[genre];

                return (
                    <div key={genre} className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
                        <div
                            className="flex-between"
                            style={{
                                padding: '1rem',
                                cursor: 'pointer',
                                background: isExpanded ? 'rgba(255,255,255,0.05)' : 'transparent'
                            }}
                            onClick={() => toggleGenre(genre)}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                                <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{genre}</span>
                                <span className="badge">{tracks.length}</span>
                            </div>
                        </div>

                        {isExpanded && (
                            <div>
                                {tracks.map((track, i) => (
                                    <div
                                        key={i}
                                        className="flex-between"
                                        style={{
                                            padding: '0.75rem',
                                            borderBottom: '1px solid var(--border)',
                                            background: 'rgba(255,255,255,0.02)'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{
                                                width: '40px', height: '40px',
                                                background: 'rgba(255,255,255,0.1)',
                                                borderRadius: '4px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <Music size={20} />
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 500 }}>
                                                    {track.metadata.title || track.filename}
                                                </div>
                                                <div className="text-muted" style={{ fontSize: '0.875rem' }}>
                                                    {track.metadata.artist || 'Unknown Artist'} • {track.metadata.album || 'Unknown Album'}
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            className="btn btn-secondary"
                                            style={{ padding: '0.5rem' }}
                                            onClick={() => handleImprove(track.path)}
                                            title="Auto-fix tags"
                                        >
                                            <Wand2 size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
