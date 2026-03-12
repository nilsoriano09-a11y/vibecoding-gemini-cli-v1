# Series Rating Finder (TVmaze Edition) 🎬⭐

Aquest projecte és una eina multi-plataforma per consultar les valoracions (ratings) d'episodis de sèries de televisió, utilitzant l'API pública de **TVmaze**. Permet cercar qualsevol sèrie, navegar per les seves temporades i veure la nota mitjana de cada capítol.

## 📂 Estructura del Projecte

El projecte consta de tres interfícies diferents:

1.  **`series_rating.py` (CLI)**: Versió per a terminal.
2.  **`series_rating_gui.py` (Desktop)**: Versió d'escriptori amb `tkinter`.
3.  **`series_rating_web.py` (Web)**: Versió web moderna construïda amb `Flask` i `Bootstrap 5`.

## 🚀 Requisits

```bash
pip install requests flask
```

## 🛠️ Ús

- **CLI**: `python series_rating.py`
- **Desktop**: `python series_rating_gui.py`
- **Web**: `python series_rating_web.py` (i obre http://localhost:5000)

## 🌐 API
Utilitza l'API de [TVmaze](https://www.tvmaze.com/api).
