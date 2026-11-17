import * as THREE from 'three';
import './style.css';

const host = document.querySelector('#stage');
const scene = new THREE.Scene();
scene.background = new THREE.Color('#182733');
scene.fog = new THREE.Fog('#182733', 26, 62);
const camera = new THREE.PerspectiveCamera(37, 9 / 16, 0.1, 120);
camera.up.set(0, 0, 1);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
host.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xe8f2ff, 0x4c3d34, 1.65));
const key = new THREE.DirectionalLight(0xffd3a0, 3.1);
key.position.set(-8, -9, 15);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
scene.add(key);
const fill = new THREE.DirectionalLight(0x8bb8d1, 1.45);
fill.position.set(9, -2, 9);
scene.add(fill);
const rim = new THREE.DirectionalLight(0xffa969, 1.9);
rim.position.set(0, 12, 10);
scene.add(rim);

const material = (color, roughness = 0.82, metalness = 0) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness });
const palette = {
  stone: material('#b69b79'),
  paleStone: material('#cfb894'),
  brick: material('#8f4937'),
  brick2: material('#ad6146'),
  timber: material('#33251f'),
  glass: material('#527b8e', 0.22, 0.12),
  roof: material('#303943'),
  road: material('#202a31', 0.56),
  paving: material('#77756d'),
  brass: material('#b7893d', 0.26, 0.72),
  parchment: material('#decaa2'),
  leather: material('#4b2d22'),
  ink: material('#463b30'),
  skin: material('#d49a70'),
  coat: material('#294e65'),
  coatTrim: material('#b77a35'),
  shoe: material('#252329'),
  lamp: new THREE.MeshStandardMaterial({
    color: '#ffb45c', emissive: '#ff8f32', emissiveIntensity: 1.25, roughness: 0.28
  })
};

function addBox(parent, name, pos, size, mat, bevel = 0.025) {
  const geometry = new THREE.BoxGeometry(...size);
  const mesh = new THREE.Mesh(geometry, mat);
  mesh.name = name;
  mesh.position.set(...pos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  if (bevel > 0) {
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({
      color: '#171a1c', transparent: true, opacity: 0.12
    }));
    mesh.add(line);
  }
  parent.add(mesh);
  return mesh;
}

function addSphere(parent, name, pos, scale, mat) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), mat);
  mesh.name = name;
  mesh.position.set(...pos);
  mesh.scale.set(...scale);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function addWindow(parent, x, z, frontY, label, blind = false) {
  const w = 0.96, h = 1.45;
  addBox(parent, label + ' recess', [x, frontY, z], [w, 0.11, h], palette.timber, 0.008);
  addBox(parent, label + ' glass', [x, frontY - 0.075, z], [w - 0.18, 0.035, h - 0.20],
    blind ? palette.stone : palette.glass, 0.008);
  const frameY = frontY - 0.12;
  for (const dx of [-w / 2, w / 2]) {
    addBox(parent, label + ' jamb', [x + dx, frameY, z], [0.1, 0.13, h + 0.12], palette.timber);
  }
  for (const dz of [-h / 2, h / 2]) {
    addBox(parent, label + ' sash', [x, frameY, z + dz], [w + 0.1, 0.13, 0.1], palette.timber);
  }
  addBox(parent, label + ' mullion', [x, frameY - 0.01, z], [0.055, 0.15, h - 0.1], palette.timber);
  addBox(parent, label + ' crossbar', [x, frameY - 0.02, z], [w - 0.1, 0.15, 0.055], palette.timber);
  addBox(parent, label + ' sill', [x, frontY - 0.2, z - h / 2 - 0.08], [w + 0.26, 0.32, 0.16], palette.paleStone);
  addBox(parent, label + ' lintel', [x, frontY - 0.16, z + h / 2 + 0.09], [w + 0.18, 0.2, 0.17], palette.paleStone);
}

const world = new THREE.Group();
scene.add(world);
addBox(world, 'Paving', [0, 0.5, -0.2], [42, 38, 0.35], palette.paving, 0.04);
addBox(world, 'Cobbled road', [0, -5, -0.01], [40, 10, 0.10], palette.road, 0.02);

const facades = [
  { x: -10.2, width: 7, height: 7.6, frontY: 6, wall: palette.paleStone, columns: 2 },
  { x: 0, width: 13, height: 9.4, frontY: 6, wall: palette.stone, columns: 4 },
  { x: 10, width: 7, height: 7.2, frontY: 6, wall: palette.paleStone, columns: 2 }
];

facades.forEach((b, bi) => {
  addBox(world, 'Georgian house ' + (bi + 1), [b.x, b.frontY + 0.85, b.height / 2],
    [b.width, 1.7, b.height], b.wall, 0.07);
  addBox(world, 'Plinth ' + (bi + 1), [b.x, b.frontY - 0.02, 0.55],
    [b.width + 0.18, 0.28, 0.65], palette.brick, 0.03);
  addBox(world, 'Cornice ' + (bi + 1), [b.x, b.frontY - 0.05, b.height - 0.1],
    [b.width + 0.3, 0.3, 0.22], palette.paleStone, 0.02);
  addBox(world, 'Slate fascia ' + (bi + 1), [b.x, b.frontY + 0.85, b.height + 0.2],
    [b.width + 0.5, 2.05, 0.45], palette.roof, 0.04);
  for (let row = 0; row < 3; row++) {
    for (let col = 0; col < b.columns; col++) {
      const x = bi === 1 ? b.x - 4.7 + col * 3.1 : b.x - 1.8 + col * 3.6;
      const z = [2.25, 4.55, 6.85][row];
      const blind = bi === 1 && row === 1 && col === 3;
      addWindow(world, x, z, b.frontY - 0.06, 'Facade ' + (bi + 1) + ' window ' + row + '-' + col, blind);
    }
  }
});

const brickWindow = { x: -1.6, z: 4.55, y: 5.55 };
const bricks = [];
for (let row = 0; row < 3; row++) for (let col = 0; col < 2; col++) {
  const end = new THREE.Vector3(
    brickWindow.x - 0.21 + col * 0.42,
    brickWindow.y,
    brickWindow.z - 0.47 + row * 0.44
  );
  const mesh = addBox(world, 'Animated tax brick ' + (row * 2 + col + 1),
    [end.x + 2.2, end.y, end.z - 1.6], [0.4, 0.16, 0.38],
    (row + col) % 2 ? palette.brick2 : palette.brick, 0.018);
  bricks.push({ mesh, start: mesh.position.clone(), end });
}

const ledger = new THREE.Group();
scene.add(ledger);
addBox(ledger, 'Assessor table', [2.7, -1, 0.78], [4, 2.1, 0.22], palette.timber, 0.08);
for (const x of [1, 4.4]) for (const y of [-1.8, -0.2]) {
  addBox(ledger, 'Table leg', [x, y, 0.34], [0.16, 0.16, 0.75], palette.timber, 0.02);
}
addBox(ledger, 'Ledger leather cover', [2.45, -0.95, 0.94], [1.45, 1.15, 0.12], palette.leather, 0.025);
addBox(ledger, 'Ledger page', [2.45, -0.92, 1.015], [1.27, 1.02, 0.025], palette.parchment, 0.01);
addBox(ledger, 'Ledger fold', [2.45, -0.92, 1.035], [0.025, 1.02, 0.02], palette.leather, 0.005);
for (let row = 0; row < 5; row++) {
  addBox(ledger, 'Ledger ruled line', [2.45, -1.30 + row * 0.18, 1.052],
    [0.86, 0.012, 0.008], palette.ink, 0.002);
}
const coins = [];
for (let i = 0; i < 9; i++) {
  const coin = new THREE.Mesh(new THREE.CylinderGeometry(0.105, 0.105, 0.035, 28), palette.brass);
  coin.position.set(3.75 + (i % 3) * 0.24, -1.20 + Math.floor(i / 3) * 0.25,
    0.91 + Math.floor(i / 3) * 0.035);
  coin.rotation.x = Math.PI / 2;
  coin.castShadow = true;
  ledger.add(coin);
  coins.push(coin);
}

for (const x of [-8.8, 8.6]) {
  addBox(world, 'Lamp post', [x, -1.2, 2.25], [0.10, 0.10, 4.4], palette.timber);
  addBox(world, 'Lamp arm', [x + 0.34, -1.2, 4.23], [0.72, 0.10, 0.10], palette.timber);
  addBox(world, 'Gas lantern', [x + 0.67, -1.2, 4.0], [0.37, 0.37, 0.55], palette.lamp);
}

const actor = new THREE.Group();
scene.add(actor);
actor.position.set(-2.6, -0.8, 0);
addBox(actor, 'Host coat', [0, 0, 1.35], [0.68, 0.44, 0.9], palette.coat, 0.12);
addSphere(actor, 'Host head', [0, -0.01, 2.22], [0.43, 0.42, 0.48], palette.skin);
addSphere(actor, 'Host hair', [0, 0, 2.52], [0.45, 0.43, 0.22], palette.timber);
for (const x of [-0.14, 0.14]) {
  addSphere(actor, 'Eye', [x, -0.39, 2.26], [0.055, 0.035, 0.08], palette.ink);
}
addSphere(actor, 'Coat button', [0, -0.24, 1.56], [0.055, 0.035, 0.055], palette.coatTrim);
const armPivots = [];
for (const x of [-0.4, 0.4]) {
  const pivot = new THREE.Group();
  pivot.position.set(x, 0, 1.68);
  actor.add(pivot);
  addSphere(pivot, 'Sleeve', [0, 0, -0.35], [0.14, 0.16, 0.42], palette.coat);
  armPivots.push(pivot);
}
const legPivots = [];
for (const x of [-0.18, 0.18]) {
  const pivot = new THREE.Group();
  pivot.position.set(x, 0, 0.94);
  actor.add(pivot);
  addSphere(pivot, 'Trouser leg', [0, 0, -0.32], [0.16, 0.17, 0.4], palette.coatTrim);
  addBox(pivot, 'Boot', [0, -0.11, -0.65], [0.2, 0.28, 0.14], palette.shoe, 0.04);
  legPivots.push(pivot);
}

const cameraKeys = [
  [0, [0, -18, 7], [0, 5, 4.3], 38],
  [5, [-4, -11, 5.2], [-4, 5, 4.2], 52],
  [10, [-2.6, -8, 2.6], [-2.6, -0.8, 1.55], 54],
  [15, [0, -10, 5.8], [0, 5, 5], 51],
  [20, [-1.6, -7, 5], [-1.6, 5, 4.55], 69],
  [25, [-1.6, -5.7, 4.7], [-1.6, 5, 4.55], 82],
  [30, [0, -13, 6.6], [0, 5, 4.4], 43],
  [35, [2.7, -5.8, 8.4], [2.7, -1, 0.9], 57],
  [40, [0, -15, 7.1], [0, 5, 5], 41],
  [45, [3.8, -8, 4.6], [3.8, 5, 4.1], 57],
  [50, [0, -17, 6.3], [0, 5, 4.4], 39],
  [55, [0, -19, 8.2], [0, 5, 4.4], 36]
];

const titleOverlay = document.createElement('div');
titleOverlay.className = 'title-overlay';
titleOverlay.textContent = 'TAXED SUNLIGHT';
host.appendChild(titleOverlay);

let elapsed = 0;
let running = true;
let cameraDistance = 1;
let actorTravel = 0.5;
let lastTime = performance.now();

function smoothstep(v) { return v * v * (3 - 2 * v); }
function updateCamera(time) {
  let index = 0;
  while (index < cameraKeys.length - 1 && time > cameraKeys[index + 1][0]) index++;
  const a = cameraKeys[index];
  const b = cameraKeys[Math.min(index + 1, cameraKeys.length - 1)];
  const u = b[0] === a[0] ? 0 : smoothstep(THREE.MathUtils.clamp((time - a[0]) / (b[0] - a[0]), 0, 1));
  const pA = new THREE.Vector3(...a[1]), pB = new THREE.Vector3(...b[1]);
  const tA = new THREE.Vector3(...a[2]), tB = new THREE.Vector3(...b[2]);
  camera.position.lerpVectors(pA, pB, u);
  camera.position.y *= cameraDistance;
  const target = new THREE.Vector3().lerpVectors(tA, tB, u);
  const lens = THREE.MathUtils.lerp(a[3], b[3], u);
  camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(24 / (2 * lens)));
  camera.updateProjectionMatrix();
  camera.lookAt(target);
}

function renderFrame() {
  const now = performance.now();
  const delta = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  if (running) elapsed = Math.min(60, elapsed + delta);
  const t = elapsed;

  actor.visible = t < 16;
  actor.position.x = -2.6 + Math.sin(t * 0.7) * actorTravel;
  actor.position.z = Math.abs(Math.sin(t * Math.PI * 2)) * 0.07;
  actor.rotation.z = Math.sin(t * 1.15) * 0.035;
  armPivots.forEach((p, i) => { p.rotation.x = Math.sin(t * 5 + i * Math.PI) * 0.34; });
  legPivots.forEach((p, i) => { p.rotation.x = Math.sin(t * 6 + i * Math.PI) * 0.52; });

  const brickProgress = THREE.MathUtils.clamp((t - 18) / 8, 0, 1);
  bricks.forEach(({ mesh, start, end }) => {
    mesh.visible = t >= 18;
    mesh.position.lerpVectors(start, end, smoothstep(brickProgress));
  });
  coins.forEach((coin, i) => { coin.rotation.z = Math.sin(t * 1.8 + i) * 0.08; });
  titleOverlay.style.opacity = t < 4 ? String(1 - Math.max(0, t - 2.8) / 1.2) : '0';
  updateCamera(t);
  renderer.render(scene, camera);

  const scrubber = document.querySelector('#timeline');
  const readout = document.querySelector('#timeReadout');
  if (scrubber && document.activeElement !== scrubber) scrubber.value = String(t);
  if (readout) {
    const seconds = Math.floor(t % 60);
    readout.textContent = '0:' + String(seconds).padStart(2, '0');
  }
  if (t >= 60) {
    running = false;
    document.querySelector('#play').textContent = 'Replay';
  }
  requestAnimationFrame(renderFrame);
}

function resize() {
  const width = host.clientWidth;
  const height = host.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(host);
resize();
requestAnimationFrame(renderFrame);

document.querySelector('#play').addEventListener('click', (event) => {
  if (elapsed >= 60) elapsed = 0;
  running = !running;
  event.currentTarget.textContent = running ? 'Pause' : 'Play';
});
document.querySelector('#restart').addEventListener('click', () => {
  elapsed = 0;
  running = true;
  document.querySelector('#play').textContent = 'Pause';
});
document.querySelector('#distance').addEventListener('input', (event) => {
  cameraDistance = Number(event.target.value);
});
document.querySelector('#travel').addEventListener('input', (event) => {
  actorTravel = Number(event.target.value);
});
document.querySelector('#timeline').addEventListener('input', (event) => {
  elapsed = Number(event.target.value);
  running = false;
  document.querySelector('#play').textContent = 'Play';
});
