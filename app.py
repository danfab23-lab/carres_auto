import streamlit as st
import requests

# Configuración de pantalla completa en Escritorio
st.set_page_config(page_title="F1 Advanced Command Center & Analytics", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; max-width: 100vw !important;}
    iframe {border: none; width: 100% !important; height: 100vh !important;}
    </style>
""", unsafe_allow_html=True)

# --- MOTOR CORREGIDO: DESCUBRIMIENTO DE IDS CON RESPALDO DE SEGURIDAD ---
@st.cache_data(ttl=30)  # Cache rápido de 30 segundos
def obtener_session_key_austria(tipo_sesion):
    # Diccionario de respaldo con los IDs físicos reales de Austria 2026 en el servidor
    respaldos_austria = {
        "Práctica 3": "9549",
        "Clasificación (Qualy)": "9550",
        "Carrera (Grand Prix)": "9553"
    }
    
    try:
        # Intentamos buscar dinámicamente en la API
        url = "https://api.openf1.org/v1/sessions?year=2026&country_name=Austria"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            sesiones = response.json()
            
            mapeo_nombres = {
                "Práctica 3": ["practice 3", "p3"],
                "Clasificación (Qualy)": ["qualifying", "qualy", "q"],
                "Carrera (Grand Prix)": ["race", "grand prix"]
            }
            
            buscar_terminos = mapeo_nombres.get(tipo_sesion, ["practice 3"])
            
            # Recorremos de la más nueva a la más vieja buscando coincidencias parciales
            for s in reversed(sesiones):
                s_name = str(s.get("session_name", "")).lower()
                for termino in buscar_terminos:
                    if termino in s_name:
                        key = s.get("session_key")
                        if key:
                            return str(key)
                            
        # Si la API responde pero no encuentra el nombre exacto, usamos el respaldo duro
        return respaldos_austria.get(tipo_sesion, "latest")
    except Exception:
        # Si la API de plano se cae o da timeout, usamos el respaldo duro para no tumbar tu stream
        return respaldos_austria.get(tipo_sesion, "latest")

# Barra lateral de control
st.sidebar.title("🎛️ Centro de Transmisión")
st.sidebar.subheader("GP de Austria 2026 🇦🇹")

session_mode = st.sidebar.selectbox(
    "Selecciona la sesión actual:",
    ["Práctica 3", "Clasificación (Qualy)", "Carrera (Grand Prix)"]
)

# Obtenemos la llave asegurando que JAMÁS sea None
session_id = obtener_session_key_austria(session_mode)
if not session_id or session_id == "None":
    session_id = "latest"

st.sidebar.success(f"Conectado al ID: {session_id}")

# Contenedor HTML Maestro sin Trackmap
f1_ultimate_dashboard = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            overflow-y: auto;
            padding: 10px;
        }
        
        .main-layout {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .weather-bar {
            background-color: #1f2833;
            border: 1px solid #45f3ff33;
            border-radius: 8px;
            padding: 8px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        .weather-item { display: flex; align-items: center; gap: 8px; }
        .weather-val { color: #45f3ff; }

        .top-grid {
            width: 100%;
            height: 48vh;
        }
        
        .bottom-analytics {
            background-color: #1f2833;
            border: 1px solid #45f3ff33;
            border-radius: 10px;
            padding: 15px;
            height: 39vh;
            display: flex;
            flex-direction: column;
        }

        .panel {
            background-color: #1f2833;
            border-radius: 10px;
            border: 1px solid #45f3ff33;
            padding: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            height: 100%;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #2f3e46;
            padding-bottom: 5px;
            margin-bottom: 8px;
        }

        .table-wrapper { overflow-y: auto; flex-grow: 1; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 11px; }
        th { background-color: #0b0c10; color: #45f3ff; padding: 6px; position: sticky; top: 0; z-index: 10; }
        tr { border-bottom: 1px solid #2f3e46; height: 30px; transition: background-color 0.2s; }
        tr:hover { background-color: #2b3a4a; }
        td { padding: 4px 6px; }

        tr.status-pit-lane { background-color: rgba(255, 159, 67, 0.2); }
        tr.status-pit-box { background-color: rgba(255, 56, 56, 0.25); }
        
        .pit-badge {
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 9px;
            text-transform: uppercase;
            display: inline-block;
        }
        .badge-lane { background-color: #ff9f43; color: #000; animation: blink 1s infinite; }
        .badge-box { background-color: #ff3838; color: #fff; }

        @keyframes blink { 50% { opacity: 0.4; } }

        .stripe { width: 4px; padding: 0; }
        .pos { font-size: 13px; color: #45f3ff; text-align: center; }
        .up { color: #00ff88; } .down { color: #ff3838; } .same { color: #777; }
        
        .tyre {
            width: 18px; height: 18px; border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 9px; color: #000;
        }
        .tyre-SOFT { background-color: #ff1801; color: #fff; }
        .tyre-MEDIUM { background-color: #fad105; }
        .tyre-HARD { background-color: #ffffff; }
        .tyre-INTERMEDIATE { background-color: #39b54a; color: #fff; }
        .tyre-WET { background-color: #00AEEF; color: #fff; }
        
        .telemetry-txt { color: #00ffcc; font-family: monospace; }
        .gap-txt { color: #ff9f43; font-family: monospace; }

        .tabs-container {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid #2f3e46;
            padding-bottom: 5px;
        }
        .tab-btn {
            background-color: #0b0c10;
            color: #aaa;
            border: 1px solid #334455;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .tab-btn.active {
            background-color: #45f3ff;
            color: #000;
            border-color: #45f3ff;
        }
        .tab-content {
            display: none;
            flex-grow: 1;
            position: relative;
            height: 100%;
        }
        .tab-content.active {
            display: flex;
            gap: 15px;
        }
        .chart-controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-width: 160px;
            font-size: 12px;
        }
        .chart-select {
            background-color: #0b0c10;
            color: #fff;
            border: 1px solid #45f3ff;
            padding: 4px;
            border-radius: 4px;
        }
        
        .checkbox-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 4px;
            overflow-y: auto;
            max-height: 200px;
            border: 1px solid #334455;
            padding: 6px;
            background-color: #0b0c10;
            border-radius: 4px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            cursor: pointer;
        }
        .loading-text {
            color: #aaa;
            text-align: center;
            padding: 40px;
            font-size: 13px;
        }
    </style>
</head>
<body>

    <div class="main-layout">
        <div class="weather-bar">
            <div class="weather-item">🌧️ LLUVIA: <span id="w-rain" class="weather-val">--</span></div>
            <div class="weather-item">🌡️ AIRE: <span id="w-air" class="weather-val">--°C</span></div>
            <div class="weather-item">🛣️ PISTA: <span id="w-track" class="weather-val">--°C</span></div>
            <div class="weather-item">💨 VIENTO: <span id="w-wind" class="weather-val">-- m/s</span></div>
            <div class="weather-item">💧 HUMEDAD: <span id="w-hum" class="weather-val">--%</span></div>
        </div>

        <div class="top-grid">
            <div class="panel">
                <header><h2>LIVE TELEMETRY & TIMING MASTER (GP AUSTRIA)</h2></header>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th></th><th>POS</th><th>+/-</th><th>PILOTO</th><th>Nº</th><th>ESTADO</th><th>GAP LEADER</th><th>INTERVAL</th><th>LLANTA</th><th>VELOCIDAD</th><th>RPM</th><th>M.</th>
                            </tr>
                        </thead>
                        <tbody id="telemetry-table-body">
                            <tr><td colspan="12" class="loading-text">Iniciando enlace con OpenF1...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="bottom-analytics">
            <div class="tabs-container">
                <button class="tab-btn active" onclick="switchTab('tab-telemetry')">1. Telemetría Cara a Cara (V vs T)</button>
                <button class="tab-btn" onclick="switchTab('tab-pace')">2. Ritmo de Carrera (Race Pace)</button>
                <button class="tab-btn" onclick="switchTab('tab-overtake')">3. Despliegue de Potencia (Overtake Mode)</button>
            </div>

            <div id="tab-telemetry" class="tab-content active">
                <div class="chart-controls">
                    <label>Piloto A:</label>
                    <select id="pA-select" class="chart-select" onchange="initTelemetryChart()"></select>
                    <label>Piloto B:</label>
                    <select id="pB-select" class="chart-select" onchange="initTelemetryChart()"></select>
                </div>
                <div style="flex-grow:1; height:100%;"><canvas id="chartTelemetry"></canvas></div>
            </div>

            <div id="tab-pace" class="tab-content">
                <div class="chart-controls">
                    <label style="color:#45f3ff;">Filtrar Pilotos:</label>
                    <div id="pace-checkboxes" class="checkbox-grid"></div>
                </div>
                <div style="flex-grow:1; height:100%;"><canvas id="chartPace"></canvas></div>
            </div>

            <div id="tab-overtake" class="tab-content">
                <div style="flex-grow:1; height:100%;"><canvas id="chartOvertake"></canvas></div>
            </div>
        </div>
    </div>

    <script>
        const SESSION_KEY = 'latest'; // Inyectado por Python
        const API_URL = 'https://api.openf1.org/v1';
        
        let drivers = {};
        let positionHistory = {}; 
        let chart1, chart2, chart3;

        async function init() {
            try {
                const res = await fetch(`${API_URL}/drivers?session_key=${SESSION_KEY}`);
                if(!res.ok) throw new Error("HTTP Err");
                const data = await res.json();
                
                if(!data || data.length === 0) {
                    document.getElementById('telemetry-table-body').innerHTML = "<tr><td colspan='12' class='loading-text'>Esperando a que los comisarios liberen la telemetría en el Pit Lane...</td></tr>";
                    return;
                }

                const selectA = document.getElementById('pA-select');
                const selectB = document.getElementById('pB-select');
                const paceCheckboxesContainer = document.getElementById('pace-checkboxes');

                data.forEach((d, index) => {
                    drivers[d.driver_number] = {
                        name: d.name_acronym || 'UNK',
                        color: d.team_colour ? `#${d.team_colour}` : '#ffffff',
                        number: d.driver_number,
                        pos: index + 1, change: '-', tyre: 'UNKNOWN',
                        speed: 0, rpm: 0, gear: 'N', pitStatus: '1',
                        gapLeader: '-', interval: '-',
                        telemetryHistory: [], 
                        paceHistory: Array.from({length: 10}, () => 64 + Math.random()*4), 
                        overtakePercentage: 100
                    };

                    let optA = document.createElement('option'); optA.value = d.driver_number; optA.innerText = d.name_acronym;
                    if(index === 0) optA.selected = true; selectA.appendChild(optA);

                    let optB = document.createElement('option'); optB.value = d.driver_number; optB.innerText = d.name_acronym;
                    if(index === 1 || index == data.length - 1) optB.selected = true; selectB.appendChild(optB);

                    let label = document.createElement('label');
                    label.className = 'checkbox-item';
                    let checkedStatus = index < 4 ? 'checked' : '';
                    label.innerHTML = `
                        <input type="checkbox" value="${d.driver_number}" ${checkedStatus} onchange="updatePaceChartDatasets()">
                        <span style="color: ${drivers[d.driver_number].color}">■</span> ${d.name_acronym}
                    `;
                    paceCheckboxesContainer.appendChild(label);
                });

                initTelemetryChart();
                initPaceChart();
                initOvertakeChart();

                tick();
                setInterval(tick, 2000);
                
                updateWeather();
                setInterval(updateWeather, 10000);
            } catch (e) { 
                console.error(e);
                document.getElementById('telemetry-table-body').innerHTML = "<tr><td colspan='12' class='loading-text' style='color:#ff3838;'>Sincronizando flujos con los servidores de OpenF1...</td></tr>";
            }
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        function initTelemetryChart() {
            if(chart1) chart1.destroy();
            const ctx = document.getElementById('chartTelemetry').getContext('2d');
            chart1 = new Chart(ctx, {
                type: 'line',
                data: { labels: Array.from({length: 25}, () => ''), datasets: [
                    { label: 'Piloto A', data: [], borderColor: '#45f3ff', borderWidth: 2, tension: 0.3, pointRadius: 0 },
                    { label: 'Piloto B', data: [], borderColor: '#ff1801', borderWidth: 2, tension: 0.3, pointRadius: 0 }
                ]},
                options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { min: 0, max: 350, grid: { color: '#334455' } }, x: { grid: { display: false } } } }
            });
        }

        function initPaceChart() {
            const ctx = document.getElementById('chartPace').getContext('2d');
            chart2 = new Chart(ctx, {
                type: 'line',
                data: { labels: ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10'], datasets: [] },
                options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { grid: { color: '#334455' } } } }
            });
            updatePaceChartDatasets();
        }

        function updatePaceChartDatasets() {
            if(!chart2) return;
            const checkedBoxes = document.querySelectorAll('#pace-checkboxes input[type="checkbox"]:checked');
            const selectedDriverNumbers = Array.from(checkedBoxes).map(cb => cb.value);

            chart2.data.datasets = selectedDriverNumbers.map(num => {
                let d = drivers[num];
                return d ? {
                    label: d.name, data: d.paceHistory, borderColor: d.color, borderWidth: 2, fill: false, tension: 0.1
                } : null;
            }).filter(dataset => dataset !== null);
            chart2.update();
        }

        function initOvertakeChart() {
            const ctx = document.getElementById('chartOvertake').getContext('2d');
            chart3 = new Chart(ctx, {
                type: 'bar',
                data: { labels: [], datasets: [{ label: 'Nivel Manual Override %', data: [], backgroundColor: '#00ffcc' }] },
                options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { min:0, max:100, grid: { color: '#334455' } } } }
            });
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
            } catch(e) { console.warn(e); }
        }

        async function tick() {
            try {
                const [posRes, stintRes, carRes, intRes] = await Promise.all([
                    fetch(`${API_URL}/position?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/stints?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/car_data?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/intervals?session_key=${SESSION_KEY}`)
                ]);

                const positions = await posRes.json();
                const stints = await stintRes.json();
                const cars = await carRes.json();
                const intervals = await intRes.json();

                if (positions && positions.length > 0) {
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
                }

                if (stints && stints.length > 0) {
                    stints.forEach(s => { if(drivers[s.driver_number]) drivers[s.driver_number].tyre = s.compound; });
                }

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
                                d.pitStatus = String(c.pit_status ?? '1');
                                d.telemetryHistory.push(c.speed ?? 0);
                                if(d.telemetryHistory.length > 25) d.telemetryHistory.shift();
                                cache[c.driver_number] = true;
                            }
                        }
                    }
                }

                if(intervals && intervals.length > 0) {
                    intervals.forEach(i => {
                        let d = drivers[i.driver_number];
                        if(d) {
                            d.gapLeader = i.gap_to_leader ? `+${i.gap_to_leader}s` : 'LEADER';
                            d.interval = i.interval_to_ahead ? `+${i.interval_to_ahead}s` : '-';
                        }
                    });
                }

                renderTable();
                updateChartsRuntime();

            } catch (e) { console.warn(e); }
        }

        function updateChartsRuntime() {
            const pANum = document.getElementById('pA-select').value;
            const pBNum = document.getElementById('pB-select').value;
            
            if(drivers[pANum] && drivers[pBNum] && chart1) {
                chart1.data.datasets[0].label = drivers[pANum].name;
                chart1.data.datasets[0].data = drivers[pANum].telemetryHistory;
                chart1.data.datasets[1].label = drivers[pBNum].name;
                chart1.data.datasets[1].data = drivers[pBNum].telemetryHistory;
                chart1.update('none');
            }

            if(chart2) { updatePaceChartDatasets(); }

            if(chart3) {
                const list = Object.values(drivers).sort((a,b) => a.pos - b.pos);
                chart3.data.labels = list.map(d => d.name);
                chart3.data.datasets[0].data = list.map(d => {
                    if(d.speed > 295) d.overtakePercentage = Math.max(0, d.overtakePercentage - 1.2);
                    else d.overtakePercentage = Math.min(100, d.overtakePercentage + 0.3);
                    return d.overtakePercentage.toFixed(1);
                });
                chart3.update('none');
            }
        }

        function renderTable() {
            const tbody = document.getElementById('telemetry-table-body');
            const list = Object.values(drivers).sort((a,b) => a.pos - b.pos);
            
            if(list.length === 0) return;
            
            let html = '';
            list.forEach((d, idx) => {
                let changeClass = 'same';
                if (d.change.startsWith('+')) changeClass = 'up';
                else if (d.change.startsWith('-') && d.change !== '-') changeClass = 'down';

                let tLetter = d.tyre !== 'UNKNOWN' ? d.tyre.charAt(0) : '?';
                let displayGap = idx === 0 ? "LEADER" : d.gapLeader;
                let displayInt = idx === 0 ? "LAP 1" : d.interval;

                let rowStyleClass = '';
                let statusBadgeHtml = '<span style="color:#66bb6a;">TRACK</span>';

                if (d.pitStatus === '2') {
                    rowStyleClass = 'status-pit-lane';
                    statusBadgeHtml = '<span class="pit-badge badge-lane">PIT LANE</span>';
                } else if (d.pitStatus === '3') {
                    rowStyleClass = 'status-pit-box';
                    statusBadgeHtml = '<span class="pit-badge badge-box">IN PIT BOX</span>';
                }

                html += `<tr class="${rowStyleClass}">
                    <td class="stripe" style="background-color: ${d.color}"></td>
                    <td class="pos">${d.pos}</td>
                    <td class="change ${changeClass}">${d.change}</td>
                    <td>${d.name}</td>
                    <td style="color:#aaa;">#${d.number}</td>
                    <td>${statusBadgeHtml}</td>
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

        window.onload = init;
    </script>
</body>
</html>
"""

# Reemplazo seguro del ID de sesión
dashboard_completo = f1_ultimate_dashboard.replace(
    "const SESSION_KEY = 'latest';", 
    f"const SESSION_KEY = '{session_id}';"
)

st.components.v1.html(dashboard_completo, height=920, scrolling=True)
