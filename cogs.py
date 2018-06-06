import discord
from discord.ext import commands
from contextlib import redirect_stdout
from reactwait import ReactWait
import youtube_dl
import inspect, aiohttp, asyncio, io, textwrap, traceback, os, ctypes, re, json, random, datetime

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
        @commands.has_permissions(manage_messages=True)
        async def say(self, ctx, *, message):
            await ctx.send(message)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def poll(self, ctx, *, time : int, poll):
            '''Start a poll. Format it like this: question|choice|choice.... Can hold a max of 10 choices. Time is in seconds.'''
            nums = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
            numlist = []
            for emoji in self.bot.get_guild(283574126029832195).emojis:
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
            await asyncio.sleep(int(time))
            sent_message = await ctx.channel.get_message(sent_message.id)
            em.title = f"Results!"
            reactions = sorted(sent_message.reactions, key=lambda x: numlist.index(x.emoji)+1)
            em.description = f'**{question}**\n\n' + '\n'.join([f"{numlist[n]} {choice} - **{reactions[n].count-1} votes**" for n,choice in enumerate(choices)])
            await ctx.send(embed=em)

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
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)


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
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)


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
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)


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
        @commands.has_permissions(manage_messages=True)
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
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
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
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def warn(self, ctx, member: discord.Member, *, reason="No Reason Given"):
            """Warns a member."""
            if member == ctx.author:
                return await ctx.send("Why are you warning yourself? 🤔")
            if member.id == 310661173596913674:
                return await ctx.send("Nice try, Samm.")
            with open("warnings.json") as f:
                warn_json = json.load(f)
            if str(member.id) not in warn_json:
                warn_json[str(member.id)] = [reason]
            else:
                warn_json[str(member.id)].append(reason)
            with open("warnings.json", "w") as f:
                f.write(json.dumps(warn_json, indent=4))
            await ctx.send(f"**{member.name}** has been warned due to **{reason.lower()}**. Total Warnings: {len(warn_json[str(member.id)])} ⚠️")
            em = discord.Embed(title="Warn", color=0xf7ca2a)
            em.add_field(name="User", value=str(member))
            em.add_field(name="Moderator", value=str(ctx.author))
            em.add_field(name="Reason", value=reason, inline=False)
            await discord.utils.get(ctx.guild.text_channels, name="audit_log").send(embed=em)

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def delwarn(self, ctx, member: discord.Member):
            """Deletes Warnings from a member."""
            with open("warnings.json") as f:
                warn_json = json.load(f)
            if str(member.id) not in warn_json:
                return await ctx.send(f"**{member}** doesn't have any warnings!")
            if len(warn_json[str(member.id)]) == 1:
                warn_json = {key: value for key, value in warn_json.items() if key != str(member.id)}
            else:
                warn_json[str(member.id)] = warn_json[str(member.id)][:-1]
            with open("warnings.json", "w") as f:
                f.write(json.dumps(warn_json, indent=4))
            await ctx.send(f"A warning has been removed from **{member}**")
            

        @commands.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def warnings(self, ctx, member: discord.Member):
            """Gets a list of warnings of a member."""
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
            rolenames_ls = rolenames.lower().split(",")
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
            rolenames_ls = rolenames.lower().split(",")
            rolenames_ls = [r.strip() for r in rolenames_ls]
            roles = [discord.utils.find(lambda r: r.name.lower() == role, ctx.guild.roles) for role in rolenames_ls]
            if None in roles:
                return await ctx.send("One of those roles does not exist!")
            for role in roles:
                await member.add_roles(role)
            await ctx.send(f"{', '.join([f'**{r.name}**' for r in roles])} added to **{member.name}**")

        @commands.group(aliases=["cc"], invoke_without_command=True)
        @commands.guild_only()
        async def customcom(self, ctx):
            """Gets a list of custom commands."""
            with open("commands.json") as f:
                comms = json.load(f)
            await ctx.send(embed=discord.Embed(color=0x181818, title="List of Available Custom Commands:", description="\n".join([f"{ctx.prefix}{comm}" for comm in list(comms.keys())])))

        @customcom.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def add(self, ctx, command, *, response):
            """Creates a custom command."""
            with open("commands.json") as f:
                comms = json.load(f)
            comms[command] = response
            with open("commands.json", "w") as f:
                f.write(json.dumps(comms, indent=4))
            await ctx.send("Added command. 👍")

        @customcom.command()
        @commands.guild_only()
        @commands.has_permissions(manage_messages=True)
        async def remove(self, ctx, command):
            """Removes a custom command."""
            with open("commands.json") as f:
                comms = json.load(f)
            comms = {comm: resp for comm, resp in comms.items() if comm != command}
            with open("commands.json", "w") as f:
                f.write(json.dumps(comms, indent=4))
            await ctx.send("Removed command. 👍")

    class Music:

        def __init__(self, bot):
            self.bot = bot
            self.vc = None
            self.queue = []

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
            async with self.bot.session.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "snippet", "key": "AIzaSyBkL3AijwPXd0fTY900HnPBEjhYh1IOLw0", "id": vid_id}) as resp:
                data = await resp.json()
                vid = data['items']
            if vid == []:
                return False
            return vid[0]['snippet']['title']

        class Logger():
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                print(msg)

        @commands.command()
        @commands.guild_only()
        async def skip(self, ctx):
            """Skip the current track."""
            if not self.vc or self.vc.is_playing():
                return
            self.vc.stop()
            await ctx.send("Skipped track.")

        @commands.command()
        @commands.guild_only()
        async def play(self, ctx, *, video):
            """Play some tunes 🎵"""
            discord.opus.load_opus(ctypes.util.find_library('opus'))
            if not self.vc:
                try:
                    self.vc = await ctx.author.voice.channel.connect()
                except:
                    return await ctx.send("You're not in a voice channel!")
            if video.startswith("http://youtube.com/watch") or video.startswith("https://youtube.com/watch") or video.startswith("https://www.youtube.com/watch") or video.startswith("http://www.youtube.com/watch"):
                url = video
                name = await self.get_name_from_vid(video)
                if not name:
                    return await ctx.send("That's not a valid url!")
            else:
                url, name = await self.get_results(video)
                if not url:
                    return await ctx.send("There aren't any search results.")

            name_file = []
            for word in re.split(" |'", name):
                if "".join(ch for ch in word if ch.isalnum()) != "":
                    name_file.append("".join(ch for ch in word if ch.isalnum()))
                if word[-1] == ":":
                    name_file.append("-")
                if word[-1] == ".":
                    name_file[-1] += "."
                if word == "-":
                    name_file.append("-")

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
            self.queue.append([name, name_file, url])
            try:
                self.vc.play(discord.FFmpegPCMAudio(f'{"_".join(self.queue[0][1])}-{self.queue[0][2].split("v=")[1]}.mp3'))
            except Exception as e:
                print(e)
            while self.vc:
                if not self.vc.is_playing():
                    queue.pop(0)
                    if self.queue == []:
                        await self.vc.disconnect()
                        self.vc = None
                        return await ctx.send("Queue finished.")
                    try:
                        self.vc.play(discord.FFmpegPCMAudio(f'{"_".join(self.queue[0][1])}-{self.queue[0][2].split("v=")[1]}.mp3'))
                    except Exception as e:
                        print(e)
                try:
                    if len(discord.utils.get(ctx.guild.voice_channels, id=self.vc.channel.id).members) <= 1:
                        await self.vc.disconnect()
                        self.vc = None
                        return await ctx.send("I'm not sticking around if noone's listening to my sweet tunes.")
                except Exception as e:
                    print(e)
                

    class Economy:

        def __init__(self, bot):
            self.bot = bot

        @commands.group(invoke_without_command=True)
        @commands.guild_only()
        async def bank(self, ctx):
            """Do !bank register to create an account, or !bank delete to delete it."""
            return

        @bank.command(hidden=True)
        @commands.guild_only()
        async def delete(self, ctx):
            """Deletes your account."""
            with open("econ.json") as f:
                economy_dict = json.load(f)
            if str(ctx.author.id) not in economy_dict:
                return await ctx.send("You don't even have an account at the RPS Bank!")
            economy_dict = {name: value for name, value in economy_dict.items() if name != str(ctx.author.id)}
            with open("econ.json", "w") as f:
                f.write(json.dumps(economy_dict, indent=4))
            await ctx.send("Account deleted.")

        @bank.command(hidden=True)
        @commands.guild_only()
        async def register(self, ctx):
            """Creates an account."""
            with open("econ.json") as f:
                economy_dict = json.load(f)
            if str(ctx.author.id) in economy_dict:
                return await ctx.send("You already have an account at the RPS Bank!")
            economy_dict[str(ctx.author.id)] = 200
            with open("econ.json", "w") as f:
                f.write(json.dumps(economy_dict, indent=4))
            await ctx.send("Account registered.")

        @commands.command()
        @commands.guild_only()
        async def blackjack(self, ctx, bid):
            """Play blackjack!"""
            with open("econ.json") as f:
                economy_dict = json.load(f)
            with open("cards.json") as f:
                cards = json.load(f)
            try:
                bid_int = int(bid)
            except:
                return await ctx.send("Invalid bid.")
            if str(ctx.author.id) not in economy_dict:
                return await ctx.send("You don't have an account in the RPS bank. Do `!bank register` to register an account.")
            if bid_int > economy_dict[str(ctx.author.id)]:
                return await ctx.send("You don't have enough money to bid that!")
            player_cards = []
            for i in range(2):
                card = cards[random.randint(0, len(cards)-1)]
                player_cards.append(card)
                cards.remove(card)
            comp_cards = []
            for i in range(2):
                card = cards[random.randint(0, len(cards)-1)]
                comp_cards.append(card)
                cards.remove(card)
            if {"value": 11, "name": "Ace"} in comp_cards and sum([card["value"] for card in comp_cards]) > 21:
                comp_cards[comp_cards.index({"value": 11, "name": "Ace"})]["value"] = 1
            if {"value": 11, "name": "Ace"} in player_cards and sum([card["value"] for card in player_cards]) > 21:
                player_cards[player_cards.index({"value": 11, "name": "Ace"})]["value"] = 1
            if sum([card["value"] for card in player_cards]) == 21:
                economy_dict[str(ctx.author.id)] += bid_int
                with open("econ.json", "w") as f:
                    f.write(json.dumps(economy_dict, indent=4))
                return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**BLACKJACK!**")
            if sum([card["value"] for card in comp_cards]) == 21:
                economy_dict[str(ctx.author.id)] -= bid_int
                with open("econ.json", "w") as f:
                    f.write(json.dumps(economy_dict, indent=4))
                return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**DEALER GOT BLACKJACK!**")
            to_send_str = f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer Shows: {comp_cards[0]['name']}\n🇭it, 🇸tay, or 🇩ouble?"
            message = await ctx.send(to_send_str)
            await message.add_reaction('🇭')
            await message.add_reaction('🇸')
            await message.add_reaction('🇩')
            
            choice = ""
            counter = 0
            while True:
                react_client = ReactWait(ctx, message)
                choice = await react_client.react_session()
                
                if choice == 'hit':
                    counter += 1
                    card = cards[random.randint(0, len(cards)-1)]
                    player_cards.append(card)
                    cards.remove(card)
                    while {"value": 11, "name": "Ace"} in comp_cards and sum([card["value"] for card in comp_cards]) > 21:
                        comp_cards[comp_cards.index({"value": 11, "name": "Ace"})]["value"] = 1
                    while {"value": 11, "name": "Ace"} in player_cards and sum([card["value"] for card in player_cards]) > 21:
                        player_cards[player_cards.index({"value": 11, "name": "Ace"})]["value"] = 1
                    if sum([card["value"] for card in player_cards]) > 21:
                        economy_dict[str(ctx.author.id)] -= bid_int
                        with open("econ.json", "w") as f:
                            f.write(json.dumps(economy_dict, indent=4))
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**BUST!**")
                    if sum([card["value"] for card in player_cards]) == 21:
                        economy_dict[str(ctx.author.id)] += bid_int
                        with open("econ.json", "w") as f:
                            f.write(json.dumps(economy_dict, indent=4))
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**BLACKJACK!**")
                    else:
                        message = await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer Shows: {comp_cards[0]['name']}\n🇭it or 🇸tay?")
                        await message.add_reaction('🇭')
                        await message.add_reaction('🇸')
                        continue
                if choice =='double':
                    if bid_int*2 > economy_dict[str(ctx.author.id)]:
                        await ctx.send("You don't have enough money to double your bid!")
                        await message.remove_reaction(reaction, ctx.author)
                        continue
                    bid_int *= 2
                    choice = 'stay'
                if choice == 'stay':
                    while sum([card["value"] for card in comp_cards]) < 16:
                        card = cards[random.randint(0, len(cards)-1)]
                        comp_cards.append(card)
                        cards.remove(card)
                    while {"value": 11, "name": "Ace"} in comp_cards and sum([card["value"] for card in comp_cards]) > 21:
                        comp_cards[comp_cards.index({"value": 11, "name": "Ace"})]["value"] = 1
                    if sum([card["value"] for card in comp_cards]) == 21:
                        economy_dict[str(ctx.author.id)] -= bid_int
                        with open("econ.json", "w") as f:
                            f.write(json.dumps(economy_dict, indent=4))
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**DEALER GOT BLACKJACK!**")
                    elif sum([card["value"] for card in comp_cards]) > 21 or sum([card["value"] for card in player_cards]) > sum([card["value"] for card in comp_cards]):
                        economy_dict[str(ctx.author.id)] += bid_int
                        with open("econ.json", "w") as f:
                            f.write(json.dumps(economy_dict, indent=4))
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**WINNER!**")
                    elif sum([card["value"] for card in player_cards]) == sum([card["value"] for card in comp_cards]):
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**DRAW!**")
                    else:
                        economy_dict[str(ctx.author.id)] -= bid_int
                        with open("econ.json", "w") as f:
                            f.write(json.dumps(economy_dict, indent=4))
                        return await ctx.send(f"{ctx.author.mention}\nYour Cards: {', '.join([card['name'] for card in player_cards])}\nYour Score: {sum([card['value'] for card in player_cards])}\nDealer's Cards: {', '.join([card['name'] for card in comp_cards])}\nDealer's Score: {sum([card['value'] for card in comp_cards])}\n**HOUSE WINS!**")


        @commands.command()
        @commands.guild_only()
        async def balance(self, ctx, member: discord.Member=None):
            with open("econ.json") as f:
                economy_dict = json.load(f)
            if not member:
                member = ctx.author
            if str(member.id) not in economy_dict:
                if str(member.id) == str(ctx.author.id):
                    return await ctx.send("You don't have an account in the RPS bank. Do `!bank register` to register an account.")
                else:
                    return await ctx.send("He doesn't have an account in the RPS bank. Do `!bank register` to register an account.")
            await ctx.send(f"{member.mention} has {economy_dict[str(member.id)]} credits!")

        @commands.command()
        @commands.guild_only()
        async def payday(self, ctx):
            """Payday!"""
            with open("gamtime.json") as f:
                gamtime = json.load(f)
            with open("econ.json") as f:
                economy_dict = json.load(f)
            if str(ctx.author.id) not in economy_dict:
                return await ctx.send("You don't have an account in the RPS bank. Do `!bank register` to register an account.")
            if str(ctx.author.id) in gamtime:
                og_datetime = datetime.datetime(gamtime[str(ctx.author.id)]["year"], gamtime[str(ctx.author.id)]["month"], gamtime[str(ctx.author.id)]["day"], gamtime[str(ctx.author.id)]["hour"], gamtime[str(ctx.author.id)]["minute"], gamtime[str(ctx.author.id)]["second"])
                if (ctx.message.created_at-og_datetime).total_seconds() < 180:
                    return await ctx.send("Too soon! The interval between each payday is 3 minutes!")
            gamtime[str(ctx.author.id)] = {"year": ctx.message.created_at.year, "month": ctx.message.created_at.month, "day": ctx.message.created_at.day, "hour": ctx.message.created_at.hour, "minute": ctx.message.created_at.minute, "second": ctx.message.created_at.second}
            economy_dict[str(ctx.author.id)] = economy_dict[str(ctx.author.id)] + 200
            with open("gamtime.json", "w") as f:
                f.write(json.dumps(gamtime, indent=4))
            with open("econ.json", "w") as f:
                f.write(json.dumps(economy_dict, indent=4))
            await ctx.send("Here's 200 credits for you!")

        @commands.command()
        @commands.guild_only()
        async def slot(self, ctx, bid):
            """Play the slot machine"""
            with open("econ.json") as f:
                economy_dict = json.load(f)
            try:
                bid_int = int(bid)
            except:
                return await ctx.send("That's an invalid bid.")
            if bid_int > economy_dict[str(ctx.author.id)]:
                return await ctx.send("You don't have enough money to bid that!")
            if str(ctx.author.id) not in economy_dict:
                return await ctx.send("You don't have an account in the RPS bank. Do `!bank register` to register an account.")
            em = discord.Embed(color=0x181818, title=f"{ctx.author}'s Bid")
            desc = []
            possible_combinations = ["🌀", "❄️", "🍒", "🌻", "❤️", "🍄", '🍪', '🍀']
            payline = [possible_combinations[random.randint(0, len(possible_combinations)-1)] for i in range(3)]
            generated_slot = f"Result:\n  {possible_combinations[random.randint(0, len(possible_combinations)-1)]} {possible_combinations[random.randint(0, len(possible_combinations)-1)]} {possible_combinations[random.randint(0, len(possible_combinations)-1)]}\n>{payline[0]} {payline[1]} {payline[2]}\n  {possible_combinations[random.randint(0, len(possible_combinations)-1)]} {possible_combinations[random.randint(0, len(possible_combinations)-1)]} {possible_combinations[random.randint(0, len(possible_combinations)-1)]}\n––––––––––––––––\n"
            em.description = generated_slot
            if payline[0] == "🍀" and payline[0] == payline[1] and payline[1] == payline[2]:
                desc = [8, "OOOOOO! Three clovers! You got lucky! Your bid has been multiplied by 8 times!"]
            if payline[0] == "🍒" and payline[0] == payline[1] and payline[1] == payline[2]:
                desc = [6, "Wow! Three cherries! Your bid has been multiplied by 6 times!"]
            elif payline[0] == payline[1] and payline[1] == payline[2]:
                desc = [3, "Three matching symbols! Your bid has been multiplied by 3 times!"]
            elif payline[0] == payline[1] or payline[1] == payline[2]:
                desc = [2, "Two consecutive symbols! Your bid has been multiplied by 2 times!"]
            else:
                desc = [0, "Nothing!"]
            if desc[0] == 0:
                final = economy_dict[str(ctx.author.id)] - bid_int
            else:
                final = economy_dict[str(ctx.author.id)] + (bid_int*desc[0])
            em.description += desc[1] + f"\nYour bid: {bid_int}\n{economy_dict[str(ctx.author.id)]} → {final}"
            economy_dict[str(ctx.author.id)] = final
            with open("econ.json", "w") as f:
                f.write(json.dumps(economy_dict, indent=4))
            return await ctx.send(embed=em)

    class Stats:
        
        def __init__(self, bot):
            self.bot = bot
            with open("crapikey.json") as f:
                self.key = json.load(f)["key"]
            self.session = aiohttp.ClientSession()

        async def get_json(self, link):
            async with self.session.get(f"https://api.royaleapi.com{link}", headers={"auth": self.key}) as resp:
                return await resp.json()

        @commands.command()
        async def profile(self, ctx, tag):
            stats = await self.get_json(f"/player/{tag}/stats")
            em = discord.Embed(color=0x181818, title=f"{stats['name']}'s Stats'")
            em.add_author(name=ctx.guild.author, icon_url=ctx.guild.author.icon_url)
            await ctx.send(embed=em)

        
        
