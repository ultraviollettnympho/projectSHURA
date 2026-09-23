import React, { useRef, useEffect, useState } from 'react';

/**
 * SHURA_02 3D Embodiment Viewer
 * 
 * Loads Three.js from CDN to avoid disk space constraints.
 * Displays the rigged GLB with animation controls.
 */

const THREE_CDN = 'https://unpkg.com/three@0.160.0/build/three.module.js';
const GLTF_CDN = 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
const MODEL_PATH = '/models/shura_02.glb';

export default function EmbodimentViewer() {
    const canvasRef = useRef(null);
    const [animations, setAnimations] = useState([]);
    const [currentAnim, setCurrentAnim] = useState('idle-loop');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const sceneRef = useRef(null);
    const mixerRef = useRef(null);
    const clockRef = useRef(null);
    const actionsRef = useRef({});
    const frameRef = useRef(null);

    useEffect(() => {
        let cancelled = false;
        
        async function init() {
            try {
                // Dynamic imports from CDN
                const THREE = await import(/* @vite-ignore */ THREE_CDN);
                const { GLTFLoader } = await import(/* @vite-ignore */ GLTF_CDN);
                
                if (cancelled) return;

                const canvas = canvasRef.current;
                if (!canvas) return;

                // Scene
                const scene = new THREE.Scene();
                scene.background = null; // Transparent
                sceneRef.current = scene;

                // Camera
                const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
                camera.position.set(0, 0.5, 4);
                camera.lookAt(0, 0, 0);

                // Renderer
                const renderer = new THREE.WebGLRenderer({ 
                    canvas, 
                    antialias: true, 
                    alpha: true,
                    powerPreference: 'high-performance'
                });
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.2;

                // Lights
                const ambient = new THREE.AmbientLight(0xffffff, 0.4);
                scene.add(ambient);

                const keyLight = new THREE.DirectionalLight(0x00d0ff, 1.2);
                keyLight.position.set(5, 5, 5);
                keyLight.castShadow = true;
                scene.add(keyLight);

                const rimLight = new THREE.DirectionalLight(0xff2a8a, 0.6);
                rimLight.position.set(-5, 5, -5);
                scene.add(rimLight);

                const fillLight = new THREE.DirectionalLight(0x6600aa, 0.3);
                fillLight.position.set(0, 2, 0);
                scene.add(fillLight);

                // Ground shadow
                const groundGeo = new THREE.PlaneGeometry(4, 4);
                const groundMat = new THREE.ShadowMaterial({ opacity: 0.2 });
                const ground = new THREE.Mesh(groundGeo, groundMat);
                ground.rotation.x = -Math.PI / 2;
                ground.position.y = -1.5;
                ground.receiveShadow = true;
                scene.add(ground);

                // Grid helper
                const grid = new THREE.GridHelper(4, 20, 0x00d0ff, 0x1a1a2e);
                grid.position.y = -1.49;
                grid.material.opacity = 0.15;
                grid.material.transparent = true;
                scene.add(grid);

                // Load model
                const loader = new GLTFLoader();
                loader.load(
                    MODEL_PATH,
                    (gltf) => {
                        if (cancelled) return;

                        const model = gltf.scene;
                        model.scale.set(1.5, 1.5, 1.5);
                        model.position.set(0, -1.5, 0);
                        
                        model.traverse((child) => {
                            if (child.isMesh) {
                                child.castShadow = true;
                                child.receiveShadow = true;
                            }
                        });

                        scene.add(model);

                        // Setup animations
                        const mixer = new THREE.AnimationMixer(model);
                        mixerRef.current = mixer;

                        const animClips = gltf.animations || [];
                        const actions = {};
                        animClips.forEach((clip) => {
                            const action = mixer.clipAction(clip);
                            actions[clip.name] = action;
                        });
                        actionsRef.current = actions;
                        setAnimations(animClips.map(c => c.name));

                        // Play default
                        const defaultAnim = animClips.find(c => c.name === 'idle-loop') || animClips[0];
                        if (defaultAnim) {
                            actions[defaultAnim.name].play();
                        }

                        setLoading(false);

                        // Animation loop
                        const clock = new THREE.Clock();
                        clockRef.current = clock;
                        
                        function animate() {
                            if (cancelled) return;
                            frameRef.current = requestAnimationFrame(animate);
                            
                            const delta = clock.getDelta();
                            mixer.update(delta);
                            
                            // Subtle model rotation
                            model.rotation.y += 0.002;
                            
                            renderer.render(scene, camera);
                        }
                        animate();
                    },
                    undefined,
                    (err) => {
                        if (!cancelled) {
                            setError('Failed to load model');
                            setLoading(false);
                        }
                    }
                );

                // Handle resize
                function onResize() {
                    if (!canvas || cancelled) return;
                    const w = canvas.clientWidth;
                    const h = canvas.clientHeight;
                    camera.aspect = w / h;
                    camera.updateProjectionMatrix();
                    renderer.setSize(w, h);
                }
                window.addEventListener('resize', onResize);

            } catch (err) {
                if (!cancelled) {
                    setError('Failed to load 3D libraries');
                    setLoading(false);
                }
            }
        }

        init();

        return () => {
            cancelled = true;
            if (frameRef.current) cancelAnimationFrame(frameRef.current);
            window.removeEventListener('resize', () => {});
        };
    }, []);

    // Change animation
    useEffect(() => {
        const actions = actionsRef.current;
        if (!actions[currentAnim]) return;

        // Fade out all
        Object.values(actions).forEach(action => {
            action.fadeOut(0.3);
        });

        // Fade in selected
        actions[currentAnim].reset().fadeIn(0.3).play();
    }, [currentAnim]);

    const presetAnimations = [
        'idle-loop', 'walk-loop', 'stand-loop', 'active_idle',
        'attack', 'floating_standby', 'power_up_float', 'bad_bitch_walk'
    ];

    return (
        <div className="relative h-full w-full overflow-hidden rounded-b3 border border-line bg-bg">
            {/* Canvas */}
            <canvas ref={canvasRef} className="h-full w-full" />

            {/* Loading */}
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-bg/80">
                    <div className="flex flex-col items-center gap-3">
                        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                        <p className="font-mono text-xs text-dim">Loading SHURA_02...</p>
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center">
                    <p className="font-mono text-sm text-flux-err">{error}</p>
                </div>
            )}

            {/* Animation Controls */}
            <div className="absolute bottom-3 left-3 right-3">
                <div className="glass-quiet flex flex-wrap items-center gap-2 p-2">
                    {presetAnimations.map((name) => (
                        <button
                            key={name}
                            onClick={() => setCurrentAnim(name)}
                            className={`
                                rounded-b1 px-2 py-1 font-mono text-[10px] uppercase tracking-wider transition-colors
                                ${currentAnim === name 
                                    ? 'bg-accent/20 text-accent border border-accent/30' 
                                    : 'bg-fill text-dim hover:text-text hover:bg-fill-2 border border-transparent'}
                            `}
                        >
                            {name.replace('-', ' ').replace('_', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Status */}
            <div className="absolute right-3 top-3">
                <div className="flex items-center gap-2 rounded-b1 border border-line bg-raised/80 px-2 py-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                    <span className="font-mono text-[10px] uppercase tracking-widest text-faint">
                        SHURA_02
                    </span>
                </div>
            </div>
        </div>
    );
}
