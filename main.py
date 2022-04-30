import os
import random
import discord
import urllib.request
import urllib.parse
import json
import garmets_data
import tokens
import re
import asyncio


if not os.path.exists("./cache"):
    os.mkdir("cache")


BOT_API_KEY = tokens.get_token("bot_token")
WEATHER_API_KEY = tokens.get_token("weather_token")
WEATHER_DEFAULT_LOCATION = (43.548899, -79.6650758)

NON_NUMERICAL_REGEX = re.compile(r'[^\d.-]+')

outfits = garmets_data.Outfit()
client = discord.Client()


def is_float(x: str):
    try:
        float(x)
        return True
    except ValueError:
        return False


def kelvin_to_celcius(kelvin: float) -> float:
    return kelvin - 273.15


def get_JSON(url):
    response = urllib.request.urlopen(url)
    response_data = response.read()
    return json.loads(response_data)


def get_weather(location):
    return get_JSON(
        f"https://api.openweathermap.org/data/2.5/weather?lat={location[0]}&lon={location[1]}&appid={WEATHER_API_KEY}"
    )


def get_image_url_query(query):
    try:
        # image from wikipedia
        response_data = get_JSON(
            "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=images&titles=" +
            urllib.parse.quote(query)
        )

        pages = response_data['query']['pages']
        # filter svgs: probably not what we're looking for
        images = [x for x in list(pages.items())[0][1]['images']
                  if not x['title'].endswith(".svg")]
        rand_image = random.choice(images)

        image_data = get_JSON(
            f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles={urllib.parse.quote(rand_image['title'])}&iiprop=url&iiurlwidth=300")
        image_pages = image_data['query']['pages']
        url = list(image_pages.items())[0][1]['imageinfo'][0]['thumburl']

        return url
    except BaseException as err:
        # fallback: unsplash
        print("Failed to get wikipedia image:", err)
        return "https://source.unsplash.com/random/280x280/?" + urllib.parse.quote(query)


async def send_message_with_image(text, image_url, channel):
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


def get_set_for_temperature(temp: float) -> int:
    if -12 < temp <= 0:
        return 1
    if 0 < temp <= 12:
        return 2
    if 12 < temp <= 24:
        return 3
    if temp > 24:
        return 4
    return 0


def get_outfit_based_on_weather(weather_data):
    data = weather_data['main']
    rain = 'rain' in data
    set = get_set_for_temperature(kelvin_to_celcius(data['temp']))
    return outfits.pick_outfit(set, rain)


async def what_should_i_wear_command(message):
    args = [float(x) for x in re.split(
        NON_NUMERICAL_REGEX, message.content) if is_float(x)]
    location = WEATHER_DEFAULT_LOCATION
    if len(args) >= 2:
        location = args[0], args[1]

    weather_data = get_weather(location)
    outfit = get_outfit_based_on_weather(weather_data)
    weather_deg_c = round(
        (kelvin_to_celcius(weather_data['main']['temp'])) * 10) / 10
    temp_description = outfits.set_type_names[get_set_for_temperature(
        weather_deg_c)]

    await message.channel.send(
        f"It's {weather_deg_c}°C in {weather_data['name'] or location}, which is {temp_description}! It's " +
        ("" if 'rain' in weather_data else "not ") +
        "raining, so you should wear:"
    )

    for i in range(len(outfits.garmet_type_info)):
        item = outfit[i]
        item_info = outfits.garmet_type_info[i]
        image_query = item
        response = f"{item} on your {item_info['goes_on']}"

        if item is None:
            response = f"nothing on your {item_info['goes_on']}"
            image_query = item_info['goes_on']

        await asyncio.sleep(2)
        await send_message_with_image(
            text=response,
            image_url=get_image_url_query(image_query),
            channel=message.channel
        )


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text_clean = message.content.lower()

    if text_clean.startswith('what should i wear'):
        await what_should_i_wear_command(message)


client.run(BOT_API_KEY)
