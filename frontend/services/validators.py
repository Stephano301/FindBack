import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email):
    if not email:
        return "Veuillez saisir votre adresse e-mail."
    if not EMAIL_PATTERN.match(email):
        return "Adresse e-mail invalide."
    return None


def validate_name(value, label):
    value = value.strip()
    if len(value) < 2:
        return f"{label} : 2 caractères minimum."
    if len(value) > 50:
        return f"{label} : 50 caractères maximum."
    return None


def validate_password(password):
    """Règles d'un nouveau mot de passe (identiques à celles du backend)."""
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères."
    if len(password) > 64 or len(password.encode("utf-8")) > 72:
        return "Le mot de passe est trop long."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return "Le mot de passe doit contenir au moins une lettre et un chiffre."
    return None
