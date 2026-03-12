from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# --- Lògica de l'API ---
def buscar_serie(nom):
    res = requests.get("https://api.tvmaze.com/singlesearch/shows", params={'q': nom})
    return res.json() if res.status_code == 200 else None

def suggerir_series(query):
    """Busca múltiples sèries que coincideixin amb el text."""
    res = requests.get("https://api.tvmaze.com/search/shows", params={'q': query})
    if res.status_code == 200:
        return [item['show'] for item in res.json()]
    return []

def obtenir_temporades(show_id):
    res = requests.get(f"https://api.tvmaze.com/shows/{show_id}/seasons")
    return res.json() if res.status_code == 200 else []

def obtenir_episodis(show_id, num_temp):
    res = requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodes")
    if res.status_code == 200:
        return [e for e in res.json() if e['season'] == int(num_temp)]
    return []

# --- Interfície HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <title>Series Rating Finder Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #e50914; /* Roig Netflix */
            --bg-color: #0f0f0f;
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-color: #ffffff;
        }

        body { 
            background: radial-gradient(circle at top, #1e1e1e 0%, var(--bg-color) 100%);
            color: var(--text-color);
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            padding: 40px 0;
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
        }

        h2 { font-weight: 800; letter-spacing: -1px; color: var(--primary-color); }

        .form-control, .form-select {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 10px;
            padding: 12px;
        }

        .form-control:focus, .form-select:focus {
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border-color: var(--primary-color);
            box-shadow: 0 0 10px rgba(229, 9, 20, 0.3);
        }

        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 12px 25px;
            transition: all 0.3s;
        }

        .btn-primary:hover {
            background-color: #ff0f1a;
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
        }

        #poster-img {
            width: 100%;
            max-width: 250px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.6);
            margin-bottom: 20px;
            animation: fadeIn 1s ease;
        }

        .summary-text {
            font-size: 0.9rem;
            opacity: 0.8;
            line-height: 1.5;
            margin: 20px 0;
            text-align: justify;
        }

        .cast-container {
            display: flex;
            overflow-x: auto;
            gap: 15px;
            padding: 10px 5px;
            scrollbar-width: none;
        }
        .cast-container::-webkit-scrollbar { display: none; }

        .cast-item {
            flex: 0 0 80px;
            text-align: center;
        }
        .cast-img {
            width: 65px;
            height: 65px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid rgba(229, 9, 20, 0.4);
            margin-bottom: 5px;
        }
        .cast-name {
            font-size: 0.7rem;
            display: block;
            line-height: 1.1;
        }

        .rating-display {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(45deg, #f39c12, #f1c40f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 20px rgba(243, 156, 18, 0.2);
        }

        /* Estils Autocompletat */
        #search-container { position: relative; }
        #suggestions-list {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #1a1a1a;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 0 0 10px 10px;
            z-index: 1000;
            max-height: 250px;
            overflow-y: auto;
            display: none;
        }
        .suggestion-item {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            transition: background 0.2s;
            display: flex;
            align-items: center;
            text-align: left;
        }
        .suggestion-item:hover { background: rgba(229, 9, 20, 0.2); }
        .suggestion-item img { width: 30px; height: 40px; object-fit: cover; border-radius: 3px; margin-right: 12px; }
        .suggestion-year { font-size: 0.8rem; opacity: 0.5; margin-left: auto; }

        .fade-in { animation: fadeIn 0.5s ease forwards; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        label { font-weight: 300; font-size: 0.9rem; opacity: 0.8; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center align-items-center">
            <!-- Columna Esquerra: Info Sèrie -->
            <div id="col_info" class="col-md-5 text-center d-none mb-4 mb-md-0">
                <img id="poster-img" src="" alt="Poster">
                <h3 id="nom_real_serie" class="mt-2 mb-0"></h3>
                <div id="sinopsis" class="summary-text px-3"></div>
                
                <div class="px-3 text-start">
                    <p class="text-uppercase mb-2" style="font-size: 0.65rem; letter-spacing: 1px; opacity: 0.5; font-weight: 600;">Repartiment</p>
                    <div id="cast_list" class="cast-container"></div>
                </div>
            </div>

            <!-- Columna Dreta: Controls -->
            <div class="col-md-6">
                <div class="glass-card">
                    <h2 class="text-center mb-4">SERIES RATING</h2>
                    
                    <div class="mb-4">
                        <label>BUSCAR SÈRIE</label>
                        <div id="search-container">
                            <div class="input-group">
                                <input type="text" id="nom_serie" class="form-control" 
                                       placeholder="Escriu per buscar..." autocomplete="off"
                                       oninput="handleInput(this.value)">
                                <button onclick="buscar()" class="btn btn-primary">BUSCAR</button>
                            </div>
                            <div id="suggestions-list"></div>
                        </div>
                    </div>

                    <div id="seccio_temps" class="mb-3 d-none fade-in">
                        <label>TRIA TEMPORADA</label>
                        <select id="select_temp" class="form-select" onchange="carregarEpisodis()"></select>
                    </div>

                    <div id="seccio_eps" class="mb-3 d-none fade-in">
                        <label>TRIA CAPÍTOL</label>
                        <select id="select_ep" class="form-select" onchange="mostrarResultat()"></select>
                    </div>

                    <div id="resultat" class="mt-5 text-center d-none fade-in">
                        <p class="text-uppercase mb-1" style="letter-spacing: 2px; opacity: 0.6;">Valoració TVmaze</p>
                        <h4 id="titol_cap" class="mb-3"></h4>
                        <div class="rating-display" id="nota_cap"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentShowId = null;
        let episodesData = [];
        let timer;

        function handleInput(val) {
            clearTimeout(timer);
            if (val.length < 2) {
                document.getElementById('suggestions-list').style.display = 'none';
                return;
            }
            timer = setTimeout(() => fetchSuggestions(val), 300);
        }

        async function fetchSuggestions(query) {
            const res = await fetch(`/api/suggest?q=${query}`);
            const shows = await res.json();
            
            const list = document.getElementById('suggestions-list');
            if (shows.length > 0) {
                let html = '';
                shows.forEach(s => {
                    const img = s.image ? s.image.medium : 'https://via.placeholder.com/30x40?text=?';
                    const year = s.premiered ? s.premiered.split('-')[0] : 'N/A';
                    html += `
                        <div class="suggestion-item" onclick="seleccionarSerie(${s.id}, '${s.name.replace(/'/g, "\\'")}')">
                            <img src="${img}">
                            <span>${s.name}</span>
                            <span class="suggestion-year">${year}</span>
                        </div>`;
                });
                list.innerHTML = html;
                list.style.display = 'block';
            } else {
                list.style.display = 'none';
            }
        }

        async function seleccionarSerie(id, nom) {
            document.getElementById('nom_serie').value = nom;
            document.getElementById('suggestions-list').style.display = 'none';
            
            const res = await fetch(`/api/show/${id}`);
            const data = await res.json();
            mostrarDadesSerie(data);
        }

        async function buscar() {
            const nom = document.getElementById('nom_serie').value;
            const res = await fetch(`/api/search?q=${nom}`);
            const data = await res.json();
            if (data) mostrarDadesSerie(data);
            else alert("No s'ha trobat la sèrie");
        }

        async function mostrarDadesSerie(data) {
            currentShowId = data.id;
            document.getElementById('nom_real_serie').innerText = data.name;
            document.getElementById('poster-img').src = data.image ? data.image.medium : 'https://via.placeholder.com/210x295?text=Sense+Poster';
            
            // Sinopsis (ve amb HTML de l'API)
            document.getElementById('sinopsis').innerHTML = data.summary || "No hi ha resum disponible.";
            
            document.getElementById('col_info').classList.remove('d-none');
            document.getElementById('col_info').classList.add('fade-in');

            // Carregar Repartiment (Cast)
            const resC = await fetch(`/api/cast/${data.id}`);
            const cast = await resC.json();
            let castHtml = '';
            cast.slice(0, 8).forEach(c => {
                const pImg = c.person.image ? c.person.image.medium : 'https://via.placeholder.com/100x100?text=?';
                castHtml += `
                    <div class="cast-item">
                        <img src="${pImg}" class="cast-img">
                        <span class="cast-name">${c.person.name}</span>
                    </div>`;
            });
            document.getElementById('cast_list').innerHTML = castHtml;

            const resT = await fetch(`/api/seasons/${data.id}`);
            const seasons = await resT.json();
            
            let html = '<option value="">Selecciona...</option>';
            seasons.forEach(s => html += `<option value="${s.number}">Temporada ${s.number}</option>`);
            
            document.getElementById('select_temp').innerHTML = html;
            document.getElementById('seccio_temps').classList.remove('d-none');
            document.getElementById('seccio_eps').classList.add('d-none');
            document.getElementById('resultat').classList.add('d-none');
        }

        async function carregarEpisodis() {
            const temp = document.getElementById('select_temp').value;
            if (!temp) return;

            const res = await fetch(`/api/episodes/${currentShowId}/${temp}`);
            episodesData = await res.json();
            
            let html = '<option value="">Selecciona...</option>';
            episodesData.forEach((e, idx) => html += `<option value="${idx}">E${e.number}: ${e.name}</option>`);
            
            document.getElementById('select_ep').innerHTML = html;
            document.getElementById('seccio_eps').classList.remove('d-none');
        }

        function mostrarResultat() {
            const idx = document.getElementById('select_ep').value;
            if (idx === "") return;

            const ep = episodesData[idx];
            document.getElementById('titol_cap').innerText = ep.name;
            const nota = ep.rating.average;
            document.getElementById('nota_cap').innerText = nota ? nota + " ⭐" : "N/A";
            document.getElementById('resultat').classList.remove('d-none');
        }

        // Tancar suggeriments si cliquem fora
        document.addEventListener('click', (e) => {
            if (!document.getElementById('search-container').contains(e.target)) {
                document.getElementById('suggestions-list').style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

# --- Rutes del Servidor ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    return jsonify(buscar_serie(request.args.get('q')))

@app.route('/api/suggest')
def api_suggest():
    return jsonify(suggerir_series(request.args.get('q')))

@app.route('/api/show/<show_id>')
def api_show(show_id):
    res = requests.get(f"https://api.tvmaze.com/shows/{show_id}")
    return jsonify(res.json()) if res.status_code == 200 else jsonify({})

@app.route('/api/cast/<show_id>')
def api_cast(show_id):
    res = requests.get(f"https://api.tvmaze.com/shows/{show_id}/cast")
    return jsonify(res.json()) if res.status_code == 200 else jsonify([])

@app.route('/api/seasons/<show_id>')
def api_seasons(show_id):
    return jsonify(obtenir_temporades(show_id))

@app.route('/api/episodes/<show_id>/<temp>')
def api_episodes(show_id, temp):
    return jsonify(obtenir_episodis(show_id, temp))

if __name__ == '__main__':
    # Mode debug i port 5000 (estàndard de Flask)
    app.run(host='0.0.0.0', port=5000, debug=True)
