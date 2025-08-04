import discord
from discord.ext import commands
import os
import logging
import datetime
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Créer le bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Dictionnaire pour stocker les rôles sauvegardés des utilisateurs mutés
muted_users_roles = {}

@bot.event
async def on_ready():
    logger.info(f'Bot connecté en tant que {bot.user}!')
    logger.info(f'Connecté à {len(bot.guilds)} serveur(s)')

@bot.event
async def on_member_update(before, after):
    """Détecte quand un membre reçoit ou perd le rôle Muted"""
    # Chercher le rôle Muted dans le serveur
    muted_role = discord.utils.get(after.guild.roles, name="Muted")
    if not muted_role:
        return
    
    # Si le membre vient de recevoir le rôle Muted
    if muted_role not in before.roles and muted_role in after.roles:
        # Sauvegarder les anciens rôles (sauf @everyone et Muted)
        old_roles = [role.id for role in before.roles if role != after.guild.default_role and role != muted_role]
        if old_roles:
            muted_users_roles[after.id] = old_roles
            role_names = [role.name for role in before.roles if role != after.guild.default_role and role != muted_role]
            logger.info(f"🔒 MUTE DÉTECTÉ: {after} - {len(old_roles)} rôles sauvegardés: {', '.join(role_names)}")
        else:
            logger.info(f"🔒 MUTE DÉTECTÉ: {after} - Aucun rôle à sauvegarder")
        
    # Si le membre vient de perdre le rôle Muted (unmute par un autre bot)
    elif muted_role in before.roles and muted_role not in after.roles:
        logger.info(f"🔓 UNMUTE AUTOMATIQUE DÉTECTÉ pour {after}")
        # Si on a des rôles sauvegardés, les restaurer automatiquement
        if after.id in muted_users_roles:
            try:
                saved_roles = [after.guild.default_role]  # Commencer avec @everyone
                restored_role_names = []
                for role_id in muted_users_roles[after.id]:
                    role = after.guild.get_role(role_id)
                    if role and role != after.guild.default_role:
                        saved_roles.append(role)
                        restored_role_names.append(role.name)
                
                await after.edit(roles=saved_roles, reason="Restauration automatique des rôles après unmute")
                logger.info(f"✅ UNMUTE AUTOMATIQUE: {after} - {len(saved_roles)-1} rôles restaurés: {', '.join(restored_role_names)}")
                del muted_users_roles[after.id]
            except Exception as e:
                logger.error(f"❌ Erreur lors de la restauration automatique des rôles pour {after}: {e}")
        else:
            logger.warning(f"⚠️ UNMUTE AUTOMATIQUE: {after} - Aucun rôle sauvegardé trouvé")

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author == bot.user:
        return
    
    # Liste des commandes valides du bot
    valid_commands = ['ping', 'test', 'ban', 'unban', 'kick', 'mute', 'unmute', 'lock', 'unlock', 'commandes']
    
    # Si le message commence par +, vérifier si c'est une commande valide
    if message.content.startswith('+'):
        command_name = message.content[1:].split()[0].lower()  # Extraire le nom de la commande
        
        # Si c'est une commande valide, logger et traiter
        if command_name in valid_commands:
            logger.info(f"MESSAGE REÇU: '{message.content}' de {message.author} dans #{message.channel}")
            await bot.process_commands(message)
        # Sinon, ignorer complètement (pas de log, pas de traitement)
        return
    
    # Pour les messages sans +, traiter normalement (au cas où il y aurait d'autres événements)
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Ne rien faire, même pas de log pour éviter le spam complet
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant. Utilisez `+commandes` pour voir la syntaxe correcte.")
        logger.error(f"Argument manquant: {error} | Message: {ctx.message.content}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires pour cette commande!")
        logger.error(f"Permissions manquantes: {error} | Utilisateur: {ctx.author}")
    else:
        logger.error(f"ERREUR COMMANDE: {error} | Message: {ctx.message.content}")
        await ctx.send(f"❌ Erreur: {error}")

@bot.command(name='ping')
async def ping(ctx):
    logger.info(f"COMMANDE PING exécutée par {ctx.author}")
    await ctx.send('🏓 Pong! Le bot fonctionne!')

@bot.command(name='test')
async def test(ctx):
    logger.info(f"COMMANDE TEST exécutée par {ctx.author}")
    await ctx.send('✅ Test réussi! Le bot répond correctement.')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    # Si pas de mention, vérifier si c'est une réponse à un message
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                # Récupérer le message original
                referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                # Vérifier que l'auteur du message est un membre du serveur
                if isinstance(referenced_message.author, discord.Member):
                    member = referenced_message.author
                else:
                    await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                    return
            except discord.NotFound:
                await ctx.send("❌ Message de référence non trouvé!")
                return
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
                return
        else:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour bannir quelqu'un!")
            return
    
    logger.info(f"COMMANDE BAN tentée par {ctx.author} sur {member}")
    
    try:
        await member.ban(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"🔨 {member} a été banni! Raison: {reason}")
        logger.info(f"BAN RÉUSSI: {member} banni par {ctx.author}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du ban: {e}")
        logger.error(f"ERREUR BAN: {e}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    # Si pas de mention, vérifier si c'est une réponse à un message
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                # Récupérer le message original
                referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                # Vérifier que l'auteur du message est un membre du serveur
                if isinstance(referenced_message.author, discord.Member):
                    member = referenced_message.author
                else:
                    await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                    return
            except discord.NotFound:
                await ctx.send("❌ Message de référence non trouvé!")
                return
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
                return
        else:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour expulser quelqu'un!")
            return
    
    logger.info(f"COMMANDE KICK tentée par {ctx.author} sur {member}")
    
    try:
        await member.kick(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"👢 {member} a été expulsé! Raison: {reason}")
        logger.info(f"KICK RÉUSSI: {member} expulsé par {ctx.author}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du kick: {e}")
        logger.error(f"ERREUR KICK: {e}")

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason="Aucune raison spécifiée"):
    logger.info(f"COMMANDE UNBAN tentée par {ctx.author} pour l'ID {user_id}")
    
    try:
        # Récupérer l'utilisateur par son ID
        user = await bot.fetch_user(user_id)
        # Débannir l'utilisateur
        await ctx.guild.unban(user, reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"✅ {user} a été débanni! Raison: {reason}")
        logger.info(f"UNBAN RÉUSSI: {user} débanni par {ctx.author}")
    except discord.NotFound:
        await ctx.send(f"❌ Aucun utilisateur banni trouvé avec l'ID: {user_id}")
        logger.error(f"ERREUR UNBAN: Utilisateur ID {user_id} non trouvé dans les bannissements")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du unban: {e}")
        logger.error(f"ERREUR UNBAN: {e}")






async def try_recover_roles_from_audit_log(guild, member):
    """Essaie de récupérer les anciens rôles depuis l'audit log"""
    try:
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if not muted_role:
            return None
        
        logger.info(f"🔍 Recherche dans l'audit log pour {member}...")
        
        # Chercher dans l'audit log les changements de rôles récents (dernières 100 entrées)
        async for entry in guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=100):
            if entry.target and entry.target.id == member.id:
                logger.info(f"📋 Entrée audit log trouvée pour {member}: {entry.created_at}")
                
                # Vérifier si c'était un ajout du rôle Muted
                if hasattr(entry, 'before') and hasattr(entry, 'after'):
                    before_roles = entry.before.roles if entry.before.roles else []
                    after_roles = entry.after.roles if entry.after.roles else []
                    
                    # Si le rôle Muted a été ajouté dans cette entrée
                    if muted_role not in before_roles and muted_role in after_roles:
                        # Récupérer les rôles qu'il avait avant le mute
                        old_roles = [role.id for role in before_roles if role != guild.default_role]
                        logger.info(f"✅ Rôles trouvés dans l'audit log: {len(old_roles)} rôles")
                        return old_roles
                        
                # Vérifier les changements dans les rôles
                if hasattr(entry.changes, 'before') and hasattr(entry.changes, 'after'):
                    for change in entry.changes:
                        if change.key == 'roles':
                            before_roles = change.before if change.before else []
                            after_roles = change.after if change.after else []
                            
                            # Chercher si le rôle Muted a été ajouté
                            muted_added = any(role.id == muted_role.id for role in after_roles) and not any(role.id == muted_role.id for role in before_roles)
                            
                            if muted_added:
                                old_roles = [role.id for role in before_roles if role.id != guild.default_role.id]
                                logger.info(f"✅ Rôles trouvés via changes: {len(old_roles)} rôles")
                                return old_roles
        
        logger.info(f"❌ Aucun rôle trouvé dans l'audit log pour {member}")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur lors de la recherche dans l'audit log: {e}")
        return None

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, *args):
    """Mute un ou plusieurs utilisateurs et sauvegarde leurs rôles"""
    if not args:
        # Vérifier si c'est une réponse à un message
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if isinstance(referenced_message.author, discord.Member):
                    members = [referenced_message.author]
                    reason = "Aucune raison spécifiée"
                else:
                    await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                    return
            except discord.NotFound:
                await ctx.send("❌ Message de référence non trouvé!")
                return
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
                return
        else:
            await ctx.send("❌ Veuillez mentionner un ou plusieurs utilisateurs ou répondre à un message pour mute quelqu'un!")
            return
    else:
        # Extraire les membres mentionnés et la raison
        members = []
        reason_parts = []
        
        for arg in args:
            # Essayer de convertir en membre
            try:
                member = await commands.MemberConverter().convert(ctx, arg)
                members.append(member)
            except commands.BadArgument:
                # Si ce n'est pas un membre, c'est probablement partie de la raison
                reason_parts.append(arg)
        
        reason = " ".join(reason_parts) if reason_parts else "Aucune raison spécifiée"
        
        if not members:
            await ctx.send("❌ Aucun membre valide trouvé dans votre commande!")
            return
    
    logger.info(f"COMMANDE MUTE tentée par {ctx.author} sur {len(members)} membre(s)")
    
    # Chercher le rôle Muted
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
        return
    
    muted_members = []
    already_muted = []
    errors = []
    
    for member in members:
        try:
            # Vérifier si l'utilisateur est déjà mute
            if muted_role in member.roles:
                already_muted.append(member)
                continue
            
            # Sauvegarder les rôles actuels (sauf @everyone)
            old_roles = [role.id for role in member.roles if role != ctx.guild.default_role]
            if old_roles:
                muted_users_roles[member.id] = old_roles
                role_names = [role.name for role in member.roles if role != ctx.guild.default_role]
                logger.info(f"🔒 MUTE: {member} - {len(old_roles)} rôles sauvegardés: {', '.join(role_names)}")
            else:
                logger.info(f"🔒 MUTE: {member} - Aucun rôle à sauvegarder")
            
            # Retirer tous les rôles sauf @everyone et ajouter Muted
            new_roles = [ctx.guild.default_role, muted_role]
            await member.edit(roles=new_roles, reason=f"Mute - {reason} - Par {ctx.author}")
            
            muted_members.append((member, len(old_roles)))
            logger.info(f"MUTE RÉUSSI: {member} mute par {ctx.author} avec {len(old_roles)} rôles sauvegardés")
            
        except Exception as e:
            errors.append((member, str(e)))
            logger.error(f"ERREUR MUTE: {e} pour {member}")
    
    # Construire le message de réponse
    response_parts = []
    
    if muted_members:
        if len(muted_members) == 1:
            member, roles_count = muted_members[0]
            response_parts.append(f"🔇 {member} a été mute! {roles_count} rôles sauvegardés.")
        else:
            muted_list = [f"{member.display_name} ({roles_count} rôles)" for member, roles_count in muted_members]
            response_parts.append(f"🔇 {len(muted_members)} membre(s) ont été mutés: {', '.join(muted_list)}")
    
    if already_muted:
        already_muted_list = [member.display_name for member in already_muted]
        response_parts.append(f"⚠️ Déjà mutés: {', '.join(already_muted_list)}")
    
    if errors:
        error_list = [f"{member.display_name} (erreur)" for member, error in errors]
        response_parts.append(f"❌ Erreurs: {', '.join(error_list)}")
    
    if response_parts:
        response_parts.append(f"Raison: {reason}")
        await ctx.send("\n".join(response_parts))
    else:
        await ctx.send("❌ Aucune action n'a pu être effectuée!")

@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, target=None, *, reason="Aucune raison spécifiée"):
    logger.info(f"COMMANDE UNMUTE tentée par {ctx.author}")
    
    # Si "all" est spécifié, démute tous les membres avec le rôle Muted
    if target and target.lower() == "all":
        count = 0
        restored_count = 0
        recovered_count = 0
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
                return
            
            for member in ctx.guild.members:
                if muted_role in member.roles:
                    restored_roles = []
                    
                    # Essayer de restaurer les anciens rôles sauvegardés
                    if member.id in muted_users_roles:
                        for role_id in muted_users_roles[member.id]:
                            role = ctx.guild.get_role(role_id)
                            if role and role != ctx.guild.default_role:
                                restored_roles.append(role)
                        del muted_users_roles[member.id]
                        restored_count += 1
                    else:
                        # Essayer de récupérer depuis l'audit log
                        recovered_roles = await try_recover_roles_from_audit_log(ctx.guild, member)
                        if recovered_roles:
                            for role_id in recovered_roles:
                                role = ctx.guild.get_role(role_id)
                                if role and role != ctx.guild.default_role:
                                    restored_roles.append(role)
                            recovered_count += 1
                    
                    # Appliquer les rôles (toujours inclure @everyone, retirer Muted)
                    final_roles = [ctx.guild.default_role] + restored_roles
                    await member.edit(roles=final_roles, reason=f"Unmute all - {reason} - Par {ctx.author}")
                    logger.info(f"UNMUTE: {member} démute avec {len(restored_roles)} rôles restaurés par {ctx.author}")
                    count += 1
            
            message = f"🔊 {count} utilisateur(s) ont été démutés!"
            if restored_count > 0:
                message += f" {restored_count} avaient leurs rôles sauvegardés automatiquement."
            if recovered_count > 0:
                message += f" {recovered_count} ont eu leurs rôles récupérés depuis l'historique."
            message += f" Raison: {reason}"
            
            await ctx.send(message)
            logger.info(f"UNMUTE ALL RÉUSSI: {count} utilisateurs démutés par {ctx.author}")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du unmute all: {e}")
            logger.error(f"ERREUR UNMUTE ALL: {e}")
        return
    
    # Sinon, traiter comme unmute d'un utilisateur spécifique
    member = None
    
    # Vérifier si c'est une mention
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
    # Vérifier si c'est une réponse à un message
    elif ctx.message.reference and ctx.message.reference.message_id:
        try:
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if isinstance(referenced_message.author, discord.Member):
                member = referenced_message.author
            else:
                await ctx.send("❌ L'auteur du message n'est pas un membre de ce serveur!")
                return
        except discord.NotFound:
            await ctx.send("❌ Message de référence non trouvé!")
            return
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération du message: {e}")
            return
    else:
        await ctx.send("❌ Veuillez mentionner un utilisateur, répondre à un message, ou utiliser `+unmute all`!")
        return
    
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
            return
        
        if muted_role not in member.roles:
            await ctx.send(f"❌ {member} n'est pas mute!")
            return
        
        restored_roles = []
        recovery_method = ""
        
        # Essayer de restaurer les anciens rôles sauvegardés
        if member.id in muted_users_roles:
            logger.info(f"🔄 Rôles sauvegardés trouvés pour {member}: {len(muted_users_roles[member.id])} rôles")
            for role_id in muted_users_roles[member.id]:
                role = ctx.guild.get_role(role_id)
                if role and role != ctx.guild.default_role:
                    restored_roles.append(role)
                    logger.info(f"✅ Rôle restauré: {role.name}")
            del muted_users_roles[member.id]
            recovery_method = "sauvegardés automatiquement"
        else:
            logger.info(f"❌ Aucun rôle sauvegardé trouvé pour {member}, recherche dans l'audit log...")
            # Essayer de récupérer depuis l'audit log
            recovered_roles = await try_recover_roles_from_audit_log(ctx.guild, member)
            if recovered_roles:
                logger.info(f"🔄 Rôles récupérés de l'audit log: {len(recovered_roles)} rôles")
                for role_id in recovered_roles:
                    role = ctx.guild.get_role(role_id)
                    if role and role != ctx.guild.default_role:
                        restored_roles.append(role)
                        logger.info(f"✅ Rôle récupéré: {role.name}")
                recovery_method = "récupérés depuis l'historique"
            else:
                logger.warning(f"⚠️ Aucun rôle trouvé pour {member} dans l'audit log")
        
        # Appliquer les rôles (toujours inclure @everyone, retirer Muted)
        final_roles = [ctx.guild.default_role] + restored_roles
        await member.edit(roles=final_roles, reason=f"Unmute - {reason} - Par {ctx.author}")
        
        if restored_roles:
            await ctx.send(f"🔊 {member} a été démute et ses {len(restored_roles)} rôles ont été {recovery_method}! Raison: {reason}")
            logger.info(f"UNMUTE RÉUSSI: {member} démute avec {len(restored_roles)} rôles {recovery_method} par {ctx.author}")
        else:
            await ctx.send(f"🔊 {member} a été démute! (Aucun ancien rôle trouvé) Raison: {reason}")
            logger.info(f"UNMUTE RÉUSSI: {member} démute sans rôles récupérés par {ctx.author}")
        
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du unmute: {e}")
        logger.error(f"ERREUR UNMUTE: {e}")

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock(ctx, target=None, *, reason="Aucune raison spécifiée"):
    """Verrouille le salon actuel ou tous les salons si 'all' est spécifié"""
    logger.info(f"COMMANDE LOCK tentée par {ctx.author} - target: {target}")
    
    # Si "all" est spécifié, verrouiller tous les salons
    if target and target.lower() == "all":
        locked_count = 0
        already_locked_count = 0
        errors = []
        
        try:
            everyone_role = ctx.guild.default_role
            
            for channel in ctx.guild.text_channels:
                try:
                    # Vérifier si le salon est déjà verrouillé
                    permissions = channel.permissions_for(everyone_role)
                    if not permissions.send_messages:
                        already_locked_count += 1
                        continue
                    
                    # Verrouiller le salon
                    await channel.set_permissions(everyone_role, send_messages=False, reason=f"Lock all - {reason} - Par {ctx.author}")
                    locked_count += 1
                    logger.info(f"LOCK ALL: Salon {channel.name} verrouillé")
                    
                except Exception as e:
                    errors.append((channel.name, str(e)))
                    logger.error(f"ERREUR LOCK ALL: {e} pour le salon {channel.name}")
            
            # Construire le message de réponse
            message_parts = []
            if locked_count > 0:
                message_parts.append(f"🔒 {locked_count} salon(s) ont été verrouillés!")
            if already_locked_count > 0:
                message_parts.append(f"⚠️ {already_locked_count} salon(s) étaient déjà verrouillés.")
            if errors:
                message_parts.append(f"❌ {len(errors)} erreur(s) rencontrées.")
            
            message_parts.append(f"Raison: {reason}")
            await ctx.send("\n".join(message_parts))
            logger.info(f"LOCK ALL RÉUSSI: {locked_count} salons verrouillés par {ctx.author}")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du verrouillage global: {e}")
            logger.error(f"ERREUR LOCK ALL: {e}")
        return
    
    # Sinon, verrouiller le salon actuel
    try:
        # Récupérer le rôle @everyone
        everyone_role = ctx.guild.default_role
        
        # Vérifier si le salon est déjà verrouillé
        permissions = ctx.channel.permissions_for(everyone_role)
        if not permissions.send_messages:
            await ctx.send("🔒 Ce salon est déjà verrouillé!")
            return
        
        # Verrouiller le salon
        await ctx.channel.set_permissions(everyone_role, send_messages=False, reason=f"Salon verrouillé - {reason} - Par {ctx.author}")
        
        await ctx.send(f"🔒 Salon **{ctx.channel.name}** verrouillé! Raison: {reason}")
        logger.info(f"LOCK RÉUSSI: Salon {ctx.channel.name} verrouillé par {ctx.author}")
        
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du verrouillage: {e}")
        logger.error(f"ERREUR LOCK: {e}")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, target=None, *, reason="Aucune raison spécifiée"):
    """Déverrouille le salon actuel ou tous les salons si 'all' est spécifié"""
    logger.info(f"COMMANDE UNLOCK tentée par {ctx.author} - target: {target}")
    
    # Si "all" est spécifié, déverrouiller tous les salons
    if target and target.lower() == "all":
        unlocked_count = 0
        already_unlocked_count = 0
        errors = []
        
        try:
            everyone_role = ctx.guild.default_role
            
            for channel in ctx.guild.text_channels:
                try:
                    # Vérifier si le salon est déjà déverrouillé
                    permissions = channel.permissions_for(everyone_role)
                    if permissions.send_messages:
                        already_unlocked_count += 1
                        continue
                    
                    # Déverrouiller le salon
                    await channel.set_permissions(everyone_role, send_messages=None, reason=f"Unlock all - {reason} - Par {ctx.author}")
                    unlocked_count += 1
                    logger.info(f"UNLOCK ALL: Salon {channel.name} déverrouillé")
                    
                except Exception as e:
                    errors.append((channel.name, str(e)))
                    logger.error(f"ERREUR UNLOCK ALL: {e} pour le salon {channel.name}")
            
            # Construire le message de réponse
            message_parts = []
            if unlocked_count > 0:
                message_parts.append(f"🔓 {unlocked_count} salon(s) ont été déverrouillés!")
            if already_unlocked_count > 0:
                message_parts.append(f"⚠️ {already_unlocked_count} salon(s) étaient déjà déverrouillés.")
            if errors:
                message_parts.append(f"❌ {len(errors)} erreur(s) rencontrées.")
            
            message_parts.append(f"Raison: {reason}")
            await ctx.send("\n".join(message_parts))
            logger.info(f"UNLOCK ALL RÉUSSI: {unlocked_count} salons déverrouillés par {ctx.author}")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du déverrouillage global: {e}")
            logger.error(f"ERREUR UNLOCK ALL: {e}")
        return
    
    # Sinon, déverrouiller le salon actuel
    try:
        # Récupérer le rôle @everyone
        everyone_role = ctx.guild.default_role
        
        # Vérifier si le salon est déjà déverrouillé
        permissions = ctx.channel.permissions_for(everyone_role)
        if permissions.send_messages:
            await ctx.send("🔓 Ce salon est déjà déverrouillé!")
            return
        
        # Déverrouiller le salon
        await ctx.channel.set_permissions(everyone_role, send_messages=None, reason=f"Salon déverrouillé - {reason} - Par {ctx.author}")
        
        await ctx.send(f"🔓 Salon **{ctx.channel.name}** déverrouillé! Raison: {reason}")
        logger.info(f"UNLOCK RÉUSSI: Salon {ctx.channel.name} déverrouillé par {ctx.author}")
        
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du déverrouillage: {e}")
        logger.error(f"ERREUR UNLOCK: {e}")

@bot.command(name='commandes')
async def commandes_command(ctx):
    logger.info(f"COMMANDE COMMANDES exécutée par {ctx.author}")
    embed = discord.Embed(title="🛡️ Commandes de Modération", color=0x00ff00)
    embed.add_field(name="+ping", value="Teste la connexion", inline=False)
    embed.add_field(name="+test", value="Test général du bot", inline=False)
    embed.add_field(name="+ban @utilisateur [raison]", value="Bannir un utilisateur (mention ou réponse)", inline=False)
    embed.add_field(name="+unban <ID_utilisateur> [raison]", value="Débannir un utilisateur avec son ID", inline=False)
    embed.add_field(name="+kick @utilisateur [raison]", value="Expulser un utilisateur (mention ou réponse)", inline=False)
    embed.add_field(name="+mute @utilisateur1 [@utilisateur2...] [raison]", value="Mute un ou plusieurs utilisateurs et sauvegarde leurs rôles", inline=False)
    embed.add_field(name="+unmute @utilisateur/all [raison]", value="Démute et restaure automatiquement les rôles sauvegardés", inline=False)
    embed.add_field(name="+lock [all] [raison]", value="Verrouille le salon actuel ou tous les salons", inline=False)
    embed.add_field(name="+unlock [all] [raison]", value="Déverrouille le salon actuel ou tous les salons", inline=False)
    embed.add_field(name="+commandes", value="Affiche cette liste de commandes", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN non trouvé!")
    else:
        logger.info("🚀 Démarrage du bot...")
        bot.run(token)