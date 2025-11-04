document.getElementById("processBtn").addEventListener("click", async () => {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Please upload a file first!");

  const mode = document.querySelector('input[name="mode"]:checked').value;
  const outputDiv = document.getElementById("output");

  const start = performance.now();
  let resultBlob;

  if (mode === "compress") {
    const { blob } = await lzwCompressFile(file);
    resultBlob = blob;
  } else {
    const { blob } = await lzwDecompressFile(file);
    resultBlob = blob;
  }

  const end = performance.now();
  const duration = (end - start).toFixed(2);
  const downloadLink = URL.createObjectURL(resultBlob);

  // Compute size stats
  let extraInfo = "";
  if (mode === "compress") {
    const compressedSize = resultBlob.size;
    const ratio = ((file.size / compressedSize) * 100).toFixed(2);
    extraInfo = `
      <p><b>Compression Ratio:</b> ${ratio}%</p>
      <p><b>Original Size:</b> ${(file.size / 1024).toFixed(2)} KB</p>
      <p><b>Compressed Size:</b> ${(compressedSize / 1024).toFixed(2)} KB</p>`;
  } else {
    const decompressedSize = resultBlob.size;
    const ratio = ((decompressedSize / file.size) * 100).toFixed(2);
    extraInfo = `
      <p><b>Expansion Ratio:</b> ${ratio}%</p>
      <p><b>Compressed Size:</b> ${(file.size / 1024).toFixed(2)} KB</p>
      <p><b>Decompressed Size:</b> ${(decompressedSize / 1024).toFixed(2)} KB</p>`;
  }

  // Display results
  outputDiv.innerHTML = `
    <p><b>Operation:</b> ${mode}</p>
    <p><b>Time Taken:</b> ${duration} ms</p>
    ${extraInfo}
    <a href="${downloadLink}" 
       download="${mode === 'compress' ? file.name + '.lzw' : file.name.replace('.lzw', '_decompressed.txt')}">
      ⬇ Download Result
    </a>
  `;
});


// ============================
// LZW Binary Compression
// ============================
async function lzwCompressFile(file) {
  const arrayBuffer = await file.arrayBuffer();
  const data = new Uint8Array(arrayBuffer);

  const extension = file.name.split('.').pop();
  const extensionBytes = new TextEncoder().encode(extension);

  const MAX_DICT_SIZE = 65535;
  let dictionary = new Map();
  for (let i = 0; i < 256; i++) dictionary.set(String.fromCharCode(i), i);

  let dictSize = 256;
  let current = "";
  const compressed = [];

  for (let i = 0; i < data.length; i++) {
    const char = String.fromCharCode(data[i]);
    const next = current + char;
    if (dictionary.has(next)) {
      current = next;
    } else {
      compressed.push(dictionary.get(current));
      if (dictSize < MAX_DICT_SIZE) {
        dictionary.set(next, dictSize++);
      } else {
        dictionary = new Map();
        for (let j = 0; j < 256; j++) dictionary.set(String.fromCharCode(j), j);
        dictSize = 256;
      }
      current = char;
    }
  }

  if (current !== "") compressed.push(dictionary.get(current));

  const headerSize = 1 + extensionBytes.length;
  const outputBuffer = new ArrayBuffer(headerSize + compressed.length * 2);
  const view = new DataView(outputBuffer);

  view.setUint8(0, extensionBytes.length);
  let offset = 1;
  extensionBytes.forEach(b => view.setUint8(offset++, b));

  compressed.forEach(code => {
    view.setUint16(offset, code, false);
    offset += 2;
  });

  const blob = new Blob([outputBuffer], { type: "application/octet-stream" });
  return { blob };
}


// ============================
// LZW Binary Decompression
// ============================
async function lzwDecompressFile(file) {
  const arrayBuffer = await file.arrayBuffer();
  const view = new DataView(arrayBuffer);

  let offset = 0;
  const extLen = view.getUint8(offset++);
  let ext = "";
  for (let i = 0; i < extLen; i++) {
    ext += String.fromCharCode(view.getUint8(offset++));
  }

  const compressed = [];
  while (offset < view.byteLength) {
    compressed.push(view.getUint16(offset, false));
    offset += 2;
  }

  const MAX_DICT_SIZE = 65535;
  let dictionary = new Map();
  for (let i = 0; i < 256; i++) dictionary.set(i, new Uint8Array([i]));

  let dictSize = 256;

  let current = dictionary.get(compressed.shift());
  const result = Array.from(current);

  for (const code of compressed) {
    let entry;
    if (dictionary.has(code)) {
      entry = dictionary.get(code);
    } else if (code === dictSize) {
      entry = new Uint8Array([...current, current[0]]);
    } else {
      throw new Error(`Bad compressed code: ${code}`);
    }

    result.push(...entry);

    if (dictSize < MAX_DICT_SIZE) {
      const newEntry = new Uint8Array([...current, entry[0]]);
      dictionary.set(dictSize++, newEntry);
    } else {
      dictionary = new Map();
      for (let i = 0; i < 256; i++) dictionary.set(i, new Uint8Array([i]));
      dictSize = 256;
    }

    current = entry;
  }

  const blob = new Blob([new Uint8Array(result)], { type: "application/octet-stream" });
  return { blob };
}
