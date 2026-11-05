from datetime import date, datetime


def parse_date_input(text):
    """Transforme '02/11/2026' en date, ou retourne None si le format est invalide."""
    try:
        return datetime.strptime(text.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def validate_item_date(text):
    if not text.strip():
        return "Veuillez saisir la date (JJ/MM/AAAA)."
    parsed = parse_date_input(text)
    if parsed is None:
        return "Date invalide. Format attendu : JJ/MM/AAAA."
    if parsed > date.today():
        return "La date ne peut pas être dans le futur."
    return None


def validate_length(value, label, minimum, maximum):
    value = value.strip()
    if len(value) < minimum:
        return f"{label} : {minimum} caractères minimum."
    if len(value) > maximum:
        return f"{label} : {maximum} caractères maximum."
    return None