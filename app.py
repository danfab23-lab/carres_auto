import streamlit as st

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
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 15px;
            height: 45vh;
        }
        
        .bottom-analytics {
            background-color: #1f2833;
            border: 1px solid #45f3ff33;
            border-radius: 10px;
            padding: 15px;
            height: 42vh;
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

        .map-wrapper {
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #0b0c10;
            border-radius: 6px;
            height: 100%;
        }
        canvas { max-width: 100%; max-height: 100%; }

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
            max-height: 220px;
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
    </style>
</head>
<body>

    <div class="main-layout">
        <!-- CLIMA -->
        <div class="weather-bar">
            <div class="weather-item">🌧️ LLUVIA: <span id="w-rain" class="weather-val">0%</span></div>
            <div class="weather-item">🌡️ AIRE: <span id="w-air" class="weather-val">--°C</span></div>
            <div class="weather-item">🛣️ PISTA: <span id="w-track" class="weather-val">--°C</span></div>
            <div class="weather-item">💨 VIENTO: <span id="w-wind" class="weather-val">-- m/s</span></div>
            <div class="weather-item">💧 HUMEDAD: <span id="w-hum" class="weather-val">--%</span></div>
        </div>

        <!-- TIMING MASTER Y GPS MAP -->
        <div class="top-grid">
            <div class="panel">
                <header><h2>LIVE TELEMETRY & TIMING MASTER</h2></header>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th></th><th>POS</th><th>+/-</th><th>PILOTO</th><th>Nº</th><th>ESTADO</th><th>GAP LEADER</th><th>INTERVAL</th><th>LLANTA</th><th>VELOCIDAD</th><th>RPM</th><th>M.</th>
                            </tr>
                        </thead>
                        <tbody id="telemetry-table-body"></tbody>
                    </table>
                </div>
            </div>

            <div class="panel">
                <header><h2>REAL-TIME GPS TRACK MAP</h2><div id="circuit-status" style="color: #45f3ff;">AUSTRIA CALIBRADO OK</div></header>
                <div class="map-wrapper"><canvas id="trackMap" width="500" height="350"></canvas></div>
            </div>
        </div>

        <!-- SECCIÓN DE GRÁFICAS -->
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
        const SESSION_KEY = 'latest'; 
        const API_URL = 'https://api.openf1.org/v1';
        
        let drivers = {};
        let positionHistory = {}; 
        let trackPoints = []; 
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

        let chart1, chart2, chart3;
        let timeLabelCounter = 0;

        // VECTORIZACIÓN EXACTA EXTRAÍDA DE LA IMAGEN image_388eba.png
        const CIRCUITO_PLANTILLAS = {
            "AUSTRIA": [
                {x: 1750, y: 700},   // Curva 1 (Inicio/Meta)
                {x: 2150, y: 1150},  // Recta de subida hacia T2
                {x: 2800, y: 1900},  // Punto ciego antes de Curva 3
                {x: 3100, y: 2200},  // Curva 3 (Remus - Vértice cerrado superior)
                {x: 2400, y: 2350},  // Bajada hacia Curva 4
                {x: 1800, y: 2450},  // Curva 4 (Glock)
                {x: 1400, y: 2100},  // Curva 5
                {x: 1150, y: 1700},  // Curva 6 (Sección interna)
                {x: 1050, y: 1250},  // Curva 7 (Rindt)
                {x: 1250, y: 900},   // Curva 8
                {x: 1500, y: 720}    // Curvas 9 y 10 (Entrada a meta principal)
            ],
            "BARCELONA": [
                {x:1200, y:2500}, {x:1800, y:2800}, {x:2500, y:2900}, {x:3200, y:2700}, {x:3600, y:2200}, 
                {x:3500, y:1500}, {x:2900, y:1100}, {x:2200, y:1000}, {x:1500, y:1300}, {x:900, y:1800}
            ],
            "MONZA": [
                {x:1180, y:4300}, {x:1420, y:4900}, {x:1850, y:5200}, {x:2300, y:4800}, {x:2600, y:4100}, 
                {x:2500, y:3100}, {x:2100, y:2200}, {x:1650, y:1450}, {x:1100, y:1900}, {x:950, y:2900}
            ]
        };

        function cargarTrazadoEstatico(nombreCircuito) {
            trackPoints = CIRCUITO_PLANTILLAS[nombreCircuito] || CIRCUITO_PLANTILLAS["AUSTRIA"];
            minX = Infinity; maxX = -Infinity; minY = Infinity; maxY = -Infinity;
            trackPoints.forEach(pt => {
                if (pt.x < minX) minX = pt.x; if (pt.x > maxX) maxX = pt.x;
                if (pt.y < minY) minY = pt.y; if (pt.y > maxY) maxY = pt.y;
            });
        }

        async function init() {
            cargarTrazadoEstatico("AUSTRIA");

            try {
                const res = await fetch(`${API_URL}/drivers?session_key=${SESSION_KEY}`);
                const data = await res.json();
                
                const selectA = document.getElementById('pA-select');
                const selectB = document.getElementById('pB-select');
                const paceCheckboxesContainer = document.getElementById('pace-checkboxes');

                data.forEach((d, index) => {
                    drivers[d.driver_number] = {
                        name: d.name_acronym,
                        color: d.team_colour ? `#${d.team_colour}` : '#ffffff',
                        number: d.driver_number,
                        pos: index + 1, change: '-', tyre: 'MEDIUM',
                        speed: 0, rpm: 0, gear: 'N', pitStatus: '1',
                        gapLeader: 'INTERVAL', interval: '-',
                        x: 0, y: 0,
                        telemetryHistory: [], 
                        paceHistory: Array.from({length: 10}, () => 65 + Math.random()*3), 
                        overtakePercentage: 40 + Math.random()*50
                    };

                    let optA = document.createElement('option');
                    optA.value = d.driver_number; optA.innerText = d.name_acronym;
                    if(index === 0) optA.selected = true;
                    selectA.appendChild(optA);

                    let optB = document.createElement('option');
                    optB.value = d.driver_number; optB.innerText = d.name_acronym;
                    if(index === 1) optB.selected = true;
                    selectB.appendChild(optB);

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
                setInterval(tick, 1500);
                
                updateWeather();
                setInterval(updateWeather, 10000);
            } catch (e) { console.error(e); }
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
                data: { labels: [], datasets: [
                    { label: 'Piloto A', data: [], borderColor: '#45f3ff', borderWidth: 2, tension: 0.3, pointRadius: 0 },
                    { label: 'Piloto B', data: [], borderColor: '#ff1801', borderWidth: 2, tension: 0.3, pointRadius: 0 }
                ]},
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 350, grid: { color: '#334455' } }, x: { grid: { display: false } } } }
            });
        }

        function initPaceChart() {
            const ctx = document.getElementById('chartPace').getContext('2d');
            chart2 = new Chart(ctx, {
                type: 'line',
                data: { labels: ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10'], datasets: [] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { grid: { color: '#334455' } } } }
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
            chart2.update('none');
        }

        function initOvertakeChart() {
            const ctx = document.getElementById('chartOvertake').getContext('2d');
            chart3 = new Chart(ctx, {
                type: 'bar',
                data: { labels: [], datasets: [{ label: 'Despliegue Overtake Mode / Manual Override %', data: [], backgroundColor: '#00ffcc' }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { min:0, max:100, grid: { color: '#334455' } } } }
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

                if(locations && locations.length > 0) {
                    locations.forEach(l => {
                        let d = drivers[l.driver_number];
                        if(d) {
                            d.x = l.x; 
                            d.y = l.y;
                        }
                    });
                }

                renderTable();
                drawMap();
                updateChartsRuntime();

            } catch (e) { console.warn(e); }
        }

        function updateChartsRuntime() {
            const pANum = document.getElementById('pA-select').value;
            const pBNum = document.getElementById('pB-select').value;
            
            if(drivers[pANum] && drivers[pBNum] && chart1) {
                chart1.data.datasets[0].label = drivers[pANum].name;
                chart1.data.datasets[0].borderColor = drivers[pANum].color;
                chart1.data.datasets[0].data = drivers[pANum].telemetryHistory;
                chart1.data.datasets[1].label = drivers[pBNum].name;
                chart1.data.datasets[1].borderColor = drivers[pBNum].color;
                chart1.data.datasets[1].data = drivers[pBNum].telemetryHistory;
                timeLabelCounter++;
                chart1.data.labels.push('');
                if(chart1.data.labels.length > 25) chart1.data.labels.shift();
                chart1.update('none');
            }

            if(chart2) { updatePaceChartDatasets(); }

            if(chart3) {
                const list = Object.values(drivers).sort((a,b) => a.pos - b.pos);
                chart3.data.labels = list.map(d => d.name);
                chart3.data.datasets[0].data = list.map(d => d.overtakePercentage.toFixed(1));
                chart3.update('none');
            }
        }

        function renderTable() {
            const tbody = document.getElementById('telemetry-table-body');
            const list = Object.values(drivers).sort((a,b) => a.pos - b.pos);
            
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

        function drawMap() {
            const canvas = document.getElementById('trackMap');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (trackPoints.length === 0) return;

            const canvasPadding = 60; 
            const scaleX = (canvas.width - canvasPadding * 2) / (maxX - minX || 1);
            const scaleY = (canvas.height - canvasPadding * 2) / (maxY - minY || 1);
            const scale = Math.min(scaleX, scaleY);

            const trackWidthInCanvas = (maxX - minX) * scale;
            const trackHeightInCanvas = (maxY - minY) * scale;

            const offsetX = (canvas.width - trackWidthInCanvas) / 2;
            const offsetY = (canvas.height - trackHeightInCanvas) / 2;

            const toCanvasX = (x) => offsetX + (x - minX) * scale;
            const toCanvasY = (y) => canvas.height - offsetY - (y - minY) * scale;

            // Dibujar el trazado fino de la base de datos fija
            ctx.strokeStyle = '#3a4f5c';
            ctx.lineWidth = 4;  
            ctx.beginPath();
            for(let i=0; i<trackPoints.length; i++) {
                let pt = trackPoints[i];
                if(i===0) ctx.moveTo(toCanvasX(pt.x), toCanvasY(pt.y));
                else ctx.lineTo(toCanvasX(pt.x), toCanvasY(pt.y));
            }
            ctx.closePath();
            ctx.stroke();

            // Ubicaciones de los monoplazas sobre el circuito precargado
            Object.values(drivers).forEach(d => {
                if (d.x && d.y) {
                    const cx = toCanvasX(d.x);
                    const cy = toCanvasY(d.y);

                    ctx.fillStyle = d.color;
                    ctx.beginPath(); ctx.arc(cx, cy, 7, 0, 2 * Math.PI); ctx.fill();
                    ctx.fillStyle = '#000000';
                    ctx.beginPath(); ctx.arc(cx, cy, 4, 0, 2 * Math.PI); ctx.fill();
                    ctx.fillStyle = '#ffffff';
                    ctx.font = '9px sans-serif';
                    ctx.fillText(d.name, cx + 9, cy + 3);
                }
            });
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# INTERFAZ DE CONTROL LATERAL DE STREAMLIT (PYTHON)
st.sidebar.title("🎛️ Transmisión Master Pro")
session_mode = st.sidebar.selectbox(
    "Monitoreo de Sesión:",
    ["Simulación (Datos Históricos)", "Práctica 3", "Clasificación (Qualy)", "Carrera (Grand Prix)"]
)

circuito_a_narrar = st.sidebar.selectbox(
    "Circuito del Fin de Semana:",
    ["Austria", "Barcelona", "Monza"]
)

if session_mode == "Simulación (Datos Históricos)":
    session_id = "9535" 
else:
    session_id = "latest"  

dashboard_completo = f1_ultimate_dashboard.replace(
    "const SESSION_KEY = 'latest';", 
    f"const SESSION_KEY = '{session_id}';"
).replace(
    'cargarTrazadoEstatico("AUSTRIA");',
    f'cargarTrazadoEstatico("{circuito_a_narrar.upper()}");'
)

st.components.v1.html(dashboard_completo, height=920, scrolling=True)
