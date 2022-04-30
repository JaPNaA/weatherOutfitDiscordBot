import discord

try:
    with open(".bot_token") as file:
        key = file.read().strip()
except:
    key = ""

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

if not key:
    key = input("Enter key: ")
    with open(".bot_token", 'w') as file:
        file.write(key)

client.run(key)
