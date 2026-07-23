'use strict';

const fs = require('fs');
const path = require('path');
const occtImport = require('occt-import-js');

const inputPath = process.argv[2] || 'ARMADO_OT1676.STEP';
const outputPath = process.argv[3] || 'ARMADO_OT1676_WEB.glb';
const manifestPath = process.argv[4] || 'ARMADO_OT1676_WEB_manifest.json';

const linearDeflection = Number(process.env.LINEAR_DEFLECTION || 0.85);
const angularDeflection = Number(process.env.ANGULAR_DEFLECTION || 0.28);

function flattenNumbers(value) {
  if (!value) return [];
  if (ArrayBuffer.isView(value)) return Array.from(value);
  if (!Array.isArray(value)) return [];
  if (value.length && Array.isArray(value[0])) return value.flat(Infinity);
  return value;
}

function safeName(value, fallback) {
  const text = String(value || fallback || 'Pieza').replace(/[\u0000-\u001f]/g, ' ').trim();
  return text || fallback || 'Pieza';
}

function roleFromName(name) {
  const s = String(name || '').toUpperCase();
  const staticWords = ['SAF', 'SNL', 'SOPORTE', 'HOUSING', 'CARCASA', 'PEDESTAL', 'BASE'];
  if (staticWords.some((word) => s.includes(word))) return 'static';
  const rotorWords = [
    'MANTO', 'POLEA', 'PULLEY', 'EJE', 'SHAFT', 'CUBO', 'HUB', 'DISCO',
    'RODAMIENTO', 'BEARING', 'MANGUITO', 'SLEEVE', 'ZAPEX', 'FLENDER',
    'ACOPLE', 'COUPLING', 'BACKSTOP', 'REXNORD', 'ANTIRRETORNO'
  ];
  return rotorWords.some((word) => s.includes(word)) ? 'rotor' : 'detail';
}

function normalizeColor(color) {
  let c = color;
  if (c && !Array.isArray(c) && typeof c === 'object') {
    c = [c.r ?? c.R ?? 0.68, c.g ?? c.G ?? 0.70, c.b ?? c.B ?? 0.72, c.a ?? c.A ?? 1];
  }
  if (!Array.isArray(c)) c = [0.68, 0.70, 0.72, 1];
  c = c.slice(0, 4).map((v, i) => {
    let n = Number(v);
    if (!Number.isFinite(n)) n = i === 3 ? 1 : 0.7;
    if (n > 1) n /= 255;
    return Math.min(1, Math.max(0, n));
  });
  while (c.length < 4) c.push(1);
  return c;
}

function walkHierarchy(node, prefix, labels) {
  if (!node || typeof node !== 'object') return;
  const here = safeName(node.name, 'Conjunto');
  const next = prefix ? `${prefix} / ${here}` : here;
  const meshIndices = Array.isArray(node.meshes) ? node.meshes : [];
  for (const index of meshIndices) {
    if (!labels.has(index)) labels.set(index, next);
  }
  for (const child of (Array.isArray(node.children) ? node.children : [])) {
    walkHierarchy(child, next, labels);
  }
}

class BinaryBuilder {
  constructor() {
    this.parts = [];
    this.length = 0;
  }
  align(alignment = 4) {
    const padding = (alignment - (this.length % alignment)) % alignment;
    if (padding) {
      this.parts.push(Buffer.alloc(padding));
      this.length += padding;
    }
  }
  append(buffer, alignment = 4) {
    this.align(alignment);
    const offset = this.length;
    const b = Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer.buffer, buffer.byteOffset, buffer.byteLength);
    this.parts.push(b);
    this.length += b.length;
    return { offset, length: b.length };
  }
  finish() {
    this.align(4);
    return Buffer.concat(this.parts, this.length);
  }
}

function minMaxVec3(array) {
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < array.length; i += 3) {
    for (let k = 0; k < 3; k += 1) {
      const v = array[i + k];
      if (v < min[k]) min[k] = v;
      if (v > max[k]) max[k] = v;
    }
  }
  return { min, max };
}

function makeGlb(json, binary) {
  const jsonBufferRaw = Buffer.from(JSON.stringify(json), 'utf8');
  const jsonPadding = (4 - (jsonBufferRaw.length % 4)) % 4;
  const jsonBuffer = Buffer.concat([jsonBufferRaw, Buffer.alloc(jsonPadding, 0x20)]);
  const binPadding = (4 - (binary.length % 4)) % 4;
  const binBuffer = Buffer.concat([binary, Buffer.alloc(binPadding)]);

  const totalLength = 12 + 8 + jsonBuffer.length + 8 + binBuffer.length;
  const header = Buffer.alloc(12);
  header.writeUInt32LE(0x46546c67, 0);
  header.writeUInt32LE(2, 4);
  header.writeUInt32LE(totalLength, 8);

  const jsonHeader = Buffer.alloc(8);
  jsonHeader.writeUInt32LE(jsonBuffer.length, 0);
  jsonHeader.writeUInt32LE(0x4e4f534a, 4);

  const binHeader = Buffer.alloc(8);
  binHeader.writeUInt32LE(binBuffer.length, 0);
  binHeader.writeUInt32LE(0x004e4942, 4);

  return Buffer.concat([header, jsonHeader, jsonBuffer, binHeader, binBuffer], totalLength);
}

(async () => {
  console.log(`Importando ${inputPath}`);
  const occt = await occtImport();
  const stepBytes = fs.readFileSync(inputPath);
  const result = occt.ReadStepFile(stepBytes, {
    linearUnit: 'millimeter',
    linearDeflectionType: 'absolute_value',
    linearDeflection,
    angularDeflection
  });

  if (!result || !result.success || !Array.isArray(result.meshes) || !result.meshes.length) {
    throw new Error('OpenCascade no pudo importar o triangular el archivo STEP.');
  }

  const labels = new Map();
  walkHierarchy(result.root, '', labels);

  const binary = new BinaryBuilder();
  const gltf = {
    asset: {
      version: '2.0',
      generator: 'SKM OT-1676 OpenCascade to GLB converter',
      extras: {
        source: path.basename(inputPath),
        sourceUnits: 'millimeter',
        rootScaleToMeters: 0.001,
        linearDeflection,
        angularDeflection
      }
    },
    scene: 0,
    scenes: [{ name: 'ARMADO OT-1676', nodes: [0] }],
    nodes: [{ name: 'ARMADO OT-1676', scale: [0.001, 0.001, 0.001], children: [] }],
    meshes: [],
    materials: [],
    accessors: [],
    bufferViews: [],
    buffers: [{ byteLength: 0 }]
  };

  const materialMap = new Map();
  const manifest = {
    source: path.basename(inputPath),
    settings: { linearDeflection, angularDeflection },
    parts: [],
    totals: { meshes: 0, vertices: 0, triangles: 0 }
  };

  function addBufferView(typedArray, target) {
    const piece = binary.append(Buffer.from(typedArray.buffer, typedArray.byteOffset, typedArray.byteLength), 4);
    const index = gltf.bufferViews.length;
    gltf.bufferViews.push({ buffer: 0, byteOffset: piece.offset, byteLength: piece.length, target });
    return index;
  }

  function addAccessor(bufferView, componentType, count, type, min, max) {
    const accessor = { bufferView, byteOffset: 0, componentType, count, type };
    if (min) accessor.min = min;
    if (max) accessor.max = max;
    const index = gltf.accessors.length;
    gltf.accessors.push(accessor);
    return index;
  }

  function materialFor(colorValue) {
    const color = normalizeColor(colorValue);
    const key = color.map((v) => v.toFixed(4)).join(',');
    if (materialMap.has(key)) return materialMap.get(key);
    const index = gltf.materials.length;
    gltf.materials.push({
      name: `Material ${index + 1}`,
      pbrMetallicRoughness: {
        baseColorFactor: color,
        metallicFactor: 0.72,
        roughnessFactor: 0.34
      },
      doubleSided: false
    });
    materialMap.set(key, index);
    return index;
  }

  result.meshes.forEach((source, sourceIndex) => {
    const positionValues = flattenNumbers(source?.attributes?.position?.array);
    let normalValues = flattenNumbers(source?.attributes?.normal?.array);
    const indexValues = flattenNumbers(source?.index?.array);
    if (positionValues.length < 9 || indexValues.length < 3) return;

    const positions = Float32Array.from(positionValues);
    if (normalValues.length !== positionValues.length) {
      normalValues = new Array(positionValues.length).fill(0);
    }
    const normals = Float32Array.from(normalValues);
    const indices = Uint32Array.from(indexValues);
    const bounds = minMaxVec3(positions);

    const positionView = addBufferView(positions, 34962);
    const normalView = addBufferView(normals, 34962);
    const indexView = addBufferView(indices, 34963);
    const positionAccessor = addAccessor(positionView, 5126, positions.length / 3, 'VEC3', bounds.min, bounds.max);
    const normalAccessor = addAccessor(normalView, 5126, normals.length / 3, 'VEC3');
    const indexAccessor = addAccessor(indexView, 5125, indices.length, 'SCALAR');

    const hierarchyName = labels.get(sourceIndex);
    const name = safeName(hierarchyName || source.name, `Pieza ${sourceIndex + 1}`);
    const role = roleFromName(name);
    const gltfMeshIndex = gltf.meshes.length;
    gltf.meshes.push({
      name,
      primitives: [{
        attributes: { POSITION: positionAccessor, NORMAL: normalAccessor },
        indices: indexAccessor,
        material: materialFor(source.color),
        mode: 4
      }],
      extras: { sourceMeshIndex: sourceIndex, role }
    });

    const nodeIndex = gltf.nodes.length;
    gltf.nodes.push({
      name,
      mesh: gltfMeshIndex,
      extras: {
        sourceMeshIndex: sourceIndex,
        role,
        bboxMinMm: bounds.min,
        bboxMaxMm: bounds.max
      }
    });
    gltf.nodes[0].children.push(nodeIndex);

    const vertices = positions.length / 3;
    const triangles = indices.length / 3;
    manifest.parts.push({
      sourceMeshIndex: sourceIndex,
      nodeIndex,
      name,
      role,
      color: normalizeColor(source.color),
      vertices,
      triangles,
      bboxMinMm: bounds.min,
      bboxMaxMm: bounds.max
    });
    manifest.totals.meshes += 1;
    manifest.totals.vertices += vertices;
    manifest.totals.triangles += triangles;
  });

  const binaryBuffer = binary.finish();
  gltf.buffers[0].byteLength = binaryBuffer.length;
  const glb = makeGlb(gltf, binaryBuffer);
  fs.writeFileSync(outputPath, glb);
  manifest.output = {
    file: path.basename(outputPath),
    bytes: glb.length,
    megabytes: Number((glb.length / 1024 / 1024).toFixed(2))
  };
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

  console.log(JSON.stringify(manifest.totals));
  console.log(`GLB generado: ${outputPath} (${manifest.output.megabytes} MB)`);
})().catch((error) => {
  console.error(error && error.stack ? error.stack : error);
  process.exit(1);
});
