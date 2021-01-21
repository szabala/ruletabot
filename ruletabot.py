# External libraries
# Pickle, PyNaCl, dotenv, ffmpeg, discord, datetime
import pickle, ffmpeg, discord
from datetime import date
from dotenv import load_dotenv
from discord.ext import commands

# Libraries (Python 3.7.4)
import os
from random import sample
from time import sleep

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("That command wasn't found! Sorry :(")
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send("Wrong parameter for this command")
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
async def roulette(ctx, n:int):

    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        if len(channel.members) >= n:
            lucky_bastards = sample(channel.members, n)
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio(source='assets/wof.mp3',executable="ffmpeg/ffmpeg.exe"))
            while vc.is_playing():
                    sleep(.1)
            today = date.today().strftime("%d-%m-%Y")
            text_channel = get_channel(ctx.guild)
            for lucky in lucky_bastards:
                if text_channel:
                    # Enviar Gif tambien
                    await text_channel.send(f"{lucky.display_name} {today}")
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