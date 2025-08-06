import discord
from discord.ext import commands
import logging
from datetime import datetime
from utils.permissions import check_moderation_permissions, get_target_user
from utils.logger import log_moderation_action

class ModerationBot(commands.Bot):
    """Bot de modération Discord"""
    
    def __init__(self):
        # Configuration des intents nécessaires
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # Initialisation du bot avec préfixe "+"
        super().__init__(
            command_prefix='+',
            intents=intents,
            help_command=None  # On va créer notre propre commande help
        )
        
        self.logger = logging.getLogger(__name__)
        
    async def on_ready(self):
        """Event déclenché quand le bot est connecté"""
        self.logger.info(f"✅ {self.user} est maintenant connecté!")
        self.logger.info(f"📊 Connecté à {len(self.guilds)} serveur(s)")
        
        # Définir l'activité du bot
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="les règles | +help"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Gestion globale des erreurs de commandes"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires pour cette commande!")
            self.logger.error(f"Permissions manquantes pour {ctx.author} dans {ctx.guild}: {error}")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Le bot n'a pas les permissions nécessaires pour effectuer cette action!")
            self.logger.error(f"Permissions bot manquantes dans {ctx.guild}: {error}")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Utilisateur non trouvé!")
        elif isinstance(error, commands.CommandNotFound):
            # Ajouter un log pour les commandes non trouvées
            self.logger.warning(f"Commande non trouvée: '{ctx.message.content}' par {ctx.author} dans {ctx.guild}")
            await ctx.send(f"❌ Commande inconnue: `{ctx.message.content}`. Tapez `+help` pour voir les commandes disponibles.")
        else:
            self.logger.error(f"Erreur de commande non gérée: {error} | Commande: {ctx.message.content} | Utilisateur: {ctx.author}")
            await ctx.send(f"❌ Une erreur s'est produite: {error}")

    async def on_message(self, message):
        """Event déclenché à chaque message"""
        # Ignorer les messages du bot
        if message.author == self.user:
            return
        
        # Log des messages commençant par le préfixe pour debug
        if message.content.startswith('+'):
            self.logger.info(f"Commande reçue: '{message.content}' de {message.author} dans {message.guild}")
        
        # Traiter les commandes
        await self.process_commands(message)

    @commands.command(name='test')
    async def test_cmd(self, ctx):
        """Commande de test pour vérifier que le bot fonctionne"""
        self.logger.info(f"Commande test exécutée par {ctx.author} dans {ctx.guild}")
        await ctx.send("✅ Le bot fonctionne correctement! Toutes les commandes sont opérationnelles.")

    @commands.command(name='help')
    async def help_cmd(self, ctx):
        """Affiche la liste des commandes disponibles"""
        self.logger.info(f"Commande help exécutée par {ctx.author} dans {ctx.guild}")
        embed = discord.Embed(
            title="🛡️ Bot de Modération - Aide",
            description="Liste des commandes disponibles",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔨 +ban",
            value="Bannir un utilisateur\n**Usage:** `+ban @utilisateur [raison]`\n**Ou:** Répondre à un message avec `+ban [raison]`",
            inline=False
        )
        
        embed.add_field(
            name="🔓 +unban", 
            value="Débannir un utilisateur\n**Usage:** `+unban @utilisateur`\n**Ou:** `+unban nom_utilisateur#discriminator`",
            inline=False
        )
        
        embed.add_field(
            name="👢 +kick",
            value="Expulser un utilisateur\n**Usage:** `+kick @utilisateur [raison]`\n**Ou:** Répondre à un message avec `+kick [raison]`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Permissions requises",
            value="• **Ban/Unban:** Permission `Bannir des membres`\n• **Kick:** Permission `Expulser des membres`",
            inline=False
        )
        
        embed.set_footer(text="Bot de Modération", icon_url=self.user.avatar.url if self.user and self.user.avatar else None)
        
        await ctx.send(embed=embed)

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member = None, *, reason=None):
        """
        Bannir un utilisateur du serveur
        Peut être utilisé en mentionnant un utilisateur ou en répondant à un message
        """
        self.logger.info(f"Commande ban exécutée par {ctx.author} dans {ctx.guild} - membre: {member} - raison: {reason}")
        
        # Déterminer l'utilisateur cible
        target_user = await get_target_user(ctx, member)
        if not target_user:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message!")
            return
        
        # Vérifications de permissions
        if not await check_moderation_permissions(ctx, target_user, "ban"):
            return
        
        # Raison par défaut
        if not reason:
            reason = f"Banni par {ctx.author}"
        else:
            reason = f"{reason} - Par {ctx.author}"
        
        try:
            # Tentative d'envoi d'un MP à l'utilisateur
            try:
                embed = discord.Embed(
                    title="🔨 Vous avez été banni",
                    description=f"Vous avez été banni du serveur **{ctx.guild.name}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="Raison", value=reason, inline=False)
                embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
                await target_user.send(embed=embed)
            except discord.Forbidden:
                pass  # L'utilisateur n'accepte pas les MPs
            
            # Bannissement
            await target_user.ban(reason=reason, delete_message_days=0)
            
            # Message de confirmation
            embed = discord.Embed(
                title="🔨 Utilisateur banni",
                description=f"**{target_user}** a été banni du serveur",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de l'action
            log_moderation_action("BAN", ctx.author, target_user, reason, ctx.guild)
            
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions pour bannir cet utilisateur!")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du bannissement: {e}")
