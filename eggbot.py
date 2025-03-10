from cogs.misc import save
from startup import load  # startup functions
import random  # to randomize egg, economy earnings, simp, and e!kiri
import sys as system

try:  # in case discord.py or simplejson isn't installed
    import discord
    from discord.ext import commands
    import simplejson as json  # to manage databases
except ModuleNotFoundError:  # install the discord modules
    import subprocess

    subprocess.check_call([system.executable, '-m', 'pip', 'install', "discord.py"])
    subprocess.check_call([system.executable, '-m', 'pip', 'install', "simplejson"])
    import discord
    from discord.ext import commands
    import simplejson as json

hosts, token, Bee, kirilist, eggs, eggTrigger, spic, simp, ohno, roles, colors, stonks, warehouse, joinRoles, insults, \
    beeEmbed, logging, dmLog, audit, deleteLog, times, activityTypes, flagFields, mmyes, scores = load(blacklist=[])

from cogs.commands.help import EmbedHelpCommand

# initialize a bunch of variables used in places
prefix = ['e!', 'E!', 'e! ', 'E! ', "e1", 'e1 ']  # you can kinda? customize this, but i honestly don't care
status = '{p}help'.format(p=prefix[0])
prefixLen = len(prefix)
intents = discord.Intents.all()
bot = commands.AutoShardedBot(command_prefix=prefix, case_insensitive=True, description=status, owner_ids=hosts,
                              help_command=EmbedHelpCommand(verify_checks=False, show_hidden=False), intents=intents)
bot.safeguard = True
bot.botSafeguard = True
async def customMessage(message):
    """placeholder function for custom fuckery"""
    return message
bot.customMessage = customMessage
bot.status = status
del status
bot.timerUsers = []
bot.roles, bot.stonks, bot.warehouse, bot.joinRoles = roles, stonks, warehouse, joinRoles
del roles, stonks, warehouse


# create functions imported by cogs
async def host_check(ctx):
    """verify that Eggbot admin exclusive commands *only* work for those privileged people"""
    if not await bot.is_owner(ctx.author):
        return False
    if audit:
        try:
            print(f"{ctx.message.author} used e!{str(ctx.command).lower()}!")
        except OSError:
            pass
    return True


async def owner_check(ctx):
    """verify that Eggbot admin exclusive commands *only* work for those privileged people"""
    if ctx.author.id != hosts[0]:
        return False
    if audit:
        try:
            print(f"{ctx.message.author} used e!{str(ctx.command).lower()}!")
        except OSError:
            pass
    return True


def joinArgs(args):
    echo = " ".join(args)
    echo = echo.strip(' ')
    return echo


def reverseBool(boolean):
    state = 'on' if boolean else 'off'
    boolean = not boolean
    return boolean, state


def markdown(textList):
    # 2/7 chance of being codeBlock or empty, then 50/50
    divisor = sum(len(i) + 1 for i in spic)
    if random.randrange(1, divisor + 1) <= 2:  # codeBlock and empty have to stay by themselves
        markedDown = pickRandomListObject(spic[-1])
    else:
        # Thanks Blue
        # Repeat until length(tempList) = amount of desired markdowns:
        #     Random = random(0, length markdown list)
        #     If !tempList.contains(markdown[random] {
        # //add to list
        # }
        length = random.randrange(1, len(spic[:-1]) + 1)
        markedDown = ''
        temp = []
        while len(temp) < length:
            thing = pickRandomListObject(spic[:-1])
            if thing not in tuple(temp):
                temp.append(thing)
                markedDown += pickRandomListObject(thing)

    return markedDown + pickRandomListObject(textList) + markedDown[::-1]


def pickRandomListObject(index):
    return index[random.randrange(0, len(index))]


def delistList(index):
    deobfuscated = []
    for i in index:
        for item in i:
            deobfuscated.append(item)
    return deobfuscated


if __name__ == '__main__':
    from cogs.commands.economy import addServerEgg
    import datetime

    import logging as logs

    logger = logs.getLogger('discord')
    logger.setLevel(logs.DEBUG)
    handler = logs.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logs.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # turn the bot "on"
    on = True
    # eggCount
    bot.eggCount = [0, True, datetime.datetime.now(tz=datetime.timezone.utc)]
    bot.scores = scores

    # verify that the bot is not running on Heroku
    try:
        import os
        os.startfile("verify.py")
        bot.heroku = False
        bot.loaded = True
    except AttributeError:
        bot.heroku = True
        bot.loaded = False


    @bot.event
    async def on_ready():
        print('We have logged in as ' + bot.user.name + "#" + bot.user.discriminator)
        if bot.heroku and not bot.loaded:  # load files from owner DMs because heroku
            async for message in bot.get_user(hosts[0]).history(limit=200):
                if message.author == bot.user and len(message.attachments) == 2:
                    for i in message.attachments:
                        os.remove(i.filename)
                        await i.save(i.filename)
                    # apply changes
                    _, _, _, _, _, _, _, _, _, bot.roles, _, bot.stonks, bot.warehouse, bot.joinRoles, _, _, _, _, _, \
                        _, _, _, _, _, bot.scores = load(blacklist=[])
                    bot.loaded = True
                    break

        await bot.change_presence(activity=discord.Game(name=bot.status))


    @bot.event
    async def on_message(message):
        """Core function of the bot"""
        if (
            str(message.channel.type) == "private" and dmLog or logging
        ) and message.author.id != bot.user.id:  # don't let the bot echo itself
            if len(message.content) > 0:
                content = "\n" + message.content
            else:
                content = message.content
            print(str('{a} says:'.format(a=str(message.author)) + content))
            if len(message.attachments) > 0:
                print("Attachments: {}".format(str(message.attachments)))
        if message.author.id == bot.user.id and bot.safeguard:
            return
        if (
            bot.botSafeguard
            and message.author.bot
            and message.author.id != bot.user.id
        ):
            return
        global stonks  # make economy things happen
        # new markdown parser utilizing replace()
        mess = message.content.lower()
        for i in delistList(spic):
            mess = mess.replace(i, '')
        a = mess.split()
        if mess in ohno:  # check if emotes are screwed up
            if message.author.id == bot.user.id:
                await message.channel.send("Woah! Looks like I don't have access to my emotes! "
                                           "Did <@" + str(hosts[0]) + "> add me to the Eggbot Discord Server?")
        else:
            if bot.user.mentioned_in(message):
                await on_client_mention(message)
            oval = random.randrange(0, 6)
            if oval > 2:
                oval = random.randrange(1, 3)
                await addServerEgg(message, oval, bot)
            try:
                if a[0].startswith(eggTrigger):
                    await message.channel.send(markdown(eggs))
                    bot.eggCount[0] += 1
                    save.sortScores(bot, edit=True)
                    try:
                        oval = random.randrange(0, 10)
                        if oval < 8:
                            bot.stonks["users"][str(message.author.id)]["global"] += 1
                    except KeyError:
                        bot.stonks["users"][str(message.author.id)] = {"global": 1, str(message.guild.id): 0,
                                                                       "notif": "False"}
                    except AttributeError:
                        pass
                    if not bot.safeguard:
                        async with message.channel.typing():
                            pass
                for i in ("simp", "sɪᴍᴘ"):
                    if a[0].startswith(i):
                        if message.author.id == bot.user.id:
                            return
                        else:
                            await message.channel.send(markdown(simp))
                for i in mmyes:
                    if a[0].startswith(i):
                        if message.author.id == bot.user.id:
                            return
                        else:
                            await message.channel.send(i)
                if message.channel.id in [714873042794315857, 719022288443539456] or \
                        a[0].startswith(('moyai', '🗿', ':moyai:', 'mooyai')):
                    await message.add_reaction('🗿')
                else:
                    await bot.process_commands(message)
                    await bot.customMessage(message)
            except IndexError:
                return

    async def on_client_mention(message):
        """Stuff to execute when the bot is mentioned"""
        await message.channel.send(message.author.mention)

    # The One Command to rule them all
    @bot.command(hidden=True, brief='{optional: channel/user mention or id} {words to echo}')
    @commands.check(host_check)
    async def say(ctx, *args):
        """Gets the bot to say what you ask it to"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("I was unable to delete the message!")
        arghs = list(args)
        channel = None
        try:
            if len(args[0]) == 22:
                channel = int(arghs[0][3:-1])
                channel = bot.get_user(channel)
                del arghs[0]
            elif len(args[0]) == 21:
                channel = int(arghs[0][2:-1])
                channel = bot.get_channel(channel)
                del arghs[0]
            elif len(args[0]) == 18:
                channel = bot.get_channel(int(args[0]))
                if not channel:
                    channel = bot.get_user(int(args[0]))
                del arghs[0]
            else:
                raise ValueError
        except (ValueError, IndexError):
            channel = ctx.channel
        finally:
            echo = joinArgs(arghs)
            if echo == "" or echo is None:
                if ctx.message.content[len(prefix) + 4 :] != "":
                    await ctx.send(ctx.message.content[len(prefix) + 4:])
                else:
                    await ctx.author.send("you idot, you can't just have me say nothing")
            else:
                try:
                    await channel.send(echo)
                except AttributeError:
                    await ctx.send(echo)


    @bot.event  # this is here because fuck you on_error doesn't get to be in a cog
    async def on_error(event, *args):
        owner = bot.get_user(int(hosts[0]))
        if str(event) != 'on_command_error':
            title = 'Error in event "{e}":'.format(e=event)
            emb = discord.Embed(title=title, description=str(system.exc_info()[1]), color=0xbc1a00)
            emb.set_footer(text='Please tell {o} "hey idiot, bot broken" if you think this '.format(o=owner) +
                                "shouldn't happen.")
            try:
                await args[0].channel.send(embed=emb)
            except discord.Forbidden:
                return
            except (discord.NotFound, IndexError):
                ApertureScienceErrorHandlingAssociate = bot.get_user(bot.owner_ids[0])
                await ApertureScienceErrorHandlingAssociate.send(embed=emb)
        raise system.exc_info()[0]


    # load commands and listeners
    from os import listdir
    cogDirectories = ['cogs/commands/', 'cogs/listeners/']  # bot will look for python files in these directories
    for cogDir in cogDirectories:
        loadDir = cogDir.replace('/', '.')
        for cog in listdir(cogDir):
            if cog.endswith('.py'):  # bot tries to load all .py files in said folders, use cogs/misc for non-cog things
                try:
                    bot.load_extension(loadDir + cog[:-3])
                except commands.NoEntryPointError:
                    print(f"{loadDir + cog[:-3]} is not a proper cog!")
                except commands.ExtensionAlreadyLoaded:
                    print('you should not be seeing this\n if you do, youre screwed')
                except commands.ExtensionFailed as failure:
                    print(f'{failure.name} failed! booooo')
                    print(failure)

    try:
        bot.run(token)
    except (FileNotFoundError, NameError):
        input("The bot token was not found! Press enter to exit...")
