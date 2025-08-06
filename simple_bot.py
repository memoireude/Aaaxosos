import discord
from discord.ext import commands
import logging
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Configuration du bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Logger pour garder trace des événements
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# ID du channel pour envoyer les notifications de redémarrage
RESTART_CHANNEL_ID = 1401557235871649873

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    logger.info(f"Bot connecté sous le nom {bot.user}")
    channel = bot.get_channel(RESTART_CHANNEL_ID)
    if channel:
        await channel.send("🔄 **Le bot a redémarré !**")

# Commande +ping
@bot.command(name='ping')
async def ping(ctx):
    """Commande de test de latence"""
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"🏓 Latence : {round(bot.latency * 1000)}ms",
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
        title="✅ Test",
        description="Le bot fonctionne correctement !",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Commande +test")
    await ctx.send(embed=embed)

# Commande +help (personnalisée)
@bot.command(name='help')
async def help_command(ctx):
    """Affiche les commandes disponibles"""
    embed = discord.Embed(
        title="🛠️ Aide - Commandes du Bot",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🔨 +ban",
        value="Bannir un utilisateur. Usage: `+ban @utilisateur [raison]`",
        inline=False
    )
    
    embed.add_field(
        name="🔓 +unban",
        value="Débannir un utilisateur. Usage: `+unban [ID/nom#discriminator]`",
        inline=False
    )
    
    embed.add_field(
        name="👢 +kick",
        value="Expulser un utilisateur. Usage: `+kick @utilisateur [raison]`",
        inline=False
    )
    
    embed.add_field(
        name="📊 +ping",
        value="Vérifier la latence du bot.",
        inline=False
    )
    
    embed.add_field(
        name="💬 +test",
        value="Vérifier que le bot fonctionne.",
        inline=False
    )
    
    embed.set_footer(text="Bot de modération - +help")
    await ctx.send(embed=embed)

# Commande +ban
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member = None, *, reason=None):
    """Bannir un utilisateur"""
    if member is None:
        await ctx.send("❌ Veuillez mentionner un utilisateur à bannir !")
        return

    if reason is None:
        reason = "Aucune raison fournie."

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Utilisateur banni",
            description=f"{member} a été banni avec succès.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        logger.info(f"{member} a été banni pour: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour bannir cet utilisateur.")

# Commande +unban
@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def unban_user(ctx, user_info: str):
    """Débannir un utilisateur"""
    try:
        banned_users = await ctx.guild.bans()
        target_user = None
        for ban_entry in banned_users:
            if user_info.lower() in str(ban_entry.user).lower():
                target_user = ban_entry.user
                break

        if target_user is None:
            await ctx.send("❌ Utilisateur non trouvé parmi les bannis.")
            return
        
        await ctx.guild.unban(target_user)
        embed = discord.Embed(
            title="🔓 Utilisateur débanni",
            description=f"{target_user} a été débanni du serveur.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
        logger.info(f"{target_user} a été débanni.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.")

# Commande +kick
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member, *, reason=None):
    """Expulser un utilisateur"""
    if reason is None:
        reason = "Aucune raison fournie."
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Utilisateur expulsé",
            description=f"{member} a été expulsé.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        logger.info(f"{member} a été expulsé pour: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour expulser cet utilisateur.")

# Commandes lock/unlock all
@bot.command(name='lockall')
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def lock_all(ctx):
    """Verrouiller tous les canaux"""
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🔒 Canaux verrouillés",
        description="Tous les canaux ont été verrouillés.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name='unlockall')
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def unlock_all(ctx):
    """Déverrouiller tous les canaux"""
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(
        title="🔓 Canaux déverrouillés",
        description="Tous les canaux ont été déverrouillés.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande pour envoyer un message de redémarrage
@bot.event
async def on_ready():
    channel = bot.get_channel(RESTART_CHANNEL_ID)
    if channel:
        await channel.send("🔄 Le bot a redémarré avec succès !")

# Lancer le bot
bot.run('DISCORD_TOKEN')
