import discord
from discord.ext import commands
import logging
import os

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intents requis
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Préfixe et création du bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    logger.info(f'✅ Connecté en tant que {bot.user} !')
    logger.info(f'🔗 Connecté à {len(bot.guilds)} serveur(s)')

# Aide personnalisée
@bot.command(name='help')
async def custom_help(ctx):
    help_text = (
        "**📖 Commandes disponibles :**\n"
        "🔹 `+ping` → Vérifie si le bot est en ligne\n"
        "🔹 `+test` → Répond avec un message de test\n"
        "🔹 `+ban @user` → Bannir un membre\n"
        "🔹 `+kick @user` → Expulser un membre\n"
        "🔹 `+lock` → Verrouille le salon actuel\n"
        "🔹 `+unlock` → Déverrouille le salon actuel\n"
        "🔹 `+lockall` → Verrouille tous les salons textuels\n"
        "🔹 `+unlockall` → Déverrouille tous les salons textuels\n"
    )
    await ctx.send(help_text)

# Commande ping
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('🏓 Pong ! Le bot fonctionne.')

# Commande test
@bot.command(name='test')
async def test(ctx):
    await ctx.send('✅ Test réussi !')

# Commande ban
@commands.has_permissions(ban_members=True)
@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} a été banni.")

# Commande kick
@commands.has_permissions(kick_members=True)
@bot.command(name='kick')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} a été expulsé.")

# Commande lock (salon actuel)
@commands.has_permissions(manage_channels=True)
@bot.command(name='lock')
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Ce salon a été verrouillé.")

# Commande unlock (salon actuel)
@commands.has_permissions(manage_channels=True)
@bot.command(name='unlock')
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Ce salon a été déverrouillé.")

# Commande lockall (verrouille tous les salons textuels)
@commands.has_permissions(manage_channels=True)
@bot.command(name='lockall')
async def lockall(ctx):
    for channel in ctx.guild.text_channels:
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Tous les salons textuels ont été verrouillés.")

# Commande unlockall (déverrouille tous les salons textuels)
@commands.has_permissions(manage_channels=True)
@bot.command(name='unlockall')
async def unlockall(ctx):
    for channel in ctx.guild.text_channels:
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Tous les salons textuels ont été déverrouillés.")

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Commande inconnue: `{ctx.message.content}`. Tapez `+help` pour voir les commandes.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Il manque un argument.")
    else:
        logger.error(f"Erreur inattendue : {error}")
        await ctx.send("❌ Une erreur est survenue.")

# Lancement du bot
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Token non trouvé dans les variables d'environnement.")
