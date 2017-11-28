import discord
from discord.ext import commands
from contextlib import redirect_stdout
import youtube_dl
import inspect, aiohttp, asyncio, io, textwrap, traceback, os, ctypes, re, json

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
        @commands.guild_only()
        @commands.has_permissions(kick_members=True)
        async def kick(self, ctx, member:discord.Member, *, reason="No Reason"):
            '''Kicks a member'''
            try:
                if reason == "No Reason":
                    await ctx.guild.kick(member)
                else:
                    await ctx.guild.kick(member, reason=reason)
                await ctx.send("Done. 👍")
            except discord.Forbidden:
                return await ctx.send("I can't kick that member!")
            em = discord.Embed(title="Kick", color=0xc90000)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.guild.get_channel(383849511920861185).send(embed=em)


        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(ban_members=True)
        async def ban(self, ctx, member:discord.Member, *, reason="No Reason"):
            '''Bans a member'''
            try:
                if reason == "No Reason":
                    await ctx.guild.ban(member)
                else:
                    await ctx.guild.ban(member, reason=reason)
                await ctx.send("Done. 👍")
            except discord.Forbidden:
                return await ctx.send("I can't ban that member!")
            em = discord.Embed(title="Ban", color=0xc90000)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.guild.get_channel(383849511920861185).send(embed=em)


        @commands.command()
        @commands.guild_only()
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
            em = discord.Embed(title="Unban", color=0x3ace00)
            em.add_field(name="User", value=str(user.user))
            em.add_field(name="Moderator", value=str(ctx.author))
            await ctx.guild.get_channel(383849511920861185).send(embed=em)


        @commands.command(aliases=['clear'])
        @commands.has_permissions(manage_messages=True)
        async def purge(self, ctx, messages: int):
            '''Purge messages! This command isn't as crappy as the movie though.'''
            await ctx.message.delete()
            async for message in ctx.channel.history(limit=messages):
                await message.delete()
            await ctx.send(f"Deleted {messages} messages. 👍")

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(mute_members=True)
        async def unmute(self, ctx, member:discord.Member, *, reason="No Reason"):
            '''Unmutes a user. He/she will finally be able to talk!'''
            muted = discord.utils.get(ctx.guild.roles, name='Muted')
            if muted not in member.roles:
                return await ctx.send("I can't unmute someone who hasn't been muted yet...")
            await member.remove_roles(muted)
            await ctx.send(f"Unmuted {member}. 👍")
            em = discord.Embed(title="Unmute", color=0x3ace00)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.guild.get_channel(383849511920861185).send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(mute_members=True)
        async def mute(self, ctx, member:discord.Member, *, reason="No Reason"):
            '''Mutes a user. What else did you think this did?!'''
            muted = discord.utils.get(ctx.guild.roles, name='Muted')
            if muted in member.roles:
                return await ctx.send("I can't mute someone who's already been muted...")
            await member.add_roles(muted)
            await ctx.send(f"Muted {member}. 👍")
            em = discord.Embed(title="Mute", color=0xef7f07)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.guild.get_channel(383849511920861185).send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_role("Server Admin")
        async def warn(self, ctx, member: discord.Member, *, reason="No Reason"):
            with open("warnings.json") as f:
                warn_json = json.load(f)
            if str(member.id) not in warn_json:
                warn_json[str(member.id)] = [reason]
            else:
                warn_json[str(member.id)].append(reason)
            with open("warnings.json", "w") as f:
                f.write(json.dumps(warn_json, indent=4))
            await ctx.send(f"Warned **{member.name}**. This is their {len(warn_json[str(member.id)])} warning. ⚠️")
            em = discord.Embed(title="Warn", color=0xf7ca2a)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await ctx.guild.get_channel(383849511920861185).send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_role("Server Admin")
        async def warnings(self, ctx, member: discord.Member):
            with open("warnings.json") as f:
                warn_json = json.load(f)
            if str(member.id) not in warn_json:
                return await ctx.send(f"**{member}** does not have any warnings!")
            await ctx.send(embed=discord.Embed(title=f"{member}'s Warnings", color=0x181818, description='\n'.join([reason for reason in warn_json[str(member.id)]])))


        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_roles=True)
        async def removerole(self, ctx, member: discord.Member, *, rolenames):
            """Removes roles from a member. I wonder what he/she did to deserve this."""
            rolenames_ls = rolenames.lower().replace("apac", "asia pacific").split(",")
            rolenames_ls = [r.strip() for r in rolenames_ls]
            roles = [discord.utils.find(lambda r: r.name.lower() == role, ctx.guild.roles) for role in rolenames_ls]
            if None in roles:
                return await ctx.send("One of those roles does not exist!")
            for role in roles:
                await member.remove_roles(role)
            await ctx.send(f"{', '.join([f'**{r.name}**' for r in roles])} removed from **{member.name}**")

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_roles=True)
        async def addrole(self, ctx, member: discord.Member, *, rolenames):
            """Adds roles to a member. Hence the name addrole."""
            rolenames_ls = rolenames.lower().replace("apac", "asia pacific").split(",")
            rolenames_ls = [r.strip() for r in rolenames_ls]
            roles = [discord.utils.find(lambda r: r.name.lower() == role, ctx.guild.roles) for role in rolenames_ls]
            if None in roles:
                return await ctx.send("One of those roles does not exist!")
            for role in roles:
                await member.add_roles(role)
            await ctx.send(f"{', '.join([f'**{r.name}**' for r in roles])} added to **{member.name}**")

    class Music:

        def __init__(self, bot):
            self.bot = bot
            self.vc = None

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
        @commands.guild_only()
        async def join(self, ctx):
            """Have the bot join the music channel."""
            if self.vc:
                return await ctx.send("Already joined a voice channel!")
            try:
                self.vc = await ctx.author.voice.channel.connect()
            except:
                return await ctx.send("You're not in a voice channel!")
            await ctx.send("Joined the music channel.")

        @commands.command()
        @commands.guild_only()
        async def leave(self, ctx):
            """Have the bot leave the music channel."""
            if not self.vc:
                return await ctx.send("I can't leave a channel if I'm not in one...")
            await self.vc.disconnect()
            self.vc = None
            await ctx.send("Left the music channel.")

        @commands.command()
        @commands.guild_only()
        async def stop(self, ctx):
            """Stop the music."""
            if not self.vc:
                return await ctx.send("I can't stop playing if I'm not even in a voice channel.")
            if not self.vc.is_playing():
                return await ctx.send("I'm not even playing music.")
            self.vc.stop()
            await ctx.send("Stopped the music.")

        @commands.command()
        @commands.guild_only()
        async def play(self, ctx, *, video):
            """Play some tunes 🎵"""
            if video.startswith("http://youtube.com/watch") or video.startswith("https://youtube.com/watch"):
                url = video
                name = await self.get_name_from_vid(video)
                if not name:
                    return await ctx.send("That's not a valid url!")
            else:
                url, name = await self.get_results(video)
                if not url:
                    return await ctx.send("There aren't any search results.")

            name_file = []
            for word in re.findall(r"[\w']+", name):
                if "".join(ch for ch in word if ch.isalnum()) != "":
                    name_file.append("".join(ch for ch in word if ch.isalnum()))

            if f'{"_".join(name_file)}-{url.split("v=")[1]}.mp3' not in os.listdir('.'):
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

            discord.opus.load_opus(ctypes.util.find_library('opus'))
            try:
                self.vc.play(discord.FFmpegPCMAudio(f'{"_".join(name_file)}-{url.split("v=")[1]}.mp3'))
            except Exception as e:
                if str(e) == "'NoneType' object has no attribute 'play'":
                    return await ctx.send(f"The bot hasn't joined a voice channel yet! Do `{ctx.prefix}join` to join a voice channel.")
                elif str(e) == "Already playing audio.":
                    return await ctx.send("The bot is already playing something. Wait till the song is finished.")
                else:
                    return await ctx.send(str(e))
            await ctx.send(f"Playing {name}")




