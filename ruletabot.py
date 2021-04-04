# External libraries
# Pickle, PyNaCl, dotenv, discord, datetime
import pickle, discord
from datetime import date
from dotenv import load_dotenv
from discord.ext import commands
import ctypes
import ctypes.util

# Libraries (Python 3.7.4)
import os
from random import sample, choice
from time import sleep

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
IMAGES = os.getenv('IMAGES')
bot = commands.Bot(command_prefix='$')

if not discord.opus.is_loaded():
    print("ctypes - Find opus:")
    a = ctypes.util.find_library('opus')
    print("Discord - Load Opus:")
    discord.opus.load_opus(a)
    print("Discord - Is loaded:")

def random_quote():
    with open('assets/quotes.txt', 'r') as f:
        lines = [line.rstrip() for line in f]
        return choice(lines)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("That command wasn't found! Sorry :(")
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send("Wrong parameter for this command")
    elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.send("You can only use the roulette once every 12 hours, you cheeky bastard")
    else:
        await ctx.send("Error 404, pls send help this is not a joke")

@bot.command(name='set_text', help='Sets text channel to send bot messages')
async def set_text(ctx, channel_name):
    id = ctx.guild.id
    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if channel:
        with open('text_channels.pickle', 'rb') as handle:
            server_channel_dict = pickle.load(handle)

        server_channel_dict[id] = channel.id
        
        with open('text_channels.pickle', 'wb') as handle:
            pickle.dump(server_channel_dict, handle)

        await ctx.send(f'{channel_name} is now the default channel for Ruletabot.')
    else:
        await ctx.send(f'{channel_name} is not a valid text channel of this server.')


@bot.command(name="roulette", help="Gracefully kicks out a number n of people in the current channel.")
@commands.cooldown(1, 43200, commands.BucketType.user)
async def roulette(ctx, n:int):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        if len(channel.members) >= n:
            lucky_bastards = sample(channel.members, n)
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio(source='assets/wof.mp3'))
            while vc.is_playing():
                    sleep(.1)
            today = date.today().strftime("%d-%m-%Y")
            text_channel = get_channel(ctx.guild)
            for lucky in lucky_bastards:
                if text_channel:
                    files = os.listdir(IMAGES)
                    image = choice(files)
                    image_file = discord.File(IMAGES + "/" + image)
                    quote = random_quote()
                    await text_channel.send(f"{lucky.mention} {today} \n {quote}", file=image_file)
                await lucky.move_to(None, reason="Unlucky")
            await vc.disconnect()
        else:
            await ctx.send(f"Can't roulette {n} people out of {len(channel.members)} that are currently in this voice channel")
    else:
        await ctx.send('You must be in a channel to use this feature.')

def get_channel(guild):
    with open('text_channels.pickle', 'rb') as handle:
        server_channel_dict = pickle.load(handle)
    if guild.id in server_channel_dict.keys():
        guild_id = server_channel_dict[guild.id]
        channel = discord.utils.get(guild.channels, id=guild_id)
        return channel
    else:
        return None

bot.run(TOKEN)