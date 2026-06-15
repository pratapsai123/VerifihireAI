import React, { useEffect, useRef } from 'react';
import VideoPlaceholder from '../VideoPlaceholder';

/**
 * VideoPanel Component
 * Implements a dynamic, responsive grid layout and a professional split-layout for screen sharing.
 * Supports simultaneous Camera + Screen sharing (Teams/Meet style).
 */
export const VideoPanel = ({
  remoteParticipants, // { userId: { stream, screenStream, name, isCameraOn, isScreenSharing, role } }
  localVideoRef,
  localStreamRef,
  localScreenStream,
  bothPartiesConnected,
  isCameraOn,
  isLocalScreenSharing,
  localName,
  localRole,
  speakerDeviceId
}) => {
  // Sync local stream whenever state or streams change
  useEffect(() => {
    const videoEl = localVideoRef.current;
    if (!videoEl) return;

    // Local user always sees their camera in their small tile, 
    // unless they are the ONLY person and sharing, but even then, camera is usually what they want to check.
    // However, VideoPanel renders a list of participants. 
    // For the LOCAL participant, we will have two entries if sharing.

    if (localStreamRef.current && videoEl.srcObject !== localStreamRef.current) {
      videoEl.srcObject = localStreamRef.current;
    }
  }, [localStreamRef, localVideoRef]);

  // 1. Build the participant list for rendering
  // We want to treat camera streams and screen streams as separate "tiles" in the UI logic.

  const cameraTiles = [
    {
      id: 'local-camera',
      name: localName,
      role: localRole?.toLowerCase(),
      isLocal: true,
      isCameraOn,
      isScreenSharing: false,
      stream: localStreamRef?.current
    },
    ...Object.keys(remoteParticipants)
      .map(uid => ({
        id: `${uid}-camera`,
        realId: uid,
        name: remoteParticipants[uid].name,
        role: remoteParticipants[uid].role,
        isCameraOn: remoteParticipants[uid].isCameraOn,
        isMuted: remoteParticipants[uid].isMuted,
        stream: remoteParticipants[uid].stream,
        joinedAt: remoteParticipants[uid].joinedAt
      }))
  ];

  // Identify if anyone is sharing a screen (Global State)
  const isAnyRemoteSharing = Object.keys(remoteParticipants).some(uid => remoteParticipants[uid].isScreenSharing);
  const isAnySharing = isLocalScreenSharing || isAnyRemoteSharing;

  let screenShareTile = null;

  if (isLocalScreenSharing) {
    screenShareTile = {
      id: 'local-screen',
      name: `${localName}'s Screen`,
      isLocal: true,
      isScreenSharing: true,
      stream: localScreenStream
    };
  } else if (isAnyRemoteSharing) {
    const sharerId = Object.keys(remoteParticipants).find(uid => remoteParticipants[uid].isScreenSharing);
    const p = remoteParticipants[sharerId];
    screenShareTile = {
      id: `${sharerId}-screen`,
      name: `${p.name}'s Screen`,
      isLocal: false,
      isScreenSharing: true,
      stream: p.screenStream // Might be null initially
    };
  }

  // Stable Sort for sidebar/grid
  const sortedCameraTiles = cameraTiles.sort((a, b) => {
    const getRolePriority = (role) => {
      if (role === 'candidate') return 1;
      if (role === 'interviewer') return 2;
      return 3;
    };
    const prioA = getRolePriority(a.role);
    const prioB = getRolePriority(b.role);
    if (prioA !== prioB) return prioA - prioB;
    const joinA = a.joinedAt || 0;
    const joinB = b.joinedAt || 0;
    if (joinA !== joinB) return joinA - joinB;
    return a.id.localeCompare(b.id);
  });

  // Video Tile Render Function
  const renderParticipantTile = (p, isSidebar = false) => {
    const isSelf = p.isLocal && !p.isScreenSharing;
    const isScreenLoading = p.isScreenSharing && !p.stream;
    const isLocalScreenShare = p.isLocal && p.isScreenSharing;
    const showVideo = !isScreenLoading && !isLocalScreenShare && (p.isScreenSharing || (isSelf ? isCameraOn : p.isCameraOn !== false));

    return (
      <div key={p.id} className={`video-tile ${isSelf ? 'local-tile' : 'remote-tile'} ${isSidebar ? 'sidebar-tile' : ''}`}>
        {isScreenLoading ? (
          <div className="screen-loading">
            <div className="spinner"></div>
            <span>Connecting to presentation...</span>
          </div>
        ) : isLocalScreenShare ? (
          <div className="local-screen-share-placeholder" style={{
            position: 'absolute', inset: 0, zIndex: 1, width: '100%', height: '100%', 
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            backgroundColor: '#1e293b', color: 'white', gap: '15px'
          }}>
            <i className="fas fa-desktop" style={{ fontSize: '48px', color: '#3b82f6' }}></i>
            <span style={{ fontSize: '18px', fontWeight: '500' }}>You are sharing your screen</span>
          </div>
        ) : (
          <video
            ref={el => {
              if (el) {
                if (p.stream && el.srcObject !== p.stream) {
                  el.srcObject = p.stream;
                }
                if (!isSelf && speakerDeviceId && typeof el.setSinkId === 'function') {
                  el.setSinkId(speakerDeviceId)
                    .catch(err => console.error('Error setting remote speaker sink ID:', err));
                }
              }
              if (isSelf) localVideoRef.current = el;
            }}
            className="video-element"
            autoPlay
            muted={isSelf || p.isScreenSharing}
            playsInline
            style={{
              objectFit: p.isScreenSharing ? 'contain' : 'cover',
              display: showVideo ? 'block' : 'none',
              transform: isSelf ? 'scaleX(-1)' : 'none'
            }}
          />
        )}

        {!showVideo && !isScreenLoading && !isLocalScreenShare && (
          <div className="video-placeholder-overlay" style={{ position: 'absolute', inset: 0, zIndex: 1, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <VideoPlaceholder name={p.name || 'Participant'} />
          </div>
        )}

        <div className="video-label">
          <span>{p.name}{isSelf ? ' (You)' : ''}</span>
          {!isSelf && !p.isScreenSharing && !p.isMuted && <i className="fas fa-microphone" style={{ fontSize: '11px', color: '#10b981' }}></i>}
          {!isSelf && !p.isScreenSharing && p.isMuted && <i className="fas fa-microphone-slash" style={{ fontSize: '11px', color: '#ef4444' }}></i>}
          {p.isScreenSharing && <span className="sharing-badge" style={{ marginLeft: '8px', fontSize: '10px', background: '#3b82f6', padding: '2px 6px', borderRadius: '4px' }}>PRESENTING</span>}
        </div>
      </div>
    );
  };

  const gridClass = `grid-layout-${Math.min(sortedCameraTiles.length || 1, 12)}`;

  return (
    <>
      <style>{`
        .video-grid-container {
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          width: 100%; height: 100%;
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          padding: 20px;
          background-color: #0f172a;
          box-sizing: border-box;
          align-content: center;
          justify-content: center;
          overflow-y: auto;
        }

        .video-cell-wrapper {
          position: relative;
          flex: 0 1 auto;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 280px;
          /* Base size for responsiveness */
          transition: all 0.3s ease;
        }

        /* Responsive width calculation based on participant count */
        .grid-layout-1 .video-cell-wrapper { width: 100%; height: 100%; }
        .grid-layout-2 .video-cell-wrapper { width: calc(50% - 15px); height: calc(100% - 30px); }
        .grid-layout-3 .video-cell-wrapper, 
        .grid-layout-4 .video-cell-wrapper { width: calc(50% - 15px); height: calc(50% - 15px); }
        .grid-layout-5 .video-cell-wrapper, 
        .grid-layout-6 .video-cell-wrapper { width: calc(33.33% - 15px); height: calc(50% - 15px); }
        
        @media (max-width: 768px) {
          .video-cell-wrapper { width: 100% !important; height: auto !important; aspect-ratio: 16/9; }
        }

        .split-layout-container {
          position: absolute; inset: 0;
          display: flex;
          flex-direction: row;
          gap: 15px;
          padding: 15px;
          background-color: #0f172a;
          box-sizing: border-box;
        }

        .main-stage {
          flex: 1;
          position: relative;
          background: #1e293b;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .sidebar {
          width: 240px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          overflow-y: auto;
          overflow-x: hidden;
          padding-right: 4px;
        }

        .sidebar::-webkit-scrollbar { width: 4px; }
        .sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }

        .video-tile {
          position: relative;
          border-radius: 12px;
          overflow: hidden;
          background-color: #1e293b;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          border: 1px solid rgba(255, 255, 255, 0.08);
          transition: transform 0.2s ease;
        }

        .sidebar-tile {
          aspect-ratio: 16/9;
          width: 100%;
          flex-shrink: 0;
          height: auto;
        }

        .video-element {
          width: 100%; height: 100%;
          object-fit: cover;
        }

        .video-label {
          position: absolute; 
          bottom: 12px; left: 12px; 
          z-index: 10; 
          background: rgba(15, 23, 42, 0.7); 
          backdrop-filter: blur(8px);
          padding: 6px 12px; 
          border-radius: 8px; 
          color: white; 
          font-size: 13px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .local-tile { border: 2px solid #3b82f6; }
        .remote-tile { }

        .screen-loading {
          position: absolute;
          inset: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(15, 23, 42, 0.9);
          color: white;
          gap: 15px;
          z-index: 5;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid rgba(255,255,255,0.1);
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        @media (max-aspect-ratio: 1/1) {
          .split-layout-container { flex-direction: column; }
          .sidebar {
            width: 100%;
            height: 120px;
            flex-direction: row;
            overflow-x: auto;
            overflow-y: hidden;
            padding-right: 0;
          }
          .sidebar-tile {
            height: 100%;
            width: auto;
          }
        }
      `}</style>

      {screenShareTile ? (
        <div className="split-layout-container">
          <div className="main-stage">
            {renderParticipantTile(screenShareTile)}
          </div>
          <div className="sidebar">
            {sortedCameraTiles.map(p => (
              <div key={p.id} className="sidebar-tile-wrapper">
                {renderParticipantTile(p, true)}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className={`video-grid-container ${gridClass}`}>
          {sortedCameraTiles.map(p => (
            <div key={p.id} className="video-cell-wrapper">
              {renderParticipantTile(p)}
            </div>
          ))}
        </div>
      )}
    </>
  );
};

export default VideoPanel;
