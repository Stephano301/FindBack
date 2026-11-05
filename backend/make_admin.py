"""Donne les droits d'administrateur à un utilisateur existant.

Utilisation (depuis le dossier backend) :
    python make_admin.py adresse@email.com
"""

import sys

from app.database import SessionLocal
from app.models import User


def main() -> None:
    if len(sys.argv) != 2:
        print("Utilisation : python make_admin.py adresse@email.com")
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"Aucun utilisateur avec l'e-mail : {email}")
            sys.exit(1)

        user.is_admin = True
        db.commit()
        print(
            f"{user.first_name} {user.last_name} ({user.email}) "
            "est maintenant administrateur."
        )


if __name__ == "__main__":
    main()