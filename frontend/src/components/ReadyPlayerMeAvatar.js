import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, Environment, OrbitControls, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import Professional3DAvatar from './Professional3DAvatar';

/**
 * ReadyPlayerMeAvatar - True 3D Avatar for Indu
 * Uses a self-hosted GLB model in /public/models/
 * Falls back to SVG avatar if 3D fails to load.
 */

// Self-hosted model (downloaded and stored locally for reliability)
const AVATAR_URL = '/models/indu-avatar.glb';

function AvatarModel({ isSpeaking }) {
    const { scene, nodes } = useGLTF(AVATAR_URL);
    const group = useRef();

    useFrame((state) => {
        if (!group.current) return;
        const t = state.clock.getElapsedTime();

        // Idle Breathing
        group.current.position.y = Math.sin(t * 1.5) * 0.015;
        // Subtle Head Tilt
        group.current.rotation.z = Math.sin(t * 0.8) * 0.008;
        group.current.rotation.x = Math.sin(t * 1.2) * 0.015;

        // Lip-Sync via morph targets (Wolf3D_Head is standard for RPM models)
        if (nodes?.Wolf3D_Head?.morphTargetInfluences && nodes?.Wolf3D_Head?.morphTargetDictionary) {
            const mouthIdx = nodes.Wolf3D_Head.morphTargetDictionary['mouthOpen'];
            if (mouthIdx !== undefined) {
                const target = isSpeaking ? 0.3 + Math.sin(t * 15) * 0.2 : 0;
                nodes.Wolf3D_Head.morphTargetInfluences[mouthIdx] = THREE.MathUtils.lerp(
                    nodes.Wolf3D_Head.morphTargetInfluences[mouthIdx], target, 0.2
                );
            }
        }

        // Also try jaw bone animation for non-RPM models  
        if (nodes?.Head) {
            // Generic head bone breathing
        }
    });

    return (
        <group ref={group} scale={1} position={[0, 0, 0]}>
            <primitive object={scene} />
        </group>
    );
}

// Error boundary for 3D loading failures
class ModelErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() { return { hasError: true }; }
    componentDidCatch(error) {
        console.warn('3D model failed, using SVG fallback:', error.message);
    }
    render() {
        return this.state.hasError ? this.props.fallback : this.props.children;
    }
}

// Loading spinner
const LoadingSpinner = () => (
    <div style={{
        width: '100%', height: '100%',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', gap: '10px'
    }}>
        <div style={{
            width: 36, height: 36,
            border: '3px solid rgba(139, 92, 246, 0.2)',
            borderTop: '3px solid #a855f7',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
        }} />
        <span style={{ color: '#94a3b8', fontSize: '11px', fontWeight: 600 }}>Loading 3D Avatar...</span>
        <style>{`@keyframes spin { to { transform: rotate(360deg); }}`}</style>
    </div>
);

const ReadyPlayerMeAvatar = ({ isSpeaking }) => {
    return (
        <ModelErrorBoundary fallback={<Professional3DAvatar isSpeaking={isSpeaking} />}>
            <div style={{ width: '100%', height: '380px', position: 'relative', overflow: 'hidden' }}>
                <Suspense fallback={<LoadingSpinner />}>
                    <Canvas shadows camera={{ position: [0, 1.2, 3.5], fov: 45 }}>
                        <ambientLight intensity={0.7} />
                        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                        <pointLight position={[-10, -10, -10]} intensity={0.5} />

                        <AvatarModel isSpeaking={isSpeaking} />
                        <Environment preset="city" />

                        {/* Diagnostic Helpers */}
                        <gridHelper args={[10, 10]} position={[0, 0, 0]} />
                        <ContactShadows opacity={0.4} scale={10} blur={2.4} far={4.5} />

                        <OrbitControls
                            enableZoom={true}
                            enablePan={true}
                            enableRotate={true}
                        />
                    </Canvas>
                </Suspense>

                {/* Glassmorphism Name Tag */}
                <div style={{
                    position: 'absolute', bottom: 15, left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(15, 23, 42, 0.6)',
                    backdropFilter: 'blur(10px)',
                    padding: '6px 20px', borderRadius: '100px',
                    border: '1px solid rgba(139, 92, 246, 0.4)',
                    color: '#e2e8f0', fontSize: '11px', fontWeight: 800,
                    letterSpacing: '1.5px', whiteSpace: 'nowrap',
                    display: 'flex', alignItems: 'center', gap: '8px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)', pointerEvents: 'none'
                }}>
                    <div style={{
                        width: 8, height: 8, borderRadius: '50%',
                        background: isSpeaking ? '#a855f7' : '#64748b',
                        boxShadow: isSpeaking ? '0 0 12px #a855f7' : 'none'
                    }} />
                    INDU • AI INTERVIEWER
                </div>
            </div>
        </ModelErrorBoundary>
    );
};

export default ReadyPlayerMeAvatar;
