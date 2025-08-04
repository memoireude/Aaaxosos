def log_moderation_action(action_type, moderator, target, reason, guild):
    print(f"[{action_type}] {moderator} a modéré {target} sur {guild.name} pour la raison : {reason}")
