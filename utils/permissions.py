async def check_moderation_permissions(ctx, member, action):
    if ctx.author.top_role <= member.top_role:
        await ctx.send("❌ Vous ne pouvez pas modérer un membre avec un rôle égal ou supérieur au vôtre.")
        return False
    if ctx.guild.me.top_role <= member.top_role:
        await ctx.send("❌ Je ne peux pas modérer ce membre (rôle trop élevé).")
        return False
    return True

async def get_target_user(ctx, member):
    if member:
        return member
    if ctx.message.reference:
        try:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            return ref_msg.author
        except:
            return None
    return None
