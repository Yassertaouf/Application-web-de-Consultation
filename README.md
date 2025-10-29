# Farire Impression — Auth (Flask + SQLite)

Projet démarrage pour ajouter **Connexion / Inscription** à votre site.

## 1) Installation locale (Windows)

```bat
cd farire_auth_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```
Puis ouvrez http://127.0.0.1:5000/

## 2) Où mettre vos pages existantes ?
- Copiez votre HTML (GitHub Pages) dans `templates/` et adaptez-le avec les blocs Jinja2 (`{% extends "base.html" %}`, `{% block content %}{% endblock %}`).
- Mettez vos images/CSS/JS dans `static/` et remplacez les liens vers CSS/JS par `{{ url_for('static', filename='...') }}`.
- Le bouton **Se connecter** doit pointer vers `{{ url_for('login') }}`.

## 3) Déploiement (idées rapides)
- Hébergez ce projet sur un service qui supporte Python (Render, Railway, Deta Space, Fly.io, etc.).
- Ajoutez une variable d'environnement `SECRET_KEY`.
- Servez `app.py` comme l'application Flask principale.