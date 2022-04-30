import discord
import urllib.request

try:
    with open(".bot_token") as file:
        key = file.read().strip()
except:
    key = ""

client = discord.Client()


def get_weather():
    # 43.548899,-79.6650758
    response = urllib.request.urlopen(
        "https://api.openweathermap.org/data/2.5/weather?lat=43.548899&lon=-79.6650758&appid=54fcadf5eb972b7b498158fa814a0841")
    response_data = response.read()
    return response_data


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

if not key:
    key = input("Enter key: ")
    with open(".bot_token", 'w') as file:
        file.write(key)

client.run(key)

