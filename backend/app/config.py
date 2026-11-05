from pathlib import Path

# Dossier "backend" (deux niveaux au-dessus de ce fichier : app -> backend)
BASE_DIR = Path(__file__).resolve().parent.parent

# Informations générales
APP_NAME = "FindBack API"

# Base de données SQLite : un simple fichier "findback.db" dans backend/
DATABASE_URL = f"sqlite:///{BASE_DIR / 'findback.db'}"

# Dossier où seront enregistrées les photos des objets
UPLOAD_DIR = BASE_DIR / "uploads"

# Réglages de sécurité (utilisés plus tard pour la connexion)
SECRET_KEY = "changez-cette-cle-par-une-longue-phrase-secrete-et-unique"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # le jeton de connexion dure 24 heures