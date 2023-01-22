import discord
from discord.ext import commands
from discord import app_commands

from bs4 import BeautifulSoup
import requests

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "deflate",
    "accept-language": "fr-FR,fr;q=0.7",
    "cache-control": "max-age=0",
    "cookie": "ig_tz=Europe%2FBrussels; ig_location=en; PHPSESSID=847f9152e14a390fcdd4065c0da572e7; G_ENABLED_IDPS=google; products_history_v2=NzA3Mg%3D%3D; ig_user_platform_id=1; ig_tz=Europe%2FBrussels",
    "referer": "https://www.instant-gaming.com/en/7072-buy-hogwarts-legacy-pc-game-steam-europe/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

def finds_game(name):
    url =f"https://www.instant-gaming.com/en/search/?query={name}"
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    games_find = []
    for pomme in soup.find_all(class_ = "item force-badge"):
        if pomme.find(class_="cover video"):
            games_find.append({"game_name":pomme.find(class_="cover video")["title"],"url_page":pomme.find(class_="cover video")["href"]})
        elif pomme.find(class_="cover"):
            games_find.append({"game_name":pomme.find(class_="cover")["title"],"url_page":pomme.find(class_="cover")["href"]})

    return games_find



class Dropdown(discord.ui.Select):
    def __init__(self,bot,games_find, price):
        self.bot = bot
        self.price = price

        options=[]
        compteur = 0
        for arg in games_find:
                options.append(discord.SelectOption(label=arg["game_name"],value=compteur))
                compteur+=1

        super().__init__(placeholder="choisissez la version du jeu", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"choix de l'option {int(self.values[0])+1} du nom de {self.options[int(self.values[0])]} je vous préviens quand il couteras moins de {self.price} euros ")

class DropdownView(discord.ui.View):
    def __init__(self,bot,games_find, price):
        super().__init__()

        self.add_item(Dropdown(bot,games_find, price))

class InstantGaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="instant_gaming",description="permet d'ajouter un jeu à la liste")
    async def add_game(self,interaction:discord.Interaction,name:str, price:float):
        view = DropdownView(self.bot,finds_game(name),price)
        await interaction.response.send_message("choisissez votre jeu",view=view,ephemeral=True)



async def setup(bot):
    await bot.add_cog(InstantGaming(bot))