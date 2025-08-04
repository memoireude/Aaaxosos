"""
Système de logging pour le bot de modération
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure le système de logging"""
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du logger principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Handler pour la console
            logging.StreamHandler(),
            # Handler pour le fichier de log
            logging.FileHandler(
                logs_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
        ]
    )
    
    # Réduire le niveau de logging pour discord.py
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    
    # Logger pour les actions de modération
    moderation_logger = logging.getLogger('moderation')
    moderation_handler = logging.FileHandler(
        logs_dir / f"moderation_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    moderation_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    moderation_logger.addHandler(moderation_handler)
    moderation_logger.setLevel(logging.INFO)

def log_moderation_action(action, moderator, target, reason, guild):
    """
    Log une action de modération
    
    Args:
        action: Type d'action (BAN, UNBAN, KICK)
        moderator: Utilisateur qui effectue l'action
        target: Utilisateur cible
        reason: Raison de l'action
        guild: Serveur où l'action a lieu
    """
    
    moderation_logger = logging.getLogger('moderation')
    
    log_message = (
        f"{action} | "
        f"Serveur: {guild.name} ({guild.id}) | "
        f"Modérateur: {moderator} ({moderator.id}) | "
        f"Cible: {target} ({target.id}) | "
        f"Raison: {reason}"
    )
    
    moderation_logger.info(log_message)
    
    # Log également dans la console pour le développement
    main_logger = logging.getLogger(__name__)
    main_logger.info(f"🔧 {action}: {target} par {moderator} - {reason}")

def log_error(error_message, exception=None):
    """
    Log une erreur
    
    Args:
        error_message: Message d'erreur
        exception: Exception Python (optionnel)
    """
    
    logger = logging.getLogger(__name__)
    
    if exception:
        logger.error(f"{error_message}: {exception}", exc_info=True)
    else:
        logger.error(error_message)

def log_warning(warning_message):
    """
    Log un avertissement
    
    Args:
        warning_message: Message d'avertissement
    """
    
    logger = logging.getLogger(__name__)
    logger.warning(warning_message)

def log_info(info_message):
    """
    Log une information
    
    Args:
        info_message: Message d'information
    """
    
    logger = logging.getLogger(__name__)
    logger.info(info_message)
