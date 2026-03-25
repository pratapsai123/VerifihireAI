import React, { useEffect, useRef, useState } from 'react';
import VideoPlaceholder from '../VideoPlaceholder';

export const VideoPanel = ({
  remoteVideoRef,
  localVideoRef, // Note: connects to thumbnailVideoRef or selfVideoRef
  isRemoteCameraOn,
  isRemoteScreenSharing,
  bothPartiesConnected,
  isCameraOn,
  remoteName,
  localName
}) => {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

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
        // Only prevent default on touch events if needed, to keep warning down
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

  return (
    <>
      {/* Remote Video */}
      <video
        ref={remoteVideoRef}
        className="remote-video full"
        autoPlay
        playsInline
        onContextMenu={e => e.preventDefault()}
        style={{ display: (isRemoteCameraOn || isRemoteScreenSharing) ? 'block' : 'none', objectFit: isRemoteScreenSharing ? 'contain' : 'cover' }}
      />
      
      {!isRemoteCameraOn && bothPartiesConnected && !isRemoteScreenSharing && (
        <div className="remote-video-placeholder" style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
          <VideoPlaceholder name={remoteName} />
        </div>
      )}

      {bothPartiesConnected && (
        <div className="video-label" style={{ top: '20px', left: '20px', bottom: 'auto' }}>
          <span>{remoteName}</span>
          <i className="fas fa-microphone" style={{ fontSize: '12px', marginLeft: '6px' }}></i>
        </div>
      )}

      {/* Local Video */}
      <div 
        className="self-video-container floating"
        ref={containerRef}
        onMouseDown={handleDragStart}
        onTouchStart={handleDragStart}
      >
        <video
          ref={localVideoRef}
          className="self-video"
          autoPlay
          muted
          playsInline
          style={{ display: isCameraOn ? 'block' : 'none' }}
        />
        {!isCameraOn && (
          <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}>
            <VideoPlaceholder name="You" width="100%" height="100%" />
          </div>
        )}
        <div className="video-label">
          <span>{localName} (You)</span>
        </div>
      </div>
    </>
  );
};

export default VideoPanel;
