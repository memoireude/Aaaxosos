import discord
from discord.ext import commands
from datetime import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

# Commande +help
@bot.command(name='help')
async def help_command(ctx):
    """Affiche la liste des commandes disponibles"""
    embed = discord.Embed(
        title="🛡️ Commandes disponibles",
        description="Voici la liste des commandes disponibles dans ce bot de modération :",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🔨 +ban", value="Bannir un utilisateur", inline=False)
    embed.add_field(name="🔓 +unban", value="Débannir un utilisateur", inline=False)
    embed.add_field(name="👢 +kick", value="Expulser un utilisateur", inline=False)
    embed.add_field(name="🔒 +lock", value="Verrouiller un canal", inline=False)
    embed.add_field(name="🔓 +unlock", value="Déverrouiller un canal", inline=False)
    embed.add_field(name="🔒 +lockall", value="Verrouiller tous les canaux", inline=False)
    embed.add_field(name="🔓 +unlockall", value="Déverrouiller tous les canaux", inline=False)
    embed.add_field(name="📶 +ping", value="Vérifier la latence du bot", inline=False)
    embed.add_field(name="🛠️ +test", value="Commande de test", inline=False)
    
    embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

# Commande +ping
@bot.command(name='ping')
async def ping(ctx):
    """Commande pour vérifier la latence du bot"""
    embed = discord.Embed(
        title="📶 Ping",
        description=f"Latence du bot : {round(bot.latency * 1000)}ms",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande +test
@bot.command(name='test')
async def test(ctx):
    """Commande de test"""
    embed = discord.Embed(
        title="🛠️ Test",
        description="Commande de test exécutée avec succès !",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande +lock
@bot.command(name='lock')
async def lock_channel(ctx, channel: discord.TextChannel = None):
    """Verrouiller un canal spécifique"""
    if not channel:
        await ctx.send("❌ Vous devez mentionner un canal à verrouiller.")
        return

    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="🔒 Canal verrouillé",
            description=f"Le canal {channel.mention} a été verrouillé. Les membres ne peuvent plus envoyer de messages.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du verrouillage du canal {channel.mention}: {str(e)}")

# Commande +unlock
@bot.command(name='unlock')
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    """Déverrouiller un canal spécifique"""
    if not channel:
        await ctx.send("❌ Vous devez mentionner un canal à déverrouiller.")
        return

    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="🔓 Canal déverrouillé",
            description=f"Le canal {channel.mention} a été déverrouillé. Les membres peuvent envoyer des messages.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du déverrouillage du canal {channel.mention}: {str(e)}")

# Commande +lockall
@bot.command(name='lockall')
async def lock_all(ctx):
    """Verrouiller tous les canaux du serveur"""
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du verrouillage du canal {channel.mention}: {str(e)}")
    
    embed = discord.Embed(
        title="🔒 Tous les canaux ont été verrouillés",
        description="Tous les canaux de ce serveur sont maintenant verrouillés. Les membres ne peuvent plus envoyer de messages.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande +unlockall
@bot.command(name='unlockall')
async def unlock_all(ctx):
    """Déverrouiller tous les canaux du serveur"""
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du déverrouillage du canal {channel.mention}: {str(e)}")
    
    embed = discord.Embed(
        title="🔓 Tous les canaux ont été déverrouillés",
        description="Tous les canaux de ce serveur sont maintenant déverrouillés. Les membres peuvent à nouveau envoyer des messages.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

# Commande +ban
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member = None, *, reason=None):
    """Bannir un utilisateur"""
    if not member:
        await ctx.send("❌ Vous devez mentionner un utilisateur à bannir.")
        return

    reason = reason or f"Banni par {ctx.author}"
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Utilisateur banni",
            description=f"{member.mention} a été banni pour : {reason}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du bannissement de {member.mention}: {str(e)}")

# Commande +unban
@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_user(ctx, user_id: int = None):
    """Débannir un utilisateur par ID"""
    if not user_id:
        await ctx.send("❌ Vous devez fournir un ID d'utilisateur à débannir.")
        return

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        embed = discord.Embed(
            title="🔓 Utilisateur débanni",
            description=f"{user.mention} a été débanni du serveur.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du débannissement de l'utilisateur {user_id}: {str(e)}")

# Commande +kick
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member = None, *, reason=None):
    """Expulser un utilisateur"""
    if not member:
        await ctx.send("❌ Vous devez mentionner un utilisateur à expulser.")
        return

    reason = reason or f"Expulsé par {ctx.author}"
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Utilisateur expulsé",
            description=f"{member.mention} a été expulsé pour : {reason}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'expulsion de {member.mention}: {str(e)}")

# Événement pour annoncer le redémarrage du bot
@bot.event
async def on_ready():
    channel = bot.get_channel(1401557235871649873)  # ID du channel
    if channel:
        await channel.send("🛠️ Le bot a redémarré avec succès!")
    print(f'Bot connecté en tant que {bot.user}')

# Utilisation de la variable d'environnement pour récupérer le token
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN:
    bot.run(TOKEN)
else:
    print("Erreur : le token Discord n'a pas été trouvé.")
