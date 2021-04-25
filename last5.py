import discord
import os
import requests
from bs4 import BeautifulSoup
import lxml
client = discord.Client()

class Gamecheck:
    def __init__(self, name):
            source = requests.get(f"https://www.11v11.com/teams/arsenal/tab/opposingTeams/opposition/{name}")
            soup = BeautifulSoup(source.text, 'lxml')
            games = soup.find_all(class_="result-status")
            allgames = []

            for game in games:
                allgames.append(game.text)
            self.last5 = allgames[-5:]

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!history'):
      team = " ".join(message.content.split()[1:]) #The team name has to be the full team name example Manchester United, with a space or it does not work
      qor = Gamecheck(team)
      print(Gamecheck(team))
      await message.channel.send(f"`Our last 5 games with this club: {qor.last5}`")
client.run("token")
