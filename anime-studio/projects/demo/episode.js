import * as THREE from 'three';
import {
  createCyberpunkCity,
  createAnimeCharacter,
  createSecurityDrone,
  createEnergyBlade,
  createRain,
  createSpeedLines,
  smoothStep
} from '../../runtime/kit.js';

/**
 * A small executable 2.5D scene. This is an engine smoke test, not final art.
 * Production episodes should replace the fallback puppets with original layered
 * character art or rigged GLB assets while retaining the same camera/lighting kit.
 */
export async function createEpisode({ scene, camera, kit }) {
  scene.background = new THREE.Color('#070a18');
  const city = createCyberpunkCity(scene, { seed: 11, density: 1.25, palette: ['#090d20', '#171b3b', '#18dce7', '#e9009f', '#ffb64a'] });

  const hero = createAnimeCharacter({
    name: 'Ari Venn',
    palette: { skin: '#eab6a3', hair: '#161526', hairAccent: '#16e2df', jacket: '#26283f', trim: '#f000a6', trousers: '#10172a', eyes: '#f6f0eb' },
    scale: 1.08,
    position: [-1.55, 0.05, 0.02]
  });
  scene.add(hero.root);

  const drone = createSecurityDrone({ color: '#e900a6', shell: '#22223c', position: [2.8, 1.65, 0.5] });
  scene.add(drone.root);

  const blade = createEnergyBlade({ color: '#1df4ee', length: 2.7 });
  scene.add(blade.root);
  blade.root.position.set(-0.45, 0.72, 1.85);

  const rain = createRain(scene, { count: 1100, area: [24, 12, 12], color: '#83dfff', opacity: 0.44, seed: 91 });
  const speedLines = createSpeedLines(scene, { count: 55, color: '#27e9ee' });

  camera.position.set(-0.2, -13.5, 6.5);
  camera.fov = 42;
  camera.lookAt(0, 1.2, 1.4);
  camera.updateProjectionMatrix();

  return {
    update(time) {
      const run = smoothStep(Math.min(1, time / 2.4)) * (1 - smoothStep(Math.max(0, (time - 4.6) / 0.8)));
      const threat = smoothStep(Math.max(0, Math.min(1, (time - 2.0) / 1.0)));
      const attack = smoothStep(Math.max(0, Math.min(1, (time - 5.05) / 0.8)));
      const launch = smoothStep(Math.max(0, Math.min(1, (time - 7.55) / 0.7)));

      hero.update(time, { run, attack, launch });
      drone.update(time, threat);
      blade.setState(attack, launch);
      city.update(time);
      rain.update(time);
      speedLines.update(time, launch);

      camera.position.x = -0.25 + Math.sin(time * 0.55) * 0.34 - launch * 0.9;
      camera.position.y = -13.5 + launch * 2.8;
      camera.position.z = 6.1 + Math.sin(time * 0.65) * 0.12 - launch * 0.28;
      camera.lookAt(-0.2 - launch * 0.65, 1.1, 1.45 + launch * 0.28);
      camera.fov = 42 - launch * 4.5;
      camera.updateProjectionMatrix();
    }
  };
}
