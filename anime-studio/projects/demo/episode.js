/** NEON VEIL — Run the Last Light: original assistant-authored 2.5D anime sequence. */
import * as THREE from 'three';
import {
  loadPaintedPlate,
  loadLayeredCutout,
  createRain,
  createSpeedLines,
  smoothStep,
  easeOutCubic
} from '../../runtime/kit.js';

const clamp = (v) => THREE.MathUtils.clamp(v, 0, 1);
const pulse = (time, start, end, fade = 0.35) =>
  smoothStep((time - start) / fade) * (1 - smoothStep((time - (end - fade)) / fade));
const mix = (a, b, t) => a + (b - a) * t;

function makeDrone(scene, position, scale = 1, tint = '#f33eae') {
  const root = new THREE.Group();
  root.position.set(...position);
  root.scale.setScalar(scale);
  scene.add(root);

  const shellMat = new THREE.MeshStandardMaterial({ color: '#26334d', metalness: 0.86, roughness: 0.24 });
  const darkMat = new THREE.MeshStandardMaterial({ color: '#080e1d', metalness: 0.72, roughness: 0.3 });
  const glowMat = new THREE.MeshBasicMaterial({ color: tint });
  const coreMat = new THREE.MeshStandardMaterial({
    color: '#f5ffff', emissive: tint, emissiveIntensity: 3.5, metalness: 0.15, roughness: 0.18
  });

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 32, 24), shellMat);
  body.scale.set(1.3, 0.74, 0.72);
  root.add(body);

  const armour = new THREE.Mesh(new THREE.OctahedronGeometry(0.48, 1), darkMat);
  armour.scale.set(1.35, 0.8, 0.7);
  root.add(armour);

  const optic = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), coreMat);
  optic.position.set(0, -0.32, 0.03);
  root.add(optic);

  const outerRing = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.055, 12, 64), shellMat);
  outerRing.rotation.x = Math.PI / 2;
  outerRing.position.z = 0.03;
  root.add(outerRing);

  const innerRing = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.018, 8, 64), glowMat);
  innerRing.rotation.x = Math.PI / 2;
  innerRing.position.z = 0.03;
  root.add(innerRing);

  const fins = [];
  for (const side of [-1, 1]) {
    const arm = new THREE.Mesh(new THREE.BoxGeometry(0.92, 0.15, 0.11), shellMat);
    arm.position.set(side * 0.62, 0.04, 0.02);
    arm.rotation.y = side * 0.18;
    root.add(arm);

    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.19, 0.08), darkMat);
    fin.position.set(side * 1.04, 0.04, 0.05);
    root.add(fin);
    fins.push(fin);

    const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 12), glowMat);
    beacon.position.set(side * 1.09, -0.01, 0.08);
    root.add(beacon);
  }

  const lensRim = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.025, 8, 36), glowMat);
  lensRim.position.set(0, -0.35, 0.03);
  root.add(lensRim);

  const lamp = new THREE.PointLight(tint, 8, 10, 2);
  lamp.position.set(0, -0.48, 0.02);
  root.add(lamp);

  const beam = new THREE.Mesh(
    new THREE.ConeGeometry(1.15, 5.2, 40, 1, true),
    new THREE.MeshBasicMaterial({ color: tint, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false })
  );
  beam.rotation.x = Math.PI / 2;
  beam.position.set(0, 0, -2.6);
  beam.visible = false;
  root.add(beam);

  const beamCore = new THREE.Mesh(
    new THREE.ConeGeometry(0.24, 5.2, 24, 1, true),
    new THREE.MeshBasicMaterial({ color: '#f6ffff', transparent: true, opacity: 0.14, side: THREE.DoubleSide, depthWrite: false })
  );
  beamCore.rotation.x = Math.PI / 2;
  beamCore.position.set(0, 0, -2.6);
  beamCore.visible = false;
  root.add(beamCore);

  return {
    root,
    beam,
    beamCore,
    update(time, threat = 0) {
      root.position.z = position[2] + Math.sin(time * 2.7) * 0.12;
      root.rotation.y = Math.sin(time * 1.2) * 0.12 + threat * 0.2;
      root.rotation.z = Math.sin(time * 2.2) * 0.06;
      outerRing.rotation.z = time * 2.2;
      innerRing.rotation.z = -time * 3.1;
      fins.forEach((fin, i) => { fin.rotation.z = Math.sin(time * 8 + i) * 0.13; });
      optic.scale.setScalar(0.88 + Math.sin(time * 5) * 0.12 + threat * 0.18);
      lamp.intensity = 5 + Math.sin(time * 7) * 2 + threat * 7;
      beam.visible = threat > 0.03;
      beamCore.visible = threat > 0.03;
      beam.material.opacity = 0.05 + threat * 0.12;
      beamCore.material.opacity = threat * 0.2;
    }
  };
}

function makeSpeeder(scene) {
  const root = new THREE.Group();
  scene.add(root);
  const shell = new THREE.MeshStandardMaterial({ color: '#182641', metalness: 0.9, roughness: 0.2 });
  const glass = new THREE.MeshStandardMaterial({ color: '#4cebf0', emissive: '#1cbdc9', emissiveIntensity: 1.8, metalness: 0.2, roughness: 0.15 });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.32, 2.1, 8, 20), shell);
  body.rotation.z = Math.PI / 2;
  body.scale.set(0.9, 0.7, 0.7);
  root.add(body);
  const cockpit = new THREE.Mesh(new THREE.SphereGeometry(0.43, 24, 16), glass);
  cockpit.scale.set(1.25, 0.55, 0.5);
  cockpit.position.z = 0.28;
  root.add(cockpit);
  for (const side of [-1, 1]) {
    const pod = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.25, 0.82, 20), shell);
    pod.rotation.x = Math.PI / 2;
    pod.position.set(side * 1.15, 0, -0.15);
    root.add(pod);
    const light = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.8, 0.1), new THREE.MeshBasicMaterial({ color: side > 0 ? '#ff46b5' : '#3df4ef' }));
    light.position.set(side * 1.15, 0, 0.02);
    root.add(light);
  }
  const glow = new THREE.PointLight('#2ceaf0', 7, 12);
  glow.position.set(0, 0, -0.45);
  root.add(glow);
  root.scale.setScalar(0.58);
  return {
    root,
    update(time, speed = 1) {
      root.position.set(4.8 - time * 1.25 * speed, 3.5, 4.1 + Math.sin(time * 2) * 0.22);
      root.rotation.y = Math.sin(time * 2.4) * 0.08;
    }
  };
}

function makeSword(scene, texture) {
  const root = new THREE.Group();
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(0.52, 2.9),
    new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false, side: THREE.DoubleSide })
  );
  plane.rotation.x = Math.PI / 2;
  root.add(plane);
  const core = new THREE.Mesh(
    new THREE.BoxGeometry(0.045, 0.07, 2.3),
    new THREE.MeshBasicMaterial({ color: '#f1ffff' })
  );
  core.position.z = 0.2;
  root.add(core);
  const aura = new THREE.PointLight('#31f8f0', 0, 8, 2);
  aura.position.set(0, -0.16, 0.65);
  root.add(aura);
  const hilt = new THREE.Mesh(
    new THREE.CylinderGeometry(0.065, 0.065, 0.5, 12),
    new THREE.MeshStandardMaterial({ color: '#a8b9cb', metalness: 0.95, roughness: 0.22 })
  );
  hilt.rotation.x = Math.PI / 2;
  hilt.position.z = -1.55;
  root.add(hilt);
  const guard = new THREE.Mesh(
    new THREE.BoxGeometry(0.52, 0.14, 0.13),
    new THREE.MeshStandardMaterial({ color: '#252e47', metalness: 0.88, roughness: 0.24 })
  );
  guard.position.z = -1.33;
  root.add(guard);
  root.visible = false;
  scene.add(root);
  return { root, aura, update() {} };
}

function makeSlash(scene) {
  const points = [];
  for (let i = 0; i <= 60; i++) {
    const a = -1.15 + (i / 60) * 2.2;
    points.push(new THREE.Vector3(Math.cos(a) * 2.4, 0, Math.sin(a) * 2.4));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const tube = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 72, 0.065, 10, false),
    new THREE.MeshBasicMaterial({ color: '#baffff', transparent: true, opacity: 0.95, depthWrite: false })
  );
  tube.visible = false;
  scene.add(tube);
  const glow = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 72, 0.19, 10, false),
    new THREE.MeshBasicMaterial({ color: '#25e9ed', transparent: true, opacity: 0.28, depthWrite: false })
  );
  glow.visible = false;
  scene.add(glow);
  return {
    tube, glow,
    update(time, amount, position) {
      const visible = amount > 0.02;
      tube.visible = visible;
      glow.visible = visible;
      const scale = 0.25 + amount * 0.9;
      tube.scale.setScalar(scale);
      glow.scale.setScalar(scale);
      tube.position.set(position[0], position[1] - 0.3, position[2]);
      glow.position.copy(tube.position);
      tube.rotation.y = -0.2 + amount * 0.45;
      glow.rotation.y = tube.rotation.y;
      tube.material.opacity = amount * 0.95;
      glow.material.opacity = amount * 0.32;
    }
  };
}

function makeEmbers(scene, count = 160) {
  const positions = new Float32Array(count * 3);
  const origin = new Float32Array(count * 3);
  const speed = new Float32Array(count);
  let seed = 781;
  const rand = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  for (let i = 0; i < count; i++) {
    origin[i * 3] = (rand() - 0.5) * 18;
    origin[i * 3 + 1] = -1 + rand() * 9;
    origin[i * 3 + 2] = 0.3 + rand() * 7;
    speed[i] = 0.2 + rand() * 1.4;
  }
  positions.set(origin);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({
    color: '#ff8aca', size: 0.035, transparent: true, opacity: 0.7, depthWrite: false
  }));
  scene.add(pts);
  return {
    update(time, intensity = 1) {
      for (let i = 0; i < count; i++) {
        const j = i * 3;
        positions[j] = origin[j] + Math.sin(time * 1.5 + i) * 0.12;
        positions[j + 1] = origin[j + 1] + Math.cos(time * 0.9 + i * 0.3) * 0.12;
        positions[j + 2] = (origin[j + 2] + time * speed[i]) % 7.2;
      }
      geo.attributes.position.needsUpdate = true;
      pts.material.opacity = 0.3 + intensity * 0.4;
    }
  };
}

export async function createEpisode({ scene, camera, THREE: T, kit }) {
  scene.background = new THREE.Color('#050817');
  scene.fog = new THREE.FogExp2('#10142a', 0.0048);

  await Promise.all([
    loadPaintedPlate(scene, '/projects/demo/assets/environments/background.svg', {
      position: [0, 11.5, 4.7], size: [28, 15.75], order: 1, transparent: false
    }),
    loadPaintedPlate(scene, '/projects/demo/assets/environments/midground.svg', {
      position: [0, 6, 4.55], size: [23.2, 13.05], order: 2, opacity: 0.98
    }),
    loadPaintedPlate(scene, '/projects/demo/assets/environments/foreground.svg', {
      position: [0, -2.6, 4.8], size: [25.4, 14.3], order: 45, opacity: 0.94
    })
  ]);

  const artRoot = await loadLayeredCutout(scene, [
    { id: 'torso-art', joint: 'torso', src: '/projects/demo/assets/characters/rin/torso.svg', pivot: [0, 0, 1.5], size: [1.28, 1.45], order: 21 },
    { id: 'head-art', joint: 'head', parentJoint: 'torso', src: '/projects/demo/assets/characters/rin/head.svg', pivot: [0, 0, 0.82], size: [1.02, 1.18], order: 26 },
    { id: 'arm-l-upper-art', joint: 'left_arm', parentJoint: 'torso', src: '/projects/demo/assets/characters/rin/arm-l-upper.svg', pivot: [-0.52, 0, 0.43], size: [0.49, 0.82], offset: [0, 0, -0.34], order: 18 },
    { id: 'arm-l-fore-art', joint: 'left_forearm', parentJoint: 'left_arm', src: '/projects/demo/assets/characters/rin/arm-l-fore.svg', pivot: [0.02, 0, -0.52], size: [0.43, 0.76], offset: [0, 0, -0.31], order: 19 },
    { id: 'arm-r-upper-art', joint: 'right_arm', parentJoint: 'torso', src: '/projects/demo/assets/characters/rin/arm-r-upper.svg', pivot: [0.52, 0, 0.43], size: [0.49, 0.82], offset: [0, 0, -0.34], order: 24 },
    { id: 'arm-r-fore-art', joint: 'right_forearm', parentJoint: 'right_arm', src: '/projects/demo/assets/characters/rin/arm-r-fore.svg', pivot: [-0.02, 0, -0.52], size: [0.43, 0.76], offset: [0, 0, -0.31], order: 25 },
    { id: 'leg-l-upper-art', joint: 'left_leg', src: '/projects/demo/assets/characters/rin/leg-l-upper.svg', pivot: [-0.25, 0, 0.82], size: [0.54, 0.92], offset: [0, 0, -0.37], order: 12 },
    { id: 'leg-l-shin-art', joint: 'left_shin', parentJoint: 'left_leg', src: '/projects/demo/assets/characters/rin/leg-l-shin.svg', pivot: [0, 0, -0.64], size: [0.51, 0.95], offset: [0, 0, -0.39], order: 13 },
    { id: 'leg-r-upper-art', joint: 'right_leg', src: '/projects/demo/assets/characters/rin/leg-r-upper.svg', pivot: [0.25, 0, 0.82], size: [0.54, 0.92], offset: [0, 0, -0.37], order: 15 },
    { id: 'leg-r-shin-art', joint: 'right_shin', parentJoint: 'right_leg', src: '/projects/demo/assets/characters/rin/leg-r-shin.svg', pivot: [0, 0, -0.64], size: [0.51, 0.95], offset: [0, 0, -0.39], order: 16 },
    { id: 'scarf-art', joint: 'scarf', parentJoint: 'torso', src: '/projects/demo/assets/characters/rin/scarf.svg', pivot: [-0.08, 0.04, 0.32], size: [1.26, 0.98], offset: [-0.42, 0, 0.04], order: 28 }
  ], { position: [-1.55, -0.25, 0.18], scale: 1.28 });

  const joints = artRoot.joints;
  const drone = makeDrone(scene, [3.5, -0.05, 5.05], 1.02, '#ff40b3');
  const escortDrone = makeDrone(scene, [5.5, 2.2, 4.3], 0.4, '#35eaf0');
  const speeder = makeSpeeder(scene);

  const bladeTexture = await new THREE.TextureLoader().loadAsync('/projects/demo/assets/characters/rin/blade.svg');
  bladeTexture.colorSpace = THREE.SRGBColorSpace;
  const sword = makeSword(scene, bladeTexture);
  const slash = makeSlash(scene);

  const rain = createRain(scene, { count: 1250, area: [26, 12, 12], color: '#94eaff', opacity: 0.38, seed: 34 });
  const speedLines = createSpeedLines(scene, { count: 74, color: '#42eaf0' });
  const embers = makeEmbers(scene, 190);

  const amb = new THREE.HemisphereLight('#c4d8ff', '#151126', 0.48);
  scene.add(amb);
  const cyanRim = new THREE.DirectionalLight('#26ecf0', 1.35);
  cyanRim.position.set(7, 3, 8);
  scene.add(cyanRim);
  const pinkRim = new THREE.DirectionalLight('#f438a8', 1.25);
  pinkRim.position.set(-7, 2, 6);
  scene.add(pinkRim);
  const heroLight = new THREE.PointLight('#35f1ed', 0, 9, 2);
  heroLight.position.set(-1.0, -1.2, 2.5);
  scene.add(heroLight);

  const floorGlow = new THREE.Mesh(
    new THREE.PlaneGeometry(8, 2.5),
    new THREE.MeshBasicMaterial({ color: '#18dce5', transparent: true, opacity: 0.17, depthWrite: false })
  );
  floorGlow.position.set(-1.4, -0.1, 0.025);
  scene.add(floorGlow);

  camera.position.set(0.1, -13.5, 5.35);
  camera.up.set(0, 0, 1);
  camera.fov = 38;
  camera.lookAt(0, 0, 3.72);
  camera.updateProjectionMatrix();

  function setJoint(name, x, y, z) {
    const joint = joints.get(name);
    if (joint) joint.rotation.set(x, y, z);
  }

  return {
    update(time) {
      const t = clamp(time / 15);
      const run = Math.max(1 - smoothStep((time - 4.6) / 0.65), pulse(time, 9.2, 12.4, 0.5) * 0.85);
      const skid = pulse(time, 4.75, 6.1, 0.42);
      const draw = pulse(time, 5.5, 8.4, 0.52);
      const charge = pulse(time, 7.65, 10.2, 0.5);
      const leap = pulse(time, 9.8, 12.1, 0.55);
      const slashPower = pulse(time, 11.65, 13.55, 0.32);
      const resolve = smoothStep((time - 13.1) / 0.65);
      const threat = pulse(time, 2.35, 8.9, 0.8);
      const sprintAgain = pulse(time, 9.4, 12.9, 0.6);

      const earlyMove = mix(-2.75, -0.95, smoothStep(time / 5.2));
      const lateMove = mix(-0.95, 0.95, smoothStep((time - 9.5) / 2.7));
      const x = time < 5.2 ? earlyMove : time < 9.5 ? -0.95 : lateMove;
      const jumpArc = Math.sin(Math.PI * clamp((time - 9.8) / 2.4)) * 1.12 * leap;

      artRoot.root.position.x = x;
      artRoot.root.position.z = 0.18 + jumpArc + resolve * 0.02;
      artRoot.root.rotation.y = -0.06 - skid * 0.24 + leap * 0.34 - slashPower * 0.1;
      artRoot.root.rotation.z = -skid * 0.16 + leap * 0.12;
      artRoot.root.scale.setScalar(1.28 + leap * 0.035);

      const gait = time * 10.8;
      setJoint('torso', 0, -0.08 - skid * 0.27 + leap * 0.12, Math.sin(gait * 0.5) * 0.035 * run);
      setJoint('head', 0, Math.sin(time * 2.2) * 0.025 - skid * 0.08, Math.sin(time * 2.6) * 0.02);
      setJoint('left_arm', 0, Math.sin(gait + Math.PI) * 0.55 * run + draw * 0.58 - slashPower * 0.45, 0.05 + skid * 0.3);
      setJoint('left_forearm', 0, -0.2 - run * 0.32 - draw * 0.6, 0.05);
      setJoint('right_arm', 0, Math.sin(gait) * 0.62 * run - draw * 0.9 - slashPower * 0.35, -0.05 - charge * 0.36);
      setJoint('right_forearm', 0, -0.16 - run * 0.4 - charge * 0.75, -0.06);
      setJoint('left_leg', 0, Math.sin(gait) * 0.62 * run - skid * 0.5 + leap * 0.65, 0);
      setJoint('left_shin', 0, Math.max(0, Math.cos(gait)) * 0.56 * run + skid * 0.85 + leap * 0.45, 0);
      setJoint('right_leg', 0, Math.sin(gait + Math.PI) * 0.62 * run + skid * 0.58 - leap * 0.55, 0);
      setJoint('right_shin', 0, Math.max(0, Math.cos(gait + Math.PI)) * 0.56 * run + skid * 0.16 + leap * 0.7, 0);
      setJoint('scarf', 0, 0.1 + Math.sin(time * 5.5) * 0.18 * (0.2 + run) + leap * 0.22, Math.sin(time * 7) * 0.08 + sprintAgain * 0.18);

      drone.root.position.x = mix(3.7, 2.05, smoothStep((time - 2.0) / 1.55)) + Math.sin(time * 1.5) * 0.09;
      drone.root.position.z = 5.05 + Math.sin(time * 2.7) * 0.14;
      drone.update(time, threat);
      escortDrone.root.position.x = 5.5 + Math.sin(time * 0.9) * 0.6;
      escortDrone.root.position.z = 4.3 + Math.sin(time * 2.1) * 0.2;
      escortDrone.update(time, threat * 0.4);
      speeder.update(time, 1.2 + sprintAgain * 0.6);

      const swordActive = draw > 0.02 || charge > 0.02 || leap > 0.02 || slashPower > 0.02;
      sword.root.visible = swordActive;
      sword.root.position.set(x + 0.58 + leap * 0.14, -0.92, 1.88 + jumpArc + charge * 0.15);
      sword.root.rotation.y = -0.12 + draw * 0.38 + charge * 0.18 - slashPower * 1.15;
      sword.root.rotation.z = -0.55 - charge * 0.45 + slashPower * 1.45;
      sword.aura.intensity = 0.7 + charge * 13 + slashPower * 9;
      sword.root.scale.setScalar(1 + charge * 0.08);

      slash.update(time, slashPower, [x + 0.8, -0.74, 2.15 + jumpArc]);
      heroLight.intensity = 2 + charge * 12 + slashPower * 10;
      floorGlow.position.x = x;
      floorGlow.material.opacity = 0.08 + charge * 0.32 + slashPower * 0.22;
      cyanRim.intensity = 1.0 + charge * 1.2;
      pinkRim.intensity = 1.05 + threat * 0.6;
      rain.update(time);
      speedLines.update(time, sprintAgain * 0.8 + slashPower * 0.65);
      embers.update(time, charge + slashPower);

      const camPush = smoothStep((time - 7.1) / 2.0) * 1.15 + slashPower * 1.0;
      const shake = (threat * 0.025 + slashPower * 0.09) * Math.sin(time * 47);
      camera.position.x = mix(0.3, x * 0.3, 0.55) + shake;
      camera.position.y = -13.5 + camPush;
      camera.position.z = 5.35 + leap * 0.25 + shake * 0.45;
      camera.lookAt(x * 0.22 + slashPower * 0.22, 0, 3.72 + leap * 0.18);
      camera.fov = 38 - camPush * 1.5 + slashPower * 1.2;
      camera.updateProjectionMatrix();

      scene.fog.density = 0.0048 + threat * 0.0012;
    }
  };
}
