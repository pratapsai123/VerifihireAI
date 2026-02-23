import React, { Suspense, useRef, useState, useEffect } from 'react';
import Professional3DAvatar from './Professional3DAvatar';

/**
 * ReadyPlayerMeAvatar - 3D Avatar Loader with SVG Fallback
 * 
 * HOW TO ACTIVATE TRUE 3D:
 * 1. Go to https://readyplayer.me and create a free avatar
 * 2. Copy the GLB URL (format: https://models.readyplayer.me/YOUR_ID.glb)
 * 3. Set AVATAR_URL below to your copied URL
 * 4. The component will automatically load the 3D model
 * 
 * Until a valid URL is set, the premium SVG avatar is used.
 */

// ── SET YOUR READY PLAYER ME URL HERE ──
// Leave as null to use the SVG avatar, or paste your RPM URL
const AVATAR_URL = null; // e.g. 'https://models.readyplayer.me/YOUR_ID.glb'

// Lazy-loaded 3D Canvas (only imported when AVATAR_URL is set)
let Canvas, useFrame, useGLTF, Environment, OrbitControls, ContactShadows, THREE;

function AvatarModel({ isSpeaking, onError }) {
    const { scene, nodes } = useGLTF(AVATAR_URL, true, true, (error) => {
        console.error('GLB Load Error:', error);
        onError?.();
    });
    const group = useRef();

    useFrame((state) => {
        if (!group.current) return;
        const t = state.clock.getElapsedTime();
        group.current.position.y = Math.sin(t * 1.5) * 0.015;
        group.current.rotation.z = Math.sin(t * 0.8) * 0.008;
        group.current.rotation.x = Math.sin(t * 1.2) * 0.015;

        // Lip-Sync via morph targets
        if (nodes?.Wolf3D_Head?.morphTargetInfluences && nodes?.Wolf3D_Head?.morphTargetDictionary) {
            const mouthIdx = nodes.Wolf3D_Head.morphTargetDictionary['mouthOpen'];
            if (mouthIdx !== undefined) {
                const target = isSpeaking ? 0.3 + Math.sin(t * 15) * 0.2 : 0;
                nodes.Wolf3D_Head.morphTargetInfluences[mouthIdx] = THREE.MathUtils.lerp(
                    nodes.Wolf3D_Head.morphTargetInfluences[mouthIdx], target, 0.2
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

const ThreeCanvas = ({ isSpeaking, onError }) => (
    <Canvas shadows camera={{ position: [0, 0, 5], fov: 35 }}>
        <ambientLight intensity={0.6} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        <Suspense fallback={null}>
            <AvatarModel isSpeaking={isSpeaking} onError={onError} />
            <Environment preset="city" />
            <ContactShadows opacity={0.4} scale={10} blur={2.4} far={4.5} />
        </Suspense>
        <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} />
    </Canvas>
);

const ReadyPlayerMeAvatar = ({ isSpeaking }) => {
    const [use3D, setUse3D] = useState(false);
    const [threeLoaded, setThreeLoaded] = useState(false);

    // Only attempt 3D if AVATAR_URL is set
    useEffect(() => {
        if (!AVATAR_URL) return;

        // Dynamically import Three.js only when needed
        Promise.all([
            import('@react-three/fiber'),
            import('@react-three/drei'),
            import('three')
        ]).then(([fiber, drei, three]) => {
            Canvas = fiber.Canvas;
            useFrame = fiber.useFrame;
            useGLTF = drei.useGLTF;
            Environment = drei.Environment;
            OrbitControls = drei.OrbitControls;
            ContactShadows = drei.ContactShadows;
            THREE = three;
            setThreeLoaded(true);
            setUse3D(true);
        }).catch(err => {
            console.warn('Three.js import failed:', err);
            setUse3D(false);
        });
    }, []);

    // Default: use the premium SVG avatar
    if (!use3D || !threeLoaded) {
        return <Professional3DAvatar isSpeaking={isSpeaking} />;
    }

    return (
        <ModelErrorBoundary fallback={<Professional3DAvatar isSpeaking={isSpeaking} />}>
            <div style={{ width: '100%', height: '320px', position: 'relative', overflow: 'hidden' }}>
                <ThreeCanvas isSpeaking={isSpeaking} onError={() => setUse3D(false)} />

                {/* Name Tag */}
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
