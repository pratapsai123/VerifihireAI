import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, Environment, OrbitControls, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import Professional3DAvatar from './Professional3DAvatar';

/**
 * BACKUP: InduAvatarBackup - Store of Indu's 3D settings
 * 
 * This file preserves the 3D configuration developed for the female avatar persona "Indu".
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

            const mouthIdx = headDict['mouthOpen'] ?? headDict['MouthOpen'] ?? headDict['jawOpen'];

            if (mouthIdx !== undefined) {
                let targetValue = 0;
                if (isSpeaking) {
                    const jitter = Math.sin(t * 26) * 0.12;
                    const syllable = Math.sin(t * 14) * 0.35;
                    const base = 0.35;
                    targetValue = Math.max(0, Math.min(0.9, base + syllable + jitter));
                }
                headInfluences[mouthIdx] = THREE.MathUtils.lerp(headInfluences[mouthIdx], targetValue, 0.45);

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
        <group ref={group} scale={3.9} position={[0, 0, 0]}>
            <primitive object={scene} />
        </group>
    );
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
        <span style={{ color: '#94a3b8', fontSize: '11px', fontWeight: 600 }}>Syncing...</span>
        <style>{`@keyframes spin { to { transform: rotate(360deg); }}`}</style>
    </div>
);

const InduAvatarBackup = ({ isSpeaking }) => {
    return (
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
        </div>
    );
};

export default InduAvatarBackup;
