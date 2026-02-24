import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, Environment, OrbitControls, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import Professional3DAvatar from './Professional3DAvatar';

/**
 * ReadyPlayerMeAvatar - True 3D Avatar for Indu
 * 
 * Optimized for models with limited morph targets.
 * Uses a "Syllabic Jitter" system to simulate speech realism.
 */

const AVATAR_URL = '/models/indu-avatar.glb';

function AvatarModel({ isSpeaking }) {
    const { scene, nodes } = useGLTF(AVATAR_URL);
    const group = useRef();

    useFrame((state) => {
        if (!group.current) return;
        const t = state.clock.getElapsedTime();

        // 1. Stable Identity (Zero idle movement)
        group.current.position.y = 0;
        group.current.rotation.x = 0;
        group.current.rotation.z = 0;

        // 2. Specialized Lip-Sync for Limited Morph Targets
        const head = nodes?.Wolf3D_Head;
        const teeth = nodes?.Wolf3D_Teeth;

        if (head?.morphTargetInfluences && head?.morphTargetDictionary) {
            const headDict = head.morphTargetDictionary;
            const headInfluences = head.morphTargetInfluences;
            const teethDict = teeth?.morphTargetDictionary;
            const teethInfluences = teeth?.morphTargetInfluences;

            // Find the best available 'opening' target (RPM usually has mouthOpen)
            const mouthIdx = headDict['mouthOpen'] ?? headDict['MouthOpen'] ?? headDict['jawOpen'];

            if (mouthIdx !== undefined) {
                let targetValue = 0;
                if (isSpeaking) {
                    // PHONETIC SIMULATOR: Combines fast jitter + mid-freq syllables + constant opening
                    const jitter = Math.sin(t * 26) * 0.12;
                    const syllable = Math.sin(t * 14) * 0.35;
                    const base = 0.35;
                    targetValue = Math.max(0, Math.min(0.9, base + syllable + jitter));
                }

                // Smoothly blend using higher lerp for snappier speech
                headInfluences[mouthIdx] = THREE.MathUtils.lerp(headInfluences[mouthIdx], targetValue, 0.45);

                // Keep teeth perfectly in sync
                if (teethInfluences && teethDict) {
                    const tMouthIdx = teethDict['mouthOpen'] ?? teethDict['MouthOpen'] ?? teethDict['jawOpen'];
                    if (tMouthIdx !== undefined) {
                        teethInfluences[tMouthIdx] = headInfluences[mouthIdx];
                    }
                }
            }
        }

        // 3. Subtle Eye Blinking
        const eyes = nodes?.Wolf3D_Head;
        if (eyes?.morphTargetDictionary && eyes?.morphTargetInfluences) {
            const blinkIdx = eyes.morphTargetDictionary['eyeBlinkLeft'] ?? eyes.morphTargetDictionary['eyesBlink'];
            if (blinkIdx !== undefined) {
                // Blink every 3-5 seconds
                const blink = Math.sin(t * 0.5) > 0.98 ? 1 : 0;
                eyes.morphTargetInfluences[blinkIdx] = THREE.MathUtils.lerp(eyes.morphTargetInfluences[blinkIdx], blink, 0.5);

                const blinkRIdx = eyes.morphTargetDictionary['eyeBlinkRight'];
                if (blinkRIdx !== undefined) {
                    eyes.morphTargetInfluences[blinkRIdx] = eyes.morphTargetInfluences[blinkIdx];
                }
            }
        }
    });

    return (
        <group ref={group} scale={3.75} position={[0, 0, 0]}>
            <primitive object={scene} />
        </group>
    );
}

class ModelErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() { return { hasError: true }; }
    render() {
        return this.state.hasError ? this.props.fallback : this.props.children;
    }
}

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
        <span style={{ color: '#94a3b8', fontSize: '11px', fontWeight: 600 }}>Syncing Indu...</span>
        <style>{`@keyframes spin { to { transform: rotate(360deg); }}`}</style>
    </div>
);

const ReadyPlayerMeAvatar = ({ isSpeaking }) => {
    return (
        <ModelErrorBoundary fallback={<Professional3DAvatar isSpeaking={isSpeaking} />}>
            <div style={{ width: '100%', height: '320px', position: 'relative', overflow: 'hidden' }}>
                <Suspense fallback={<LoadingSpinner />}>
                    <Canvas shadows camera={{ position: [0.15, 6.37, 2.71], fov: 35 }}>
                        <ambientLight intensity={0.8} />
                        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                        <pointLight position={[-10, -10, -10]} intensity={0.5} />
                        <AvatarModel isSpeaking={isSpeaking} />
                        <Environment preset="city" />
                        <ContactShadows opacity={0.4} scale={10} blur={2.4} far={4.5} />
                        <OrbitControls
                            enableZoom={false}
                            enablePan={false}
                            enableRotate={false}
                            target={[-0.11, 6.13, -1.58]}
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
