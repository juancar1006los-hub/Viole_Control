const $ = id => document.getElementById(id);
const speed = $('speed'); 
let active = null;

// Fungsi untuk mengirimkan perintah pergerakan ke API backend
const command = async (name) => {
  if (name === active && name !== 'stop') return;
  active = name === 'stop' ? null : name;
  try { 
    const r = await fetch('/api/command', {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify({ command: name, speed: +speed.value })
    }); 
    if (!r.ok) throw new Error((await r.json()).detail); 
  }
  catch(e) { 
    $('status').textContent = 'ESP32 offline'; 
    console.warn(e); 
  }
};

// Fungsi pembantu untuk menghentikan robot
const stop = () => command('stop');

// Event listener untuk tombol kendali di UI (Maju, Mundur, Kiri, Kanan)
document.querySelectorAll('[data-command]').forEach(b => { 
  const go = e => { e.preventDefault(); command(b.dataset.command); }; 
  b.addEventListener('pointerdown', go); 
  b.addEventListener('pointerup', stop); 
  // Catatan: b.addEventListener('pointerleave', stop); DIHAPUS karena menyebabkan robot stuttering/berhenti mendadak
});

// Event listener untuk tombol stop manual di tengah UI
$('stop').onclick = stop;

// Menampilkan nilai persentase slider kecepatan secara real-time di UI
speed.oninput = () => $('speed-value').textContent = speed.value;

// Kontrol menggunakan Keyboard (Tombol Ditekan)
document.addEventListener('keydown', e => { 
  if (e.repeat) return; 
  const keys = {
    ArrowUp: 'forward', w: 'forward',
    ArrowDown: 'backward', s: 'backward',
    ArrowLeft: 'left', a: 'left',
    ArrowRight: 'right', d: 'right',
    ' ': 'stop'
  }; 
  if (keys[e.key]) { 
    e.preventDefault(); 
    command(keys[e.key]); 
  } 
});

// Kontrol menggunakan Keyboard (Tombol Dilepas)
document.addEventListener('keyup', e => {
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'a', 's', 'd'].includes(e.key)) {
    stop();d
  }
});

// Fungsi untuk merender/menampilkan data telemetri ke layar UI
function render(t) { 
  if (t.battery != null) $('battery').textContent = `${t.battery} V`; 
  if (t.distance != null) $('distance').textContent = `${t.distance} cm`; 
  if (t.temperature != null) $('temperature').textContent = `${t.temperature} °C`; 
  $('status').textContent = t.status || 'online'; 
}

// Setup awal: Mengambil konfigurasi stream kamera dan telemetri awal dari server
async function setup() { 
  const c = await fetch('/api/config').then(r => r.json()); 
  const img = $('camera'); 
  img.src = c.camera_stream_url; 
  img.onload = () => {
    $('camera-state').textContent = 'Live';
    $('camera-placeholder').style.display = 'none';
  }; 
  img.onerror = () => {
    $('camera-state').textContent = 'Stream tidak tersedia';
  }; 
  fetch('/api/telemetry').then(r => r.json()).then(render); 
}

// Inisialisasi dan manajemen koneksi WebSocket secara Real-Time
// Ganti fungsi socket() lama Anda dengan kode ini
function socket() {
  $('connection').textContent = '● Dashboard online (Serverless)';
  $('connection').className = 'badge online';

  // Melakukan fetch telemetri secara berkala setiap 2 detik ke backend
  setInterval(async () => {
    try {
// Di dalam fungsi polling interval Anda:
const r = await fetch('/api/telemetry');
if (r.ok) {
    const data = await r.json();
    
    // VERIFIKASI BARIS INI:
    // Cari elemen gambar kamera Anda (misal id-nya 'camera-stream')
    const imgCam = document.getElementById('camera-stream'); 
    
    // Ubah src gambar secara dinamis ke URL Ngrok yang dikirim backend
    if (imgCam && data.camera_url) {
        imgCam.src = data.camera_url;
    }
    
    render(data);
}

    } catch (e) {
      $('connection').textContent = '● Terputus dari server';
      $('connection').className = 'badge offline';
    }
  }, 2000); 
}

// Menjalankan fungsi setup dan websocket saat halaman dimuat
setup();
socket();