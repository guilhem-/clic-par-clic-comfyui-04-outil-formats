"""Installer l'outil « Atelier d'images » et le modèle du même nom dans Open WebUI, par son API.

Fait ce que le module 4 de la série « Générer des images dans Open WebUI avec ComfyUI » fait à
l'écran, dans l'espace de travail :
  1. crée (ou met à jour) l'outil atelier_images avec le code de open-webui/atelier_images.py,
     ouvert à tous les utilisateurs ;
  2. règle sa vanne : variantes_max = 3 ;
  3. crée (ou met à jour) le modèle atelier-d-images : modèle de base, consignes
     (open-webui/consignes-atelier.txt), outil coché, ouvert à tous les utilisateurs.
La page Images (workflow, correspondance, modèle d'image) n'est pas touchée : l'outil utilise celle
du serveur d'images de l'organisation (modules 1 et 2).

Usage :
  python installer_atelier.py              # installe ou met à jour l'outil et le modèle
  python installer_atelier.py --verifier   # contrôle : outil, schéma lu par le modèle, vanne, modèle
  python installer_atelier.py --retirer    # supprime le modèle puis l'outil

Réglages : fichier .env (voir .env.example) ; les variables d'environnement l'emportent.
Aucune dépendance : Python 3.10 ou plus récent, bibliothèque standard seulement.
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent
CODE = ICI / "open-webui" / "atelier_images.py"
CONSIGNES = ICI / "open-webui" / "consignes-atelier.txt"
VARIABLES = ("OWUI_URL", "OWUI_JETON", "MODELE_BASE", "VARIANTES_MAX")

OUTIL = {"id": "atelier_images", "nom": "Atelier d'images"}
MODELE = {"id": "atelier-d-images", "nom": "Atelier d'images"}
# Ouverts à tous les utilisateurs (lecture) : un utilisateur ne peut se servir que d'un outil
# auquel il a accès. À réserver à un groupe au module 5.
PUBLIC = [{"principal_type": "user", "principal_id": "*", "permission": "read"}]


def reglages() -> dict:
    """Valeurs par défaut, puis .env (clé=valeur), puis l'environnement, qui l'emporte."""
    r = {"OWUI_URL": "http://127.0.0.1:8080", "VARIANTES_MAX": "3"}
    env = ICI / ".env"
    if env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#") and "=" in ligne:
                cle, valeur = ligne.split("=", 1)
                r[cle.strip()] = valeur.strip()
    for cle in VARIABLES:
        if os.environ.get(cle):
            r[cle] = os.environ[cle]
    return r


R = reglages()


def api(methode: str, chemin: str, corps=None, tolerer=False):
    """Appel de l'API d'Open WebUI avec le jeton d'un administrateur."""
    if not R.get("OWUI_JETON"):
        sys.exit("OWUI_JETON manquant (.env) : jeton d'un compte administrateur d'Open WebUI.")
    donnees = None if corps is None else json.dumps(corps).encode()
    req = urllib.request.Request(
        R["OWUI_URL"].rstrip("/") + chemin, data=donnees, method=methode,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {R['OWUI_JETON']}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as rep:
            texte = rep.read().decode()
    except urllib.error.HTTPError as e:
        if tolerer:
            return None
        sys.exit(f"{methode} {chemin} : {e.code} {e.read().decode()[:300]}")
    return json.loads(texte) if texte.strip() else None


def installer() -> None:
    if not R.get("MODELE_BASE"):
        sys.exit("MODELE_BASE manquant (.env) : identifiant du modèle de conversation (capable d'appeler des outils).")
    code = CODE.read_text(encoding="utf-8")
    outil = {"id": OUTIL["id"], "name": OUTIL["nom"], "content": code, "meta": {"description": "", "manifest": {}}, "access_grants": PUBLIC}
    if api("GET", f"/api/v1/tools/id/{OUTIL['id']}", tolerer=True):
        api("POST", f"/api/v1/tools/id/{OUTIL['id']}/update", outil)
        print(f"Outil {OUTIL['id']} mis à jour.")
    else:
        api("POST", "/api/v1/tools/create", outil)
        print(f"Outil {OUTIL['id']} créé.")
    api("POST", f"/api/v1/tools/id/{OUTIL['id']}/valves/update", {"variantes_max": int(R["VARIANTES_MAX"])})
    print(f"Vanne variantes_max = {R['VARIANTES_MAX']}.")

    modele = {
        "id": MODELE["id"], "name": MODELE["nom"], "base_model_id": R["MODELE_BASE"],
        "meta": {"profile_image_url": "/static/favicon.png", "description": "Visuels aux formats de l'organisation", "toolIds": [OUTIL["id"]]},
        "params": {"system": CONSIGNES.read_text(encoding="utf-8").strip()},
        "access_grants": PUBLIC,
    }
    if api("GET", f"/api/v1/models/model?id={MODELE['id']}", tolerer=True):
        api("POST", "/api/v1/models/model/update", modele)
        print(f"Modèle {MODELE['id']} mis à jour.")
    else:
        api("POST", "/api/v1/models/create", modele)
        print(f"Modèle {MODELE['id']} créé (base : {R['MODELE_BASE']}).")


def verifier() -> None:
    outil = api("GET", f"/api/v1/tools/id/{OUTIL['id']}", tolerer=True)
    if not outil:
        sys.exit(f"Outil {OUTIL['id']} absent.")
    specs = {s["name"]: s for s in outil.get("specs", [])}
    if list(specs) != ["creer_visuel"]:
        print(f"Attention : fonctions exposées au modèle : {list(specs)} (attendu : creer_visuel seule)")
    proprietes = specs.get("creer_visuel", {}).get("parameters", {}).get("properties", {})
    print("Formats proposés au modèle :", proprietes.get("format", {}).get("enum"))
    print("Vannes :", api("GET", f"/api/v1/tools/id/{OUTIL['id']}/valves"))
    modele = api("GET", f"/api/v1/models/model?id={MODELE['id']}", tolerer=True)
    if not modele:
        sys.exit(f"Modèle {MODELE['id']} absent.")
    print("Outils du modèle :", modele.get("meta", {}).get("toolIds"))
    config = api("GET", "/api/v1/images/config")
    if not config.get("ENABLE_IMAGE_GENERATION") or config.get("IMAGE_GENERATION_ENGINE") != "comfyui":
        print("Attention : la génération d'images n'est pas branchée sur ComfyUI (page Images).")


def retirer() -> None:
    api("POST", "/api/v1/models/model/delete", {"id": MODELE["id"]}, tolerer=True)
    api("DELETE", f"/api/v1/tools/id/{OUTIL['id']}/delete", tolerer=True)
    print("Modèle et outil retirés.")


if __name__ == "__main__":
    actions = {"--verifier": verifier, "--retirer": retirer}
    actions.get(sys.argv[1] if len(sys.argv) > 1 else "", installer)()
