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
        name = name.lower()
        regions = ['americas', 'europa', 'asia pacific', 'clear']
        if name not in regions:
            return await ctx.send("The available regions are: `Americas`, `Europa`, and `Asia Pacific`. You could also use `clear` to clear your region setting.")
        for role in ctx.author.roles:
            if role.name.lower() in regions:
                await ctx.author.remove_roles(role)
        if name == 'clear':
            return await ctx.send('Region cleared. 👍')
        for role in ctx.guild.roles:
            if role.name.lower() == name:
                found_role = role
        await ctx.author.add_roles(found_role)
        await ctx.send("Region set. 👍")

if __name__ == '__main__':
    RPSBot().run("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs")
