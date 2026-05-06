import { useState, useCallback, useRef } from 'react';

export const useScreenShare = (peerConnectionsRef, localStreamRef, sendMessage, showNotification, MY_ROLE) => {
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [screenShareLocked, setScreenShareLocked] = useState(false);
  const [screenShareHolder, setScreenShareHolder] = useState(null);
  const screenShareStreamRef = useRef(null);
  const pendingScreenShareGrantResolverRef = useRef(null);

  const toggleScreenShare = useCallback(async () => {
    if (!isScreenSharing) {
      if (screenShareLocked && screenShareHolder && screenShareHolder !== MY_ROLE) {
        if (showNotification) showNotification(`${screenShareHolder} is already sharing their screen.`, 'warning');
        return;
      }

      const granted = await new Promise((resolve) => {
        pendingScreenShareGrantResolverRef.current = resolve;
        sendMessage({ type: 'screen_share_request' });
        
        setTimeout(() => {
          if (pendingScreenShareGrantResolverRef.current) {
            const r = pendingScreenShareGrantResolverRef.current;
            pendingScreenShareGrantResolverRef.current = null;
            r(false);
          }
        }, 4000);
      });

      if (!granted) {
        if (screenShareLocked && screenShareHolder) {
          if (showNotification) showNotification(`${screenShareHolder} is already sharing. Please wait.`, 'warning');
        }
        return;
      }

      try {
        const screenShareStream = await navigator.mediaDevices.getDisplayMedia({
          video: { displaySurface: 'monitor', cursor: 'always' },
          audio: false
        });

        screenShareStreamRef.current = screenShareStream;
        setIsScreenSharing(true);
        if (showNotification) showNotification('Screen sharing started', 'success');

        const videoTrack = screenShareStream.getVideoTracks()[0];
        
        // 🔥 Apply to ALL peer connections
        const pcs = peerConnectionsRef.current || {};
        for (const userId in pcs) {
          const pc = pcs[userId];
          const senders = pc.getSenders();
          const videoSender = senders.find(s => s.track && s.track.kind === 'video');

          if (videoSender) {
            await videoSender.replaceTrack(videoTrack);
          } else {
            pc.addTrack(videoTrack, screenShareStream);
            // Must re-negotiate if adding new track
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            sendMessage({ type: 'video_offer', sdp: offer, target: userId });
          }
        }

        sendMessage({ type: 'screen_share_state', active: true });

        if (videoTrack) {
          videoTrack.onended = () => stopScreenSharing();
        }
      } catch (error) {
        console.error('Error starting screen share:', error);
        if (showNotification) showNotification('Failed to access screen share', 'error');
        sendMessage({ type: 'screen_share_release' });
      }
    } else {
      stopScreenSharing();
    }
  }, [isScreenSharing, screenShareLocked, screenShareHolder, MY_ROLE, sendMessage, showNotification, peerConnectionsRef]);

  const stopScreenSharing = useCallback(async () => {
    if (screenShareStreamRef.current) {
      screenShareStreamRef.current.getTracks().forEach(track => {
        track.stop();
      });
      screenShareStreamRef.current = null;
    }
    
    setIsScreenSharing(false);
    
    sendMessage({ type: 'screen_share_state', active: false });
    sendMessage({ type: 'screen_share_release' });

    // Restore camera track for ALL peers
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = true;
        const pcs = peerConnectionsRef.current || {};
        for (const userId in pcs) {
          const pc = pcs[userId];
          try {
            const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender) {
              await sender.replaceTrack(videoTrack);
            }
          } catch (e) {
            console.warn(`Failed to restore camera for ${userId}:`, e);
          }
        }
      }
    }
  }, [sendMessage, peerConnectionsRef, localStreamRef]);

  // Handle incoming screen share granted message
  const handleScreenShareGranted = useCallback(() => {
    if (pendingScreenShareGrantResolverRef.current) {
      const resolver = pendingScreenShareGrantResolverRef.current;
      pendingScreenShareGrantResolverRef.current = null;
      resolver(true);
    }
  }, []);

  const handleScreenShareDenied = useCallback(() => {
    if (pendingScreenShareGrantResolverRef.current) {
      const resolver = pendingScreenShareGrantResolverRef.current;
      pendingScreenShareGrantResolverRef.current = null;
      resolver(false);
    }
  }, []);

  return {
    isScreenSharing,
    screenShareLocked,
    setScreenShareLocked,
    screenShareHolder,
    setScreenShareHolder,
    toggleScreenShare,
    stopScreenSharing,
    handleScreenShareGranted,
    handleScreenShareDenied,
    screenShareStreamRef
  };
};

export default useScreenShare;
