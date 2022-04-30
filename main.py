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


def get_image_url_query(query):
    try:
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
    except:
        # fallback: unsplash
        return "https://source.unsplash.com/random/280x280/?" + urllib.parse.quote(query)


async def send_message_with_image(text, image_url, channel, **extention):
    global cache_file_index

    cache_file_path = f"./cache/{urllib.parse.quote(image_url, safe='')}"
    # check if extention doesn't exists
    if cache_file_path.rfind(".") < len(cache_file_path) - 4:
        cache_file_path += ".jpg"

    if not os.path.exists(cache_file_path):
        image_req = urllib.request.urlopen(image_url)
        with open(cache_file_path, 'wb') as file:
            file.write(image_req.read())

    with open(cache_file_path, 'rb') as file:
        discord_file = discord.File(file)
        await channel.send(text, file=discord_file)

def get_outfit_based_on_weather(weather_data):
    data = weather_data['main']
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
        weather_data = get_weather()
        outfit = get_outfit_based_on_weather(weather_data)
        await message.channel.send(
            f"It's {weather_data['main']['temp'] -273.15} degrees outside and " +
            ("" if 'rain' in weather_data else "not ") + "raining, so you should wear:"
        )
        for item in outfit:
            await send_message_with_image(
                text=item,
                image_url=get_image_url_query(item),
                channel=message.channel
            )


client.run(bot_key)

