import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)

# Dictionnaire pour stocker l'état des salons verrouillés
locked_channels = {}

@bot.event
async def on_ready():
    """Notifie quand le bot est prêt et connecté."""
    print(f'Bot {bot.user} est connecté !')
    
    # Envoie un message dans un channel spécifique lors du redémarrage du bot
    channel_id = 1401557235871649873  # ID du channel où envoyer le message
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send("Le bot a redémarré avec succès!")

@bot.command(name='ping')
async def ping(ctx):
    """Teste la latence du bot."""
    latency = round(bot.latency * 1000)  # Latence en ms
    await ctx.send(embed=discord.Embed(
        title="Pong!",
        description=f"Latence : {latency}ms",
        color=discord.Color.green()
    ))

@bot.command(name='test')
async def test(ctx):
    """Commande de test pour vérifier que le bot fonctionne."""
    await ctx.send(embed=discord.Embed(
        title="Test réussi",
        description="Le bot fonctionne correctement !",
        color=discord.Color.green()
    ))

@bot.command(name='help')
async def help_command(ctx):
    """Affiche la liste des commandes disponibles"""
    embed = discord.Embed(
        title="🛡️ Aide du bot de modération",
        description="Liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔒 +lock",
        value="Verrouille un salon spécifique. Utilisation : `+lock [channel]`",
        inline=False
    )
    embed.add_field(
        name="🔓 +unlock",
        value="Déverrouille un salon spécifique. Utilisation : `+unlock [channel]`",
        inline=False
    )
    embed.add_field(
        name="🔒 +lockall",
        value="Verrouille tous les salons. Seuls les salons non verrouillés seront affectés.",
        inline=False
    )
    embed.add_field(
        name="🔓 +unlockall",
        value="Déverrouille tous les salons verrouillés. Les utilisateurs pourront envoyer des messages dans ces salons.",
        inline=False
    )
    embed.add_field(
        name="⚒️ +ban",
        value="Bannit un utilisateur. Utilisation : `+ban @utilisateur [raison]`",
        inline=False
    )
    embed.add_field(
        name="⚒️ +kick",
        value="Expulse un utilisateur. Utilisation : `+kick @utilisateur [raison]`",
        inline=False
    )
    embed.add_field(
        name="⚡ +ping",
        value="Teste la latence du bot.",
        inline=False
    )
    embed.add_field(
        name="🔑 +test",
        value="Commande de test pour vérifier que le bot fonctionne.",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bannir un utilisateur"""
    reason = reason or "Aucune raison fournie"
    await member.ban(reason=reason)
    await ctx.send(embed=discord.Embed(
        title="🔨 Utilisateur banni",
        description=f"{member.mention} a été banni pour : {reason}",
        color=discord.Color.red()
    ))

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Expulser un utilisateur"""
    reason = reason or "Aucune raison fournie"
    await member.kick(reason=reason)
    await ctx.send(embed=discord.Embed(
        title="👢 Utilisateur expulsé",
        description=f"{member.mention} a été expulsé pour : {reason}",
        color=discord.Color.orange()
    ))

@bot.command(name='lock')
async def lock(ctx, channel: discord.TextChannel = None):
    """Verrouille un salon spécifique en désactivant la possibilité d'envoyer des messages"""
    channel = channel or ctx.channel

    # Si le salon est déjà verrouillé, on ne fait rien
    if channel.id in locked_channels:
        await ctx.send(embed=discord.Embed(
            title="🔒 Salon déjà verrouillé",
            description=f"Le salon {channel.mention} est déjà verrouillé.",
            color=discord.Color.red()
        ))
        return

    # Modifie les permissions pour empêcher les messages
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    # Sauvegarde l'état du salon
    locked_channels[channel.id] = True

    await ctx.send(embed=discord.Embed(
        title="🔒 Salon verrouillé",
        description=f"Le salon {channel.mention} est désormais verrouillé. Personne ne peut y envoyer de messages.",
        color=discord.Color.green()
    ))

@bot.command(name='unlock')
async def unlock(ctx, channel: discord.TextChannel = None):
    """Déverrouille un salon spécifique en rétablissant la possibilité d'envoyer des messages"""
    channel = channel or ctx.channel

    # Si le salon n'est pas verrouillé, on ne fait rien
    if channel.id not in locked_channels:
        await ctx.send(embed=discord.Embed(
            title="🔓 Salon déjà déverrouillé",
            description=f"Le salon {channel.mention} est déjà déverrouillé.",
            color=discord.Color.red()
        ))
        return

    # Rétablit la permission d'envoyer des messages
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)

    # Supprime l'état de verrouillage du salon
    del locked_channels[channel.id]

    await ctx.send(embed=discord.Embed(
        title="🔓 Salon déverrouillé",
        description=f"Le salon {channel.mention} a été déverrouillé. Les utilisateurs peuvent maintenant y envoyer des messages.",
        color=discord.Color.green()
    ))

@bot.command(name='lockall')
async def lockall(ctx):
    """Verrouille tous les salons en désactivant la possibilité d'envoyer des messages"""
    for channel in ctx.guild.text_channels:
        # Si le salon n'est pas déjà verrouillé, verrouille-le
        if channel.id not in locked_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            locked_channels[channel.id] = True

    await ctx.send(embed=discord.Embed(
        title="🔒 Tous les salons ont été verrouillés",
        description="Tous les salons qui n'étaient pas déjà verrouillés sont maintenant verrouillés. Personne ne peut envoyer de messages.",
        color=discord.Color.green()
    ))

@bot.command(name='unlockall')
async def unlockall(ctx):
    """Déverrouille tous les salons verrouillés en rétablissant la possibilité d'envoyer des messages"""
    for channel in ctx.guild.text_channels:
        if channel.id in locked_channels:
            # Réactive la possibilité d'envoyer des messages pour les salons verrouillés
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            del locked_channels[channel.id]

    await ctx.send(embed=discord.Embed(
        title="🔓 Tous les salons ont été déverrouillés",
        description="Tous les salons verrouillés sont maintenant déverrouillés. Les utilisateurs peuvent envoyer des messages dans ces salons.",
        color=discord.Color.green()
    ))

bot.run(os.getenv('DISCORD_TOKEN'))
