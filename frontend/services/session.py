class Session:
    """Garde en mémoire le jeton et l'utilisateur connecté."""

    def __init__(self):
        self.token = None
        self.user = None

    @property
    def is_logged_in(self):
        return self.token is not None and self.user is not None

    def set(self, token, user):
        self.token = token
        self.user = user

    def update_user(self, user):
        self.user = user

    def clear(self):
        self.token = None
        self.user = None


# Une seule session, partagée par toute l'application
session = Session()