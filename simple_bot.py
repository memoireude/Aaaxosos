import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents)

# Stocke les salons verrouillés
locked_channels = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} est connecté !')

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
        value="Déverrouille tous les salons qui ont été verrouillés.",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='lock')
async def lock(ctx, channel: discord.TextChannel = None):
    """Verrouille un salon spécifique"""
    channel = channel or ctx.channel
    overwrites = channel.overwrites_for(ctx.guild.default_role)
    
    # Vérifie si le salon est déjà verrouillé
    if overwrites.read_messages is False:
        await ctx.send(embed=discord.Embed(
            title="🔒 Salon déjà verrouillé",
            description=f"Le salon {channel.mention} est déjà verrouillé.",
            color=discord.Color.red()
        ))
        return
    
    await channel.set_permissions(ctx.guild.default_role, read_messages=False)
    
    # Sauvegarde l'état verrouillé
    locked_channels[channel.id] = 'locked'
    
    await ctx.send(embed=discord.Embed(
        title="🔒 Salon verrouillé",
        description=f"Le salon {channel.mention} a été verrouillé avec succès.",
        color=discord.Color.green()
    ))

@bot.command(name='unlock')
async def unlock(ctx, channel: discord.TextChannel = None):
    """Déverrouille un salon spécifique"""
    channel = channel or ctx.channel
    overwrites = channel.overwrites_for(ctx.guild.default_role)

    # Vérifie si le salon est déjà déverrouillé
    if overwrites.read_messages is None or overwrites.read_messages is True:
        await ctx.send(embed=discord.Embed(
            title="🔓 Salon déjà déverrouillé",
            description=f"Le salon {channel.mention} est déjà déverrouillé.",
            color=discord.Color.red()
        ))
        return
    
    await channel.set_permissions(ctx.guild.default_role, read_messages=True)
    
    # Supprime l'état verrouillé
    if channel.id in locked_channels:
        del locked_channels[channel.id]
    
    await ctx.send(embed=discord.Embed(
        title="🔓 Salon déverrouillé",
        description=f"Le salon {channel.mention} a été déverrouillé avec succès.",
        color=discord.Color.green()
    ))

@bot.command(name='lockall')
async def lockall(ctx):
    """Verrouille tous les salons"""
    for channel in ctx.guild.text_channels:
        if channel.id not in locked_channels:  # Verrouille seulement les salons qui ne sont pas déjà verrouillés
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            locked_channels[channel.id] = 'locked'
    
    await ctx.send(embed=discord.Embed(
        title="🔒 Tous les salons ont été verrouillés",
        description="Tous les salons ont été verrouillés avec succès.",
        color=discord.Color.green()
    ))

@bot.command(name='unlockall')
async def unlockall(ctx):
    """Déverrouille tous les salons"""
    for channel in ctx.guild.text_channels:
        if channel.id in locked_channels:  # Déverrouille seulement les salons qui ont été verrouillés
            await channel.set_permissions(ctx.guild.default_role, read_messages=True)
            del locked_channels[channel.id]
    
    await ctx.send(embed=discord.Embed(
        title="🔓 Tous les salons ont été déverrouillés",
        description="Tous les salons verrouillés ont été déverrouillés avec succès.",
        color=discord.Color.green()
    ))

bot.run(os.getenv('DISCORD_TOKEN'))
