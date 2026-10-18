# Modèle « Atelier d'images » — réglages

Créé dans Open WebUI › Espace de travail › Modèles › « + » (ou par `python installer_atelier.py`).

| Champ | Valeur |
|---|---|
| Nom | `Atelier d'images` |
| Identifiant | `atelier-d-images` (proposé par l'interface à partir du nom) |
| Modèle de base | le modèle de conversation habituel de l'organisation, capable d'appeler des outils (appel de fonction « natif », réglage par défaut d'Open WebUI 0.11) |
| Prompt système | le texte de [`consignes-atelier.txt`](consignes-atelier.txt) |
| Outils | **Atelier d'images** coché (`atelier_images`) |
| Capacités | celles par défaut ; l'interrupteur « Image » n'est pas nécessaire : l'outil est attaché au modèle |
| Accès | public (lecture pour tous les utilisateurs) ; réservé à un groupe au module 5 |

## Outil « Atelier d'images »

| Champ | Valeur |
|---|---|
| Nom | `Atelier d'images` |
| Identifiant | `atelier_images` (l'interface propose `atelier_d_images` : remplacé, les modules suivants s'y réfèrent) |
| Code | [`atelier_images.py`](atelier_images.py), collé dans l'éditeur |
| Accès | public : un utilisateur ne peut se servir que d'un outil auquel il a accès, même attaché à un modèle (réservé à un groupe au module 5) |
| Vanne `variantes_max` | `3` (par défaut : `1`) |

## Ce que voit le modèle

Une seule fonction, `creer_visuel` (les méthodes dont le nom commence par `_` ne sont pas
proposées au modèle) :

- `description` (texte) : ce que montre l'image, sans texte ni style ;
- `format` : énumération `affiche`, `banniere`, `carre` (type `Literal` de Python, converti en
  `enum` dans le schéma JSON de l'outil) ;
- `variantes` (entier, 1 par défaut), plafonné par la vanne.

Les tailles (`FORMATS`) : affiche 832 × 1216, bannière 1536 × 640, carré 1024 × 1024 — multiples de
64, environ un million de pixels chacune, ce que le modèle d'image de l'organisation calcule en une
trentaine de secondes sur une carte de 8 Go.
