import discord
from discord import app_commands
from discord.ext import commands

import time,json
from typing import Optional

line = ["course/payment",["article 1","article2"],"price","date"]
FILE = "courses.txt"

class courses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_course",description="permet d'ajouter un achat au magasin")
    async def add_course(self, interaction:discord.Interaction,articles:str,montant:float):
        course = ["course",articles.split(","),montant,time.time()]
        with open(FILE,"a") as f:
            f.write(json.dumps(course) + "\n")
        if len(articles.split(","))==1:
            await interaction.response.send_message(f"l'article {articles} accheté pour un montant de {montant} a bien été ajouté ")
        else:
            articles_str = ""
            for article in articles.split(","):
                articles_str+=article
                if not article==articles.split(",")[-1]:
                    articles_str+=","
            await interaction.response.send_message(f"les articles {articles_str} pour un montant total de {montant} ont bien été ajoutés ")

    @app_commands.command(name="add_payment",description="permet d'ajouter un payment")
    async def add_payment(self, interaction:discord.Interaction,montant:float):
        payment = ["payment",[],montant,time.time()]
        with open(FILE,"a") as f:
            f.write(json.dumps(payment) + "\n")
        await interaction.response.send_message(f"le payment de {montant} a bien été joué ")
    
    @app_commands.command(name="how_much_i_have",description="permet de voir le montant possédé pour les courses")
    async def how_much_i_have(self, interaction:discord.Interaction):
        montant = 0
        with open(FILE,"r") as f:
            for line in f:
                line = json.loads(line)
                if line[0]=="payment":
                    montant+=line[2]
                else:
                    montant-=line[2]
        await interaction.response.send_message(f"vous avez encore {round(montant,2)} euros ")

    @app_commands.command(name="historique",description="permet de voir l'historique")
    async def historique(self, interaction:discord.Interaction, last:int=10):
        text=[]
        with open(FILE,"r") as f:
            compteur=0
            lines = [i for i in f]
            lines.reverse()
            for line in lines:
                if last==compteur:
                    break
                compteur+=1
                line = json.loads(line)
                articles = ""
                for article in line[1]:
                    articles+=article
                    if not article==line[1][-1]:
                        articles+=","
                    else:
                        articles+=" "
                text.append(f"{articles}{line[0]} de {line[2]} euros.{time.ctime(line[3])} \n")
        await interaction.response.send_message("".join(text))
        


async def setup(bot):
    await bot.add_cog(courses(bot))
