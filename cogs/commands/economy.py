from asyncio import sleep
from random import randrange

import discord
from discord.ext import commands

from eggbot import joinArgs


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["moneyHelp"])
    async def economyHelp(self, ctx):
        """Displays the manual for Eggbot's economy system"""
        emb = discord.Embed(title="Eggbot Economy Commands", color=0x00ff55)
        emb.add_field(name="Global Eggs", value="Eggs rewarded for using Eggbot commands, usable in e!shop.",
                      inline=False)
        emb.add_field(name="Server Eggs", value="Eggs rewarded for speaking in the server.", inline=False)
        await ctx.send(embed=emb)
        emb.add_field(name="e!fridge", value="", inline=False)
        emb.add_field(name="e!shop", value="Displays the selection of items on sale.", inline=False)
        emb.add_field(name="e!buy", value="Buys an item from the shop.", inline=False)
        emb.add_field(name="e!inv", value="Shows your inventory.", inline=False)
        emb.add_field(name="e!bank", value="Shows the current number of server eggs donated to the server.",
                      inline=False)
        emb.add_field(name="e!goals",
                      value="Displays the server goals. One can contribute to the funding of the goals by "
                            "using e!donate.", inline=False)
        emb.add_field(name="e!donate {number}", value="Donates the specified number of eggs to the server.",
                      inline=False)
        emb.add_field(name="e!setGoal {cost} {name}", value="Sets a server goal. (admin only)", inline=False)
        emb.add_field(name="e!deleteGoal {name}", value="Deletes a server goal. (admin only)", inline=False)
        emb.add_field(name="e!addEggs {number}", value="Adds eggs to the server bank. (admin only)", inline=False)
        emb.add_field(name="e!removeEggs {number}", value="Removes eggs from the server bank. (admin only)",
                      inline=False)
        emb.add_field(name="e!confirmGoal {name}",
                      value="Confirms goal completion. (Deducts eggs from the server bank, "
                            "deletes goal) (admin only)", inline=False)

    @commands.command(aliases=["notifications"], brief="{on/off}")
    async def notifs(self, ctx, arg1):
        """Sets notifications for when you gain egg(s)"""
        try:
            if arg1.lower() in ['on', "true", "yes", "y"]:
                self.bot.stonks["users"][str(ctx.author.id)]["notif"] = "True"
                await ctx.send("Egg gain notifications have been turned on.")
            else:
                self.bot.stonks["users"][str(ctx.author.id)]["notif"] = "False"
                await ctx.send("Egg gain notifications have been turned off.")
        except KeyError:
            await sleep(1)
            await self.notifs(ctx, arg1)

    @commands.command(aliases=['bal', 'balance'])
    async def fridge(self, ctx):
        """Shows the number of global and server eggs you own."""
        emb = discord.Embed(title="{u}'s fridge:".format(u=str(ctx.author)), color=0xfefefe)
        emb.set_footer(text="Protip: Use e!notifs to be notified of the number of eggs you receive.")
        try:
            wallet = self.bot.stonks["users"][str(ctx.author.id)]
            try:
                emb.add_field(name="Global Eggs:", value=wallet["global"])
            except KeyError:
                raise KeyError
            try:
                emb.add_field(name="Eggs for this Server:", value=wallet[str(ctx.guild.id)])
            except KeyError:
                wallet[str(ctx.guild.id)] = 0
                emb.add_field(name="Eggs for this Server:", value="0")
            except AttributeError:
                pass
            await ctx.send(embed=emb)
        except KeyError:
            await sleep(1)
            await self.fridge(ctx)
        except AttributeError:
            pass

    @commands.command(aliases=['serverBal', 'serverBalance', 'serverEggs'])
    async def bank(self, ctx):
        """Shows the current number of server eggs donated to the server."""
        try:
            emb = discord.Embed(title="{s} Bank Balance:".format(s=str(ctx.guild)),
                                description=str(self.bot.stonks["servers"][str(ctx.guild.id)]), color=0xfefefe)
            await ctx.send(embed=emb)
        except KeyError:
            self.bot.stonks["servers"][str(ctx.guild.id)] = 0
            emb = discord.Embed(title="{s} Bank Balance:".format(s=str(ctx.guild)), description="0", color=0xfefefe)
            await ctx.send(embed=emb)
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command()
    async def goals(self, ctx):
        """Displays any goals set in the current server"""
        try:
            emb = discord.Embed(title="{s} Server Goals:".format(s=str(ctx.guild)), color=0x00ff55)
            a = self.bot.warehouse[str(ctx.guild.id)]
            if len(a) > 0:
                i = len(a) // 2
                b = 0
                c = 1
                while i > 0:
                    v = "1 egg" if a[c] == 1 else "{e} eggs".format(e=str(a[c]))
                    emb.add_field(name=a[b], value=v, inline=False)
                    b += 2
                    c += 2
                    i -= 1
            else:
                emb.add_field(name="None", value="There are no goals set in this server.")
            await ctx.send(embed=emb)
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")
        except KeyError:
            self.bot.warehouse[str(ctx.guild.id)] = []
            emb = discord.Embed(title="{s} Server Goals:".format(s=str(ctx.guild)), color=0x00ff55)
            emb.add_field(name="None", value="There are no goals set in this server.")
            await ctx.send(embed=emb)

    @commands.command(aliases=['deposit'], brief="{number of eggs}")
    async def donate(self, ctx, arg1):
        """Donates eggs to the server bank, making progress toward any goals."""
        try:
            wallet = self.bot.stonks["users"][str(ctx.author.id)][str(ctx.guild.id)]
            arg1 = int(arg1)
        except KeyError:
            await ctx.send("Don't be cheeky, you don't have any eggs to donate!")
            return
        except AttributeError:
            await ctx.send("Don't be cheeky, this isn't even a server!")
            return
        try:
            if wallet < arg1:
                await ctx.send("Don't be cheeky, you don't have that many eggs to donate!")
                return
            elif arg1 <= 0:
                await ctx.send("bruh how do you donate less than 1 egg the heck")
                return
            self.bot.stonks["servers"][str(ctx.guild.id)] += arg1
        except KeyError:
            self.bot.stonks["servers"][str(ctx.guild.id)] = arg1
        self.bot.stonks["users"][str(ctx.author.id)][str(ctx.guild.id)] -= arg1
        emb = discord.Embed(title="👍 Donated {e} eggs to {s} Server".format(e=str(arg1), s=str(ctx.guild)),
                            color=0x00ff55)
        await ctx.send(embed=emb)

    @commands.command(aliases=['addGoal'], brief="{cost} {name}")
    async def setGoal(self, ctx, *args):
        """Adds a goal to the server (admins only)"""
        try:
            if ctx.author.guild_permissions.administrator:
                try:
                    a = self.bot.warehouse[str(ctx.guild.id)]
                except KeyError:
                    a = self.bot.warehouse[str(ctx.guild.id)] = []
                try:
                    if len(a) <= 8:
                        args = list(args)
                        cost = int(args[0])
                        if cost <= 0:
                            await ctx.send(
                                "dude what the heck how do you buy something for 0 or less money?!? the heck?")
                            return
                        del args[0]
                        name = joinArgs(args)
                        name = name.strip(' ')
                        if len(name) == 0:
                            raise IndexError
                        a.append(name)
                        a.append(cost)
                        await ctx.send("Set a goal of `{c}` egg(s) for `{g}`.".format(c=str(cost), g=name))
                    else:
                        await ctx.send("You have reached the limit of goals you can set. You can only have 5 goals.")
                except (IndexError, ValueError):
                    await ctx.send("You didn't provide the correct syntax. The syntax is `e!setGoal [cost] [name]`.")
            else:
                await ctx.send("Bruh, you can't do that!")
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command(aliases=['removeGoal'], brief="{name}")
    async def deleteGoal(self, ctx, *args):
        """Removes a goal from the server (admins only)"""
        try:
            if ctx.author.guild_permissions.administrator:
                try:
                    if len(self.bot.warehouse[str(ctx.guild.id)]) == 0:
                        await ctx.send("You don't have any goals to delete???????????")
                    else:
                        args = list(args)
                        name = joinArgs(args)
                        name = name.strip(' ')
                        a = 0
                        for _ in self.bot.warehouse[str(ctx.guild.id)]:
                            if name == self.bot.warehouse[str(ctx.guild.id)][a]:
                                del self.bot.warehouse[str(ctx.guild.id)][a], self.bot.warehouse[str(ctx.guild.id)][a]
                                await ctx.send("Deleted the `{g}` goal.".format(g=name))
                                return
                            else:
                                a += 1
                        await ctx.send("There is no goal called `{g}` to delete.".format(g=name))
                except (IndexError, ValueError):
                    await ctx.send("You didn't provide the correct syntax. The syntax is `e!deleteGoal [name]`.")
            else:
                await ctx.send("Bruh, you can't do that!")
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command(brief="{number}")
    async def addEggs(self, ctx, arg1):
        """Adds eggs to the server bank (admins only)"""
        try:
            if ctx.author.guild_permissions.administrator:
                arg1 = int(arg1)
                try:
                    self.bot.stonks["servers"][str(ctx.guild.id)] += arg1
                except KeyError:
                    self.bot.stonks["servers"][str(ctx.guild.id)] = arg1
                await ctx.send("Added {e} eggs to the server's egg bank.".format(e=str(arg1)))
            else:
                await ctx.send("Bruh, you can't do that!")
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command(brief="{number}")
    async def removeEggs(self, ctx, arg1):
        """Removes eggs from the server bank (admins only)"""
        try:
            if ctx.author.guild_permissions.administrator:
                arg1 = int(arg1)
                try:
                    if arg1 <= self.bot.stonks["servers"][str(ctx.guild.id)]:
                        self.bot.stonks["servers"][str(ctx.guild.id)] -= arg1
                        await ctx.send("Removed {e} eggs from the server's egg bank.".format(e=str(arg1)))
                    else:
                        self.bot.stonks["servers"][str(ctx.guild.id)] = 0
                        await ctx.send("Emptied the server's egg bank.")
                except KeyError:
                    self.bot.stonks["servers"][str(ctx.guild.id)] = 0
                    await ctx.send("The server bank doesn't have any eggs to remove?")
            else:
                await ctx.send("Bruh, you can't do that!")
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command(brief="{name}")
    async def confirmgoal(self, ctx, *args):
        """Deletes a goal and deducts the cost from the server bank (admins only)"""
        try:
            if ctx.author.guild_permissions.administrator:
                try:
                    try:
                        if len(self.bot.warehouse[str(ctx.guild.id)]) == 0:
                            await ctx.send("You don't have any goals to confirm???????????")
                        else:
                            args = list(args)
                            name = joinArgs(args)
                            name = name.strip(' ')
                            a = 0
                            for _ in self.bot.warehouse[str(ctx.guild.id)]:
                                if name == self.bot.warehouse[str(ctx.guild.id)][a]:
                                    cost = self.bot.warehouse[str(ctx.guild.id)][a + 1]
                                    try:
                                        if cost <= self.bot.stonks["servers"][str(ctx.guild.id)]:
                                            self.bot.stonks["servers"][str(ctx.guild.id)] -= cost
                                            del self.bot.warehouse[str(ctx.guild.id)][a]
                                            del self.bot.warehouse[str(ctx.guild.id)][a]
                                            await ctx.send("Confirmed the `{g}` goal transaction.".format(g=name))
                                        else:
                                            await ctx.send("The server bank doesn't that many eggs!?!")
                                        return
                                    except KeyError:
                                        self.bot.stonks["servers"][str(ctx.guild.id)] = 0
                                        await ctx.send("There are no eggs to spend.")
                                        return
                                else:
                                    a += 1
                            await ctx.send("There is no goal called `{g}` to confirm.".format(g=name))
                            return
                    except KeyError:
                        await ctx.send("There are no goals to confirm.")
                        return
                except (IndexError, ValueError):
                    await ctx.send("You didn't provide the correct syntax. The syntax is `e!confirmGoal [name]`.")
                    return
            else:
                await ctx.send("Bruh, you can't do that!")
        except AttributeError:
            await ctx.send("Bruh, this isn't a server!?!")

    @commands.command(aliases=['store'])
    async def shop(self, ctx):
        """Displays items purchasable with global eggs"""
        emb = discord.Embed(title="Eggbot Shop", color=0x00ff55)
        a = self.bot.warehouse["global"]
        if len(a) > 0:
            i = len(a) // 3
            b = 0
            while i > 0:
                v = "1 egg" if a[b + 1] == 1 else "{e} eggs".format(e=str(a[b + 1]))
                emb.add_field(name='{item} - {price}'.format(item=a[b], price=v), value=a[b + 2], inline=False)
                b += 3
                i -= 1
            emb.add_field(name="4 eggs - 5 eggs", value="obligatory money sink")
        else:
            emb.add_field(name="None", value="There are no items in stock.")
        emb.set_footer(text="We only take global eggs.")
        await ctx.send(embed=emb)

    @commands.command(aliases=['inv', 'items'])
    async def inventory(self, ctx):
        """Displays your collection of items"""
        try:
            inventory = self.bot.stonks["users"][str(ctx.message.author.id)]["inv"]
            if inventory == "None":
                emb = discord.Embed(title="{u}'s Inventory:".format(u=str(ctx.author)), description="{u} owns no items!"
                                    .format(u=str(ctx.author)), color=0xff0000)
            elif type(inventory) is dict:
                emb = discord.Embed(title="{u}'s Inventory:".format(u=str(ctx.author)), color=0xfefefe)
                for item in inventory:
                    emb.add_field(name=item, value=inventory[item], inline=True)
            else:
                self.bot.stonks["users"][str(ctx.author.id)] = {"global": 0, str(ctx.guild.id): 0, "notif": "False",
                                                                "inv": "None"}
                emb = discord.Embed(title="{u}'s Inventory:".format(u=str(ctx.author)), description=f"{str(ctx.author)}"
                                                                                                    f"'s inventory "
                                                                                                    f"appears to be "
                                                                                                    f"corrupted! The "
                                                                                                    f"user's inventory "
                                                                                                    f"has been reset",
                                    color=0xff0000)
        except KeyError:
            emb = discord.Embed(title="Error:",
                                description="There was an error loading your inventory. Check back later.",
                                color=0xff0000)
            self.bot.stonks["users"][str(ctx.author.id)] = {"global": 0, str(ctx.guild.id): 0, "notif": "False",
                                                            "inv": "None"}
        await ctx.send(embed=emb)

    @commands.command(aliases=['purchase'], brief="{item name}")
    async def buy(self, ctx, *args):
        """Buys an item from the shop"""
        args = list(args)
        name = joinArgs(args)
        del args
        name = name.strip(' ').lower()
        a = 0
        for item in self.bot.warehouse["global"]:
            if name == item:
                cost = self.bot.warehouse["global"][a + 1]
                try:
                    if cost <= self.bot.stonks["users"][str(ctx.author.id)]["global"]:
                        self.bot.stonks["users"][str(ctx.author.id)]["global"] -= cost
                        try:
                            self.bot.stonks["users"][str(ctx.author.id)]["inv"][item] += 1
                        except KeyError:
                            self.bot.stonks["users"][str(ctx.author.id)]["inv"][item] = 1
                        except TypeError:
                            self.bot.stonks["users"][str(ctx.author.id)]["inv"] = {item: 1}
                        await ctx.send("Bought `{g}`.".format(g=item))
                    else:
                        await ctx.send("You can't afford that item!?!")
                    return
                except KeyError:
                    await ctx.send("You don't have any eggs to spend?!?")
                    return
            a += 1
        if name in ("4 eggs", "four eggs"):
            try:
                if self.bot.stonks["users"][str(ctx.author.id)]["global"] >= 5:
                    self.bot.stonks["users"][str(ctx.author.id)]["global"] -= 1
                    await ctx.send("Bought `{g}` for `5 eggs`.".format(g=name))
                else:
                    await ctx.send("You can't afford that item!?!")
                return
            except KeyError:
                await ctx.send("You don't have any eggs to spend?!?")
            return
        await ctx.send("That item isn't on sale??? How do you buy something that isn't on sale???")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            if str(ctx.author.id) not in self.bot.stonks["users"]:
                raise KeyError
            args = ctx.message.content.split(' ')[0]
            args = args[2:]
            if args not in ("help", "invite", "server", "github", "admins", "test_args", "fridge", "bank", "notifs",
                                "save", "say", "rolegiver", "addroles", "backuproles", "save", "reloadroles", 'log',
                                'auditlog', 'spam', 'botspam', 'shutdown', 'print_emoji', 'economyhelp', 'donate',
                                'goals',
                                'setgoal', 'deletegoal', 'addeggs', 'removeeggs', 'confirmgoal', 'buy', 'inv', 'shop',
                                'save', 'notifs'):
                oval = randrange(0, 10)
                if oval < 8:
                    oval = randrange(1, 3)
                    self.bot.stonks["users"][str(ctx.author.id)]["global"] += oval
                    if self.bot.stonks["users"][str(ctx.author.id)]["notif"] == "True":
                        await ctx.send("You got {e} eggs!".format(e=str(oval)))
        except KeyError:
            self.bot.stonks["users"][str(ctx.author.id)] = {"global": 0, str(ctx.guild.id): 0, "notif": "False",
                                                            "inv": "None"}
        except AttributeError:
            pass


async def addServerEgg(message, eggs, bot):
    try:
        userData = bot.stonks["users"][str(message.author.id)]
        try:
            userData[str(message.guild.id)] += eggs
        except KeyError:
            userData[str(message.guild.id)] = eggs
        if userData["notif"] == "True":
            await message.channel.send("You got {e} {s} eggs!".format(e=str(eggs), s=str(message.guild)))
    except KeyError:
        try:
            bot.stonks["users"][str(message.author.id)] = {"global": 0, str(message.guild.id): eggs,
                                                           "notif": "False", 'inv': "None"}
        except AttributeError:
            pass
    except AttributeError:
        pass


def setup(bot):
    bot.add_cog(Economy(bot))
