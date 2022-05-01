import os
import random
from typing import Dict
import discord
import urllib.request
import urllib.parse
import json
import garmets_data
import tokens
import re
import asyncio
from outfit_saves import OutfitItem, OutfitSet, SavedOutfits


if not os.path.exists("./cache"):
    os.mkdir("cache")


BOT_API_KEY = tokens.get_token("bot_token")
WEATHER_API_KEY = tokens.get_token("weather_token")
WEATHER_DEFAULT_LOCATION = (43.548899, -79.6650758)

NON_NUMERICAL_REGEX = re.compile(r'[^\d.-]+')
NUMBER_REGEX = re.compile(r'\d+')
BRACKETS_REGEX = re.compile(r'\s*\(.+\)\s*')

outfits = garmets_data.Outfit()
saved_outfits = SavedOutfits()
client = discord.Client()

last_sent_outfit_sets_map: Dict[int, OutfitSet] = {}


def is_float(x: str):
    try:
        float(x)
        return True
    except ValueError:
        return False


def kelvin_to_celcius(kelvin: float) -> float:
    return kelvin - 273.15


def remove_brackets(string: str) -> str:
    return re.sub(BRACKETS_REGEX, "", string)


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

    cache_file_name = (urllib.parse.quote(image_url, safe=''))[-100:]
    cache_file_path = f"./cache/{cache_file_name}"
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
    rain_or_snow = ('rain' in weather_data) or ('snow' in weather_data)
    main_data = weather_data['main']
    set = get_set_for_temperature(kelvin_to_celcius(main_data['temp']))
    return outfits.pick_outfit(set, rain_or_snow)


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

    outfit_set = OutfitSet()

    for i in range(len(outfits.garmet_type_info)):
        item = outfit[i]
        image_url = get_image_url_query(
            remove_brackets(item) if item else
            outfits.garmet_type_info[i]['goes_on']
        )
        outfit_set.add_item(OutfitItem(i, item, image_url))

    await _send_outfit_set(outfit_set, message.channel)
    await message.channel.send("You can save this outfit by telling me to `save outfit`!")
    last_sent_outfit_sets_map[message.channel.id] = outfit_set


async def _send_outfit_set(outfit_set: OutfitSet, channel):
    for item in outfit_set.items:
        item_info = outfits.garmet_type_info[item.garmet_type]
        response = f"{item.garmet_name} on your {item_info['goes_on']}"

        if not item.garmet_name:
            response = f"nothing on your {item_info['goes_on']}"

        await asyncio.sleep(2)
        await send_message_with_image(
            text=response,
            image_url=item.image_url,
            channel=channel
        )


async def save_outfit_command(message):
    if message.channel.id not in last_sent_outfit_sets_map:
        await message.channel.send("You must request an outfit first.")
        return

    saved_outfits.save_outfit(
        message.channel.id, last_sent_outfit_sets_map[message.channel.id])
    saved_outfits.save()
    await message.channel.send("Saved outfit. You can see your `saved outfits` by asking.")


async def saved_outfits_command(message):
    outfits = saved_outfits.get_saved_outfit(message.channel.id)
    if len(outfits) <= 0:
        await message.channel.send("There are no saved outfits in this channel")
        return

    specific_index_matches = re.findall(NUMBER_REGEX, message.content)
    if not specific_index_matches:
        response = "Which saved outfit do you want to see? ..."
        for i in range(len(outfits)):
            response += f"\n`saved outfit {i + 1}`"
        await message.channel.send(response)
        return

    specific_index = int(specific_index_matches[0]) - 1
    if not (0 <= specific_index < len(outfits)):
        await message.channel.send("Invalid index")
        return

    await message.channel.send(f"Saved outfit {specific_index + 1}:")
    await _send_outfit_set(outfits[specific_index], message.channel)


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
    elif text_clean.startswith('save outfit'):
        await save_outfit_command(message)
    elif text_clean.startswith('saved outfit'):
        await saved_outfits_command(message)


client.run(BOT_API_KEY)
