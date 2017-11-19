import discord
from discord.ext import commands
import inspect, aiohttp

class RPSBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def on_connect(self):
        for name, func in inspect.getmembers(self):
            if isinstance(func, commands.Command):
                self.add_command(func)

    async def on_ready(self):
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

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, messages: int):
        '''Purge messages! This command isn't as crappy as the movie though.'''
        async for message in ctx.channel.history(limit=messages):
            await message.delete()
        await ctx.send(f"Deleted {messages} messages. 👍")

if __name__ == '__main__':
    RPSBot().run("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs")
