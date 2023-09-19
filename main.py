import discord
import aiohttp
import random
import os
from discord.ext import commands
from PIL import Image
import io
from keep_alive import keep_alive
mytoken = os.environ['secretToken']
TOKEN = mytoken

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

async def fetch_pokemon_data(pokemon_id, is_shiny):
    api_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                name = data['name'].capitalize()
                stats = data['stats']
                base_stat_total = sum(stat['base_stat'] for stat in stats)
                sprite_url = data['sprites']['front_shiny' if is_shiny else 'front_default']

                shiny_name = f'**{name}**' if is_shiny else name

                stat_names = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
                stat_list = [f'{stat_names[i]}: {stat["base_stat"]}' for i, stat in enumerate(stats)]
                stat_text = '\n'.join(stat_list)

                name_emoji = '★' if is_shiny else ''

                embed = discord.Embed(
                    title=f'{shiny_name} {name_emoji}',
                    description=f'Base Stat Total: {base_stat_total}',
                    color=discord.Color.blue()
                )
                embed.add_field(name='Stats', value=stat_text, inline=False)

                async with session.get(sprite_url) as sprite_response:
                    if sprite_response.status == 200:
                        sprite_data = await sprite_response.read()
                        with Image.open(io.BytesIO(sprite_data)) as img:
                            img = img.resize((img.width * 5, img.height * 5))
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='PNG')
                            img_bytes.seek(0)
                            file = discord.File(img_bytes, filename='sprite.png')
                            embed.set_image(url='attachment://sprite.png')
                            return embed, file
                    else:
                        return None, None
            else:
                return None, None

@bot.command(name='wild')
async def wild_pokemon(ctx):
    is_shiny = random.random() <= 1 / 13
    random_pokemon_id = random.randint(1, 1014)
    embed, sprite_file = await fetch_pokemon_data(random_pokemon_id, is_shiny)
    
    if embed:
        await ctx.send(embed=embed, file=sprite_file)
    else:
        await ctx.send('Failed to fetch Pokémon data.')

@bot.command(name='starter')
async def starter_pokemon(ctx):
    starter_ids = [1, 4, 7, 152, 155, 158, 252, 255, 258, 387, 390, 393, 495, 498, 501, 650, 653, 656, 722, 725, 728, 810, 813, 816, 909, 912, 906]

    random_starter_id = random.choice(starter_ids)
    is_shiny = random.random() <= 5 / 13
    embed, sprite_file = await fetch_pokemon_data(random_starter_id, is_shiny)

    if embed:
        await ctx.send(embed=embed, file=sprite_file)
    else:
        await ctx.send(f'Failed to fetch data for Pokémon with ID {random_starter_id}')
keep_alive()
bot.run(TOKEN)
