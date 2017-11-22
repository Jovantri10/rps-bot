import discord
from discord.ext import commands
from contextlib import redirect_stdout
import inspect, aiohttp, asyncio, io, textwrap, traceback, os

class Cog:
    def __init__(self, bot):
        self.bot = bot

    def all_cogs(clss):
        attrs = []
        for name, attr in inspect.getmembers(clss):
            if inspect.isclass(attr):
                attrs.append(attr)
        return attrs

    class Moderator:
        def __init__(self, bot):
            self.bot = bot
            self.session = bot.session

        def __str__(self):
            return "Moderator"

        @commands.command()
        @commands.has_permissions(kick_members=True)
        async def kick(self, ctx, member:discord.Member):
            '''Kicks a member'''
            try:
                await ctx.guild.kick(member)
                await ctx.send("Done. 👍")
            except discord.Forbidden:
                return await ctx.send("I can't kick that member!")

        @commands.command()
        @commands.has_permissions(ban_members=True)
        async def ban(self, ctx, member:discord.Member):
            '''Bans a member'''
            try:
                await ctx.guild.ban(member)
                await ctx.send("Done. 👍")
            except discord.Forbidden:
                return await ctx.send("I can't ban that member!")

        @commands.command()
        @commands.has_permissions(ban_members=True)
        async def unban(self, ctx, *, username):
            '''Unbans a member'''
            bans = await ctx.guild.bans()
            user = None
            for ban in bans:
                if username == ban.user.name:
                    user = ban
            if not user:
                return await ctx.send('Either that user is not in the banlist, or it doesn\'nt even exist.')
            await ctx.guild.unban(user.user)
            await ctx.send("Done. 👍")

        @commands.command(aliases=['clear'])
        @commands.has_permissions(manage_messages=True)
        async def purge(self, ctx, messages: int):
            '''Purge messages! This command isn't as crappy as the movie though.'''
            await ctx.message.delete()
            async for message in ctx.channel.history(limit=messages):
                await message.delete()
            await ctx.send(f"Deleted {messages} messages. 👍")

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
        @commands.has_permissions(manage_roles=True)
        async def mute(self, ctx, member:discord.Member):
            '''Mutes a user. What else did you think this did?!'''
            muted = discord.utils.get(ctx.guild.roles, name='Muted')
            if muted in member.roles:
                return await ctx.send("I can't mute someone who's already been muted...")
            await member.add_roles(muted)
            await ctx.send(f"Muted {member}. 👍")
