import { useRef, useCallback } from 'react';

export const useWebRTC = (sendMessage) => {
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const remoteStreamRef = useRef(null);
  const remoteIceQueueRef = useRef([]);

  const createPeerConnection = useCallback((onTrackCallback) => {
    const configuration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' },
        {
          urls: 'turn:openrelay.metered.ca:80',
          username: 'openrelayproject',
          credential: 'openrelayproject'
        },
        {
          urls: 'turn:openrelay.metered.ca:443',
          username: 'openrelayproject',
          credential: 'openrelayproject'
        },
        {
          urls: 'turn:openrelay.metered.ca:443?transport=tcp',
          username: 'openrelayproject',
          credential: 'openrelayproject'
        }
      ],
      iceCandidatePoolSize: 10,
      iceTransportPolicy: 'all',
      bundlePolicy: 'max-bundle',
      rtcpMuxPolicy: 'require',
      sdpSemantics: 'unified-plan'
    };

    const peerConnection = new RTCPeerConnection(configuration);
    peerConnectionRef.current = peerConnection;

    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        sendMessage({
          type: 'ice_candidate',
          candidate: event.candidate
        });
      }
    };

    peerConnection.ontrack = (event) => {
      console.log('🎥 Received remote track!', event.track.kind);
      const remoteStream = event.streams[0];
      if (remoteStream) {
        remoteStreamRef.current = remoteStream;
        if (onTrackCallback) onTrackCallback(remoteStream);
      }
    };

    return peerConnection;
  }, [sendMessage]);

  const initLocalStream = useCallback(async (videoConstraints = true, audioConstraints = true) => {
    try {
      const localStream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints ? { width: { ideal: 1280, max: 1920 }, height: { ideal: 720, max: 1080 }, frameRate: { ideal: 30, max: 60 }, facingMode: 'user' } : false,
        audio: audioConstraints ? { echoCancellation: true, noiseSuppression: true, autoGainControl: true, sampleRate: 44100 } : false
      });
      localStreamRef.current = localStream;
      return localStream;
    } catch (error) {
      console.error('❌ Media access failed:', error);
      throw error;
    }
  }, []);

  const addLocalTracksToPC = useCallback((peerConnection, localStream) => {
    if (!localStream) return;
    localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, localStream);
    });
  }, []);

  const createVideoOffer = useCallback(async (options = {}) => {
    if (!peerConnectionRef.current) return;
    try {
      const offer = await peerConnectionRef.current.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true,
        ...options
      });
      await peerConnectionRef.current.setLocalDescription(offer);
      sendMessage({
        type: 'video_offer',
        offer: offer
      });
    } catch (error) {
      console.error('Error creating video offer:', error);
    }
  }, [sendMessage]);

  const handleVideoOffer = useCallback(async (offer) => {
    if (!peerConnectionRef.current) return;
    try {
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(offer));
      const answer = await peerConnectionRef.current.createAnswer();
      await peerConnectionRef.current.setLocalDescription(answer);
      sendMessage({
        type: 'video_answer',
        answer: answer
      });

      // Process queued ICE candidates
      if (remoteIceQueueRef.current.length > 0) {
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
          } catch (e) {
            console.warn('Failed to add ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('Error handling video offer:', error);
    }
  }, [sendMessage]);

  const handleVideoAnswer = useCallback(async (answer) => {
    if (!peerConnectionRef.current) return;
    try {
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(answer));
      if (remoteIceQueueRef.current.length > 0) {
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
          } catch (e) {
            console.warn('Failed to add ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('Error handling video answer:', error);
    }
  }, []);

  const handleIceCandidate = useCallback(async (candidate) => {
    if (!peerConnectionRef.current) return;
    try {
      if (!peerConnectionRef.current.remoteDescription) {
        remoteIceQueueRef.current.push(candidate);
      } else {
        await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (e) {
      console.warn('ICE candidate error:', e);
    }
  }, []);

  const stopWebRTC = useCallback(() => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
  }, []);

  return {
    peerConnectionRef,
    localStreamRef,
    remoteStreamRef,
    remoteIceQueueRef,
    createPeerConnection,
    initLocalStream,
    addLocalTracksToPC,
    createVideoOffer,
    handleVideoOffer,
    handleVideoAnswer,
    handleIceCandidate,
    stopWebRTC
  };
};

export default useWebRTC;
