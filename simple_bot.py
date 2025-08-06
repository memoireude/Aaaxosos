import discord
from discord.ext import commands
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Bot
bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f'✅ Bot connecté en tant que {bot.user} sur {len(bot.guilds)} serveur(s) !')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Commande inconnue: `{ctx.message.content}`. Tapez `+help` pour voir les commandes disponibles.")
    else:
        logger.error(f"Erreur: {error}")
        await ctx.send(f"❌ Une erreur est survenue : {error}")

# ========== Commandes ==========

@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong ! Le bot fonctionne correctement.')

@bot.command()
async def test(ctx):
    await ctx.send('✅ Test réussi !')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée."):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} a été banni. Raison : {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison spécifiée."):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} a été kick. Raison : {reason}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 Le salon {channel.mention} a été verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"🔓 Le salon {channel.mention} a été déverrouillé.")

@bot.command(name='lockall')
@commands.has_permissions(manage_channels=True)
async def lock_all(ctx):
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Tous les salons textuels ont été verrouillés.")

@bot.command(name='unlockall')
@commands.has_permissions(manage_channels=True)
async def unlock_all(ctx):
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Tous les salons textuels ont été déverrouillés.")

@bot.command(name='help')
async def custom_help(ctx):
    embed = discord.Embed(title="📖 Commandes disponibles", color=0x3498db)
    embed.add_field(name="+ping", value="Vérifie si le bot fonctionne.", inline=False)
    embed.add_field(name="+test", value="Commande de test.", inline=False)
    embed.add_field(name="+ban @membre [raison]", value="Ban un membre.", inline=False)
    embed.add_field(name="+kick @membre [raison]", value="Kick un membre.", inline=False)
    embed.add_field(name="+lock", value="Verrouille le salon actuel.", inline=False)
    embed.add_field(name="+unlock", value="Déverrouille le salon actuel.", inline=False)
    embed.add_field(name="+lockall", value="Verrouille tous les salons textuels.", inline=False)
    embed.add_field(name="+unlockall", value="Déverrouille tous les salons textuels.", inline=False)
    await ctx.send(embed=embed)

# ========== Démarrage ==========
# Remplace os.getenv("TOKEN") par ton token si tu ne l’utilises pas via .env
import os
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ TOKEN manquant. Assure-toi d'avoir mis le token dans l'environnement.")
else:
    bot.run(TOKEN)
