import discord
from discord.ext import commands
import logging
import os
from datetime import datetime

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Création du bot avec le préfixe + et désactivation de la commande help par défaut
bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# ID du channel pour le message de redémarrage
RESTART_CHANNEL_ID = 1401557235871649873

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    logger.info(f"Bot connecté sous le nom {bot.user}")
    channel = bot.get_channel(RESTART_CHANNEL_ID)
    if channel:
        await channel.send("🔄 **Le bot a redémarré avec succès !**")

# Commande +ping
@bot.command(name='ping')
async def ping(ctx):
    """Commande de test de latence"""
    embed = discord.Embed(
        title="🏓 **Pong!**",
        description=f"🏓 Latence du bot : {round(bot.latency * 1000)} ms",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Commande +ping")
    await ctx.send(embed=embed)

# Commande +test
@bot.command(name='test')
async def test(ctx):
    """Commande pour tester que tout fonctionne"""
    embed = discord.Embed(
        title="✅ **Test de fonctionnement**",
        description="Le bot fonctionne correctement et répond à la commande +test.",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Commande +test")
    await ctx.send(embed=embed)

# Commande d'aide personnalisée pour remplacer la commande native 'help'
@bot.command(name='help')
async def help_command(ctx):
    """Affiche les commandes disponibles"""
    embed = discord.Embed(
        title="🛠️ **Aide - Commandes du Bot**",
        description="Voici la liste des commandes disponibles pour gérer le serveur.",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🔨 **+ban**",
        value="Bannir un utilisateur. Usage : `+ban @utilisateur [raison]`",
        inline=False
    )
    
    embed.add_field(
        name="🔓 **+unban**",
        value="Débannir un utilisateur. Usage : `+unban [ID/nom#discriminator]`",
        inline=False
    )
    
    embed.add_field(
        name="👢 **+kick**",
        value="Expulser un utilisateur. Usage : `+kick @utilisateur [raison]`",
        inline=False
    )
    
    embed.add_field(
        name="📊 **+ping**",
        value="Vérifier la latence du bot.",
        inline=False
    )
    
    embed.add_field(
        name="💬 **+test**",
        value="Vérifier que le bot fonctionne correctement.",
        inline=False
    )
    
    embed.add_field(
        name="🔒 **+lock**",
        value="Verrouiller un canal (empêche l'envoi de messages). Usage : `+lock #canal`",
        inline=False
    )
    
    embed.add_field(
        name="🔓 **+unlock**",
        value="Déverrouiller un canal (permet l'envoi de messages). Usage : `+unlock #canal`",
        inline=False
    )

    embed.add_field(
        name="🔒🔓 **+lock all**",
        value="Verrouiller tous les canaux du serveur.",
        inline=False
    )

    embed.add_field(
        name="🔓🔒 **+unlock all**",
        value="Déverrouiller tous les canaux du serveur.",
        inline=False
    )

    embed.set_footer(text="Bot de modération - +help")
    await ctx.send(embed=embed)

# Commande +lock
@bot.command(name='lock')
async def lock(ctx, channel: discord.TextChannel = None):
    """Verrouiller un canal spécifique"""
    if not channel:
        channel = ctx.channel  # Si aucun canal n'est mentionné, utiliser le canal actuel
    
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="🔒 **Canal Verrouillé**",
            description=f"Le canal {channel.mention} est maintenant verrouillé. Les membres ne peuvent plus envoyer de messages.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du verrouillage du canal : {str(e)}")

# Commande +unlock
@bot.command(name='unlock')
async def unlock(ctx, channel: discord.TextChannel = None):
    """Déverrouiller un canal spécifique"""
    if not channel:
        channel = ctx.channel  # Si aucun canal n'est mentionné, utiliser le canal actuel
    
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="🔓 **Canal Déverrouillé**",
            description=f"Le canal {channel.mention} est maintenant déverrouillé. Les membres peuvent à nouveau envoyer des messages.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du déverrouillage du canal : {str(e)}")

# Commande +lock all
@bot.command(name='lock all')
async def lock_all(ctx):
    """Verrouiller tous les canaux du serveur"""
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du verrouillage du canal {channel.mention}: {str(e)}")
    
    embed = discord.Embed(
        title="🔒 **Tous les canaux ont été verrouillés**",
        description="Tous les canaux de ce serveur sont maintenant verrouillés.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande +unlock all
@bot.command(name='unlock all')
async def unlock_all(ctx):
    """Déverrouiller tous les canaux du serveur"""
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du déverrouillage du canal {channel.mention}: {str(e)}")
    
    embed = discord.Embed(
        title="🔓 **Tous les canaux ont été déverrouillés**",
        description="Tous les canaux de ce serveur sont maintenant déverrouillés.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Lancer le bot avec le token depuis la variable d'environnement
bot.run(os.getenv('DISCORD_TOKEN'))
