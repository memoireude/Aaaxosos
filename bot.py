"""
Bot Discord de modération avec commandes ban/unban/kick
"""

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

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_user(self, ctx, *, user_info=None):
        """
        Débannir un utilisateur du serveur
        Usage: +unban @utilisateur ou +unban nom#discriminator
        """
        if not user_info:
            await ctx.send("❌ Veuillez spécifier l'utilisateur à débannir!\n**Usage:** `+unban nom#discriminator` ou `+unban ID_utilisateur`")
            return
        
        try:
            # Récupération de la liste des utilisateurs bannis
            banned_users = []
            async for ban_entry in ctx.guild.bans():
                banned_users.append(ban_entry.user)
            
            if not banned_users:
                await ctx.send("❌ Aucun utilisateur banni trouvé sur ce serveur!")
                return
            
            target_user = None
            
            # Recherche par ID
            if user_info.isdigit():
                user_id = int(user_info)
                target_user = discord.utils.get(banned_users, id=user_id)
            else:
                # Recherche par nom#discriminator ou nom
                if '#' in user_info:
                    name, discriminator = user_info.split('#')
                    target_user = discord.utils.get(banned_users, name=name, discriminator=discriminator)
                else:
                    # Recherche par nom seulement
                    target_user = discord.utils.find(lambda u: u.name.lower() == user_info.lower(), banned_users)
            
            if not target_user:
                # Afficher les utilisateurs bannis disponibles
                banned_list = '\n'.join([f"• {user.name}#{user.discriminator} (ID: {user.id})" for user in banned_users[:10]])
                if len(banned_users) > 10:
                    banned_list += f"\n... et {len(banned_users) - 10} autre(s)"
                
                embed = discord.Embed(
                    title="❌ Utilisateur non trouvé",
                    description=f"Utilisateur banni non trouvé: `{user_info}`",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Utilisateurs bannis disponibles:",
                    value=banned_list if banned_list else "Aucun",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Débannissement
            await ctx.guild.unban(target_user, reason=f"Débanni par {ctx.author}")
            
            # Message de confirmation
            embed = discord.Embed(
                title="🔓 Utilisateur débanni",
                description=f"**{target_user}** a été débanni du serveur",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de l'action
            log_moderation_action("UNBAN", ctx.author, target_user, f"Débanni par {ctx.author}", ctx.guild)
            
        except discord.NotFound:
            await ctx.send("❌ Utilisateur non trouvé dans les bannissements!")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions pour débannir cet utilisateur!")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du débannissement: {e}")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member = None, *, reason=None):
        """
        Expulser un utilisateur du serveur
        Peut être utilisé en mentionnant un utilisateur ou en répondant à un message
        """
        # Déterminer l'utilisateur cible
        target_user = await get_target_user(ctx, member)
        if not target_user:
            await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à un message!")
            return
        
        # Vérifications de permissions
        if not await check_moderation_permissions(ctx, target_user, "kick"):
            return
        
        # Raison par défaut
        if not reason:
            reason = f"Expulsé par {ctx.author}"
        else:
            reason = f"{reason} - Par {ctx.author}"
        
        try:
            # Tentative d'envoi d'un MP à l'utilisateur
            try:
                embed = discord.Embed(
                    title="👢 Vous avez été expulsé",
                    description=f"Vous avez été expulsé du serveur **{ctx.guild.name}**",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Raison", value=reason, inline=False)
                embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
                embed.add_field(name="Note", value="Vous pouvez rejoindre le serveur avec un nouveau lien d'invitation", inline=False)
                await target_user.send(embed=embed)
            except discord.Forbidden:
                pass  # L'utilisateur n'accepte pas les MPs
            
            # Expulsion
            await target_user.kick(reason=reason)
            
            # Message de confirmation
            embed = discord.Embed(
                title="👢 Utilisateur expulsé",
                description=f"**{target_user}** a été expulsé du serveur",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de l'action
            log_moderation_action("KICK", ctx.author, target_user, reason, ctx.guild)
            
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions pour expulser cet utilisateur!")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'expulsion: {e}")