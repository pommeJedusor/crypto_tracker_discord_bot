import discord
from discord.ext import tasks, commands

import json,requests
from datas import datas


MY_GUILD = discord.Object(id=datas.MY_GUILD)
FILE = "datas/wallets_adress.txt"
intents = discord.Intents.all()
bot=commands.Bot(command_prefix="!", intents=intents)

async def verif_wallet_fichier(adress):
    """
    vérifie l'occurence de l'adresse du wallet dans la base de donné
    """
    with open(FILE,"r") as f:
        for line in f:
            line = json.loads(line)
            if line[1]==adress:
                return True
        return False



@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced) } command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="wallets",description="permet de voir les wallets")
async def wallets(interaction: discord.Interaction):

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'2',
    'convert':'EUR'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': datas.COIN_MARKET_CAP,
    }
    r = requests.get(url,params=parameters,headers=headers)
    json_datas =json.loads(r.text)
    BTC_price = json_datas["data"][0]["quote"]["EUR"]["price"]
    ETH_price = json_datas["data"][1]["quote"]["EUR"]["price"]
    BTC_price = int(str(BTC_price).split(".")[0])
    ETH_price = int(str(ETH_price).split(".")[0])


    lines=[]
    with open(FILE,"r") as f:
        for line in f:
            lines.append(json.loads(line))

    eth_quantity=0
    btc_quantity=0
    for line in lines:
        if line[0]=="eth":
            url = f"https://api.etherscan.io/api?module=account&action=balance&address={line[1]}&tag=latest&apikey={datas.etherscan_key}"
            r = requests.get(url)
            print("eth",r)
            result = r.json()["result"]
            eth_quantity += int(result)/10**18
        elif line[0]=="btc":
            url = f"https://btcscan.org/api/address/{line[1]}"
            r = requests.get(url)
            print("BTC",r)
            result = r.json()["chain_stats"]["funded_txo_sum"]-r.json()["chain_stats"]["spent_txo_sum"]
            btc_quantity+=result
            

    #eth
    eth_eur = str(eth_quantity * ETH_price).split(".")[0]
    eth_quantity = str(eth_quantity).split(".")
    text=f"vous possédez {eth_quantity[0]},{eth_quantity[1][:3]} Ethers pour une valeur de {eth_eur} euros "

    #btc
    btc_quantity=str(btc_quantity)
    while len(btc_quantity)<8:
        btc_quantity="0"+btc_quantity
    if len(btc_quantity)>8:
        btc_quantity = btc_quantity[:len(btc_quantity)-8]+","+btc_quantity[-8:]
    else:
        btc_quantity = "0,"+btc_quantity
    btc_eur = str(float(btc_quantity.replace(",",".")) * BTC_price).split(".")[0]
    text+=f"\nvous possédez {btc_quantity} bitcoin pour une valeur de {btc_eur} euros "
    

    await interaction.response.send_message(text)
    
@bot.tree.command(name="add_wallets",description="permet d'ajouter un wallet")
@discord.app_commands.choices(blockchain=[
    discord.app_commands.Choice(name='etherum',value="eth"),
    discord.app_commands.Choice(name='bitcoin',value="btc")
])
async def add_wallets(interaction: discord.Interaction,blockchain:discord.app_commands.Choice[str],adress:str):
    if not await verif_wallet_fichier(adress):
        with open(FILE,"a") as f:
            f.write(json.dumps([blockchain.value,adress])+"\n")
        await interaction.response.send_message(f"l'adresse {adress} a bien été ajouté ")
    else:
        await interaction.response.send_message(f"l'adresse {adress} éxiste déja dans la base de donné ")

@bot.tree.command(name="remove_wallet",description="permet de retirer un wallet")
async def remove_wallet(interaction: discord.Interaction,adress:str):
    line_to_delete = ""
    file_content=""
    with open(FILE,"r") as f:
        for line in f:
            file_content+=line
            line = json.loads(line)
            if line[1]==adress:
                line_to_delete = json.dumps(line)+"\n"
    with open(FILE,"w") as f:
        f.write(file_content.replace(line_to_delete,""))
    if line_to_delete:
        await interaction.response.send_message(f"le wallet {adress} a bien été retiré de la base de donné ")
    else:
        await interaction.response.send_message(f"le wallet {adress} n'as pas été trouvé ")

bot.run(datas.TOKEN)