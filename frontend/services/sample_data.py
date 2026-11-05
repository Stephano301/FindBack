# Données d'exemple pour construire l'interface (remplacées par l'API à l'étape 4)

SAMPLE_USER = {
    "id": 1,
    "first_name": "Stéphano",
    "last_name": "Razafimandimby",
    "email": "stephano@example.com",
    "occupation": "Étudiant",
    # True pour pouvoir tester l'écran Administration (à repasser à False plus tard)
    "is_admin": True,
}

SAMPLE_CATEGORIES = [
    {"id": 1, "name": "Clés"},
    {"id": 2, "name": "Téléphone"},
    {"id": 3, "name": "Sac"},
    {"id": 4, "name": "Portefeuille"},
    {"id": 5, "name": "Documents"},
    {"id": 6, "name": "Vêtements"},
    {"id": 7, "name": "Électronique"},
    {"id": 8, "name": "Bijoux"},
    {"id": 9, "name": "Autre"},
]

SAMPLE_STATS = {
    "total_lost": 2,
    "total_found": 3,
    "total_recovered": 1,
    "pending_claims": 1,
}

_OWNER_ME = {
    "id": 1,
    "first_name": "Stéphano",
    "last_name": "Razafimandimby",
    "occupation": "Étudiant",
}
_OWNER_OTHER = {
    "id": 2,
    "first_name": "Jean",
    "last_name": "Rakoto",
    "occupation": "Étudiant",
}

# Utilisateurs affichés dans l'onglet « Utilisateurs » de l'écran admin
# (SAMPLE_USER est réutilisé tel quel : même objet, mêmes données)
SAMPLE_USERS = [
    SAMPLE_USER,
    {
        "id": 2,
        "first_name": "Jean",
        "last_name": "Rakoto",
        "email": "jean.rakoto@example.com",
        "occupation": "Étudiant",
        "is_admin": False,
    },
    {
        "id": 3,
        "first_name": "Hanta",
        "last_name": "Rasoanaivo",
        "email": "hanta.rasoa@example.com",
        "occupation": "Enseignante",
        "is_admin": False,
    },
]

SAMPLE_ITEMS = [
    {
        "id": 1,
        "kind": "lost",
        "title": "Sac à dos noir",
        "description": "Sac à dos noir avec une petite poche sur le côté.",
        "location": "Bibliothèque",
        "event_date": "2026-11-02",
        "status": "pending",
        "photo_url": None,
        "category": {"id": 3, "name": "Sac"},
        "owner": _OWNER_ME,
    },
    {
        "id": 2,
        "kind": "found",
        "title": "Clés avec porte-clé bleu",
        "description": "Trois clés attachées à un porte-clé bleu, trouvées près de la cantine.",
        "location": "Cantine",
        "event_date": "2026-11-03",
        "status": "pending",
        "photo_url": None,
        "category": {"id": 1, "name": "Clés"},
        "owner": _OWNER_OTHER,
    },
    {
        "id": 3,
        "kind": "lost",
        "title": "Téléphone Samsung",
        "description": "Téléphone Samsung noir avec une coque transparente.",
        "location": "Amphithéâtre A",
        "event_date": "2026-10-30",
        "status": "recovered",
        "photo_url": None,
        "category": {"id": 2, "name": "Téléphone"},
        "owner": _OWNER_OTHER,
    },
]

# Demandes (claims) : "item" pointe vers les MÊMES objets que SAMPLE_ITEMS,
# car l'écran admin compare par identité (c["item"] is not item).
# status possibles : "pending", "accepted", "rejected"
SAMPLE_CLAIMS = [
    {
        "id": 1,
        "status": "pending",
        "message": "Ce sont bien mes clés, il y a un petit autocollant dessus.",
        "item": SAMPLE_ITEMS[1],
        "claimant": SAMPLE_USERS[0],
    },
    {
        "id": 2,
        "status": "accepted",
        "message": "C'est mon téléphone, je peux donner le code de verrouillage.",
        "item": SAMPLE_ITEMS[2],
        "claimant": SAMPLE_USERS[2],
    },
    {
        "id": 3,
        "status": "rejected",
        "message": "Je crois avoir vu ce sac hier.",
        "item": SAMPLE_ITEMS[0],
        "claimant": SAMPLE_USERS[1],
    },
]