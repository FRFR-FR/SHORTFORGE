import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { kit } from './kit.js';

const params = new URLSearchParams(location.search);
const width = Number(params.get('width') || 1280);
const height = Number(params.get('height') || 720);
const fps = Number(params.get('fps') || 30);
const episodePath = params.get('episode');

const stage = document.querySelector('#stage');
const errorNode = document.querySelector('#error');
function fail(error) {
  errorNode.style.display = 'block';
  errorNode.textContent = error?.stack || String(error);
  window.__ANIME_ERROR__ = errorNode.textContent;
}

if (!episodePath || !episodePath.startsWith('/projects/')) {
  fail('Missing or invalid local episode module path.');
  throw new Error('Missing local episode module.');
}

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  powerPreference: 'high-performance',
  preserveDrawingBuffer: true
});
renderer.setPixelRatio(1);
renderer.setSize(width, height, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#070a18');
scene.fog = new THREE.FogExp2('#11142a', 0.009);
scene.add(new THREE.HemisphereLight('#cad7ff', '#20152e', 1.45));

const keyLight = new THREE.DirectionalLight('#fff0dc', 2.6);
keyLight.position.set(-7, -9, 13);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.left = -24;
keyLight.shadow.camera.right = 24;
keyLight.shadow.camera.top = 24;
keyLight.shadow.camera.bottom = -24;
scene.add(keyLight);

const cyanRim = new THREE.DirectionalLight('#19e6f4', 2.6);
cyanRim.position.set(8, 4, 8);
scene.add(cyanRim);
const magentaFill = new THREE.DirectionalLight('#ed159f', 1.9);
magentaFill.position.set(-9, 2, 5);
scene.add(magentaFill);

const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 180);
camera.up.set(0, 0, 1);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(width, height), 0.82, 0.52, 0.72);
composer.addPass(bloom);

const FilmShader = {
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
    uIntensity: { value: 0.12 }
  },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: [
    'uniform sampler2D tDiffuse;',
    'uniform float uTime;',
    'uniform float uIntensity;',
    'varying vec2 vUv;',
    'float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)) + uTime * 19.17) * 43758.5453); }',
    'void main(){',
    'vec4 col = texture2D(tDiffuse, vUv);',
    'float d = distance(vUv, vec2(0.5));',
    'float vignette = smoothstep(0.82, 0.22, d);',
    'float grain = (hash(gl_FragCoord.xy) - 0.5) * 0.025;',
    'col.rgb *= mix(0.72, 1.0, vignette);',
    'col.rgb += grain * uIntensity;',
    'gl_FragColor = col;',
    '}'
  ].join('\n')
};
const film = new ShaderPass(FilmShader);
composer.addPass(film);
composer.addPass(new OutputPass());

let activeEpisode;
let activeConfig;
let currentFrame = -1;
const episodeUrl = new URL(episodePath, location.origin).href;

try {
  const response = await fetch(episodePath.replace(/\.js$/, '.json'));
  if (response.ok) activeConfig = await response.json();
  const module = await import(episodeUrl);
  if (typeof module.createEpisode !== 'function') throw new Error('episode.js must export createEpisode()');
  activeEpisode = await module.createEpisode({ THREE, scene, camera, renderer, composer, kit, config: activeConfig });
  if (!activeEpisode || typeof activeEpisode.update !== 'function') throw new Error('createEpisode() must return { update(time, frame) }');
  window.setFrame = async (frame) => {
    const safeFrame = Math.max(0, Math.min(Math.floor(frame), 10000000));
    if (safeFrame === currentFrame) return;
    currentFrame = safeFrame;
    const time = safeFrame / fps;
    await activeEpisode.update(time, safeFrame, { THREE, scene, camera, renderer, composer, kit, config: activeConfig });
    film.uniforms.uTime.value = time;
    composer.render();
  };
  await window.setFrame(0);
  window.__ANIME_READY__ = true;
} catch (error) {
  fail(error);
  throw error;
}
