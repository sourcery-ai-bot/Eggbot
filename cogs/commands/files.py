import datetime
from asyncio import sleep

import simplejson as json

import discord
from discord.ext import commands, tasks

from cogs.misc.save import write
from eggbot import host_check, hosts


def getFiles(targets: list):
    """Gets a list of discord.Files objects based on the passed in file paths"""
    return [discord.File(filename=i, fp=i) for i in targets]


class Files(commands.Cog, name="File Management"):
    def __init__(self, bot):
        self.bot = bot
        self.autoSave.start()

    @commands.command(hidden=True)
    @commands.check(host_check)
    async def files(self, ctx):
        """Sends Eggbot's saved data."""
        try:
            await ctx.send(files=getFiles(['discord.log', 'roles.json', 'stonks.json']))
            if ctx.author.id == hosts[0]:
                await ctx.author.send(file=discord.File(filename="config.json", fp="config.json"))
        except Exception as E:
            await ctx.send('There was an error getting your files!')
            raise E

    @commands.command(hidden=True)
    @commands.check(host_check)
    async def save(self, ctx):
        """Saves the roles and economy databases to their respective JSONs"""
        write(self.bot)
        await ctx.send("Saved the roles and economy database!")

    @commands.command(hidden=True)
    @commands.check(host_check)
    async def backupRoles(self, ctx):
        """Creates a roles.json.bak based on the current roles database"""
        with open("roles.json.bak", "w") as j:
            dick = {"reactions": self.bot.roles, "join": self.bot.joinRoles}
            json.dump(dick, j, encoding="utf-8")
        await ctx.send("Backed up the current role database!")

    @commands.command(hidden=True)
    @commands.check(host_check)
    async def backupEconomy(self, ctx):
        """Creates a stonks.json.bak based on the current economy database"""
        with open("stonks.json.bak", "w") as j:
            dick = {"moneys": self.bot.stonks, "amazon": self.bot.warehouse}
            json.dump(dick, j, encoding="utf-8")
        await ctx.send("Backed up the current economy database!")

    def cog_unload(self):
        self.autoSave.cancel()

    @tasks.loop(hours=6)
    async def autoSave(self):
        write(self.bot)
        if self.bot.heroku:  # dm the files for safe-keeping
            await self.bot.get_user(hosts[0]).send(content='Autosaving...', files=getFiles(['roles.json',
                                                                                            'stonks.json']))

    @autoSave.after_loop
    async def on_autoSave_cancel(self):
        if self.autoSave.is_being_cancelled():
            print('The autosave timer has been reset.')

    @autoSave.before_loop
    async def before_autoSave(self):
        await self.bot.wait_until_ready()
        # sleep until the clock strikes an hour because im fucking sick of seeing uneven timestamps
        now = datetime.datetime.now()
        remaining = (now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0) - now).total_seconds()
        await sleep(remaining)


def setup(bot):
    bot.add_cog(Files(bot))
