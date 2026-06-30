import { useRef, useCallback } from 'react';

export const useWebRTC = (sendMessage, myUserId) => {
  const peerConnectionsRef = useRef({}); // { userId: RTCPeerConnection }
  const localStreamRef = useRef(null);
  const remoteStreamsRef = useRef({}); // { userId: MediaStream }
  const remoteIceQueuesRef = useRef({}); // { userId: [RTCIceCandidate] }

  const createPeerConnection = useCallback((userId, onTrackCallback, additionalStreams = []) => {
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
          target: userId 
        });
      }
    };

    peerConnection.ontrack = (event) => {
      console.log(`🎥 Received track from ${userId}!`, event.track.kind, 'Stream ID:', event.streams[0]?.id);
      const remoteStream = event.streams[0];
      if (remoteStream) {
        // Store the last received stream in the ref for generic access
        remoteStreamsRef.current[userId] = remoteStream;
        // Pass more context to the callback
        if (onTrackCallback) onTrackCallback(userId, remoteStream, event);
      }
    };

    peerConnection.oniceconnectionstatechange = () => {
        console.log(`❄️ ICE Connection [${userId}]:`, peerConnection.iceConnectionState);
    };

    // Add all provided streams (usually [localStream, screenShareStream])
    const streamsToAdd = [localStreamRef.current, ...additionalStreams].filter(Boolean);
    streamsToAdd.forEach(stream => {
        stream.getTracks().forEach(track => {
            const sender = peerConnection.getSenders().find(s => s.track === track);
            if (!sender) {
                console.log(`📡 Adding track ${track.kind} (${track.label}) to PC for ${userId}`);
                peerConnection.addTrack(track, stream);
            }
        });
    });

    return peerConnection;
  }, []);

  const removePeerConnection = useCallback((userId) => {
    if (peerConnectionsRef.current[userId]) {
        console.log(`🗑️ Removing peer connection for ${userId}`);
        peerConnectionsRef.current[userId].close();
        delete peerConnectionsRef.current[userId];
    }
    delete remoteStreamsRef.current[userId];
    delete remoteIceQueuesRef.current[userId];
  }, []);

  const initLocalStream = useCallback(async (videoConstraints = true, audioConstraints = true, videoDeviceId = null, audioDeviceId = null) => {
    try {
      console.log('🎙️ Initializing local stream...');
      const videoOptions = videoConstraints
        ? {
            width: { ideal: 1280, max: 1920 },
            height: { ideal: 720, max: 1080 },
            frameRate: { ideal: 30, max: 60 },
            facingMode: 'user',
            ...(videoDeviceId ? { deviceId: { exact: videoDeviceId } } : {})
          }
        : false;

      const audioOptions = audioConstraints
        ? {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            sampleRate: 44100,
            ...(audioDeviceId ? { deviceId: { exact: audioDeviceId } } : {})
          }
        : false;

      const localStream = await navigator.mediaDevices.getUserMedia({
        video: videoOptions,
        audio: audioOptions
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
      console.log(`📥 Handling offer from ${userId}. Current state: ${pc.signalingState}`);
      
      const isOfferCollision = (pc.signalingState !== 'stable');
      const isImpolite = myUserId && userId && myUserId < userId;

      if (isOfferCollision) {
          if (isImpolite) {
              console.warn(`[WebRTC] Collision detected. I am impolite, ignoring offer from ${userId}`);
              return;
          }
          console.log(`[WebRTC] Collision detected. I am polite, rolling back and accepting offer from ${userId}`);
          await Promise.all([
              pc.setLocalDescription({type: "rollback"}),
              pc.setRemoteDescription(new RTCSessionDescription(description))
          ]);
      } else {
          await pc.setRemoteDescription(new RTCSessionDescription(description));
      }
      
      if (pc.signalingState !== 'have-remote-offer') {
          console.warn(`[WebRTC] Wrong state for answer: ${pc.signalingState}`);
          return;
      }
      
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
      // 🔥 FIX: If PC is already stable, this answer is stale (from a rolled-back negotiation).
      // Ignore it silently to prevent InvalidStateError.
      if (pc.signalingState === 'stable') {
        console.warn(`[WebRTC] Ignoring stale answer from ${userId} — PC already in stable state (glare resolved).`);
        return;
      }
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
    removePeerConnection,
    initLocalStream,
    createVideoOffer,
    handleVideoOffer,
    handleVideoAnswer,
    handleIceCandidate,
    stopWebRTC
  };
};

export default useWebRTC;
