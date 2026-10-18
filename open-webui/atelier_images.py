"""
title: Atelier d'images
author: Société Exemple
description: Crée des visuels aux formats de la Société Exemple (affiche, bannière, carré) avec le serveur d'images de l'organisation.
version: 1.0.0
licence: MIT
"""

from typing import Literal

from pydantic import BaseModel, Field

from open_webui.models.chats import Chats
from open_webui.models.users import UserModel
from open_webui.routers.images import (
    CreateImageForm,
    get_image_config,
    image_generations,
)
from open_webui.utils.access_control import has_permission
from open_webui.utils.chat_id import is_saved_chat_id

# Formats de la Société Exemple, en pixels (largeur x hauteur) :
# multiples de 64, environ un million de pixels chacun.
FORMATS = {
    "affiche": "832x1216",  # en hauteur, pour l'impression
    "banniere": "1536x640",  # très large, en-tête de l'intranet
    "carre": "1024x1024",  # vignette, lettre interne
}


class Tools:
    class Valves(BaseModel):
        variantes_max: int = Field(
            default=1, ge=1, le=6, description="Nombre maximal de variantes par demande"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def creer_visuel(
        self,
        description: str,
        format: Literal["affiche", "banniere", "carre"] = "carre",
        variantes: int = 1,
        __request__=None,
        __user__: dict = None,
        __event_emitter__=None,
        __chat_id__: str = None,
        __message_id__: str = None,
    ) -> str:
        """
        Crée une ou plusieurs images avec le serveur d'images de l'organisation.
        :param description: la scène seule (sujet, décor, ambiance), en une ou deux phrases, sans nommer l'usage, terminée par « sans aucun texte » ; la charte est ajoutée par le serveur
        :param format: affiche (en hauteur, document imprimé), banniere (très large, en-tête de l'intranet) ou carre (vignette, lettre interne)
        :param variantes: nombre de versions différentes à proposer, de 1 à 3
        """
        utilisateur = UserModel(**__user__)

        # 1. Le droit de générer des images, comme pour l'outil intégré (module 5).
        if not await self._autorise(utilisateur):
            return (
                "Refusé : ce compte ne peut pas générer d'images. Dites-le simplement."
            )

        # 2. Le nombre de variantes, plafonné par la vanne de l'administrateur.
        n = max(1, min(int(variantes), self.valves.variantes_max))
        await self._statut(__event_emitter__, f"{n} visuel(s) au format {format}…")

        # 3. Une variante = un calcul complet du workflow, avec sa propre graine.
        taille, images = FORMATS[format], []
        try:
            for _ in range(n):
                images += await self._generer(
                    __request__, utilisateur, description, taille
                )
        except Exception as erreur:
            await self._statut(
                __event_emitter__, "Serveur d'images indisponible", fini=True
            )
            return f"Échec du serveur d'images ({erreur}). Dites-le à l'utilisateur."

        # 4. Les images sont rattachées au message, puis affichées dans la conversation.
        fichiers = [{"type": "image", **image} for image in images]
        if is_saved_chat_id(__chat_id__) and __message_id__:
            fichiers = (
                await Chats.add_message_files_by_id_and_message_id(
                    __chat_id__, __message_id__, fichiers
                )
                or fichiers
            )
        if __event_emitter__:
            await __event_emitter__(
                {"type": "chat:message:files", "data": {"files": fichiers}}
            )
        await self._statut(__event_emitter__, "Visuels prêts", fini=True)

        # 5. La réponse au modèle : les images sont déjà à l'écran, ne pas les répéter.
        return (
            f"{len(images)} image(s) au format {format}, déjà affichée(s) dans la conversation. "
            "Ne les réaffichez pas et ne donnez pas de lien : présentez-les en une phrase."
        )

    async def _autorise(self, utilisateur: UserModel) -> bool:
        """Génération activée dans la page Images, et permission « Génération d'image »."""
        config = await get_image_config()
        if not config.ENABLE_IMAGE_GENERATION:
            return False
        return utilisateur.role == "admin" or await has_permission(
            utilisateur.id, "features.image_generation", config.USER_PERMISSIONS
        )

    async def _generer(
        self, requete, utilisateur, description: str, taille: str
    ) -> list:
        """Une image : le workflow et la correspondance de la page Images, à la taille du format."""
        return await image_generations(
            request=requete,
            form_data=CreateImageForm(prompt=description, size=taille),
            user=utilisateur,
        )

    async def _statut(self, emetteur, texte: str, fini: bool = False) -> None:
        """Message d'avancement affiché au-dessus de la réponse."""
        if emetteur:
            await emetteur(
                {"type": "status", "data": {"description": texte, "done": fini}}
            )
