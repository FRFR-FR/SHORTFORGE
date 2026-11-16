import * as THREE from 'three';
import './style.css';

const host = document.querySelector('#stage');
const scene = new THREE.Scene();
scene.background = new THREE.Color('#a8cddd');
scene.fog = new THREE.Fog('#a8cddd', 18, 42);
const camera = new THREE.PerspectiveCamera(34, 9 / 16, 0.1, 100);
camera.up.set(0, 0, 1);
camera.position.set(0, -13.2, 4.2);
camera.lookAt(0, 1.1, 2.0);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
host.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xe7f5ff, 0x786b5d, 2.1));
const key = new THREE.DirectionalLight(0xffe0ba, 3.2);
key.position.set(-6, -8, 12);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
scene.add(key);
const rim = new THREE.DirectionalLight(0x9bcce4, 1.5);
rim.position.set(7, 3, 8);
scene.add(rim);

const mat = (color, roughness = 0.82) => new THREE.MeshStandardMaterial({ color, roughness });
const mats = {
  ground: mat('#8c887c'), road: mat('#252f39'), sidewalk: mat('#bbb6a8'),
  buildings: ['#bd6f5d', '#4b9196', '#c4a071', '#82799f'].map(c => mat(c)),
  window: mat('#4f8092', 0.3), leaf: mat('#3b7747'), trunk: mat('#684a35'),
  primary: mat('#237bb6'), accent: mat('#e99432'), skin: mat('#d79662'),
  dark: mat('#202a35'), white: mat('#f4eee4'), lane: mat('#ebcf8e')
};

function box(parent, name, pos, size, material, bevel = false) {
  const geometry = new THREE.BoxGeometry(...size);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  mesh.position.set(...pos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function ball(parent, name, pos, scale, material) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12), material);
  mesh.name = name;
  mesh.position.set(...pos);
  mesh.scale.set(...scale);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

const ground = box(scene, 'Ground', [0, 2, -0.22], [28, 36, 0.4], mats.ground);
box(scene, 'Road', [0, -0.2, 0], [28, 7.2, 0.08], mats.road);
box(scene, 'Far sidewalk', [0, 3.65, 0.07], [28, 1.2, 0.16], mats.sidewalk);
box(scene, 'Near sidewalk', [0, -4.05, 0.07], [28, 1.2, 0.16], mats.sidewalk);
for (let x = -12; x <= 12; x += 3) box(scene, 'Road dash', [x, -0.2, 0.06], [1.35, 0.13, 0.035], mats.lane);

[-10, -5.2, 0, 5.2, 10].forEach((x, i) => {
  const width = i % 2 ? 3.8 : 4.2;
  const height = [5.4, 6.5, 5.8, 7.0, 5.2][i];
  box(scene, `Building ${i}`, [x, 6.5, height / 2], [width, 2.1, height], mats.buildings[i % 4]);
  const cols = Math.max(2, Math.floor(width / 0.9));
  const rows = Math.max(2, Math.floor(height / 1.05) - 1);
  for (let row = 0; row < rows; row++) for (let col = 0; col < cols; col++) {
    const wx = x - width / 2 + (col + 0.5) * width / cols;
    box(scene, 'Window', [wx, 5.43, 0.85 + row * 1.05], [0.42, 0.045, 0.55], mats.window);
  }
});
for (const x of [-8.2, -3, 3, 8.2]) {
  box(scene, 'Tree trunk', [x, 3.8, 0.68], [0.2, 0.2, 1.35], mats.trunk);
  ball(scene, 'Tree crown', [x, 3.8, 1.55], [0.65, 0.58, 0.7], mats.leaf);
}

// A Three.js-only previs character mirrors the Blender blocking proportions.
const actor = new THREE.Group();
scene.add(actor);
const torso = box(actor, 'Torso', [0, 0, 1.48], [0.74, 0.48, 0.86], mats.primary);
const head = ball(actor, 'Head', [0, -0.015, 2.32], [0.47, 0.43, 0.48], mats.skin);
ball(actor, 'Hair', [0, 0.005, 2.63], [0.49, 0.44, 0.24], mats.dark);
for (const x of [-0.16, 0.16]) {
  ball(actor, 'Eye white', [x, -0.405, 2.34], [0.075, 0.045, 0.105], mats.white);
  ball(actor, 'Eye pupil', [x, -0.448, 2.33], [0.035, 0.024, 0.055], mats.dark);
}
ball(actor, 'Mouth', [0, -0.433, 2.12], [0.09, 0.025, 0.025], mats.dark);
const limbs = [];
for (const [side, x, direction] of [['L', -0.43, 1], ['R', 0.43, -1]]) {
  const pivot = new THREE.Group();
  pivot.position.set(x, 0, 1.82);
  actor.add(pivot);
  ball(pivot, `Arm ${side}`, [0, 0, -0.38], [0.145, 0.16, 0.46], mats.primary);
  ball(pivot, `Hand ${side}`, [0, -0.015, -0.76], [0.15, 0.15, 0.15], mats.skin);
  limbs.push({ pivot, direction, phase: 0 });
}
for (const [side, x, direction] of [['L', -0.2, -1], ['R', 0.2, 1]]) {
  const pivot = new THREE.Group();
  pivot.position.set(x, 0, 1.08);
  actor.add(pivot);
  ball(pivot, `Leg ${side}`, [0, 0, -0.36], [0.18, 0.19, 0.46], mats.accent);
  ball(pivot, `Shoe ${side}`, [0, -0.12, -0.72], [0.18, 0.28, 0.15], mats.dark);
  limbs.push({ pivot, direction, phase: Math.PI });
}

const car = new THREE.Group();
scene.add(car);
box(car, 'Car body', [0, 0, 0.45], [1.55, 0.78, 0.46], mat('#e94e27'));
box(car, 'Cabin', [-0.08, 0, 0.82], [0.83, 0.68, 0.42], mat('#477f91'));
for (const x of [-0.48, 0.48]) for (const y of [-0.34, 0.34]) ball(car, 'Wheel', [x, y, 0.2], [0.19, 0.12, 0.19], mat('#20252b'));

const titleCanvas = document.createElement('canvas');
titleCanvas.width = 1024; titleCanvas.height = 160;
const ctx = titleCanvas.getContext('2d');
ctx.fillStyle = 'rgba(13, 27, 39, 0.78)';
ctx.fillRect(80, 18, 864, 124);
ctx.fillStyle = '#fff0ce';
ctx.font = '800 58px system-ui';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillText('SHORTFORGE', 512, 82);
const titleTexture = new THREE.CanvasTexture(titleCanvas);
const titleMesh = new THREE.Mesh(new THREE.PlaneGeometry(6.3, 0.98), new THREE.MeshBasicMaterial({ map: titleTexture, transparent: true, depthWrite: false }));
titleMesh.position.set(0, -0.4, 4.65);
titleMesh.rotation.x = Math.PI / 2;
scene.add(titleMesh);

const clock = new THREE.Clock();
let running = true;
let elapsed = 0;
let travel = 0.45;
let cameraDistance = 13.2;
function resize() {
  const width = host.clientWidth;
  const height = host.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(host);
resize();

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  if (running) elapsed += delta;
  const t = elapsed;
  actor.position.x = Math.sin(t * 0.55) * travel;
  actor.position.z = Math.abs(Math.sin(t * Math.PI * 2)) * 0.08;
  actor.rotation.z = Math.sin(t * 1.3) * 0.035;
  limbs.forEach(({ pivot, direction, phase }) => { pivot.rotation.x = Math.sin(t * Math.PI * 2 + phase) * 0.72 * direction; });
  car.position.set(-10.5 + ((t * 2.2) % 21), 1.7, 0);
  camera.position.set(0.12 * Math.sin(t * 0.18), -cameraDistance, 4.2 + Math.sin(t * 0.25) * 0.12);
  camera.lookAt(0, 1.1, 2.0);
  renderer.render(scene, camera);
}
animate();

document.querySelector('#play').addEventListener('click', (event) => {
  running = !running;
  event.currentTarget.textContent = running ? 'Pause' : 'Play';
});
document.querySelector('#restart').addEventListener('click', () => { elapsed = 0; running = true; document.querySelector('#play').textContent = 'Pause'; });
document.querySelector('#distance').addEventListener('input', (event) => { cameraDistance = Number(event.target.value); });
document.querySelector('#travel').addEventListener('input', (event) => { travel = Number(event.target.value); });
