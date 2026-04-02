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

    console.log('🏗️ PeerConnection created with state:', peerConnection.signalingState);

    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('📡 Local ICE candidate:', event.candidate.candidate.substring(0, 40) + '...');
        sendMessage({
          type: 'ice_candidate',
          candidate: event.candidate
        });
      }
    };

    peerConnection.ontrack = (event) => {
      console.log('🎥 Received remote track!', event.track.kind, 'Stream count:', event.streams.length);
      const remoteStream = event.streams[0];
      if (remoteStream) {
        remoteStreamRef.current = remoteStream;
        console.log('✅ Remote stream set successfully');
        if (onTrackCallback) onTrackCallback(remoteStream);
      } else {
        console.warn('⚠️ ontrack event has no streams!');
      }
    };

    peerConnection.oniceconnectionstatechange = () => {
        console.log('❄️ ICE Connection State:', peerConnection.iceConnectionState);
    };

    peerConnection.onsignalingstatechange = () => {
        console.log('📣 Signaling State:', peerConnection.signalingState);
    };

    return peerConnection;
  }, [sendMessage]);

  const initLocalStream = useCallback(async (videoConstraints = true, audioConstraints = true) => {
    try {
      console.log('🎙️ Initializing local stream...');
      const localStream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints ? { width: { ideal: 1280, max: 1920 }, height: { ideal: 720, max: 1080 }, frameRate: { ideal: 30, max: 60 }, facingMode: 'user' } : false,
        audio: audioConstraints ? { echoCancellation: true, noiseSuppression: true, autoGainControl: true, sampleRate: 44100 } : false
      });
      console.log('✅ Local stream obtained. Tracks:', localStream.getTracks().map(t => t.kind));
      localStreamRef.current = localStream;
      return localStream;
    } catch (error) {
      console.error('❌ Media access failed:', error);
      throw error;
    }
  }, []);

  const addLocalTracksToPC = useCallback((peerConnection, localStream) => {
    if (!localStream || !peerConnection) return;
    console.log('🛤️ Adding tracks to PeerConnection...');
    localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, localStream);
    });
    console.log('✅ Local tracks added successfully');
  }, []);

  const createVideoOffer = useCallback(async (options = {}) => {
    if (!peerConnectionRef.current) return;
    if (peerConnectionRef.current.signalingState !== 'stable') {
      console.warn('Skipping offer, signaling not stable');
      return;
    }
    try {
      console.log('📤 Creating video offer...', options);
      const offer = await peerConnectionRef.current.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true,
        ...options
      });
      await peerConnectionRef.current.setLocalDescription(offer);
      sendMessage({
        type: 'video_offer',
        sdp: offer
      });
      console.log('✅ Video offer sent');
    } catch (error) {
      console.error('❌ Error creating video offer:', error);
    }
  }, [sendMessage]);

  const handleVideoOffer = useCallback(async (description) => {
    if (!peerConnectionRef.current) return;
    try {
      console.log('📥 Handling video offer...', peerConnectionRef.current.signalingState);
      
      // Guard against stale offers during rapid signaling
      if (peerConnectionRef.current.signalingState !== 'stable' && 
          peerConnectionRef.current.signalingState !== 'have-local-offer') {
          console.warn('⚠️ Unexpected signaling state for offer handler:', peerConnectionRef.current.signalingState);
      }

      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(description));
      
      // ✅ Fix: Ensure local tracks are added BEFORE creating the answer
      if (localStreamRef.current) {
        console.log('🛤️ Adding local tracks before answer...');
        localStreamRef.current.getTracks().forEach(track => {
          const exists = peerConnectionRef.current
            .getSenders()
            .some(sender => sender.track === track);
            
          if (!exists) {
            peerConnectionRef.current.addTrack(track, localStreamRef.current);
            console.log(`✅ Added ${track.kind} track`);
          }
        });
      }

      const answer = await peerConnectionRef.current.createAnswer();
      await peerConnectionRef.current.setLocalDescription(answer);
      sendMessage({
        type: 'video_answer',
        sdp: answer
      });
      console.log('✅ Video answer sent with tracks');

      // Process queued ICE candidates
      if (remoteIceQueueRef.current.length > 0) {
        console.log(`🧊 Processing ${remoteIceQueueRef.current.length} queued ICE candidates`);
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
          } catch (e) {
            console.warn('Failed to add queued ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('❌ Error handling video offer:', error);
    }
  }, [sendMessage]);

  const handleVideoAnswer = useCallback(async (description) => {
    if (!peerConnectionRef.current) return;
    
    console.log('📥 Handling video answer. Current state:', peerConnectionRef.current.signalingState);
    if (peerConnectionRef.current.signalingState !== 'have-local-offer') {
      console.warn('⚠️ Skipping handleVideoAnswer: signalingState is not have-local-offer');
      return;
    }

    try {
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(description));
      console.log('✅ Remote description set with answer');
      
      if (remoteIceQueueRef.current.length > 0) {
        console.log(`🧊 Processing ${remoteIceQueueRef.current.length} queued ICE candidates`);
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
          } catch (e) {
            console.warn('Failed to add queued ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('❌ Error handling video answer:', error);
    }
  }, []);

  const handleIceCandidate = useCallback(async (candidate) => {
    if (!peerConnectionRef.current) return;
    try {
      if (!peerConnectionRef.current.remoteDescription) {
        console.log('🧊 Queuing remote ICE candidate');
        remoteIceQueueRef.current.push(candidate);
      } else {
        await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (e) {
      console.warn('🧊 ICE candidate error:', e);
    }
  }, []);

  const stopWebRTC = useCallback(() => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }
    if (remoteStreamRef.current) {
      remoteStreamRef.current.getTracks().forEach(track => track.stop());
      remoteStreamRef.current = null;
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
