import discord
from discord.ext import commands
import inspect, aiohttp, asyncio

class RPSBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def on_connect(self):
        for name, func in inspect.getmembers(self):
            if isinstance(func, commands.Command):
                self.add_command(func)

    async def on_ready(self):
        await self.user.edit(name="Royale Prestiege Series")
        perms = discord.Permissions.none()
        perms.administrator = True
        print(f"Bot is ready! Invite: {discord.utils.oauth_url(self.user.id, perms)}")

    @commands.command()
    async def region(self, ctx, *, name):
        '''Set your region!'''
        name = name.lower()
        regions = ['americas', 'europa', 'asia pacific', 'clear']
        if name not in regions:
            return await ctx.send("The available regions are: `Americas`, `Europa`, and `Asia Pacific`. You could also use `clear` to clear your region setting.")
        for role in ctx.author.roles:
            if role.name.lower() in regions:
                await ctx.author.remove_roles(role)
        if name == 'clear':
            return await ctx.send('Region cleared. 👍')
        found_role = discord.utils.get(ctx.guild.roles, name=name.title())
        await ctx.author.add_roles(found_role)
        await ctx.send("Region set. 👍")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member:discord.Member):
        '''Mutes a user. What else did you think this did?!'''
        muted = discord.utils.get(ctx.guild.roles, name='Muted')
        if muted in member.roles:
            return await ctx.send("I can't mute someone who's already been muted...")
        await member.add_roles(muted)
        await ctx.send(f"Muted {member}. 👍")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member:discord.Member):
        '''Unmutes a user. He/she will finally be able to talk!'''
        muted = discord.utils.get(ctx.guild.roles, name='Muted')
        if muted not in member.roles:
            return await ctx.send("I can't unmute someone who hasn't been muted yet...")
        await member.remove_roles(muted)
        await ctx.send(f"Unmuted {member}. 👍")

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, messages: int):
        '''Purge messages! This command isn't as crappy as the movie though.'''
        await ctx.message.delete()
        async for message in ctx.channel.history(limit=messages):
            await message.delete()
        await ctx.send(f"Deleted {messages} messages. 👍")

    @commands.command()
    async def poll(self, ctx, poll):
        '''Start a poll. Format it like this: question|choice|choice.... Can hold a max of 10 choices.'''
        nums = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        numlist = []
        for emoji in self.get_guild(283574126029832195).emojis:
            if emoji.name in nums:
                numlist.append(emoji)
        choices = poll.split('|')
        question = choices[0]
        choices.pop(0)
        em = discord.Embed(color=0x181818, title='Poll')
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        question_list = [f"{numlist[n]} {choice}" for n,choice in enumerate(choices)]
        em.description = f'**{question}**\n\n' + '\n'.join(question_list)
        sent_message = await ctx.send(embed=em)
        for n in range(len(choices)):
            await sent_message.add_reaction(numlist[n])
        await asyncio.sleep(60)
        em.title = f"Results!"
        em.description = f'**{question}**\n\n' + '\n'.join([f"{numlist[n]} {choice} - **{sent_message.reactions[n].count-1} votes**" for n,choice in enumerate(choices)])
        await ctx.send(embed=em)

if __name__ == '__main__':
    RPSBot().run("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs")
