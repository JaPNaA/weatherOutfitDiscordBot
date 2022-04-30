import os
import discord
import urllib.request
import json
import garmets_data

if not os.path.exists("./cache"):
    os.mkdir("cache")

try:
    with open("cache/.bot_token") as file:
        bot_key = file.read().strip()
except:
    bot_key = ""

if not bot_key:
    bot_key = input("Enter bot token: ")
    with open("cache/.bot_token", 'w') as file:
        file.write(bot_key)

try:
    with open("cache/.weather_token") as file:
        weather_key = file.read().strip()
except:
    weather_key = ""

if not weather_key:
    weather_key = input("Enter weather token: ")
    with open("cache/.weather_token", 'w') as file:
        file.write(weather_key)

client = discord.Client()

cache_file_index = 0

def get_weather():
    # 43.548899,-79.6650758
    response = urllib.request.urlopen(
        "https://api.openweathermap.org/data/2.5/weather?lat=43.548899&lon=-79.6650758&appid=" + weather_key)
    response_data = response.read()
    return json.loads(response_data)


async def send_message_with_unsplash_image(text, query, channel):
    global cache_file_index

    image_req = urllib.request.urlopen(
        "https://source.unsplash.com/random/280x280/?" + query)

    cache_file_index += 1
    _local_cache_file_index = cache_file_index
    cache_file_path = f"./cache/image{_local_cache_file_index}.jpg"

    with open(cache_file_path, 'wb') as file:
        file.write(image_req.read())
    with open(cache_file_path, 'rb') as file:
        discord_file = discord.File(file)
        await channel.send(text, file=discord_file)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        # await message.channel.send('Hello!')
        await message.channel.send(get_weather())
    elif message.content.startswith('$unsplash'):
        outfit = garmets_data.Outfit().pick_outfit(1, False)
        await send_message_with_unsplash_image(
            text=outfit[0], 
            query=outfit[0],
            channel=message.channel
        )

client.run(bot_key)

