import React, { useEffect, useRef, useState } from 'react';
import VideoPlaceholder from '../VideoPlaceholder';

export const VideoPanel = ({
  remoteParticipants, // { userId: { stream, name, isCameraOn, isScreenSharing } }
  localVideoRef,
  bothPartiesConnected,
  isCameraOn,
  localName
}) => {
  const containerRef = useRef(null);
  const videoRefs = useRef({}); // { userId: HTMLVideoElement }
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

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

  const handleDragStart = (e) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const clientX = e.clientX ?? (e.touches && e.touches[0].clientX);
      const clientY = e.clientY ?? (e.touches && e.touches[0].clientY);
      setDragOffset({
        x: clientX - rect.left,
        y: clientY - rect.top
      });
      setIsDragging(true);
    }
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging && containerRef.current) {
        if (e.type !== 'mousemove') e.preventDefault();
        const container = containerRef.current;
        const parent = container.parentElement;
        if (!parent) return;

        const parentRect = parent.getBoundingClientRect();
        const clientX = e.clientX ?? (e.touches && e.touches[0].clientX);
        const clientY = e.clientY ?? (e.touches && e.touches[0].clientY);

        const newLeft = clientX - parentRect.left - dragOffset.x;
        const newTop = clientY - parentRect.top - dragOffset.y;

        const maxLeft = parentRect.width - container.offsetWidth;
        const maxTop = parentRect.height - container.offsetHeight;

        container.style.left = `${Math.max(0, Math.min(newLeft, maxLeft))}px`;
        container.style.top = `${Math.max(0, Math.min(newTop, maxTop))}px`;
        container.style.bottom = 'auto';
        container.style.right = 'auto';
      }
    };

    const handleMouseUp = () => setIsDragging(false);

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove, { passive: false });
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleMouseMove, { passive: false });
      document.addEventListener('touchend', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchmove', handleMouseMove);
      document.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  const participantIds = Object.keys(remoteParticipants);
  const participantCount = participantIds.length;

  // Grid logic: 1 user = full, 2 = 50/50 or stacked, 3-4 = 2x2
  const gridClass = participantCount <= 1 ? 'grid-1' : participantCount === 2 ? 'grid-2' : 'grid-multi';

  return (
    <div className={`video-grid-container ${gridClass}`} style={{ width: '100%', height: '100%', position: 'relative', display: 'grid', gap: '10px', padding: '10px', backgroundColor: '#0f172a' }}>
      
      {participantIds.map(userId => {
        const p = remoteParticipants[userId];
        const showVideo = p.isCameraOn !== false || p.isScreenSharing;

        return (
          <div key={userId} className="remote-video-wrapper" style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', backgroundColor: '#1e293b' }}>
            <video
              ref={el => videoRefs.current[userId] = el}
              className="remote-video"
              autoPlay
              playsInline
              style={{ width: '100%', height: '100%', objectFit: p.isScreenSharing ? 'contain' : 'cover', display: showVideo ? 'block' : 'none' }}
            />
            
            {!showVideo && (
              <div className="remote-video-placeholder" style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
                <VideoPlaceholder name={p.name || 'Participant'} />
              </div>
            )}

            <div className="video-label" style={{ position: 'absolute', bottom: '15px', left: '15px', zIndex: 2, background: 'rgba(0,0,0,0.5)', padding: '4px 12px', borderRadius: '20px', color: 'white', fontSize: '13px' }}>
              <span>{p.name || 'Participant'}</span>
              <i className="fas fa-microphone" style={{ fontSize: '11px', marginLeft: '6px', color: '#10b981' }}></i>
            </div>
          </div>
        );
      })}

      {/* Local Video - Floating */}
      <div 
        className="self-video-container floating"
        ref={containerRef}
        onMouseDown={handleDragStart}
        onTouchStart={handleDragStart}
        style={{ position: 'absolute', bottom: '20px', right: '20px', width: '200px', height: '150px', zIndex: 100, borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', cursor: 'move', border: '2px solid rgba(255,255,255,0.1)' }}
      >
        <video
          ref={localVideoRef}
          className="self-video"
          autoPlay
          muted
          playsInline
          style={{ width: '100%', height: '100%', objectFit: 'cover', display: isCameraOn ? 'block' : 'none' }}
        />
        {!isCameraOn && (
          <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}>
            <VideoPlaceholder name="You" width="100%" height="100%" />
          </div>
        )}
        <div className="video-label" style={{ position: 'absolute', bottom: '10px', left: '10px', background: 'rgba(0,0,0,0.5)', padding: '2px 8px', borderRadius: '4px', color: 'white', fontSize: '11px' }}>
          <span>{localName} (You)</span>
        </div>
      </div>
    </div>
  );
};

export default VideoPanel;
