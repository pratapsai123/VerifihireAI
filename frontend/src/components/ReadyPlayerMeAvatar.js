import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, OrbitControls, ContactShadows, Float, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';
import Professional3DAvatar from './Professional3DAvatar';

/**
 * ProfessionalAIBot - Procedural 3D Bot Avatar
 * 
 * Replaces the GLB model with a sleek, digital entity.
 * Uses Three.js primitives for instant loading and technical aesthetic.
 */

function BotModel({ isSpeaking }) {
    const headRef = useRef();
    const visorRef = useRef();
    const coreRef = useRef();

    useFrame((state) => {
        const t = state.clock.getElapsedTime();

        // 1. Subtle Scanning Micro-movements
        if (headRef.current) {
            headRef.current.rotation.y = Math.sin(t * 0.5) * 0.15;
            headRef.current.rotation.x = Math.cos(t * 0.3) * 0.05;
        }

        // 2. Speech Reactivity: Pulsing Visor and Core
        if (visorRef.current && coreRef.current) {
            const pulse = isSpeaking ? (0.8 + Math.sin(t * 30) * 0.5) : 0.5;
            visorRef.current.material.emissiveIntensity = pulse * 2;
            coreRef.current.material.emissiveIntensity = pulse * 1.5;

            // Subtle "Scale pulse" when speaking
            const scalePulse = isSpeaking ? (1 + Math.sin(t * 15) * 0.02) : 1;
            visorRef.current.scale.set(scalePulse, scalePulse, scalePulse);
        }
    });

    return (
        <group position={[0, 0, 0]}>
            {/* Main Head Structure */}
            <mesh ref={headRef} position={[0, 0, 0]}>
                <sphereGeometry args={[1, 32, 32]} />
                <meshStandardMaterial
                    color="#2c3e50"
                    roughness={0.1}
                    metalness={0.9}
                    envMapIntensity={1}
                />

                {/* Futuristic Visor */}
                <mesh ref={visorRef} position={[0, 0.1, 0.85]}>
                    <boxGeometry args={[1.2, 0.15, 0.2]} />
                    <meshStandardMaterial
                        emissive="#00f2ff"
                        emissiveIntensity={2}
                        color="#00f2ff"
                    />
                </mesh>

                {/* Inner Core (Visible through gaps or design) */}
                <mesh ref={coreRef} position={[0, -0.4, 0.7]}>
                    <sphereGeometry args={[0.2, 16, 16]} />
                    <meshStandardMaterial
                        emissive="#00f2ff"
                        emissiveIntensity={1}
                        color="#00f2ff"
                    />
                </mesh>
            </mesh>

            {/* Torso / Base Unit */}
            <mesh position={[0, -1.8, 0]}>
                <capsuleGeometry args={[0.8, 1.2, 4, 16]} />
                <meshStandardMaterial
                    color="#1a202c"
                    roughness={0.2}
                    metalness={0.8}
                />
            </mesh>

            {/* Glowing Accent Rings */}
            <mesh position={[0, -1, 0]} rotation={[Math.PI / 2, 0, 0]}>
                <torusGeometry args={[0.85, 0.02, 16, 100]} />
                <meshStandardMaterial emissive="#00f2ff" emissiveIntensity={0.5} />
            </mesh>
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
            border: '3px solid rgba(0, 242, 255, 0.2)',
            borderTop: '3px solid #00f2ff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
        }} />
        <span style={{ color: '#00f2ff', fontSize: '11px', fontWeight: 600 }}>Booting AI Bot...</span>
        <style>{`@keyframes spin { to { transform: rotate(360deg); }}`}</style>
    </div>
);

const ReadyPlayerMeAvatar = ({ isSpeaking }) => {
    return (
        <div style={{
            width: '100%', height: '320px', position: 'relative', overflow: 'hidden',
            background: 'radial-gradient(circle at center, #1a202c 0%, #0f172a 100%)'
        }}>
            <Suspense fallback={<LoadingSpinner />}>
                <Canvas shadows camera={{ position: [0, 0, 5], fov: 35 }}>
                    <ambientLight intensity={0.5} />
                    <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                    <pointLight position={[-10, -10, -10]} intensity={0.5} />

                    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                        <BotModel isSpeaking={isSpeaking} />
                    </Float>

                    <Environment preset="city" />
                    <ContactShadows position={[0, -3, 0]} opacity={0.4} scale={10} blur={2.4} far={4.5} />

                    <OrbitControls
                        enableZoom={false}
                        enablePan={false}
                        enableRotate={false}
                        target={[0, -0.5, 0]}
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
                border: '1px solid rgba(0, 242, 255, 0.4)',
                color: '#e2e8f0', fontSize: '11px', fontWeight: 800,
                letterSpacing: '1.5px', whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)', pointerEvents: 'none'
            }}>
                <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: isSpeaking ? '#00f2ff' : '#64748b',
                    boxShadow: isSpeaking ? '0 0 12px #00f2ff' : 'none'
                }} />
                INDU • PROFESSIONAL AI BOT
            </div>
        </div>
    );
};

export default ReadyPlayerMeAvatar;
