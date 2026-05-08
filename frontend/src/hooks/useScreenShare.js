import { useState, useCallback, useRef } from 'react';

export const useScreenShare = (peerConnectionsRef, localStreamRef, sendMessage, showNotification, MY_ROLE, createVideoOffer) => {
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [screenShareLocked, setScreenShareLocked] = useState(false);
  const [screenShareHolder, setScreenShareHolder] = useState(null);
  const screenShareStreamRef = useRef(null);
  const screenShareSendersRef = useRef({}); // { userId: RTCRtpSender }
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
        
        // 🔥 ADD track to ALL peer connections (don't replace camera)
        const pcs = peerConnectionsRef.current || {};
        for (const userId in pcs) {
          const pc = pcs[userId];
          try {
            const sender = pc.addTrack(videoTrack, screenShareStream);
            screenShareSendersRef.current[userId] = sender;
            
            // 🔥 Trigger re-negotiation
            if (createVideoOffer) {
              await createVideoOffer(userId);
            }
          } catch (e) {
            console.error(`Error adding screen track for ${userId}:`, e);
          }
        }

        // Broadcast state with stream ID so others can identify it
        sendMessage({ 
          type: 'screen_share_state', 
          active: true, 
          streamId: screenShareStream.id 
        });

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
  }, [isScreenSharing, screenShareLocked, screenShareHolder, MY_ROLE, sendMessage, showNotification, peerConnectionsRef, createVideoOffer]);

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

    // Remove screen track from ALL peers and re-negotiate
    const pcs = peerConnectionsRef.current || {};
    for (const userId in pcs) {
      const pc = pcs[userId];
      const sender = screenShareSendersRef.current[userId];
      if (sender && pc.signalingState !== 'closed') {
        try {
          pc.removeTrack(sender);
          delete screenShareSendersRef.current[userId];
          
          // Re-negotiate after removal
          if (createVideoOffer) {
            await createVideoOffer(userId);
          }
        } catch (e) {
          console.warn(`Failed to remove screen track for ${userId}:`, e);
        }
      }
    }

    // Ensure camera track is still active and enabled
    if (localStreamRef.current) {
      const cameraTrack = localStreamRef.current.getVideoTracks()[0];
      if (cameraTrack) {
        cameraTrack.enabled = true;
      }
    }
  }, [sendMessage, peerConnectionsRef, localStreamRef, createVideoOffer]);

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
