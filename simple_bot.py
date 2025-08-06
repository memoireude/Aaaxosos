import discord
from discord.ext import commands
import logging
from datetime import datetime

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Création du bot avec le préfixe +
bot = commands.Bot(command_prefix='+', intents=intents)

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

# Commande +help personnalisée
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

    embed.set_footer(text="Bot de modération - +help")
    await ctx.send(embed=embed)

# Commande +ban
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member = None, *, reason=None):
    """Bannir un utilisateur"""
    if member is None:
        embed = discord.Embed(
            title="❌ **Erreur**",
            description="Vous devez mentionner un utilisateur à bannir ! Exemple : `+ban @utilisateur [raison]`",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Commande +ban")
        await ctx.send(embed=embed)
        return

    if reason is None:
        reason = "Aucune raison fournie."

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 **Utilisateur banni**",
            description=f"{member} a été banni avec succès.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        logger.info(f"{member} a été banni pour: {reason}")
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ **Erreur**",
            description="Je n'ai pas les permissions nécessaires pour bannir cet utilisateur.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Commande +ban")
        await ctx.send(embed=embed)

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
            embed = discord.Embed(
                title="❌ **Erreur**",
                description=f"Utilisateur `{user_info}` non trouvé parmi les bannis.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.guild.unban(target_user)
        embed = discord.Embed(
            title="🔓 **Utilisateur débanni**",
            description=f"{target_user} a été débanni du serveur.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
        logger.info(f"{target_user} a été débanni.")
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ **Erreur**",
            description="Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)

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
            title="👢 **Utilisateur expulsé**",
            description=f"{member} a été expulsé du serveur.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        logger.info(f"{member} a été expulsé pour: {reason}")
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ **Erreur**",
            description="Je n'ai pas les permissions nécessaires pour expulser cet utilisateur.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)

# Commandes lockall et unlockall
@bot.command(name='lockall')
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def lock_all(ctx):
    """Verrouiller tous les canaux"""
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🔒 **Canaux verrouillés**",
        description="Tous les canaux du serveur ont été verrouillés.",
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
        title="🔓 **Canaux déverrouillés**",
        description="Tous les canaux du serveur ont été déverrouillés.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Lancer le bot
bot.run('DISCORD_TOKEN')
