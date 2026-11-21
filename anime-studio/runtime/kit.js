import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const toon = (color, extra = {}) => new THREE.MeshToonMaterial({
  color,
  gradientMap: null,
  ...extra
});
const ink = new THREE.MeshBasicMaterial({ color: '#080914', side: THREE.BackSide });
const capsuleGeometry = (radius, length, radialSegments = 10) => {
  const geometry = new THREE.CapsuleGeometry(radius, length, 6, radialSegments);
  geometry.rotateX(Math.PI / 2); // Scene convention is Z-up.
  return geometry;
};
const seeded = (seed) => {
  let value = seed >>> 0;
  return () => {
    value = (value * 1664525 + 1013904223) >>> 0;
    return value / 4294967296;
  };
};
export const smoothStep = (value) => {
  const t = THREE.MathUtils.clamp(value, 0, 1);
  return t * t * (3 - 2 * t);
};
export const easeOutCubic = (value) => 1 - Math.pow(1 - THREE.MathUtils.clamp(value, 0, 1), 3);

function outlinedMesh(geometry, material, scale = 1.035) {
  const group = new THREE.Group();
  const shell = new THREE.Mesh(geometry, ink);
  shell.scale.setScalar(scale);
  shell.renderOrder = 1;
  const surface = new THREE.Mesh(geometry, material);
  surface.renderOrder = 2;
  surface.castShadow = true;
  surface.receiveShadow = true;
  group.add(shell, surface);
  return group;
}
function addBox(parent, position, size, color, opts = {}) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), toon(color, opts.emissive ? { emissive: opts.emissive, emissiveIntensity: opts.intensity ?? 1 } : {}));
  mesh.position.set(...position);
  mesh.castShadow = opts.shadow !== false;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function addNeonBar(parent, position, size, color, intensity = 2.2) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), new THREE.MeshStandardMaterial({
    color, emissive: color, emissiveIntensity: intensity, roughness: 0.25, metalness: 0.1
  }));
  mesh.position.set(...position);
  parent.add(mesh);
  return mesh;
}
function makeGlow(parent, position, color, intensity, distance, size = 0.24) {
  const light = new THREE.PointLight(color, intensity, distance, 2);
  light.position.set(...position);
  parent.add(light);
  const orb = new THREE.Mesh(new THREE.SphereGeometry(size, 16, 12), new THREE.MeshBasicMaterial({ color }));
  orb.position.copy(light.position);
  parent.add(orb);
  return light;
}

function createSign(parent, text, position, color, width = 2.8, height = 0.72) {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 256;
  const context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = 'rgba(8, 8, 24, 0.88)';
  context.fillRect(8, 8, 1008, 240);
  context.strokeStyle = color;
  context.lineWidth = 12;
  context.strokeRect(14, 14, 996, 228);
  context.shadowColor = color;
  context.shadowBlur = 34;
  context.fillStyle = '#ffffff';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.font = '900 114px Arial, sans-serif';
  context.fillText(text.toUpperCase(), 512, 128, 930);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true, side: THREE.DoubleSide, depthWrite: false });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
  mesh.position.set(...position);
  mesh.rotation.x = Math.PI / 2;
  parent.add(mesh);
  return mesh;
}

/**
 * Layered 2.5D neon megacity with road reflections, foreground occlusion,
 * midground towers, distant skyline, emissive signs and motivated practicals.
 */
export function createCyberpunkCity(scene, options = {}) {
  const random = seeded(options.seed ?? 31);
  const palette = options.palette ?? ['#070b1a', '#171b36', '#18e5ed', '#ef149f', '#ffb74d'];
  const far = new THREE.Group();
  const mid = new THREE.Group();
  const near = new THREE.Group();
  scene.add(far, mid, near);

  const sky = new THREE.Mesh(
    new THREE.PlaneGeometry(130, 55),
    new THREE.MeshBasicMaterial({ color: '#10112c' })
  );
  sky.position.set(0, 28, 16);
  sky.rotation.x = Math.PI / 2;
  far.add(sky);

  for (let i = 0; i < 54; i++) {
    const width = 1.2 + random() * 2.4;
    const height = 4 + random() * 18;
    const depth = 0.6 + random() * 1.6;
    const x = -36 + i * 1.35 + random() * 0.8;
    const building = addBox(far, [x, 17 + random() * 3, height / 2 - 1], [width, depth, height], i % 3 === 0 ? '#25213f' : '#171b34', { shadow: false });
    building.material = toon(i % 4 === 0 ? '#24213e' : '#161b31');
    for (let row = 0; row < Math.min(10, Math.floor(height / 1.45)); row++) {
      for (let col = 0; col < Math.max(1, Math.floor(width / 0.5)); col++) {
        if (random() > 0.42) continue;
        const color = random() > 0.62 ? palette[2] : random() > 0.4 ? palette[3] : '#ffbd69';
        addNeonBar(far, [x - width / 2 + 0.25 + col * 0.42, 16.15, 0.5 + row * 1.18], [0.13, 0.035, 0.34], color, 0.6);
      }
    }
    if (i % 5 === 0) {
      addNeonBar(far, [x, 17 - depth / 2 - 0.05, height * 0.72], [width * 0.72, 0.08, 0.09], palette[i % 2 ? 2 : 3], 2.1);
    }
  }

  for (let i = 0; i < 22; i++) {
    const x = -25 + i * 2.4 + random() * 0.7;
    const width = 1.8 + random() * 2.4;
    const height = 8 + random() * 12;
    const building = addBox(mid, [x, 8.5 + random() * 1.8, height / 2 - 0.5], [width, 2.8, height], i % 2 ? '#252540' : '#1a213a');
    building.material.color.set(i % 3 === 0 ? '#302344' : '#202842');
    addNeonBar(mid, [x, 6.97 + random() * 0.4, height - 0.3], [width * 0.9, 0.08, 0.12], i % 2 ? palette[2] : palette[3], 2.6);
    for (let floor = 0; floor < Math.floor(height / 1.5); floor++) {
      for (let side = -1; side <= 1; side += 2) {
        if (random() < 0.3) continue;
        addNeonBar(mid, [x + side * (width * 0.28), 6.99, 0.8 + floor * 1.36], [0.24, 0.045, 0.66], random() > 0.5 ? '#43dfea' : '#ff5bb9', 0.9);
      }
    }
    if (i % 4 === 1) createSign(mid, ['NOVA', 'KAIRO', 'VOID', 'ARCADIA'][i % 4], [x, 6.35, height * 0.64], palette[i % 2 ? 2 : 3], 1.8, 0.52);
  }

  const asphalt = new THREE.Mesh(
    new THREE.PlaneGeometry(90, 50),
    new THREE.MeshStandardMaterial({ color: '#101528', roughness: 0.22, metalness: 0.55 })
  );
  asphalt.position.set(0, 0, -0.08);
  scene.add(asphalt);

  const roadGrid = new THREE.GridHelper(70, 65, '#123e56', '#15233c');
  roadGrid.rotation.x = Math.PI / 2;
  roadGrid.position.set(0, -0.18, 0.01);
  roadGrid.material.transparent = true;
  roadGrid.material.opacity = 0.27;
  scene.add(roadGrid);

  for (let i = 0; i < 12; i++) {
    const x = -18 + i * 3.25;
    addNeonBar(scene, [x, 0.05, 0.025], [0.09, 21, 0.035], i % 2 ? palette[2] : palette[3], 1.15);
  }

  for (const x of [-16, -8, 7, 15]) {
    const mast = addBox(near, [x, -3.6, 4.2], [0.16, 0.22, 8.4], '#171b2d');
    mast.material = toon('#171b2d');
    addNeonBar(near, [x, -3.75, 7.8], [0.34, 0.12, 0.12], x < 0 ? palette[2] : palette[3], 2.3);
    makeGlow(near, [x, -3.8, 7.6], x < 0 ? palette[2] : palette[3], 5, 14, 0.15);
  }

  createSign(near, 'NIGHT SHIFT', [-8.5, -5.2, 6.3], palette[3], 3.5, 0.88);
  createSign(near, '24 / 7', [9.5, -4.5, 4.6], palette[2], 2.1, 0.68);

  const fog = new THREE.Mesh(
    new THREE.PlaneGeometry(90, 8),
    new THREE.MeshBasicMaterial({ color: '#23445e', transparent: true, opacity: 0.13, depthWrite: false })
  );
  fog.position.set(0, 3.2, 1.1);
  fog.rotation.x = Math.PI / 2;
  scene.add(fog);

  const practicals = [];
  practicals.push(makeGlow(scene, [-10, 0.2, 3.7], palette[3], 18, 22, 0.22));
  practicals.push(makeGlow(scene, [8, 0.4, 3.0], palette[2], 16, 20, 0.2));
  practicals.push(makeGlow(scene, [0, 4.5, 8.0], '#ff9f56', 13, 25, 0.18));

  return {
    far, mid, near,
    update(time) {
      far.position.x = Math.sin(time * 0.13) * 0.12;
      mid.position.x = Math.sin(time * 0.24) * 0.34;
      near.position.x = Math.sin(time * 0.4) * 0.68;
      fog.material.opacity = 0.1 + (Math.sin(time * 1.5) + 1) * 0.025;
      practicals.forEach((light, index) => {
        light.intensity = 13 + Math.sin(time * 2.4 + index) * 2.2;
      });
    }
  };
}

/** Procedural articulated fallback puppet; use layered original art / rigged GLB for final masters. */
export function createAnimeCharacter(options = {}) {
  const p = options.palette ?? {};
  const color = {
    skin: p.skin ?? '#e6b3a1', hair: p.hair ?? '#171426', hairAccent: p.hairAccent ?? '#1edce5',
    jacket: p.jacket ?? '#26243f', trim: p.trim ?? '#f20b9f', trousers: p.trousers ?? '#11172b', eyes: p.eyes ?? '#f7f0e9'
  };
  const root = new THREE.Group();
  const scale = options.scale ?? 1;
  root.scale.setScalar(scale);
  if (options.position) root.position.set(...options.position);

  const torso = new THREE.Group();
  torso.position.z = 1.42;
  root.add(torso);
  torso.add(outlinedMesh(capsuleGeometry(0.34, 0.52, 12), toon(color.jacket), 1.045));
  addNeonBar(torso, [0, -0.31, 0.02], [0.42, 0.045, 0.08], color.trim, 1.1);
  addBox(torso, [-0.24, -0.2, 0.28], [0.12, 0.08, 0.42], color.jacket);
  addBox(torso, [0.24, -0.2, 0.28], [0.12, 0.08, 0.42], color.jacket);

  const headPivot = new THREE.Group();
  headPivot.position.set(0, 0, 2.16);
  root.add(headPivot);
  headPivot.add(outlinedMesh(new THREE.SphereGeometry(0.38, 22, 16), toon(color.skin), 1.04));
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.405, 22, 16, 0, Math.PI * 2, 0, Math.PI * 0.58), toon(color.hair));
  hair.position.set(0, 0.025, 0.15);
  headPivot.add(hair);
  for (let i = 0; i < 7; i++) {
    const spike = new THREE.Mesh(new THREE.ConeGeometry(0.115, 0.42 + (i % 3) * 0.09, 6), toon(i === 1 || i === 2 ? color.hairAccent : color.hair));
    spike.position.set(-0.3 + i * 0.1, 0.02 + (i % 2) * 0.04, 0.37 - Math.abs(3 - i) * 0.035);
    spike.rotation.y = (i - 3) * -0.22;
    spike.rotation.x = -0.3;
    headPivot.add(spike);
  }
  for (const x of [-0.145, 0.145]) {
    const eyeWhite = new THREE.Mesh(new THREE.SphereGeometry(0.071, 12, 10), new THREE.MeshBasicMaterial({ color: color.eyes }));
    eyeWhite.position.set(x, -0.335, -0.015);
    eyeWhite.scale.set(1.0, 0.42, 0.72);
    headPivot.add(eyeWhite);
    const iris = new THREE.Mesh(new THREE.SphereGeometry(0.036, 12, 10), new THREE.MeshBasicMaterial({ color: '#17253e' }));
    iris.position.set(x, -0.369, -0.022);
    headPivot.add(iris);
    addNeonBar(headPivot, [x, -0.355, 0.087], [0.15, 0.045, 0.035], color.hair, 0.1);
  }
  const mouth = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.025, 0.018), new THREE.MeshBasicMaterial({ color: '#6d283f' }));
  mouth.position.set(0, -0.36, -0.18);
  headPivot.add(mouth);

  const armPivots = [];
  for (const side of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.set(side * 0.38, 0, 1.76);
    root.add(pivot);
    pivot.add(outlinedMesh(capsuleGeometry(0.115, 0.42, 10), toon(color.jacket)));
    const forearm = new THREE.Group();
    forearm.position.set(0, 0, -0.62);
    pivot.add(forearm);
    forearm.add(outlinedMesh(capsuleGeometry(0.088, 0.38, 10), toon(color.skin)));
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 10), toon(color.skin));
    hand.position.z = -0.31;
    forearm.add(hand);
    armPivots.push({ upper: pivot, lower: forearm, side });
  }

  const legPivots = [];
  for (const side of [-1, 1]) {
    const hip = new THREE.Group();
    hip.position.set(side * 0.18, 0, 0.96);
    root.add(hip);
    hip.add(outlinedMesh(capsuleGeometry(0.145, 0.43, 10), toon(color.trousers)));
    const knee = new THREE.Group();
    knee.position.z = -0.55;
    hip.add(knee);
    knee.add(outlinedMesh(capsuleGeometry(0.12, 0.42, 10), toon(color.jacket)));
    addBox(knee, [0, -0.08, -0.38], [0.25, 0.42, 0.16], '#101323');
    legPivots.push({ hip, knee, side });
  }

  const scarf = new THREE.Mesh(new THREE.ConeGeometry(0.19, 1.2, 5), toon(color.trim));
  scarf.position.set(-0.35, 0.04, 1.63);
  scarf.rotation.x = -Math.PI / 2;
  scarf.rotation.y = -0.36;
  root.add(scarf);

  return {
    root,
    update(time, motion = {}) {
      const run = motion.run ?? 0;
      const attack = motion.attack ?? 0;
      const launch = motion.launch ?? 0;
      root.position.z = (options.position?.[2] ?? 0) + Math.abs(Math.sin(time * 13)) * 0.065 * run + launch * 0.2;
      root.rotation.y = -0.12 + attack * 0.7 - launch * 0.18 + Math.sin(time * 1.8) * 0.025;
      torso.rotation.y = attack * -0.45 + Math.sin(time * 8) * 0.035 * run;
      headPivot.rotation.y = -attack * 0.28 + Math.sin(time * 2.2) * 0.035;
      armPivots.forEach(({ upper, lower, side }) => {
        upper.rotation.y = Math.sin(time * 11 + (side > 0 ? Math.PI : 0)) * 0.72 * run - attack * (side > 0 ? 1.25 : -0.25);
        lower.rotation.y = -0.22 - attack * (side > 0 ? 0.62 : -0.15);
      });
      legPivots.forEach(({ hip, knee, side }) => {
        hip.rotation.y = Math.sin(time * 11 + (side > 0 ? Math.PI : 0)) * 0.86 * run - attack * 0.2;
        knee.rotation.y = Math.max(0, Math.sin(time * 11 + (side > 0 ? 0 : Math.PI))) * 0.8 * run;
      });
      scarf.rotation.z = Math.sin(time * 8) * 0.18 * run + launch * 0.8;
    }
  };
}

export function createSecurityDrone(options = {}) {
  const root = new THREE.Group();
  root.position.set(...(options.position ?? [0, 0, 0]));
  const shell = new THREE.Mesh(new THREE.OctahedronGeometry(0.52, 1), toon(options.shell ?? '#292741'));
  shell.scale.set(1.28, 0.74, 0.72);
  root.add(outlinedMesh(shell.geometry, shell.material, 1.04));
  const optic = new THREE.Mesh(new THREE.SphereGeometry(0.18, 18, 14), new THREE.MeshBasicMaterial({ color: options.color ?? '#f000a3' }));
  optic.position.set(0, -0.43, 0);
  root.add(optic);
  makeGlow(root, [0, -0.5, 0], options.color ?? '#f000a3', 4.8, 7, 0.12);
  const fins = [];
  for (const side of [-1, 1]) {
    const fin = addBox(root, [side * 0.77, 0.12, 0.08], [0.72, 0.11, 0.08], '#32304f');
    fin.rotation.y = side * 0.2;
    fins.push(fin);
    addNeonBar(root, [side * 0.85, 0.03, 0.13], [0.34, 0.06, 0.065], options.color ?? '#f000a3', 2.3);
  }
  return {
    root,
    update(time, threat = 0) {
      root.position.z += 0;
      root.position.y = (options.position?.[1] ?? 0) + Math.sin(time * 2.3) * 0.18;
      root.rotation.y = Math.sin(time * 1.6) * 0.12;
      root.rotation.x = Math.sin(time * 2.1) * 0.08 - threat * 0.2;
      fins.forEach((fin, index) => { fin.rotation.z = Math.sin(time * 5 + index) * 0.12; });
      root.scale.setScalar(0.92 + threat * 0.1);
    }
  };
}

export function createEnergyBlade(options = {}) {
  const root = new THREE.Group();
  const color = options.color ?? '#22f6ef';
  const hilt = addBox(root, [0, 0, -0.12], [0.13, 0.14, 0.46], '#27243c');
  hilt.rotation.y = 0.2;
  addNeonBar(root, [0, -0.08, -0.24], [0.24, 0.2, 0.08], '#e6a84c', 1);
  const blade = new THREE.Mesh(new THREE.BoxGeometry(0.085, 0.08, options.length ?? 2.7), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.94 }));
  blade.position.z = 1.2;
  root.add(blade);
  const core = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.09, options.length ?? 2.7), new THREE.MeshBasicMaterial({ color: '#e9ffff' }));
  core.position.z = 1.2;
  root.add(core);
  const glow = makeGlow(root, [0, -0.2, 1.25], color, 0, 5, 0.09);
  root.visible = false;
  return {
    root,
    setState(progress, launch = 0) {
      const active = smoothStep(progress);
      root.visible = active > 0.02;
      blade.scale.z = Math.max(0.001, active);
      core.scale.z = Math.max(0.001, active);
      blade.material.opacity = 0.18 + active * 0.82;
      glow.intensity = active * 7;
      root.rotation.y = -0.45 + launch * 0.3;
    }
  };
}

export function createRain(scene, options = {}) {
  const random = seeded(options.seed ?? 23);
  const count = options.count ?? 900;
  const [width, depth, height] = options.area ?? [24, 12, 12];
  const positions = new Float32Array(count * 3);
  const velocity = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (random() - 0.5) * width;
    positions[i * 3 + 1] = (random() - 0.5) * depth;
    positions[i * 3 + 2] = random() * height;
    velocity[i] = 8 + random() * 9;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    color: options.color ?? '#a4eaff',
    size: 0.035,
    transparent: true,
    opacity: options.opacity ?? 0.45,
    depthWrite: false,
    sizeAttenuation: true
  });
  const points = new THREE.Points(geometry, material);
  scene.add(points);
  return {
    update(time) {
      for (let i = 0; i < count; i++) {
        const index = i * 3;
        positions[index + 1] -= 0.028;
        positions[index + 2] -= velocity[i] / 30;
        if (positions[index + 2] < -0.2) {
          positions[index + 2] = height;
          positions[index] = (random() - 0.5) * width;
          positions[index + 1] = (random() - 0.5) * depth;
        }
      }
      geometry.attributes.position.needsUpdate = true;
      points.rotation.y = Math.sin(time * 0.5) * 0.025;
    }
  };
}

export function createSpeedLines(scene, options = {}) {
  const random = seeded(81);
  const count = options.count ?? 40;
  const vertices = [];
  for (let i = 0; i < count; i++) {
    const x = (random() - 0.5) * 25;
    const z = 1 + random() * 9;
    vertices.push(x, -4.8, z, x + 0.8 + random() * 2, -4.8, z + (random() - 0.5) * 0.18);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  const material = new THREE.LineBasicMaterial({ color: options.color ?? '#25dce9', transparent: true, opacity: 0, depthWrite: false });
  const lines = new THREE.LineSegments(geometry, material);
  scene.add(lines);
  return {
    update(time, intensity = 0) {
      material.opacity = smoothStep(intensity) * 0.6;
      lines.position.x = Math.sin(time * 13) * intensity * 0.2;
    }
  };
}

export async function loadRiggedCharacter(scene, url, options = {}) {
  if (typeof url !== 'string' || !url.startsWith('/projects/')) throw new Error('Rigged model URL must be a local /projects/ asset path');
  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync(url);
  const root = gltf.scene;
  root.rotation.x = Math.PI / 2; // Convert glTF Y-up into the scene's Z-up convention.
  root.position.set(...(options.position ?? [0, 0, 0]));
  root.scale.setScalar(options.scale ?? 1);
  scene.add(root);
  const mixer = new THREE.AnimationMixer(root);
  const actions = gltf.animations.map((clip) => {
    const action = mixer.clipAction(clip);
    action.play();
    return action;
  });
  return {
    root,
    clips: gltf.animations.map((clip) => clip.name),
    update(delta) { mixer.update(delta); }
  };
}

export async function loadLayeredCutout(scene, layerManifest, options = {}) {
  if (!Array.isArray(layerManifest) || layerManifest.length === 0) throw new Error('Layered cutout needs a non-empty layers array');
  const root = new THREE.Group();
  root.position.set(...(options.position ?? [0, 0, 0]));
  const joints = new Map();
  const loader = new THREE.TextureLoader();
  for (const layer of layerManifest) {
    if (!layer.src || !layer.src.startsWith('/projects/')) throw new Error('Character layer src must be a local /projects/ asset path');
    const texture = await loader.loadAsync(layer.src);
    texture.colorSpace = THREE.SRGBColorSpace;
    const pivot = new THREE.Group();
    pivot.name = layer.joint ?? layer.id;
    pivot.position.set(...(layer.pivot ?? [0, 0, 0]));
    const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true, alphaTest: 0.02, side: THREE.DoubleSide, depthWrite: false });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(...(layer.size ?? [1, 1])), material);
    mesh.rotation.x = Math.PI / 2; // Cutout faces the Y-negative camera.
    mesh.position.set(...(layer.offset ?? [0, 0, 0]));
    mesh.rotation.z = layer.rotation ?? 0;
    mesh.renderOrder = layer.order ?? 10;
    pivot.add(mesh);
    root.add(pivot);
    if (layer.joint) joints.set(layer.joint, pivot);
  }
  scene.add(root);
  return {
    root,
    joints,
    setPose(pose = {}) {
      for (const [name, rotation] of Object.entries(pose)) {
        const joint = joints.get(name);
        if (joint) joint.rotation.set(rotation[0] ?? 0, rotation[1] ?? 0, rotation[2] ?? 0);
      }
    }
  };
}

export const kit = {
  createCyberpunkCity,
  createAnimeCharacter,
  createSecurityDrone,
  createEnergyBlade,
  createRain,
  createSpeedLines,
  loadRiggedCharacter,
  loadLayeredCutout,
  smoothStep,
  easeOutCubic
};
