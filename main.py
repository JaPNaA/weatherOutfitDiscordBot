import os
import random
import discord
import urllib.request, urllib.parse
import json
import garmets_data

outfits = garmets_data.Outfit()

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

def get_JSON(url):
    response = urllib.request.urlopen(url)
    response_data = response.read()
    return json.loads(response_data)


def get_weather():
    # 43.548899,-79.6650758
    return get_JSON("https://api.openweathermap.org/data/2.5/weather?lat=43.548899&lon=-79.6650758&appid=" + weather_key)


def get_wikimedia_image(query):
    response_data = get_JSON(
        "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=images&titles=" +
        query
    )

    pages = response_data['query']['pages']
    images = list(pages.items())[0][1]['images']
    rand_image = random.choice(images)

    image_data = get_JSON(f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles={urllib.parse.quote(rand_image['title'])}&iiprop=url&iiurlwidth=300")
    image_pages = image_data['query']['pages']
    url = list(image_pages.items())[0][1]['imageinfo'][0]['thumburl']

    return url


async def send_message_with_image(text, image_url, channel):
    global cache_file_index

    cache_file_path = f"./cache/{urllib.parse.quote(image_url, safe='')}"

    if not os.path.exists(cache_file_path):
        image_req = urllib.request.urlopen(image_url)
        with open(cache_file_path, 'wb') as file:
            file.write(image_req.read())

    with open(cache_file_path, 'rb') as file:
        discord_file = discord.File(file)
        await channel.send(text, file=discord_file)

def get_outfit_based_on_weather():
    data = get_weather()['main']
    rain = 'rain' in data
    set = 0
    if -12 < data['temp'] <= 0:
        set = 1
    if 0 < data['temp'] <= 12:
        set = 2
    if 12 < data['temp'] <= 24:
        set = 3
    if data['temp'] > 24:
        set = 4
    return outfits.pick_outfit(set, rain)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text_clean = message.content.lower()

    if text_clean.startswith('what should i wear'):
        outfit = get_outfit_based_on_weather()
        await send_message_with_image(
            text=outfit[0], 
            image_url=get_wikimedia_image(outfit[0]),
            channel=message.channel
        )


client.run(bot_key)

