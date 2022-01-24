from .audit import audit


async def dm(ctx, message=None):
    success_users = []
    failure_users = []

    for user in ctx.guild.members:
        if not user.bot:
            try:
                await user.send(message)
                success_users.append(user)
            except:
                failure_users.append(user)

    success_users_string = ', '.join([user.mention for user in success_users])
    failure_users_string = ', '.join([user.mention for user in failure_users])
    audit_message = f'Users DM\'d: {success_users_string}\nUnable to DM these users: {failure_users_string}\n\nMessage:\n```{message}```\nDM sent to:\n\n'

    await audit(ctx, message=audit_message)
