import discord
from discord.ext import commands
from contextlib import redirect_stdout
import inspect, aiohttp, asyncio, io, textwrap, traceback

class RPSBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")
        self.session = aiohttp.ClientSession(loop=self.loop)
        self._last_result = None

    async def on_connect(self):
        self.remove_command('help')
        for name, func in inspect.getmembers(self):
            if isinstance(func, commands.Command):
                self.add_command(func)

    async def on_ready(self):
        perms = discord.Permissions.none()
        perms.administrator = True
        print(f"Bot is ready! Invite: {discord.utils.oauth_url(self.user.id, perms)}")

    async def on_member_join(self, member):
        await self.get_guild(371220792844746752).get_channel(371220792844746754).send(f"Hello {member.mention}! Welcome to **Royale Prestige Series**! Do `!region` to select your region! We hope you enjoy your time here! 😃")

    async def on_member_remove(self, member):
        await self.get_guild(371220792844746752).get_channel(371220792844746754).send(f"{member.mention} just left Royale Prestige Series. Bye Felicia! 👋")

    async def on_command_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{ctx.command.signature}``", description=ctx.command.short_doc))
        raise error

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
    async def poll(self, ctx, *, poll):
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
        await asyncio.sleep(5)
        sent_message = await ctx.channel.get_message(sent_message.id)
        em.title = f"Results!"
        reactions = sorted(sent_message.reactions, key=lambda x: numlist.index(x.emoji)+1, reverse=True)
        em.description = f'**{question}**\n\n' + '\n'.join([f"{numlist[n]} {choice} - **{reactions[n].count-1} votes**" for n,choice in enumerate(choices)])
        await ctx.send(embed=em)

    @commands.command(name='help')
    async def _help(self, ctx, command=None):
        '''Shows this page'''
        if command:
            command = discord.utils.get(self.commands, name=command.lower())
            return await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{command.signature}``", description=command.short_doc))
        em = discord.Embed(title='Help', color=0x181818)
        em.set_author(name='Royale Prestiege Series', icon_url=self.user.avatar_url)
        commands = []
        for command in self.commands:
            if command.hidden:
                continue
            commands.append(f"``{ctx.prefix}{command.name}{' '*(10-len(command.name))}{command.short_doc}``")
        em.description = '\n\n'.join(commands)
        em.set_footer(text="Type !help command for more info on a command.")
        await ctx.send(embed=em)


    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str, edit=False):
        """Evaluates python code"""

        if ctx.author.id != 273381165229146112:
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
                        paginated_text = ctx.paginate(value)
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
                    paginated_text = ctx.paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
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
    RPSBot().run("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs")
