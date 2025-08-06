import discord
from discord.ext import commands
import os

# Récupérer le token depuis la variable d'environnement
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    # Envoyer un message dans le canal spécifique lorsque le bot redémarre
    channel = bot.get_channel(1401557235871649873)
    if channel:
        await channel.send("🔄 L'instance du bot a redémarré ou s'est lancée avec succès!")

# Commande +help
@bot.command()
async def bothelp(ctx):
    embed = discord.Embed(
        title="🛡️ Commandes du Bot",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="+ban", value="Bannir un utilisateur. Usage: `+ban @utilisateur [raison]`", inline=False)
    embed.add_field(name="+unban", value="Débannir un utilisateur. Usage: `+unban ID_utilisateur`", inline=False)
    embed.add_field(name="+kick", value="Expulser un utilisateur. Usage: `+kick @utilisateur [raison]`", inline=False)
    embed.add_field(name="+lockall", value="Verrouiller tous les salons textuels.", inline=False)
    embed.add_field(name="+unlockall", value="Déverrouiller tous les salons textuels.", inline=False)
    embed.add_field(name="+lock all", value="Verrouiller tous les salons textuels. Usage: `+lock all`", inline=False)
    embed.add_field(name="+unlock all", value="Déverrouiller tous les salons textuels. Usage: `+unlock all`", inline=False)
    
    await ctx.send(embed=embed)

# Commande +ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if not member:
        await ctx.send("❌ Veuillez mentionner un utilisateur à bannir.")
        return
    if not reason:
        reason = f"Banni par {ctx.author}"
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été banni pour la raison suivante : {reason}")

# Commande +unban
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user} a été débanni.")
    except discord.NotFound:
        await ctx.send("❌ Utilisateur non trouvé.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.")

# Commande +kick
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason=None):
    if not member:
        await ctx.send("❌ Veuillez mentionner un utilisateur à expulser.")
        return
    if not reason:
        reason = f"Expulsé par {ctx.author}"
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été expulsé pour la raison suivante : {reason}")

# Commande +lockall
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockall(ctx):
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Tous les salons textuels sont maintenant verrouillés.")

# Commande +unlockall
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockall(ctx):
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Tous les salons textuels sont maintenant déverrouillés.")

# Commandes avec espace dans le nom (lock all et unlock all)
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, *, option=None):
    if option == "all":
        await lockall(ctx)
    else:
        await ctx.send("❌ Usage incorrect, utilisez `+lock all`.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, *, option=None):
    if option == "all":
        await unlockall(ctx)
    else:
        await ctx.send("❌ Usage incorrect, utilisez `+unlock all`.")

# Lancer le bot
bot.run(TOKEN)
