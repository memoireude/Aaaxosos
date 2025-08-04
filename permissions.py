"""
Utilitaires pour la gestion des permissions de modération
"""

import discord
import logging

logger = logging.getLogger(__name__)

async def check_moderation_permissions(ctx, target_user, action_type):
    """
    Vérifie les permissions pour une action de modération
    
    Args:
        ctx: Contexte de la commande
        target_user: Utilisateur cible
        action_type: Type d'action ("ban", "kick", etc.)
    
    Returns:
        bool: True si l'action est autorisée, False sinon
    """
    
    # Vérifier que l'utilisateur cible est bien un membre du serveur (pour ban/kick)
    if action_type in ["ban", "kick"] and not isinstance(target_user, discord.Member):
        await ctx.send("❌ L'utilisateur spécifié n'est pas membre de ce serveur!")
        return False
    
    # Empêcher l'auto-modération
    if target_user.id == ctx.author.id:
        await ctx.send("❌ Vous ne pouvez pas utiliser cette commande sur vous-même!")
        return False
    
    # Empêcher la modération du bot
    if target_user.id == ctx.bot.user.id:
        await ctx.send("❌ Je ne peux pas utiliser cette commande sur moi-même!")
        return False
    
    # Vérifier la hiérarchie des rôles pour les membres du serveur
    if isinstance(target_user, discord.Member):
        # L'auteur de la commande ne peut pas modérer quelqu'un de rang supérieur ou égal
        if target_user.top_role >= ctx.author.top_role:
            await ctx.send("❌ Vous ne pouvez pas modérer un utilisateur ayant un rôle supérieur ou égal au vôtre!")
            return False
        
        # Le bot ne peut pas modérer quelqu'un de rang supérieur ou égal
        if target_user.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ Je ne peux pas modérer un utilisateur ayant un rôle supérieur ou égal au mien!")
            return False
        
        # Vérifier si l'utilisateur cible est propriétaire du serveur
        if target_user.id == ctx.guild.owner_id:
            await ctx.send("❌ Je ne peux pas modérer le propriétaire du serveur!")
            return False
    
    return True

async def get_target_user(ctx, mentioned_member):
    """
    Détermine l'utilisateur cible en fonction de la mention ou du message de réponse
    
    Args:
        ctx: Contexte de la commande
        mentioned_member: Membre mentionné dans la commande (peut être None)
    
    Returns:
        discord.Member ou discord.User: L'utilisateur cible, ou None si non trouvé
    """
    
    # Si un utilisateur est mentionné directement
    if mentioned_member:
        return mentioned_member
    
    # Si la commande est une réponse à un message
    if ctx.message.reference and ctx.message.reference.message_id:
        try:
            # Récupérer le message original
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            return referenced_message.author
        except discord.NotFound:
            logger.warning("Message de référence non trouvé")
        except discord.Forbidden:
            logger.warning("Pas d'autorisation pour récupérer le message de référence")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du message de référence: {e}")
    
    # Vérifier s'il y a des mentions dans le message
    if ctx.message.mentions:
        return ctx.message.mentions[0]
    
    return None

def has_moderation_role(member, required_permission):
    """
    Vérifie si un membre a les permissions de modération requises
    
    Args:
        member: Le membre à vérifier
        required_permission: La permission requise ("ban_members", "kick_members", etc.)
    
    Returns:
        bool: True si le membre a la permission, False sinon
    """
    
    # Le propriétaire du serveur a toutes les permissions
    if member.id == member.guild.owner_id:
        return True
    
    # Vérifier les permissions du membre
    permissions = member.guild_permissions
    return getattr(permissions, required_permission, False)
