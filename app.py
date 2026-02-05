import json
import unicodedata
from pathlib import Path
import streamlit as st

# --------------------------------------------------
# Configuration générale
# --------------------------------------------------
st.set_page_config(
    page_title="UTC–Uvira | Santé & Bien-être",
    page_icon="🥤",
    layout="centered"
)

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "melanges.json"

DISCLAIMER = (
    "ℹ️ **Informations éducatives et préventives — sans se substituer à un avis médical.** "
    "Les conseils en santé naturelle sont nombreux sur les réseaux sociaux, mais souvent dispersés."
)

# --------------------------------------------------
# Compteur de visites (simple, anonyme)
# --------------------------------------------------
COUNTER_FILE = APP_DIR / "visits.json"

def count_visit() -> int:
    """
    Incrémente un compteur global dans visits.json.
    Compte 1 fois par session (piloté via st.session_state plus bas).
    """
    if COUNTER_FILE.exists():
        try:
            data = json.loads(COUNTER_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {"visits": 0}
        except Exception:
            data = {"visits": 0}
    else:
        data = {"visits": 0}

    visits = int(data.get("visits", 0)) + 1
    data["visits"] = visits

    COUNTER_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return visits

# --------------------------------------------------
# Utilitaire : normalisation des textes
# --------------------------------------------------
def normalize(text: str) -> str:
    """
    Normalise une chaîne pour comparaison robuste :
    - minuscules
    - suppression des accents
    - apostrophes typographiques → simples
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.replace("’", "'")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.strip()

# --------------------------------------------------
# Chargement sécurisé du fichier JSON
# --------------------------------------------------
@st.cache_data(ttl=1)
def load_melanges():
    if not DATA_FILE.exists():
        st.error("❌ melanges.json introuvable. Il doit être au même niveau que app.py.")
        st.stop()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            st.error("❌ melanges.json doit contenir une LISTE d’objets [ {...}, {...} ].")
            st.stop()

        # sécuriser les entrées
        cleaned = [m for m in data if isinstance(m, dict)]
        return cleaned

    except json.JSONDecodeError as e:
        st.error("❌ Erreur de format JSON dans melanges.json.")
        st.exception(e)
        st.stop()

# --------------------------------------------------
# Comptage de la visite (1 fois par session)
# --------------------------------------------------
if "visit_counted" not in st.session_state:
    st.session_state.visit_counted = True
    visits = count_visit()
else:
    # lecture simple (si le fichier existe)
    if COUNTER_FILE.exists():
        try:
            visits = json.loads(COUNTER_FILE.read_text(encoding="utf-8")).get("visits", 0)
        except Exception:
            visits = 0
    else:
        visits = 0

# --------------------------------------------------
# Données
# --------------------------------------------------
melanges = load_melanges()

# --------------------------------------------------
# Extraction et normalisation des objectifs
# --------------------------------------------------
# Map : objectif_normalisé -> libellé original
objectif_map = {}

for m in melanges:
    for obj in m.get("objectifs", []):
        if isinstance(obj, str):
            objectif_map[normalize(obj)] = obj

objectifs_affiches = sorted(objectif_map.values())

# --------------------------------------------------
# Interface
# --------------------------------------------------
st.title("UTC–Uvira | Santé & Bien-être")
st.markdown(DISCLAIMER)
st.caption(f"👥 Visites totales de la plateforme : {visits}")

if not objectifs_affiches:
    st.error("❌ Aucun objectif détecté dans melanges.json.")
    st.stop()

objectif_label = st.selectbox(
    "Indiquez votre objectif santé :",
    objectifs_affiches
)

objectif_norm = normalize(objectif_label)

# --------------------------------------------------
# Filtrage des recommandations (normalisé)
# --------------------------------------------------
recs = [
    m for m in melanges
    if any(normalize(o) == objectif_norm for o in m.get("objectifs", []))
]

# --------------------------------------------------
# Affichage des résultats
# --------------------------------------------------
st.subheader("Recommandations")

if not recs:
    st.info("Aucune recommandation disponible pour cet objectif pour le moment.")
else:
    for r in recs:
        with st.container(border=True):
            st.markdown(f"### {r.get('nom', 'Sans nom')}")

            # Ingrédients
            ingredients = r.get("ingredients", [])
            if isinstance(ingredients, str):
                ingredients = [ingredients]
            if not isinstance(ingredients, list):
                ingredients = []

            st.markdown("**Ingrédients**")
            st.write(", ".join(ingredients) if ingredients else "—")

            # Préparation
            preparation = r.get("preparation", [])
            if isinstance(preparation, str):
                preparation = [preparation]
            if not isinstance(preparation, list):
                preparation = []

            st.markdown("**Préparation**")
            if preparation:
                for i, step in enumerate(preparation, start=1):
                    st.write(f"{i}. {step}")
            else:
                st.write("—")

            # Précautions
            precautions = r.get("precautions", "")
            if isinstance(precautions, str) and precautions.strip():
                st.warning(precautions)
# visits.json (fichier initial)
# Crée un fichier visits.json dans le même dossier que app.py (app/visits.json) avec ce contenu :
{
  "visits": 0
}
