import requests

def buscar_serie(nom_serie):
    """Busca una sèrie i retorna el seu ID de TVmaze."""
    url = "https://api.tvmaze.com/singlesearch/shows"
    params = {'q': nom_serie}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            dades = response.json()
            return dades['id'], dades['name']
    except requests.exceptions.RequestException:
        print("[!] Error de connexió amb el servidor.")
    return None, None

def obtenir_nota_capitol(show_id, temporada, capitol):
    """Obté la nota d'un capítol específic usant l'ID de la sèrie."""
    url = f"https://api.tvmaze.com/shows/{show_id}/episodebynumber"
    params = {'season': temporada, 'number': capitol}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            dades = response.json()
            # TVmaze posa la nota dins de 'rating' -> 'average'
            nota = dades.get('rating', {}).get('average')
            titol = dades.get('name')
            return nota, titol
    except requests.exceptions.RequestException:
        print("[!] Error de connexió al carregar el capítol.")
    return None, None

def obtenir_temporades(show_id):
    """Retorna una llista amb la informació de totes les temporades."""
    url = f"https://api.tvmaze.com/shows/{show_id}/seasons"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def obtenir_episodis_temporada(show_id, num_temporada):
    """Retorna la llista d'episodis d'una temporada específica."""
    url = f"https://api.tvmaze.com/shows/{show_id}/episodes"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            episodis = response.json()
            # Filtrem només els de la temporada que ens interessa
            return [e for e in episodis if e['season'] == num_temporada]
    except requests.exceptions.RequestException:
        pass
    return []

def main():
    while True:
        print("\n=== SERIES RATING FINDER (Powered by TVmaze) ===")
        nom = input("\nEntra el nom de la sèrie (o 'sortir'): ")
        
        if nom.lower() in ['sortir', 'exit', 'quit']:
            break
            
        show_id, nom_real = buscar_serie(nom)
        
        if show_id:
            temporades = obtenir_temporades(show_id)
            num_temps = len(temporades)
            print(f"\nSèrie trobada: {nom_real}")
            print(f"-> Aquesta sèrie té {num_temps} temporades.")
            
            try:
                temp = int(input(f"Tria una temporada (1-{num_temps}): "))
                
                episodis = obtenir_episodis_temporada(show_id, temp)
                num_eps = len(episodis)
                
                if num_eps > 0:
                    print(f"-> La temporada {temp} té {num_eps} capítols.")
                    cap = int(input(f"Tria un capítol (1-{num_eps}): "))
                    
                    # Busquem el capítol a la llista que ja tenim per estalviar una crida a l'API
                    dades_cap = next((e for e in episodis if e['number'] == cap), None)
                    
                    if dades_cap:
                        nota = dades_cap.get('rating', {}).get('average')
                        titol_cap = dades_cap.get('name')
                        print(f"\nResultat: S{temp:02d}E{cap:02d} - {titol_cap}")
                        print(f"NOTA: {nota if nota else 'N/A'} / 10 ⭐")
                    else:
                        print(f"[!] El capítol {cap} no existeix en aquesta temporada.")
                else:
                    print(f"[!] No s'han trobat capítols per a la temporada {temp}.")
                    
            except ValueError:
                print("[!] Error: Introdueix un número vàlid.")
        else:
            print(f"\n[!] No s'ha trobat la sèrie '{nom}'.")
        
        if input("\nVols buscar una altra? (s/n): ").lower() != 's':
            break

if __name__ == "__main__":
    main()
