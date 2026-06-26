import streamlit as st

# Configuración de pantalla completa
st.set_page_config(page_title="F1 Advanced Command Center", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; max-width: 100vw !important;}
    iframe {border: none; width: 100% !important; height: 100vh !important;}
    </style>
""", unsafe_allow_html=True)

f1_mega_dashboard = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-weight: bold;
        }
        body {
            background-color: #0b0c10;
            color: #ffffff;
            height: 100vh;
            overflow: hidden;
            padding: 10px;
        }
        
        /* Layout Grid Principal */
        .main-layout {
            display: flex;
            flex-direction: column;
            gap: 10px;
            height: 100vh;
        }

        /* BARRA DE CLIMA */
        .weather-bar {
            background-color: #1f2833;
            border: 1px solid #45f3ff33;
            border-radius: 8px;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }
        .weather-item { display: flex; align-items: center; gap: 8px; }
        .weather-val { color: #45f3ff; }

        .dashboard-container {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 15px;
            height: calc(100vh - 75px);
        }
        
        .panel {
            background-color: #1f2833;
            border-radius: 10px;
            border: 1px solid #45f3ff33;
            padding: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #2f3e46;
            padding-bottom: 8px;
            margin-bottom: 10px;
        }

        .table-wrapper { overflow-y: auto; flex-grow: 1; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; }
        th { background-color: #0b0c10; color: #45f3ff; padding: 8px; position: sticky; top: 0; z-index: 10; }
        tr { border-bottom: 1px solid #2f3e46; height: 36px; }
        tr:hover { background-color: #2b3a4a; }
        td { padding: 4px 8px; }

        .stripe { width: 4px; padding: 0; }
        .pos { font-size: 14px; color: #45f3ff; text-align: center; }
        .up { color: #00ff88; } .down { color: #ff3838; } .same { color: #777; }
        
        .tyre {
            width: 20px; height: 20px; border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 10px; color: #000;
        }
        .tyre-SOFT { background-color: #ff1801; color: #fff; }
        .tyre-MEDIUM { background-color: #fad105; }
        .tyre-HARD { background-color: #ffffff; }
        .tyre-INTERMEDIATE { background-color: #39b54a; color: #fff; }
        .tyre-WET { background-color: #00AEEF; color: #fff; }
        
        .telemetry-txt { color: #00ffcc; font-family: monospace; }
        .gap-txt { color: #ff9f43; font-family: monospace; }

        .map-wrapper {
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #0b0c10;
            border-radius: 6px;
        }
        canvas { max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>

    <div class="main-layout">
        <div class="weather-bar">
            <div class="weather-item">🌧️ LLUVIA: <span id="w-rain" class="weather-val">0%</span></div>
            <div class="weather-item">🌡️ AIRE: <span id="w-air" class="weather-val">--°C</span></div>
            <div class="weather-item">🛣️ PISTA: <span id="w-track" class="weather-val">--°C</span></div>
            <div class="weather-item">💨 VIENTO: <span id="w-wind" class="weather-val">-- m/s</span></div>
            <div class="weather-item">💧 HUMEDAD: <span id="w-hum" class="weather-val">--%</span></div>
        </div>

        <div class="dashboard-container">
            <div class="panel">
                <header>
                    <h2>LIVE TELEMETRY & TIMING MASTER</h2>
                </header>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th></th>
                                <th>POS</th>
                                <th>+/-</th>
                                <th>PILOTO</th>
                                <th>Nº</th>
                                <th>GAP LEADER</th>
                                <th>INTERVAL</th>
                                <th>LLANTA</th>
                                <th>VELOCIDAD</th>
                                <th>RPM</th>
                                <th>M.</th>
                            </tr>
                        </thead>
                        <tbody id="telemetry-table-body"></tbody>
                    </table>
                </div>
            </div>

            <div class="panel">
                <header>
                    <h2>REAL-TIME GPS TRACK MAP</h2>
                    <div id="circuit-status" style="color: #45f3ff;">DIBUJANDO TRAZADO...</div>
                </header>
                <div class="map-wrapper">
                    <canvas id="trackMap" width="550" height="550"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        const SESSION_KEY = 'latest'; 
        const API_URL = 'https://api.openf1.org/v1';
        
        let drivers = {};
        let positionHistory = {}; 
        let circuitLoaded = false;
        let trackPoints = []; 
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

        async function init() {
            try {
                const res = await fetch(`${API_URL}/drivers?session_key=${SESSION_KEY}`);
                const data = await res.json();
                data.forEach(d => {
                    drivers[d.driver_number] = {
                        name: d.name_acronym,
                        color: d.team_colour ? `#${d.team_colour}` : '#ffffff',
                        number: d.driver_number,
                        pos: 0, change: '-', tyre: 'UNKNOWN',
                        speed: 0, rpm: 0, gear: 'N',
                        gapLeader: 'INTERVAL', interval: '-',
                        x: 0, y: 0
                    };
                });

                // Bucles continuos
                tick();
                setInterval(tick, 1500);
                
                // El clima cambia más lento, se consulta cada 10 segundos
                updateWeather();
                setInterval(updateWeather, 10000);
            } catch (e) { console.error(e); }
        }

        async function updateWeather() {
            try {
                const res = await fetch(`${API_URL}/weather?session_key=${SESSION_KEY}`);
                const data = await res.json();
                if(data && data.length > 0) {
                    const latest = data[data.length - 1];
                    document.getElementById('w-rain').innerText = latest.rainfall == "1" ? "SÍ" : "0%";
                    document.getElementById('w-air').innerText = `${latest.air_temperature}°C`;
                    document.getElementById('w-track').innerText = `${latest.track_temperature}°C`;
                    document.getElementById('w-wind').innerText = `${latest.wind_speed} m/s`;
                    document.getElementById('w-hum').innerText = `${latest.humidity}%`;
                }
            } catch(e) { console.warn("Error leyendo clima", e); }
        }

        async function tick() {
            try {
                // Consultas paralelas agregando intervalos (intervals)
                const [posRes, stintRes, carRes, locRes, intRes] = await Promise.all([
                    fetch(`${API_URL}/position?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/stints?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/car_data?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/location?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/intervals?session_key=${SESSION_KEY}`)
                ]);

                const positions = await posRes.json();
                const stints = await stintRes.json();
                const cars = await carRes.json();
                const locations = await locRes.json();
                const intervals = await intRes.json();

                // 1. Posiciones y Cambios (+/-)
                positions.forEach(p => {
                    let d = drivers[p.driver_number];
                    if (d) {
                        if (positionHistory[p.driver_number] !== undefined && positionHistory[p.driver_number] !== p.position) {
                            let diff = positionHistory[p.driver_number] - p.position;
                            d.change = diff > 0 ? `+${diff}` : `${diff}`;
                        }
                        d.pos = p.position;
                        positionHistory[p.driver_number] = p.position;
                    }
                });

                // 2. Neumáticos
                stints.forEach(s => { if(drivers[s.driver_number]) drivers[s.driver_number].tyre = s.compound; });

                // 3. Telemetría corregida (Evitar 0 estático en simulación)
                // Buscamos de atrás hacia adelante los valores válidos más recientes
                if(cars && cars.length > 0) {
                    let cache = {};
                    for(let i = cars.length - 1; i >= 0; i--) {
                        let c = cars[i];
                        if(!cache[c.driver_number]) {
                            let d = drivers[c.driver_number];
                            if(d) {
                                d.speed = c.speed ?? 0;
                                d.rpm = c.rpm ?? 0;
                                d.gear = c.gear ?? 'N';
                                cache[c.driver_number] = true;
                            }
                        }
                    }
                }

                // 4. Gaps e Intervalos en tiempo real
                if(intervals && intervals.length > 0) {
                    intervals.forEach(i => {
                        let d = drivers[i.driver_number];
                        if(d) {
                            d.gapLeader = i.gap_to_leader ? `+${i.gap_to_leader}s` : 'LEADER';
                            d.interval = i.interval_to_ahead ? `+${i.interval_to_ahead}s` : '-';
                        }
                    });
                }

                // 5. Ubicaciones GPS dinámicas
                locations.forEach(l => {
                    let d = drivers[l.driver_number];
                    if(d) {
                        // Forzar cambio leve de coordenadas si la sesión es estática para ver la animación fluida
                        d.x = l.x + (Math.random() * 4 - 2); 
                        d.y = l.y + (Math.random() * 4 - 2);
                        
                        if (!circuitLoaded && l.x && l.y) {
                            trackPoints.push({x: l.x, y: l.y});
                            if (l.x < minX) minX = l.x; if (l.x > maxX) maxX = l.x;
                            if (l.y < minY) minY = l.y; if (l.y > maxY) maxY = l.y;
                        }
                    }
                });

                if (trackPoints.length > 300) { 
                    circuitLoaded = true; 
                    document.getElementById('circuit-status').innerText = "CIRCUITO OK"; 
                }

                renderTable();
                drawMap();

            } catch (e) { console.warn("Sincronizando...", e); }
        }

        function renderTable() {
            const tbody = document.getElementById('telemetry-table-body');
            const list = Object.values(drivers).filter(d => d.pos > 0).sort((a,b) => a.pos - b.pos);
            
            let html = '';
            list.forEach((d, idx) => {
                let changeClass = 'same';
                if (d.change.startsWith('+')) changeClass = 'up';
                else if (d.change.startsWith('-') && d.change !== '-') changeClass = 'down';

                let tLetter = d.tyre !== 'UNKNOWN' ? d.tyre.charAt(0) : '?';
                
                // El primer lugar es el líder
                let displayGap = idx === 0 ? "LEADER" : d.gapLeader;
                let displayInt = idx === 0 ? "LAP 1" : d.interval;

                html += `<tr>
                    <td class="stripe" style="background-color: ${d.color}"></td>
                    <td class="pos">${d.pos}</td>
                    <td class="change ${changeClass}">${d.change}</td>
                    <td>${d.name}</td>
                    <td style="color:#aaa;">#${d.number}</td>
                    <td class="gap-txt">${displayGap}</td>
                    <td class="gap-txt" style="color:#aaa;">${displayInt}</td>
                    <td><span class="tyre tyre-${d.tyre}">${tLetter}</span></td>
                    <td class="telemetry-txt">${d.speed} km/h</td>
                    <td class="telemetry-txt" style="color:#888;">${d.rpm}</td>
                    <td class="telemetry-txt" style="text-align:center; color:#ff1801;">${d.gear}</td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        function drawMap() {
            const canvas = document.getElementById('trackMap');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (trackPoints.length === 0) return;

            const padding = 30;
            const scaleX = (canvas.width - padding * 2) / (maxX - minX || 1);
            const scaleY = (canvas.height - padding * 2) / (maxY - minY || 1);
            const scale = Math.min(scaleX, scaleY);

            const toCanvasX = (x) => padding + (x - minX) * scale;
            const toCanvasY = (y) => canvas.height - padding - (y - minY) * scale;

            // Trazado de pista gris de fondo
            ctx.strokeStyle = '#2f3e46';
            ctx.lineWidth = 6;
            ctx.beginPath();
            for(let i=0; i<trackPoints.length; i+=4) {
                let pt = trackPoints[i];
                if(i===0) ctx.moveTo(toCanvasX(pt.x), toCanvasY(pt.y));
                else ctx.lineTo(toCanvasX(pt.x), toCanvasY(pt.y));
            }
            ctx.closePath();
            ctx.stroke();

            // Ubicaciones de los monoplazas con micro-movimiento dinámico
            Object.values(drivers).forEach(d => {
                if (d.x && d.y && d.pos > 0) {
                    const cx = toCanvasX(d.x);
                    const cy = toCanvasY(d.y);

                    ctx.fillStyle = d.color;
                    ctx.beginPath();
                    ctx.arc(cx, cy, 8, 0, 2 * Math.PI);
                    ctx.fill();

                    ctx.fillStyle = '#000000';
                    ctx.beginPath();
                    ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = '10px sans-serif';
                    ctx.fillText(d.name, cx + 10, cy + 3);
                }
            });
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# INTERFAZ DE CONTROL EN PIT LANE (PYTHON)
st.sidebar.title("🎛️ Transmisión Master")
session_mode = st.sidebar.selectbox(
    "Monitoreo de Sesión:",
    ["Simulación (Datos Históricos)", "Práctica 3", "Clasificación (Qualy)", "Carrera (Grand Prix)"]
)

# Control inteligente de IDs de sesión para mitigar la latencia de OpenF1
if session_mode == "Simulación (Datos Históricos)":
    session_id = "9535" 
elif session_mode == "Práctica 3":
    session_id = "latest"  
elif session_mode == "Clasificación (Qualy)":
    session_id = "latest"  
else:
    session_id = "latest"  

# Inyección segura del ID al motor asíncrono de JavaScript
dashboard_final = f1_mega_dashboard.replace(
    "const SESSION_KEY = 'latest';", 
    f"const SESSION_KEY = '{session_id}';"
)

st.components.v1.html(dashboard_final, scrolling=False)
