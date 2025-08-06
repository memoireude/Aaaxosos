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
async def on_message(message):
    # Ignorer les messages du bot
    if message.author == bot.user:
        return

    # Traitement des commandes
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Ne rien faire pour les commandes inconnues
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

# Commandes simples pour tester le bot

@bot.command(name='ping')
async def ping(ctx):
    logger.info(f"COMMANDE PING exécutée par {ctx.author}")
    await ctx.send('🏓 Pong! Le bot fonctionne!')

@bot.command(name='test')
async def test(ctx):
    logger.info(f"COMMANDE TEST exécutée par {ctx.author}")
    await ctx.send('✅ Test réussi! Le bot répond correctement.')

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

# Initialisation du token
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN non trouvé!")
    else:
        logger.info("🚀 Démarrage du bot...")
        bot.run(token)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
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
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour bannir quelqu'un!")
            return
    
    try:
        await member.ban(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"🔨 {member} a été banni! Raison: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du ban: {e}")
        logger.error(f"ERREUR BAN: {e}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        if ctx.message.reference and ctx.message.reference.message_id:
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
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message pour expulser quelqu'un!")
            return
    
    try:
        await member.kick(reason=f"{reason} - Par {ctx.author}")
        await ctx.send(f"👢 {member} a été expulsé! Raison: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du kick: {e}")
        logger.error(f"ERREUR KICK: {e}")

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, *args):
    if not args:
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
        members = []
        reason_parts = []
        for arg in args:
            try:
                member = await commands.MemberConverter().convert(ctx, arg)
                members.append(member)
            except commands.BadArgument:
                reason_parts.append(arg)
        
        reason = " ".join(reason_parts) if reason_parts else "Aucune raison spécifiée"
        
        if not members:
            await ctx.send("❌ Aucun membre valide trouvé dans votre commande!")
            return
    
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        await ctx.send("❌ Aucun rôle 'Muted' trouvé sur ce serveur!")
        return
    
    for member in members:
        try:
            if muted_role in member.roles:
                continue
            old_roles = [role.id for role in member.roles if role != ctx.guild.default_role]
            if old_roles:
                muted_users_roles[member.id] = old_roles
            new_roles = [ctx.guild.default_role, muted_role]
            await member.edit(roles=new_roles, reason=f"Mute - {reason} - Par {ctx.author}")
            await ctx.send(f"🔇 {member} a été mute! Raison: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du mute de {member}: {e}")
            logger.error(f"ERREUR MUTE: {e} pour {member}")
            
            bot.run(os.getenv("DISCORD_TOKEN"))
