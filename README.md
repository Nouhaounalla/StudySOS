# StudySOS – Guide de démarrage complet

## Structure du projet

```
studysos/
├── manage.py
├── requirements.txt
├── .env.example
├── studysos/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── users/          # Auth, profils, WebSocket, messagerie
│   ├── questions/      # Questions, réponses, matières
│   ├── sessions/       # Sessions d'aide, avis
│   ├── notifications/  # Notifications temps réel
│   └── admin_panel/    # Tableau de bord administrateur
├── templates/
│   ├── layouts/base.html
│   ├── auth/auth.html
│   ├── profile/        # profile.html, profile_info.html, tutors.html, public_profile.html
│   ├── questions/      # questions.html, question_detail.html
│   ├── sessions/       # sessions.html
│   └── admin/          # dashboard, users, questions, reports, sessions, statistics
└── static/
    ├── css/main.css
    └── js/api.js
```

---

## 1. Installation

### Créer et activer l'environnement virtuel
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Installer les dépendances
```bash
pip install -r requirements.txt
# Si Neon PostgreSQL: pip install dj-database-url
pip install dj-database-url
```

---

## 2. Configuration

### Copier et remplir le fichier .env
```bash
cp .env.example .env
```

Éditez `.env` :
```env
SECRET_KEY=votre-cle-secrete-tres-longue-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Neon PostgreSQL (remplacez avec vos vraies credentials)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/studysos?sslmode=require
```

> **Sans Neon** : laissez `DATABASE_URL` vide → SQLite sera utilisé automatiquement.

---

## 3. Base de données

```bash
python manage.py makemigrations users
python manage.py makemigrations questions
python manage.py makemigrations sessions
python manage.py makemigrations notifications
python manage.py makemigrations admin_panel
python manage.py migrate
```

### Charger les matières initiales
```bash
python manage.py loaddata apps/questions/fixtures/subjects.json
```

### Créer un superadmin
```bash
python manage.py createsuperuser
# Entrez email, username, password
# Le rôle sera automatiquement 'admin'
```

---

## 4. Lancer le serveur

### Mode développement (HTTP simple)
```bash
python manage.py runserver
```
→ http://localhost:8000

### Mode développement avec WebSocket (Daphne ASGI)
```bash
daphne -b 0.0.0.0 -p 8000 studysos.asgi:application
```
→ http://localhost:8000 (avec WebSocket actif)

---

## 5. URLs principales

| URL | Description |
|-----|-------------|
| `/` | Accueil → redirige vers profil ou auth |
| `/auth/` | Connexion / Inscription |
| `/profile/` | Mon profil |
| `/profile/complete/` | Complétion du profil |
| `/profile/<username>/` | Profil public |
| `/questions/` | Liste des questions |
| `/questions/<id>/` | Détail d'une question |
| `/tutors/` | Annuaire des tuteurs |
| `/sessions/` | Mes sessions |
| `/admin-panel/` | Tableau de bord admin |

### API REST

| Endpoint | Description |
|----------|-------------|
| `POST /api/users/register/` | Inscription |
| `POST /api/users/login/` | Connexion JWT |
| `POST /api/users/logout/` | Déconnexion |
| `GET/PATCH /api/users/profile/` | Profil utilisateur |
| `GET /api/questions/` | Liste questions |
| `POST /api/questions/` | Publier question |
| `GET /api/questions/subjects/` | Matières |
| `GET /api/sessions/` | Mes sessions |
| `POST /api/sessions/` | Réserver session |
| `GET /api/notifications/` | Mes notifications |
| `WS /ws/chat/<room>/` | WebSocket messagerie |
| `WS /ws/notifications/` | WebSocket notifs |

---

## 6. Sprints implémentés

### Sprint 1 – Gestion des utilisateurs ✅
- Inscription / Connexion avec JWT (cookies HTTP-only)
- Profil complet (photo, cover, bio, rôle)
- Changement de mot de passe
- WebSocket pour messagerie temps réel
- Déconnexion avec blacklist token

### Sprint 2 – Questions & Réponses ✅
- Publication de questions (avec option anonyme)
- Réponses + vote positif (upvote)
- Accepter une meilleure réponse
- Filtrage par matière, statut, recherche
- Marquer une question comme résolue
- Signalement de questions

### Sprint 3 – Sessions & Notifications ✅
- Réservation de sessions avec tuteurs
- Confirmation / annulation de sessions
- Système d'évaluation (rating 1–5)
- Notifications temps réel via WebSocket
- Mise à jour du score de satisfaction du tuteur

### Sprint 4 – Administration ✅
- Tableau de bord avec statistiques
- Gestion des utilisateurs (activer/désactiver/supprimer)
- Modération des questions
- Traitement des signalements
- Statistiques visuelles (graphiques)
- Annuaire des tuteurs avec recherche

---

## 7. Notes importantes

### Migrations séparées par app
Chaque app utilise un `label` différent pour éviter les conflits :
- `users` → `apps.users`
- `questions` → `apps.questions`
- `study_sessions` → `apps.sessions`
- `notifications` → `apps.notifications`
- `admin_panel` → `apps.admin_panel`

### WebSocket en développement
Sans Redis, le projet utilise `InMemoryChannelLayer`. Pour la production :
```bash
pip install channels-redis
```
Et dans `settings.py` :
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    }
}
```

### Fichiers médias
En développement, Django sert les fichiers via `MEDIA_URL`. En production, configurez un serveur de fichiers (S3, Cloudinary, etc.).

---

## 8. Dépannage rapide

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: No module named 'apps'` | Lancez depuis le dossier `studysos/` contenant `manage.py` |
| Erreur de migration | Supprimez `db.sqlite3` et relancez `migrate` |
| JWT non reconnu | Vérifiez que les cookies sont activés dans le navigateur |
| WebSocket ne se connecte pas | Utilisez `daphne` au lieu de `runserver` |
| Images ne s'affichent pas | Vérifiez `MEDIA_ROOT` et `MEDIA_URL` dans `settings.py` |
