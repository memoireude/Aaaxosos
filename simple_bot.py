import discord
from discord.ext import commands
import logging
import os

# Configuration du logging (utile sur Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Création du bot
bot = commands.Bot(command_prefix='+', intents=intents)

# =================== Événements ===================

@bot.event
async def on_ready():
    logger.info(f"✅ Bot connecté en tant que {bot.user}")
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Argument manquant.")
    elif isinstance(error, commands.CommandNotFound):
        return  # On ignore les commandes inconnues
    else:
        await ctx.send(f"❌ Erreur : {str(error)}")
        logger.error(f"Erreur inconnue : {str(error)}")

# =================== Commandes Utiles ===================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong !")

@bot.command()
async def test(ctx):
    await ctx.send("✅ Le bot fonctionne correctement !")

# =================== Commandes Modération ===================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🥾 {member} a été expulsé. Raison : {reason or 'Aucune'}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} a été banni. Raison : {reason or 'Aucune'}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user):
    banned_users = await ctx.guild.bans()
    name, discriminator = user.split('#')

    for ban_entry in banned_users:
        if ban_entry.user.name == name and ban_entry.user.discriminator == discriminator:
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f"✅ {user} a été débanni.")
            return

    await ctx.send(f"❌ Utilisateur {user} non trouvé dans la liste des bannis.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Le salon est maintenant verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Le salon est maintenant déverrouillé.")

# =================== Lancement du bot ===================

TOKEN = os.getenv("DISCORD_TOKEN")  # Mets ton token dans les variables Render
if not TOKEN:
    logger.error("❌ Le token n'est pas défini. Ajoute DISCORD_TOKEN dans tes variables Render.")
else:
    bot.run(TOKEN)
