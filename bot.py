import discord, mtranslate
from discord.ext import commands
from contextlib import redirect_stdout
import inspect, aiohttp, asyncio, io, textwrap, traceback, os, json, urbanasync
from cogs import Cog
import random
from paginator import PaginatorSession

class RPSBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")
        self.session = aiohttp.ClientSession(loop=self.loop)
        self._last_result = None
        self.urban_client = urbanasync.Client(session=self.session)
        self.maintenance = False
        self.role_message_ids = [[439701001210167306, 439701431088447489, 439701716234141696]]
        self.get_roles_lang = [
            ["🇬🇧", 390820109620477952],
            ["🇪🇸", 390820111310651395],
            ["🇮🇹", 390820130109652992],
            ["🇫🇷", 412266663317078016],
            ["🇩🇪", 390820128964608002],
            ["🇵🇹", 390820477641424896]
        ]
        self.get_roles_region = [
            ["🇺🇸", 393226619579400193],
            ["🇬🇧", 393226622247108621],
            ["🇦🇺", 393226625333985280]
        ]

    def paginate(self, text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text)-1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    async def on_connect(self):
        self.remove_command('help')
        for name, func in inspect.getmembers(self):
            if isinstance(func, commands.Command):
                self.add_command(func)
        for cog in Cog.all_cogs(Cog):
            try:
                self.add_cog(cog(self))
                print(f"Added cog: {cog.__name__}")
            except Exception as e:
                print(f"ERROR: {e}")

    async def on_ready(self):
        perms = discord.Permissions.none()
        perms.administrator = True
        print(f"Bot is ready! Invite: {discord.utils.oauth_url(self.user.id, perms)}")

    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == 390788953025806336:
            guild = discord.utils.get(self.guilds, id=payload.guild_id)
            user = discord.utils.get(guild.members, id=payload.user_id)
            if payload.message_id == self.role_message_ids[0][0] and payload.emoji.id == 429157195117232128:
                await user.add_roles(discord.utils.get(guild.roles, id=393217384112193557))
            elif payload.message_id == self.role_message_ids[0][1]:
                for role in self.get_roles_region:
                    if str(payload.emoji) == role[0]:
                        await user.remove_roles(discord.utils.get(guild.roles, id=393226619579400193), discord.utils.get(guild.roles, id=393226622247108621), discord.utils.get(guild.roles, id=393226625333985280))
                        await user.add_roles(discord.utils.get(guild.roles, id=role[1]))
            elif payload.message_id == self.role_message_ids[0][2]:
                for role in self.get_roles_lang:
                    if str(payload.emoji) == role[0]:
                        await user.add_roles(discord.utils.get(guild.roles, id=role[1]))

    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id == 390788953025806336:
            guild = discord.utils.get(self.guilds, id=payload.guild_id)
            user = discord.utils.get(guild.members, id=payload.user_id)
            if payload.message_id == self.role_message_ids[0][0] and payload.emoji.id == 429157195117232128:
                await user.remove_roles(discord.utils.get(guild.roles, id=393217384112193557))
            elif payload.message_id == self.role_message_ids[0][1]:
                await user.remove_roles(discord.utils.get(guild.roles, id=393226619579400193), discord.utils.get(guild.roles, id=393226622247108621), discord.utils.get(guild.roles, id=393226625333985280))
            elif payload.message_id == self.role_message_ids[0][2]:
                for role in self.get_roles_lang:
                    if str(payload.emoji) == role[0]:
                        await user.remove_roles(discord.utils.get(guild.roles, id=role[1]))
            

    async def on_member_join(self, member):
        try:
            await member.add_roles(discord.utils.get(member.guild.roles, id=388471876013391886))
        except:
            pass
        await discord.utils.get(member.guild.text_channels, name="welcome").send(f"Hello {member.mention}! Welcome to **{member.guild}**! Please read through the league <#390797608677015552> and <#414605548600950784> channels! We hope you enjoy your time here! 😃\n\n**Important:** Read and react to the messages in <#436817007057305601> corresponding with your intentions to gain roles and access our channels. Make sure you react with {discord.utils.get(member.guild.emojis, id=429157195117232128)} in order to obtain the visitor role which allows you to talk within our server!")

    async def on_member_remove(self, member):
        await discord.utils.get(member.guild.text_channels, name="welcome").send(f"**{member.name}** just left {member.guild.name}. Bye Felicia! 👋")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            return await ctx.send("You don't have the permissions to run that command!")
        await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{ctx.command.signature}``", description=ctx.command.short_doc))
        raise error

    async def on_message(self, message):
        if self.maintenance:
            return await message.channel.send("Bot is under maintenance right now, so all commands are temporarily disabled.")
        await self.process_commands(message)
        with open("commands.json") as f:
            comms = json.load(f)
        if message.content.startswith("!"):
            message_str = message.content.replace("!", "").split(" ")[0]
            if message_str in comms:
                await message.channel.send(comms[message_str])

    @commands.command()
    @commands.guild_only()
    async def region(self, ctx, *, name):
        '''The available regions are: `Americas`, `Europa`, and `Asia Pacific`. You could also use `clear` to clear your region setting.'''
        name = name.lower()
        regions = ['americas', 'europa', 'asia pacific', 'clear']
        if name == 'apac':
            name = 'asia pacific'
        if name == 'europe':
            name = 'europa'
        if name == 'america':
            name = 'americas'
        if name not in regions:
            return await ctx.send("The available regions are: `Americas`, `Europa`, and `Asia Pacific`. You could also use `clear` to clear your region setting.")
        for role in ctx.author.roles:
            if role.name.lower() in regions:
                await ctx.author.remove_roles(role)
        if name == 'clear':
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Region Unverified"))
            return await ctx.send('Region cleared. 👍')
        found_role = discord.utils.get(ctx.guild.roles, name=name.title())
        await ctx.author.add_roles(found_role)
        await ctx.send("Region set. 👍")

    @commands.command(aliases=["ui"])
    async def userinfo(self, ctx, user:discord.Member=None):
        """Gets a user info. Defaults to the user who called the command."""
        if not user:
            user = ctx.author
        em = discord.Embed(title=str(user), description=f"This user joined Discord since {user.created_at.strftime('%b %d, %Y %H:%M:%S')}. In other words this account is {(ctx.message.created_at - user.created_at).days} days old. 👴", color=0x181818)
        em.set_thumbnail(url=user.avatar_url)
        em.add_field(name="Nickname", value=user.nick)
        em.add_field(name="Joined At", value=user.joined_at.strftime('%b %d, %Y %H:%M:%S'))
        em.add_field(name="Status", value=f"Chilling in {user.status} mode.")
        em.add_field(name="Tag", value=user.mention)
        em.add_field(name="Roles", value=", ".join([role.name for role in list(reversed(user.roles)) if not role.is_default()]), inline=False)
        await ctx.send(embed=em)

    @commands.command()
    async def urban(self, ctx, *, search_term):
        '''Searches for a term in Urban Dictionary'''
        try:
            definition_number = int(search_term.split(" ")[-1])-1
        except:
            definition_number = 0
        try:
            term = await self.urban_client.get_term(search_term)
        except LookupError:
            return await ctx.send("Term does not exist!")
        definition = term[definition_number]
        em = discord.Embed(title=definition.word, description=definition.definition, color=0x181818)
        em.add_field(name="Example", value=definition.example)
        em.add_field(name="Popularity", value=f"{definition.upvotes} 👍 {definition.downvotes} 👎")
        em.add_field(name="Author", value=definition.author)
        em.add_field(name="Permalink", value=f"[Click here!]({definition.permalink})")
        await ctx.send(embed=em)

    
    @commands.command(hidden=True, name="maintenance")
    async def _maintenance(self, ctx):
        if ctx.author.id != 273381165229146112:
            return
        if not self.maintenance:
            await self.change_presence(game=discord.Game(name="Maintenance!"), status=discord.Status.dnd)
            await ctx.send("Bot set to maintenance mode.")
            self.maintenance = True
        else:
            await self.change_presence(game=discord.Game(name="DM For Support."), status=discord.Status.online)
            await ctx.send("Removed maintenance mode.")
            self.maintenance = False
        

    @commands.command(name='help')
    async def _help(self, ctx, command=None):
        '''Shows this page'''
        ems = []
        for cog in Cog.all_cogs(Cog):
            if cog.__name__ == "ReactWait":
                continue
            em = discord.Embed(title='Help', color=0x181818)
            em.set_author(name='Royale Prestige Series', icon_url=self.user.avatar_url)
            em.add_field(name=cog.__name__, value="```\n"+'\n\n'.join([f"{ctx.prefix}{attr.name}{' '*(15-len(attr.name))}{attr.short_doc}" for name, attr in inspect.getmembers(cog) if isinstance(attr, commands.Command)])+'\n```')
            ems.append(em)
        if command:
            command = discord.utils.get(self.commands, name=command.lower())
            return await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{command.signature}``", description=command.short_doc))
        comms = []
        for command in self.commands:
            if command.cog_name == "RPSBot" and not command.hidden:
                comms.append(f"{ctx.prefix}{command.name}{' '*(15-len(command.name))}{command.short_doc}")
        em = discord.Embed(title='Help', color=0x181818)
        em.set_author(name='Royale Prestige Series', icon_url=self.user.avatar_url)
        em.add_field(name="Bot Related", value=f"```\n"+'\n\n'.join(comms)+"\n```")
        ems.append(em)
        session = PaginatorSession(ctx=ctx, pages=ems, footer_text="Type !help command for more info on a command.")
        await session.run()

    @commands.command(aliases=['si'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Returns a server's info."""
        em = discord.Embed(color=0x181818, title=ctx.guild.name, description=f"This server has been here since {ctx.guild.created_at.strftime('%b %d, %Y %H:%M:%S')}. In other words this server is {(ctx.message.created_at - ctx.guild.created_at).days} days old. 👴")
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(name="ID", value=str(ctx.guild.id))
        em.add_field(name='Members Online', value=f"{len([member for member in ctx.guild.members if member.status != discord.Status.offline])}/{len(ctx.guild.members)}")
        em.add_field(name='Owner', value=ctx.guild.owner.mention)
        em.add_field(name='Text-Voice Channels', value=f"{len(ctx.guild.text_channels)}-{len(ctx.guild.voice_channels)}")
        em.add_field(name="Region", value=ctx.guild.region)
        em.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)}/50")
        em.add_field(name="Roles", value=str(len(ctx.guild.roles)))
        bans = await ctx.guild.bans()
        em.add_field(name="Bans", value=str(len(bans)))

        await ctx.send(embed=em)

    @commands.command(aliases=["ri"])
    @commands.guild_only()
    async def roleinfo(self, ctx, *, rolename):
        """Returns a role's info."""
        role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.guild.roles)
        if not role:
            return await ctx.send("That role does not exist!")
        if role.is_default():
            return await ctx.send("I think you know very well what this role is...")
        em = discord.Embed(color=role.color, title=role.name, description=f"This role has been here since {role.created_at.strftime('%b %d, %Y %H:%M:%S')}. In other words this role is {(ctx.message.created_at - role.created_at).days} days old. 👴")
        em.add_field(name="ID", value=str(role.id))
        em.add_field(name="Members", value=str(len(role.members)))
        em.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
        em.add_field(name="Displayed Separately", value="Yes" if role.hoist else "No")
        em.add_field(name="Position", value=str(role.position))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def rolemembers(self, ctx, *, rolename):
        """Shows all the members that have this role."""
        rolename = rolename.lower().replace("apac", "asia pacific")
        role = discord.utils.find(lambda r: r.name.lower() == rolename, ctx.guild.roles)
        if not role:
            return await ctx.send("That role does not exist!")
        if role.is_default():
            return await ctx.send("I think you know very well who has this role...")
        member_str = ""
        for n, member in enumerate(role.members):
            member_str += " " + member.mention
            if n % 2 == 0:
                member_str += "\n"
        await ctx.send(embed=discord.Embed(color=role.color, title=role.name, description=member_str))

    @commands.command(aliases=["t"])
    async def translate(self, ctx, language, *, message):
        """Translate messages into different languages."""
        with open("langcodes.json") as f:
            langcodes = json.load(f)
            print(langcodes)
        for lang_test in langcodes:
            if language.title() == lang_test["name"] or language.lower() == lang_test["code"]:
                lang_set = lang_test
                break
        try:
            await ctx.send(embed=discord.Embed(color=0x181818, title=f"Translated to {lang_test['name']}", description=mtranslate.translate(message, lang_set["code"], "auto")))
        except:
            await ctx.send("That isn't a valid language!")

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str, edit=False):
        """Evaluates python code"""

        if ctx.author.id != 295368465005543424:
            return

        env = {
            'bot': self,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
            'source': inspect.getsource
        }

        env.update(globals())

        body = self.cleanup_code(body)
        if edit: await self.edit_to_codeblock(ctx, body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await err.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if "MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs" in value:
                value = value.replace("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs", "[EXPUNGED]")
            if ret is None:
                if value:
                    try:
                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = self.paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                self._last_result = ret
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = self.paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await self.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await out.add_reaction('\u2705')  # tick
        elif err:
            await err.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')

    async def edit_to_codeblock(self, ctx, body, pycc='blank'):
        if pycc == 'blank':
            msg = f'{ctx.prefix}eval\n```py\n{body}\n```'
        else:
            msg = f'{ctx.prefix}cc make {pycc}\n```py\n{body}\n```'
        await ctx.message.edit(content=msg)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

if __name__ == '__main__':
    with open("token.json") as f:
        token = json.load(f)["token"]
    RPSBot().run(token)
