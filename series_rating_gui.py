import tkinter as tk
from tkinter import messagebox, ttk
import requests

class SeriesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Series Rating Finder")
        self.root.geometry("450x550")
        self.root.configure(padx=20, pady=20)

        # Variables de control
        self.show_id = None
        self.temporades_data = []
        self.episodis_data = []

        # --- Estils ---
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Result.TLabel", font=("Arial", 12, "bold"), foreground="#2c3e50")

        # --- Interfície ---
        ttk.Label(root, text="Buscador de Sèries", style="Header.TLabel").pack(pady=(0, 20))

        # Cercador
        search_frame = ttk.Frame(root)
        search_frame.pack(fill="x", pady=5)
        ttk.Label(search_frame, text="Nom de la sèrie:").pack(side="left")
        self.entry_nom = ttk.Entry(search_frame)
        self.entry_nom.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_buscar = ttk.Button(search_frame, text="Buscar", command=self.buscar_serie)
        self.btn_buscar.pack(side="left")

        # Info Sèrie
        self.lbl_serie_trobada = ttk.Label(root, text="", font=("Arial", 10, "italic"))
        self.lbl_serie_trobada.pack(pady=5)

        # Selecció Temporada
        self.lbl_temp = ttk.Label(root, text="Selecciona Temporada:")
        self.lbl_temp.pack(pady=(15, 0), anchor="w")
        self.combo_temp = ttk.Combobox(root, state="readonly")
        self.combo_temp.pack(fill="x", pady=5)
        self.combo_temp.bind("<<ComboboxSelected>>", self.carregar_episodis)

        # Selecció Episodi
        self.lbl_ep = ttk.Label(root, text="Selecciona Episodi:")
        self.lbl_ep.pack(pady=(10, 0), anchor="w")
        self.combo_ep = ttk.Combobox(root, state="readonly")
        self.combo_ep.pack(fill="x", pady=5)
        self.combo_ep.bind("<<ComboboxSelected>>", self.mostrar_resultat)

        # Resultat
        self.res_frame = ttk.LabelFrame(root, text=" Resultat ", padding=15)
        self.res_frame.pack(fill="both", expand=True, pady=20)
        
        self.lbl_titol_cap = ttk.Label(self.res_frame, text="", wraplength=350, justify="center")
        self.lbl_titol_cap.pack(pady=5)
        
        self.lbl_nota = ttk.Label(self.res_frame, text="", style="Result.TLabel")
        self.lbl_nota.pack(pady=5)

    def buscar_serie(self):
        nom = self.entry_nom.get()
        if not nom: return

        url = "https://api.tvmaze.com/singlesearch/shows"
        try:
            res = requests.get(url, params={'q': nom}, timeout=10)
            if res.status_code == 200:
                dades = res.json()
                self.show_id = dades['id']
                self.lbl_serie_trobada.config(text=f"Sèrie: {dades['name']}", foreground="green")
                self.carregar_temporades()
            else:
                messagebox.showerror("Error", "No s'ha trobat la sèrie.")
        except:
            messagebox.showerror("Error", "Error de connexió.")

    def carregar_temporades(self):
        url = f"https://api.tvmaze.com/shows/{self.show_id}/seasons"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                self.temporades_data = res.json()
                noms_temps = [f"Temporada {t['number']}" for t in self.temporades_data]
                self.combo_temp['values'] = noms_temps
                self.combo_temp.set("")
                self.combo_ep['values'] = []
                self.combo_ep.set("")
                self.netejar_resultat()
        except: pass

    def carregar_episodis(self, event=None):
        num_temp = self.combo_temp.current() + 1
        url = f"https://api.tvmaze.com/shows/{self.show_id}/episodes"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                tots = res.json()
                self.episodis_data = [e for e in tots if e['season'] == num_temp]
                noms_eps = [f"E{e['number']:02d}: {e['name']}" for e in self.episodis_data]
                self.combo_ep['values'] = noms_eps
                self.combo_ep.set("")
                self.netejar_resultat()
        except: pass

    def mostrar_resultat(self, event=None):
        idx = self.combo_ep.current()
        if idx < 0: return
        
        ep = self.episodis_data[idx]
        nota = ep.get('rating', {}).get('average')
        titol = ep.get('name')
        
        self.lbl_titol_cap.config(text=f"Capítol: {titol}")
        if nota:
            self.lbl_nota.config(text=f"NOTA: {nota} / 10 ⭐", foreground="#2c3e50")
        else:
            self.lbl_nota.config(text="NOTA: No disponible", foreground="grey")

    def netejar_resultat(self):
        self.lbl_titol_cap.config(text="")
        self.lbl_nota.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = SeriesApp(root)
    root.mainloop()
