import discord
from discord.ext import commands
import logging
from datetime import datetime
import os

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Configuration du bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Logger pour le bot
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ID du channel où les notifications de redémarrage/arrêt seront envoyées
NOTIFY_CHANNEL_ID = 1401557235871649873

@bot.event
async def on_ready():
    """Message de notification lorsque le bot est prêt"""
    logger.info(f'{bot.user} est maintenant en ligne et prêt à exécuter des commandes!')
    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if channel:
        await channel.send(f'🔵 {bot.user} vient de démarrer !')

@bot.event
async def on_disconnect():
    """Message de notification lorsque le bot se déconnecte"""
    logger.info(f'{bot.user} a été déconnecté!')
    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if channel:
        await channel.send(f'🔴 {bot.user} a été déconnecté.')

@bot.command(name='help')
async def help_command(ctx):
    """Commande d'aide pour afficher les commandes disponibles"""
    embed = discord.Embed(
        title="🛡️ Aide du Bot de Modération",
        description="Voici les commandes disponibles :",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.add_field(name="🔨 +ban", value="Bannir un utilisateur. Usage: `+ban @utilisateur [raison]`", inline=False)
    embed.add_field(name="🔓 +unban", value="Débannir un utilisateur. Usage: `+unban ID_utilisateur`", inline=False)
    embed.add_field(name="👢 +kick", value="Expulser un utilisateur. Usage: `+kick @utilisateur [raison]`", inline=False)
    embed.add_field(name="🔒 +lock", value="Verrouiller un channel. Usage: `+lock`", inline=False)
    embed.add_field(name="🔓 +unlock", value="Déverrouiller un channel. Usage: `+unlock`", inline=False)
    embed.add_field(name="🔒 +lockall", value="Verrouiller tous les channels. Usage: `+lockall`", inline=False)
    embed.add_field(name="🔓 +unlockall", value="Déverrouiller tous les channels. Usage: `+unlockall`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member, *, reason=None):
    """Commande pour bannir un utilisateur"""
    if not reason:
        reason = "Aucune raison fournie."
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été banni pour : {reason}")

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_user(ctx, user_id: int):
    """Commande pour débannir un utilisateur par son ID"""
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} a été débanni!")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member, *, reason=None):
    """Commande pour expulser un utilisateur"""
    if not reason:
        reason = "Aucune raison fournie."
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été expulsé pour : {reason}")

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    """Verrouille un channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 Le channel {ctx.channel.mention} a été verrouillé.")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    """Déverrouille un channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"🔓 Le channel {ctx.channel.mention} a été déverrouillé.")

@bot.command(name='lockall')
@commands.has_permissions(manage_channels=True)
async def lock_all_channels(ctx):
    """Verrouille tous les channels"""
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Tous les channels ont été verrouillés.")

@bot.command(name='unlockall')
@commands.has_permissions(manage_channels=True)
async def unlock_all_channels(ctx):
    """Déverrouille tous les channels"""
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Tous les channels ont été déverrouillés.")

# Ne pas oublier de mettre le token du bot dans les variables d'environnement
bot.run(os.getenv("DISCORD_TOKEN"))
