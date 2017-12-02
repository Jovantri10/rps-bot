import discord, asyncio
    
class ReactWait:

    def __init__(self, ctx, message):
        self.ctx = ctx
        self.message = message
        self.emojis = ['🇭', '🇸', '🇩']

    def check(self, reaction, user):
        if user.id != self.ctx.author.id:
            return False
        if not reaction.emoji in self.emojis:
            return False
        if reaction.message.id != self.message.id:
            return False
        return True

    async def react_session(self, timeout=15.0):
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_add', check=self.check, timeout=timeout)
                print(reaction)
            except asyncio.TimeoutError:
                return "stay"
            else:
                if reaction.emoji == '🇭':
                    return "hit"
                elif reaction.emoji == '🇸':
                    return "stay"
                elif reaction.emoji == '🇩':
                    return "double"
                else:
                    continue