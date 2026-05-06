import React, { useEffect, useRef, useState } from 'react';
import VideoPlaceholder from '../VideoPlaceholder';

export const VideoPanel = ({
  remoteParticipants, // { userId: { stream, name, isCameraOn, isScreenSharing, role } }
  localVideoRef,
  localStreamRef,
  bothPartiesConnected,
  isCameraOn,
  localName,
  localRole
}) => {
  const videoRefs = useRef({}); // { userId: HTMLVideoElement }

  // Sync streams to video elements
  useEffect(() => {
    Object.keys(remoteParticipants).forEach(userId => {
      const participant = remoteParticipants[userId];
      const videoEl = videoRefs.current[userId];
      if (videoEl && participant.stream && videoEl.srcObject !== participant.stream) {
        console.log(`🔗 Syncing stream for ${userId}`);
        videoEl.srcObject = participant.stream;
      }
    });
  }, [remoteParticipants]);

  // Sync local stream
  useEffect(() => {
    if (localVideoRef.current && localStreamRef?.current && localVideoRef.current.srcObject !== localStreamRef.current) {
        localVideoRef.current.srcObject = localStreamRef.current;
    }
  }, [localStreamRef]);

  // 1. Combine local and remote into a list, FILTERING OUT remote participants without streams
  const allParticipants = [
    { id: 'local', name: localName, role: localRole?.toLowerCase(), isLocal: true, isCameraOn, stream: localStreamRef?.current },
    ...Object.keys(remoteParticipants)
        .map(uid => ({ id: uid, ...remoteParticipants[uid] }))
        .filter(p => p.stream) // 🔥 REQUIRED FIX: Remove empty tiles (only if they have a stream)
  ];

  // 2. Stable Sort: Candidate > Interviewer > Panelist
  const sortedParticipants = allParticipants.sort((a, b) => {
    const getRolePriority = (role) => {
        if (role === 'candidate') return 1;
        if (role === 'interviewer') return 2;
        return 3; // Panelists or other
    };
    const prioA = getRolePriority(a.role);
    const prioB = getRolePriority(b.role);
    if (prioA !== prioB) return prioA - prioB;
    // Step 4: Stable ordering using joinedAt
    const joinA = a.joinedAt || 0;
    const joinB = b.joinedAt || 0;
    if (joinA !== joinB) return joinA - joinB;
    return a.id.localeCompare(b.id);
  });

  const totalCount = sortedParticipants.length;

  const getGridLayout = () => {
    if (totalCount === 1) return { gridTemplateColumns: '1fr', gridTemplateRows: '1fr' };
    if (totalCount === 2) return { gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr' };
    if (totalCount <= 4) return { gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr' };
    return { gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gridTemplateRows: 'auto' };
  };

  return (
    <div className="video-grid-container" style={{ 
        width: '100%', 
        height: '100%', 
        display: 'grid', 
        gap: '15px', 
        padding: '15px', 
        backgroundColor: '#0f172a',
        alignContent: 'center',
        justifyContent: 'center',
        ...getGridLayout()
    }}>
      
      {sortedParticipants.map(p => {
        const isSelf = p.isLocal;
        const showVideo = isSelf ? isCameraOn : (p.isCameraOn !== false || p.isScreenSharing);

        return (
          <div key={p.id} className={`video-tile ${isSelf ? 'local-tile' : 'remote-tile'}`} style={{ 
            position: 'relative', 
            borderRadius: '16px', 
            overflow: 'hidden', 
            backgroundColor: '#1e293b', 
            border: isSelf ? '2px solid #3b82f6' : '1px solid rgba(255,255,255,0.1)',
            aspectRatio: '16/9',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
          }}>
            <video
              ref={el => {
                if (isSelf) localVideoRef.current = el;
                else videoRefs.current[p.id] = el;
              }}
              className="video-element"
              autoPlay
              muted={isSelf}
              playsInline
              style={{ width: '100%', height: '100%', objectFit: p.isScreenSharing ? 'contain' : 'cover', display: showVideo ? 'block' : 'none' }}
            />
            
            {!showVideo && (
              <div className="video-placeholder-overlay" style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
                <VideoPlaceholder name={p.name || 'Participant'} />
              </div>
            )}

            <div className="video-label" style={{ 
              position: 'absolute', 
              bottom: '15px', 
              left: '15px', 
              zIndex: 2, 
              background: 'rgba(15, 23, 42, 0.7)', 
              backdropFilter: 'blur(4px)',
              padding: '6px 14px', 
              borderRadius: '10px', 
              color: 'white', 
              fontSize: '13px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>{p.name}{isSelf ? ' (You)' : ''}</span>
              {!isSelf && !p.isMuted && <i className="fas fa-microphone" style={{ fontSize: '11px', color: '#10b981' }}></i>}
              {!isSelf && p.isMuted && <i className="fas fa-microphone-slash" style={{ fontSize: '11px', color: '#ef4444' }}></i>}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default VideoPanel;
