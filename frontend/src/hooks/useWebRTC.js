import { useRef, useCallback } from 'react';

export const useWebRTC = (sendMessage) => {
  const peerConnectionsRef = useRef({}); // { userId: RTCPeerConnection }
  const localStreamRef = useRef(null);
  const remoteStreamsRef = useRef({}); // { userId: MediaStream }
  const remoteIceQueuesRef = useRef({}); // { userId: [RTCIceCandidate] }

  const createPeerConnection = useCallback((userId, onTrackCallback) => {
    // 🔥 Cleanup existing connection for this user if any
    if (peerConnectionsRef.current[userId]) {
      console.log(`🧹 Cleaning up existing PC for ${userId}`);
      peerConnectionsRef.current[userId].close();
      delete peerConnectionsRef.current[userId];
    }

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
        }
      ],
      iceCandidatePoolSize: 10,
      iceTransportPolicy: 'all',
      bundlePolicy: 'max-bundle',
      rtcpMuxPolicy: 'require',
      sdpSemantics: 'unified-plan'
    };

    const peerConnection = new RTCPeerConnection(configuration);
    peerConnectionsRef.current[userId] = peerConnection;
    remoteIceQueuesRef.current[userId] = [];

    console.log(`🏗️ PC created for ${userId}. State:`, peerConnection.signalingState);

    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        sendMessage({
          type: 'ice_candidate',
          candidate: event.candidate,
          target: userId // 🔥 Targeted
        });
      }
    };

    peerConnection.ontrack = (event) => {
      console.log(`🎥 Received track from ${userId}!`, event.track.kind);
      const remoteStream = event.streams[0];
      if (remoteStream) {
        remoteStreamsRef.current[userId] = remoteStream;
        if (onTrackCallback) onTrackCallback(userId, remoteStream);
      }
    };

    peerConnection.oniceconnectionstatechange = () => {
        console.log(`❄️ ICE Connection [${userId}]:`, peerConnection.iceConnectionState);
    };

    // Auto-add local tracks if stream exists
    if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStreamRef.current);
        });
    }

    return peerConnection;
  }, [sendMessage]);

  const initLocalStream = useCallback(async (videoConstraints = true, audioConstraints = true) => {
    try {
      console.log('🎙️ Initializing local stream...');
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

  const createVideoOffer = useCallback(async (userId, options = {}) => {
    const pc = peerConnectionsRef.current[userId];
    if (!pc) return;
    
    try {
      console.log(`📤 Creating offer for ${userId}`);
      const offer = await pc.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true,
        ...options
      });
      await pc.setLocalDescription(offer);
      sendMessage({
        type: 'video_offer',
        sdp: offer,
        target: userId
      });
    } catch (error) {
      console.error(`❌ Error creating offer for ${userId}:`, error);
    }
  }, [sendMessage]);

  const handleVideoOffer = useCallback(async (userId, description, onTrackCallback) => {
    let pc = peerConnectionsRef.current[userId];
    if (!pc) {
        pc = createPeerConnection(userId, onTrackCallback);
    }

    try {
      console.log(`📥 Handling offer from ${userId}`);
      await pc.setRemoteDescription(new RTCSessionDescription(description));
      
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      sendMessage({
        type: 'video_answer',
        sdp: answer,
        target: userId
      });

      // Process queued ICE candidates
      const queue = remoteIceQueuesRef.current[userId] || [];
      if (queue.length > 0) {
        for (const candidate of queue) {
          await pc.addIceCandidate(new RTCIceCandidate(candidate)).catch(e => console.warn(e));
        }
        remoteIceQueuesRef.current[userId] = [];
      }
    } catch (error) {
      console.error(`❌ Error handling offer from ${userId}:`, error);
    }
  }, [sendMessage, createPeerConnection]);

  const handleVideoAnswer = useCallback(async (userId, description) => {
    const pc = peerConnectionsRef.current[userId];
    if (!pc) return;
    
    try {
      console.log(`📥 Handling answer from ${userId}`);
      await pc.setRemoteDescription(new RTCSessionDescription(description));
      
      const queue = remoteIceQueuesRef.current[userId] || [];
      if (queue.length > 0) {
        for (const candidate of queue) {
          await pc.addIceCandidate(new RTCIceCandidate(candidate)).catch(e => console.warn(e));
        }
        remoteIceQueuesRef.current[userId] = [];
      }
    } catch (error) {
      console.error(`❌ Error handling answer from ${userId}:`, error);
    }
  }, []);

  const handleIceCandidate = useCallback(async (userId, candidate) => {
    const pc = peerConnectionsRef.current[userId];
    if (!pc || !pc.remoteDescription) {
      if (!remoteIceQueuesRef.current[userId]) remoteIceQueuesRef.current[userId] = [];
      remoteIceQueuesRef.current[userId].push(candidate);
    } else {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(candidate));
      } catch (e) {
        console.warn(`🧊 ICE candidate error [${userId}]:`, e);
      }
    }
  }, []);

  const stopWebRTC = useCallback(() => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }
    
    Object.keys(peerConnectionsRef.current).forEach(userId => {
      peerConnectionsRef.current[userId].close();
    });
    peerConnectionsRef.current = {};
    remoteStreamsRef.current = {};
    remoteIceQueuesRef.current = {};
  }, []);

  return {
    peerConnectionsRef,
    localStreamRef,
    remoteStreamsRef,
    createPeerConnection,
    initLocalStream,
    createVideoOffer,
    handleVideoOffer,
    handleVideoAnswer,
    handleIceCandidate,
    stopWebRTC
  };
};

export default useWebRTC;
