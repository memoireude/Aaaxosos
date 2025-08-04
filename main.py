#!/usr/bin/env python3
"""
Point d'entrée principal pour le bot Discord de modération
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from simple_bot import bot
from logger import setup_logging

# Charger les variables d'environnement depuis .env
load_dotenv()

def main():
    """Fonction principale pour démarrer le bot"""
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Récupération du token Discord depuis les variables d'environnement
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ Token Discord non trouvé!")
        logger.error("Veuillez définir la variable d'environnement DISCORD_TOKEN")
        logger.error("Exemple: export DISCORD_TOKEN='votre_token_ici'")
        return
    
    # Démarrage du bot
    try:
        logger.info("🤖 Démarrage du bot de modération...")
        logger.info("📋 Commandes disponibles:")
        logger.info("   +ping - Tester la connexion")
        logger.info("   +test - Test général")
        logger.info("   +ban @utilisateur [raison] - Bannir un utilisateur")  
        logger.info("   +kick @utilisateur [raison] - Expulser un utilisateur")
        logger.info("   +help - Afficher l'aide")
        logger.info("✅ Bot prêt! Connecté et en attente de commandes...")
        
        # Démarrage du bot
        bot.run(token)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage du bot: {e}")

if __name__ == "__main__":
    main()
