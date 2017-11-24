import discord
from discord.ext import commands
from contextlib import redirect_stdout
import youtube_dl
import inspect, aiohttp, asyncio, io, textwrap, traceback, os

class Cog:
    def __init__(self, bot):
        self.bot = bot

    def all_cogs(clss):
        attrs = []
        for name, attr in inspect.getmembers(clss):
            if inspect.isclass(attr):
                if attr.__name__ != "type":
                    attrs.append(attr)
        return attrs

    class Moderator:
        def __init__(self, bot):
            self.bot = bot
            self.session = bot.session

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

    class Music:

        def __init__(self, bot):
            self.bot = bot

        async def get_results(self, video):
            async with self.bot.session.get("https://www.googleapis.com/youtube/v3/search", params={"part": "snippet", "key": "AIzaSyBkL3AijwPXd0fTY900HnPBEjhYh1IOLw0", "q": video}) as resp:
                data = await resp.json()
                search_list = data['items']
            video_list = [search for search in search_list if search["id"]["kind"] == "youtube#video"]
            if video_list == []:
                return [False, False]
            return [f"https://youtube.com/watch?v={video_list[0]['id']['videoId']}", video_list[0]["snippet"]["title"]]

        async def get_name_from_vid(self, video):
            vid_id = video.split("v=")[1]
            async with self.bot.session.get("https://www.googleapis.com/youtube/v3/video", params={"part": "snippet", "key": "AIzaSyBkL3AijwPXd0fTY900HnPBEjhYh1IOLw0", "id": vid_id}) as resp:
                data = await resp.json()
                vid = data['items']
            if vid == []:
                return False
            return vid['items']['snippet']['title']

        class Logger():
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                print(msg)
            

        @commands.command()
        async def play(self, ctx, *, video):
            if video.startswith("http://youtube.com/watch") or video.startswith("https://youtube.com/watch"):
                url = video
                name = await self.get_name_from_vid(video)
                if not name:
                    return await ctx.send("That's not a valid url!")
            else:
                url, name = await self.get_results(video)
                if not url:
                    return await ctx.send("There aren't any search results.")

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'logger': self.Logger()
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            vc = await ctx.guild.get_channel(371289859127771146).connect()
            vc.play(discord.FFmpegPCMAudio(f'{name}.mp3'), after=lambda a: os.remove(f'{name}.mp3'))
            await ctx.send(f"Playing {name}")






