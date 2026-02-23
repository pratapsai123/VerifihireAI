import React, { Suspense, useRef, useEffect } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { useGLTF, Environment, OrbitControls, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

/**
 * ReadyPlayerMeAvatar Component
 * Integrates a high-quality 3D avatar from Ready Player Me.
 * Features:
 * 1. GLB Loading from RPM CDN.
 * 2. Lip-Sync: Reactively scales the mouth/jaw area based on isSpeaking prop.
 * 3. Idle Animations: Smooth breathing and head tilting.
 */
function AvatarModel({ isSpeaking }) {
    // Use a professional female avatar from Ready Player Me
    // Defaulting to a high-quality professional Indian female persona if possible, 
    // otherwise a standard professional professional model.
    const { scene, nodes, materials } = useGLTF('https://models.readyplayer.me/65d8ba151240c1e8609560f7.glb');
    const group = useRef();
    const mouthRef = useRef();

    // Find the head/mouth area for lip-sync scaling
    useEffect(() => {
        scene.traverse((child) => {
            if (child.isMesh && (child.name.includes('Head') || child.name.includes('Beard') || child.name.includes('Teeth'))) {
                // We can target specific morph targets if available, 
                // but for a generic GLB, we'll use subtle scaling if no blendshapes are easily accessible
            }
        });
    }, [scene]);

    useFrame((state) => {
        const t = state.clock.getElapsedTime();

        // 1. Idle Breathing Animation
        group.current.position.y = Math.sin(t * 1.5) * 0.02;

        // 2. Subtle Head Tilt
        group.current.rotation.z = Math.sin(t * 0.8) * 0.01;
        group.current.rotation.x = Math.sin(t * 1.2) * 0.02;

        // 3. Lip-Sync Simulation (Generic)
        // Most RPM models have 'mouthOpen' morph target
        if (nodes.Wolf3D_Head && nodes.Wolf3D_Head.morphTargetInfluences) {
            const mouthOpenIdx = nodes.Wolf3D_Head.morphTargetDictionary['mouthOpen'];
            if (mouthOpenIdx !== undefined) {
                const target = isSpeaking ? 0.3 + Math.sin(t * 15) * 0.2 : 0;
                nodes.Wolf3D_Head.morphTargetInfluences[mouthOpenIdx] = THREE.MathUtils.lerp(
                    nodes.Wolf3D_Head.morphTargetInfluences[mouthOpenIdx],
                    target,
                    0.2
                );
            }
        }
    });

    return (
        <group ref={group} scale={2.8} position={[0, -3.2, 0]}>
            <primitive object={scene} />
        </group>
    );
}

const ReadyPlayerMeAvatar = ({ isSpeaking }) => {
    return (
        <div style={{ width: '100%', height: '320px', position: 'relative', overflow: 'hidden' }}>
            <Canvas shadows camera={{ position: [0, 0, 5], fov: 35 }}>
                <ambientLight intensity={0.6} />
                <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                <pointLight position={[-10, -10, -10]} intensity={0.5} />

                <Suspense fallback={null}>
                    <AvatarModel isSpeaking={isSpeaking} />
                    <Environment preset="city" />
                    <ContactShadows opacity={0.4} scale={10} blur={2.4} far={4.5} />
                </Suspense>

                {/* Prevent user from rotating the avatar manually for a standardized view */}
                <OrbitControls
                    enableZoom={false}
                    enablePan={false}
                    enableRotate={false}
                    minPolarAngle={Math.PI / 2.2}
                    maxPolarAngle={Math.PI / 2.2}
                />
            </Canvas>

            {/* Glassmorphism Name Tag Overlay */}
            <div style={{
                position: 'absolute', bottom: 15, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(15, 23, 42, 0.6)',
                backdropFilter: 'blur(10px)',
                padding: '6px 20px',
                borderRadius: '100px',
                border: '1px solid rgba(139, 92, 246, 0.4)',
                color: '#e2e8f0',
                fontSize: '11px', fontWeight: 800,
                letterSpacing: '1.5px',
                whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                pointerEvents: 'none'
            }}>
                <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: isSpeaking ? '#a855f7' : '#64748b',
                    boxShadow: isSpeaking ? '0 0 12px #a855f7' : 'none'
                }} />
                INDU • AI INTERVIEWER
            </div>
        </div>
    );
};

export default ReadyPlayerMeAvatar;
