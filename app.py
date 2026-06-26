import streamlit as st

# Configuración de la página en modo vertical/ajustado
st.set_page_config(page_title="F1 Live Tracker TikTok", layout="centered")

# Ocultar los menús por defecto de Streamlit para que quede limpio en el stream
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Todo nuestro HTML, CSS y JavaScript unificado en un bloque de texto
f1_tracker_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
        }
        body {
            background-color: #00ff00; /* Fondo Croma */
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        .tiktok-container {
            width: 100vw;
            height: 100vh;
            background-color: rgba(17, 17, 17, 0.95);
            display: flex;
            flex-direction: column;
            padding: 15px;
        }
        .live-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .live-badge {
            background-color: #ff1801;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            animation: blink 1s infinite;
        }
        @keyframes blink { 50% { opacity: 0; } }
        .leaderboard-grid {
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex-grow: 1;
            overflow-y: auto;
        }
        .driver-row {
            display: flex;
            align-items: center;
            background-color: #222;
            color: white;
            padding: 6px 10px;
            border-radius: 6px;
            height: 38px;
            transition: all 0.5s ease-in-out;
        }
        .team-stripe {
            width: 6px;
            height: 100%;
            border-radius: 3px;
            margin-right: 10px;
        }
        .position-num { width: 25px; font-size: 14px; color: #aaa; }
        .driver-name { width: 50px; font-size: 16px; }
        .tyre-badge {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            color: black;
            margin-right: 12px;
        }
        .tyre-SOFT { background-color: #ff1801; color: white; }
        .tyre-MEDIUM { background-color: #fad105; }
        .tyre-HARD { background-color: #ffffff; }
        .tyre-INTERMEDIATE { background-color: #39b54a; color: white; }
        .tyre-WET { background-color: #00AEEF; color: white; }
        .car-placeholder { font-size: 16px; margin-right: 15px; }
        .driver-telemetry { margin-left: auto; font-size: 14px; color: #00ffcc; }
        .loading { color: white; text-align: center; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="tiktok-container">
        <header class="live-header">
            <div class="live-badge">LIVE</div>
            <h2 style="font-size: 16px;">TRACKER TRANSMISIÓN</h2>
            <div id="session-type" style="color: #ff1801;">F1</div>
        </header>
        <div id="leaderboard" class="leaderboard-grid">
            <div class="loading">Conectando con OpenF1...</div>
        </div>
    </div>

    <script>
        const SESSION_KEY = 'latest'; // Intentará jalar la última sesión registrada en el servidor automáticamente
        const API_URL = 'https://api.openf1.org/v1';
        let driversDatabase = {};

        async function initTracker() {
            try {
                const res = await fetch(`${API_URL}/drivers?session_key=${SESSION_KEY}`);
                const drivers = await res.json();
                drivers.forEach(d => {
                    driversDatabase[d.driver_number] = {
                        name: d.name_acronym,
                        teamColor: d.team_colour ? `#${d.team_colour}` : '#ffffff'
                    };
                });
                fetchRealTimeData();
                setInterval(fetchRealTimeData, 2000);
            } catch (err) {
                document.getElementById('leaderboard').innerHTML = "<div class='loading'>Error OpenF1</div>";
            }
        }

        async function fetchRealTimeData() {
            try {
                const [posRes, stintRes] = await Promise.all([
                    fetch(`${API_URL}/position?session_key=${SESSION_KEY}`),
                    fetch(`${API_URL}/stints?session_key=${SESSION_KEY}`)
                ]);
                const positionData = await posRes.json();
                const stintData = await stintRes.json();

                const latestPositions = {};
                positionData.forEach(p => { latestPositions[p.driver_number] = p.position; });

                const latestTyres = {};
                stintData.forEach(s => { latestTyres[s.driver_number] = s.compound; });

                const leaderboardArray = Object.keys(latestPositions).map(driverNum => {
                    return {
                        number: driverNum,
                        position: latestPositions[driverNum],
                        compound: latestTyres[driverNum] || 'UNKNOWN',
                        info: driversDatabase[driverNum] || { name: 'UNK', teamColor: '#555' }
                    };
                }).sort((a, b) => a.position - b.position);

                renderLeaderboard(leaderboardArray);
            } catch (err) { console.warn(err); }
        }

        function renderLeaderboard(driversList) {
            const container = document.getElementById('leaderboard');
            container.innerHTML = '';
            driversList.forEach(driver => {
                const tyreLetter = driver.compound !== 'UNKNOWN' ? driver.compound.charAt(0) : '?';
                const row = document.createElement('div');
                row.className = 'driver-row';
                row.innerHTML = `
                    <div class="team-stripe" style="background-color: ${driver.info.teamColor}"></div>
                    <div class="position-num">${driver.position}</div>
                    <div class="tyre-badge tyre-${driver.compound}">${tyreLetter}</div>
                    <div class="car-placeholder">🏎️</div>
                    <div class="driver-name">${driver.info.name}</div>
                    <div class="driver-telemetry"><span>P${driver.number}</span></div>
                `;
                container.appendChild(row);
            });
        }
        window.onload = initTracker;
    </script>
</body>
</html>
"""
# Cambia 'scroller' por 'scrolling'
st.components.v1.html(f1_tracker_html, width=400, height=750, scrolling=False)
