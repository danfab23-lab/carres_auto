import streamlit as st

# Configuración obligatoria para Pantalla Completa en Escritorio
st.set_page_config(page_title="F1 Team Command Center", layout="wide")

# Limpieza total del entorno Streamlit para que parezca una app nativa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; max-width: 100vw !important;}
    iframe {border: none; width: 100% !important; height: 100vh !important;}
    </style>
""", unsafe_allow_html=True)

f1_desktop_dashboard = """
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
            padding: 15px;
        }
        /* Contenedor Principal en Grid Horizontal (Pantallas anchas) */
        .dashboard-container {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 20px;
            height: calc(100vh - 30px);
        }
        
        /* PANALES IZQUIERDO Y DERECHO */
        .panel {
            background-color: #1f2833;
            border-radius: 10px;
            border: 1px solid #45f3ff33;
            padding: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #2f3e46;
            padding-bottom: 10px;
            margin-bottom: 12px;
        }
        .live-indicator {
            background-color: #ff1801;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            text-transform: uppercase;
        }

        /* TABLA DE POSICIONES EXTENDIDA */
        .table-wrapper {
            overflow-y: auto;
            flex-grow: 1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }
        th {
            background-color: #0b0c10;
            color: #45f3ff;
            padding: 10px;
            position: sticky;
            top: 0;
        }
        tr {
            border-bottom: 1px solid #2f3e46;
            height: 40px;
            transition: background-color 0.2s;
        }
        tr:hover { background-color: #2b3a4a; }
        td { padding: 5px 10px; }

        /* Estilos de datos específicos */
        .stripe { width: 5px; padding: 0; height: 100%; }
        .pos { font-size: 16px; color: #45f3ff; text-align: center; }
        .change { font-weight: bold; text-align: center; }
        .up { color: #00ff88; }
        .down { color: #ff3838; }
        .same { color: #777; }
        
        .tyre {
            width: 22px; height: 22px; border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 11px; color: #000;
        }
        .tyre-SOFT { background-color: #ff1801; color: #fff; }
        .tyre-MEDIUM { background-color: #fad105; }
        .tyre-HARD { background-color: #ffffff; }
        .tyre-INTERMEDIATE { background-color: #39b54a; color: #fff; }
        .tyre-WET { background-color: #00AEEF; color: #fff; }
        
        .telemetry-txt { color: #00ffcc; font-family: monospace; }

        /* SECCIÓN DEL MAPA */
        .map-wrapper {
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            background-color: #0b0c10;
            border-radius: 6px;
        }
        canvas {
            max-width: 100%;
            max-height: 100%;
        }
    </style>
</head>
<body>

    <div class="dashboard-container">
        <div class="panel">
            <header>
                <h2>TELEMETRY & TIMING</h2>
                <div class="live-indicator">Mesa de Ingeniería</div>
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
                            <th>LLANTA</th>
                            <th>VELOCIDAD</th>
                            <th>RPM</th>
                            <th>MARCHA</th>
                        </tr>
                    </thead>
                    <tbody id="telemetry-table-body">
                        </tbody>
                </table>
            </div>
        </div>

        <div class="panel">
            <header>
                <h2>GPS LIVE TRACK MAP</h2>
                <div id="circuit-name" style="color: #45f3ff;">DIBUJANDO TRAZADO...</div>
            </header>
            <div class="map-wrapper">
                <canvas id="trackMap" width="600" height="600"></canvas>
            </div>
        </div>
    </div>

    <script>
        const SESSION_KEY = 'latest'; // Cambia por IDs específicos en pruebas si está offline
        const API_URL = 'https://api.openf1.org/v1';
        
        let drivers = {};
        let positionHistory = {}; // Para calcular el cambio de posición (+/-)
        let circuitLoaded = false;
        
        // Almacenes de mapeo de coordenadas
        let trackPoints = []; 
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

        async function init() {
            try {
                // Descargar datos fijos de los pilotos
                const res = await fetch(`${API_URL}/drivers?session_key=${SESSION_KEY}`);
                const data = await res.json();
                data.forEach(d => {
                    drivers[d.driver_number] = {
                        name: d.name_acronym,
                        color: d.team_colour ? `#${d.team_colour}` : '#ffffff',
                        number: d.driver_number,
                        pos: 0,
                        change: '-',
                        tyre: 'UNKNOWN',
                        speed: 0,
                        rpm: 0,
                        gear: 0,
                        x: 0, y: 0
                    };
                });

                // Carga inicial y bucle en vivo cada 1.5 segundos
                tick();
                setInterval(tick, 1500);
            } catch (e) { console.error("Error al arrancar telemetría:", e); }
        }

        async function tick() {
            try {
                // Hacer las peticiones simultáneas de Posición, Neumáticos, Datos del coche y Localización GPS
                const [posRes, stintRes, carRes, locRes] = await Promise.all([
                    fetch(`${API_URL}/position?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/stints?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/car_data?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/location?session_key=${SESSION_KEY}`)
                ]);

                const positions = await posRes.json();
                const stints = await stintRes.json();
                const cars = await carRes.json();
                const locations = await locRes.json();

                // 1. Procesar Cambios de Posición (+/-)
                positions.forEach(p => {
                    let d = drivers[p.driver_number];
                    if (d) {
                        if (positionHistory[p.driver_number] !== undefined && positionHistory[p.driver_number] !== p.position) {
                            let diff = positionHistory[p.driver_number] - p.position; // Viejo - Nuevo
                            d.change = diff > 0 ? `+${diff}` : `${diff}`;
                        }
                        d.pos = p.position;
                        positionHistory[p.driver_number] = p.position;
                    }
                });

                // 2. Procesar Compuestos (Llantas)
                stints.forEach(s => { if(drivers[s.driver_number]) drivers[s.driver_number].tyre = s.compound; });

                // 3. Procesar Telemetría del motor (Velocidad instantánea)
                // Tomamos las últimas muestras leyendo el arreglo al revés para optimizar
                cars.forEach(c => {
                    let d = drivers[c.driver_number];
                    if(d) { d.speed = c.speed; d.rpm = c.rpm; d.gear = c.gear; }
                });

                // 4. Procesar Ubicaciones GPS (Coordenadas X, Y)
                locations.forEach(l => {
                    let d = drivers[l.driver_number];
                    if(d) {
                        d.x = l.x; d.y = l.y;
                        // Si no hemos mapeado el circuito, acumulamos coordenadas para calibrar el Canvas
                        if (!circuitLoaded && l.x && l.y) {
                            trackPoints.push({x: l.x, y: l.y});
                            if (l.x < minX) minX = l.x; if (l.x > maxX) maxX = l.x;
                            if (l.y < minY) minY = l.y; if (l.y > maxY) maxY = l.y;
                        }
                    }
                });

                if (trackPoints.length > 500) { circuitLoaded = true; document.getElementById('circuit-name').innerText = "CIRCUITO MAPS OK"; }

                renderTable();
                drawMap();

            } catch (e) { console.warn("Sincronizando flujo...", e); }
        }

        function renderTable() {
            const tbody = document.getElementById('telemetry-table-body');
            // Filtrar y ordenar pilotos que tengan posición asignada
            const list = Object.values(drivers).filter(d => d.pos > 0).sort((a,b) => a.pos - b.pos);
            
            let html = '';
            list.forEach(d => {
                let changeClass = 'same';
                if (d.change.startsWith('+')) changeClass = 'up';
                else if (d.change.startsWith('-') && d.change !== '-') changeClass = 'down';

                let tLetter = d.tyre !== 'UNKNOWN' ? d.tyre.charAt(0) : '?';

                html += `<tr>
                    <td class="stripe" style="background-color: ${d.color}"></td>
                    <td class="pos">${d.pos}</td>
                    <td class="change ${changeClass}">${d.change}</td>
                    <td>${d.name}</td>
                    <td style="color:#aaa;">#${d.number}</td>
                    <td><span class="tyre tyre-${d.tyre}">${tLetter}</span></td>
                    <td class="telemetry-txt">${d.speed} km/h</td>
                    <td class="telemetry-txt" style="color:#888;">${d.rpm}</td>
                    <td class="telemetry-txt" style="text-align:center;">${d.gear}</td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        function drawMap() {
            const canvas = document.getElementById('trackMap');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (trackPoints.length === 0) return;

            // Función para escalar los puntos cartesianos de la F1 al tamaño del Canvas del navegador
            const padding = 40;
            const scaleX = (canvas.width - padding * 2) / (maxX - minX || 1);
            const scaleY = (canvas.height - padding * 2) / (maxY - minY || 1);
            const scale = Math.min(scaleX, scaleY); // Mantener la proporción geométrica perfecta del circuito

            const toCanvasX = (x) => padding + (x - minX) * scale;
            // Invertir Y para que las curvas vayan hacia el lado correcto (F1 usa el estándar de ingeniería)
            const toCanvasY = (y) => canvas.height - padding - (y - minY) * scale;

            // 1. Dibujar la línea gris del circuito
            ctx.strokeStyle = '#334455';
            ctx.lineWidth = 4;
            ctx.beginPath();
            // Para no pintar miles de puntos, tomamos muestras espaciadas si estamos cargando
            for(let i=0; i<trackPoints.length; i+=5) {
                let pt = trackPoints[i];
                if(i===0) ctx.moveTo(toCanvasX(pt.x), toCanvasY(pt.y));
                else ctx.lineTo(toCanvasX(pt.x), toCanvasY(pt.y));
            }
            ctx.closePath();
            ctx.stroke();

            // 2. Dibujar las burbujas de los pilotos sobre el circuito
            Object.values(drivers).forEach(d => {
                if (d.x && d.y && d.pos > 0) {
                    const cx = toCanvasX(d.x);
                    const cy = toCanvasY(d.y);

                    // Círculo exterior con el color de su equipo
                    ctx.fillStyle = d.color;
                    ctx.beginPath();
                    ctx.arc(cx, cy, 9, 0, 2 * Math.PI);
                    ctx.fill();

                    // Núcleo negro
                    ctx.fillStyle = '#000000';
                    ctx.beginPath();
                    ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
                    ctx.fill();

                    // Siglas del piloto en texto flotante al lado
                    ctx.fillStyle = '#ffffff';
                    ctx.font = '10px monospace';
                    ctx.fillText(d.name, cx + 12, cy + 3);
                }
            });
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Inyectamos el Dashboard en formato completo de pantalla horizontal
st.components.v1.html(f1_desktop_dashboard, scrolling=False)
