# Un outil qui choisit le format — « Atelier d'images » pour Open WebUI et ComfyUI

Démonstration du module 4 de la série « Clic par clic » **Générer des images dans Open WebUI avec
ComfyUI**. Dans Open WebUI, l'outil intégré de génération d'image ne reçoit qu'une description :
toutes les images ont la taille fixée dans la page Images, la même pour toute l'instance. L'outil
maison **« Atelier d'images »** laisse le modèle de conversation choisir le **format** (affiche,
bannière, vignette carrée) et le **nombre de variantes**, tout en réutilisant le workflow ComfyUI et
la correspondance de l'organisation (charte graphique comprise).

Vidéo : {{video}}

## But

- Lire l'outil intégré `generate_image` d'Open WebUI 0.11 (`open_webui/tools/builtin.py`) : un seul
  paramètre, aucune taille ; images rattachées au message, réponse « déjà visible » au modèle.
- Écrire un outil Open WebUI (`open-webui/atelier_images.py`, version 1) :
  - `FORMATS` : affiche 832 × 1216, bannière 1536 × 640, carré 1024 × 1024 ;
  - une vanne `variantes_max` (1 par défaut, 3 dans la vidéo) ;
  - une seule fonction proposée au modèle, `creer_visuel(description, format, variantes)`, dont le
    format est une énumération (`Literal`) et dont chaque paramètre est décrit pour le modèle ;
  - le droit de générer des images vérifié comme pour l'outil intégré, un message d'avancement,
    une génération par variante (`image_generations` d'Open WebUI, à la taille du format), les
    images rattachées au message et affichées, une réponse qui évite au modèle de les répéter.
- L'installer, régler sa vanne, l'attacher à un modèle « Atelier d'images » ; vérifier dans les
  appels d'outil ce que le modèle a choisi.

| Fichier | Contenu |
|---|---|
| `open-webui/atelier_images.py` | L'outil, **tel que collé dans la vidéo** |
| `open-webui/consignes-atelier.txt` | Le prompt système du modèle « Atelier d'images » |
| `open-webui/modele-atelier.md` | Réglages du modèle et de l'outil, ce que voit le modèle |
| `installer_atelier.py` | Outil et modèle installés par l'API d'Open WebUI, contrôle, retrait |
| `workflows/affiches-v2.json` | Le workflow de l'organisation (module 2) que l'outil réutilise, au format API |

## Prérequis

- Le serveur d'images des modules 1 et 2 : ComfyUI v0.41 sur une carte graphique, branché dans
  Open WebUI 0.11 (page Images, workflow `affiches-v2`, correspondance `string_b` / 34) —
  [`clic-par-clic-comfyui-01-brancher`](https://github.com/guilhem-/clic-par-clic-comfyui-01-brancher),
  [`clic-par-clic-comfyui-02-workflow-organisation`](https://github.com/guilhem-/clic-par-clic-comfyui-02-workflow-organisation).
  L'outil n'a **aucun réglage propre au serveur d'images** : il passe par la page Images.
- Un compte **administrateur** d'Open WebUI (les outils exécutent du code sur le serveur : seul un
  administrateur, ou un utilisateur autorisé, peut en créer).
- Un modèle de conversation capable d'appeler des outils (appel de fonction « natif », réglage par
  défaut d'Open WebUI 0.11).
- Pour les utilisateurs : la génération d'images activée dans la page Images, et la permission
  « Génération d'image » (module 5).

## Installation pas à pas

### 1. À la main, comme dans la vidéo

1. **Espace de travail › Outils › « + »** : nom `Atelier d'images`, identifiant `atelier_images`,
   collez le contenu de `open-webui/atelier_images.py`, **Accès** : public (un utilisateur ne peut
   se servir que d'un outil auquel il a accès), **Enregistrer & Créer**, confirmez.
2. Dans la liste des outils, roue **Vannes** de l'outil : `variantes_max` à `3`, **Enregistrer**.
3. **Espace de travail › Modèles › « + »** : nom `Atelier d'images`, modèle de base, prompt système
   = `open-webui/consignes-atelier.txt`, **Outils** : cochez « Atelier d'images », **Accès** :
   public (ou un groupe), **Enregistrer & Créer**.

### 2. Par l'API

```bash
cp .env.example .env                    # OWUI_URL, OWUI_JETON (administrateur), MODELE_BASE
python installer_atelier.py             # crée ou met à jour l'outil, sa vanne et le modèle
python installer_atelier.py --verifier  # fonctions vues par le modèle, formats, vanne, outils du modèle
python installer_atelier.py --retirer   # supprime le modèle puis l'outil
```

## Essai

Avec un compte utilisateur, nouvelle conversation avec le modèle **Atelier d'images** (sans activer
« Image » : l'outil est attaché au modèle) :

1. « Prépare l'affiche de la formation Sécurité au travail à Lyon, et une bannière pour l'annoncer
   sur l'intranet. » — deux appels de `creer_visuel`, un par format : une image en hauteur, une
   très large.
2. « Propose trois versions carrées pour la vignette de la lettre interne. » — un appel, format
   `carre`, `variantes` : 3 ; trois images, trois graines.

Dépliez les appels d'outil pour lire les arguments choisis par le modèle.

## Bon à savoir

- **Une variante, c'est un calcul complet** (une trentaine de secondes par image sur une carte de
  8 Go) : trois variantes, trois fois le temps. La vanne protège la file d'attente de ComfyUI.
- **La charte** est dans le workflow (module 2) : elle s'applique à tous les formats, quel que soit
  le texte écrit par le modèle.
- **Méthodes privées** : Open WebUI propose au modèle toutes les méthodes publiques de la classe
  `Tools`. Les fonctions d'aide (`_autorise`, `_generer`, `_statut`) commencent par `_` pour rester
  invisibles.
- **Code évolutif** : la version 2 (module 6) ajoute le contrôle de la charte de contenu avant la
  boucle ; la version 3 (module 8) remplace `_generer` pour marquer les images.
- **L'outil intégré** reste disponible avec l'interrupteur « Image ».
- **Alternative** : une fonction Pipe par workflow, qui apparaît comme un modèle dans la liste ;
  l'utilisateur choisit, le modèle de conversation n'intervient pas.

## Série

- Module précédent : **Retoucher une image** —
  [`clic-par-clic-comfyui-03-retouche`](https://github.com/guilhem-/clic-par-clic-comfyui-03-retouche).
- Module suivant : **Qui peut générer des images ?** (permissions par groupe) —
  `clic-par-clic-comfyui-05-…` (à paraître).

## Licence

MIT (voir `LICENSE`). ComfyUI : GPL-3.0 ; Z-Image Turbo : Apache 2.0 ; Open WebUI : sa propre
licence (le code cité dans la vidéo reste le sien, il n'est pas recopié ici).
