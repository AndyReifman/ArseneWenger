#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A cog with useful commands around fixtures
"""
import discord
import requests, requests.auth
from bs4 import BeautifulSoup
from fotmob import fotmob
from datetime import datetime,timedelta
from datetime import date
from discord.ext import commands
from discord import app_commands
from utils import clamp_int, make_discord_timestamp


class FixturesCog(commands.Cog):
    def __init__(self, bot):
        """Save our bot argument that is passed in to the class."""
        self.bot = bot

    @app_commands.command(
        name="fixtures",
        description="Display the next N fixtures, default 3, max 10."
    )
    async def fixtures(self, interaction: discord.Interaction, count: int = 3):
        count = clamp_int(count, 1, 10)
        fixtures = parse_arsenal("fixtures")
        fixture_list = findFixtures(fixtures, count)

        embed = discord.Embed(color=0x9C824A)

        embed.set_author(
            name=f"Next {len(fixture_list)} Fixtures",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        for fixture in fixture_list:
            date_string = f"""{fixture.date} {date.today().year}  {fixture.time}"""
            discord_aware_stamp = make_discord_timestamp(date_string)
            embed.add_field(
                name=f"{fixture.team} - {fixture.comp}",
                value=f"{discord_aware_stamp}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="next",
        description="Display the time between now in utc and the next match."
    )
    async def next(self, interaction: discord.Interaction):
        """Returns how many days, hours, and minutes are left until the next fixture"""
        fixtures = parse_arsenal("fixtures")
        fixture = findFixtures(fixtures, 1)[0]
        if (date.today()).month == 12 and "jan" in fixture.date.lower():
            next_match_date = f"""{fixture.date} {date.today().year+1}  {fixture.time}"""
        else:
            next_match_date = f"""{fixture.date} {(date.today()).year}  {fixture.time}"""

        date_object = datetime.strptime(next_match_date, '%b %d %Y %H:%M')
        if bst_flag():
            delta = date_object - (datetime.utcnow() + timedelta(hours=1))
        else:
            delta = date_object - datetime.utcnow()

        discord_timestamp = make_discord_timestamp(date_object)

        if delta.days > 0:
            response = f"Next match is {fixture.team} in {delta.days} days, {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes \n On {discord_timestamp}"
        elif delta.days == 0:
            response = f"Next match is {fixture.team} in {delta.seconds//3600} hours, {(delta.seconds//60)%60} minutes \n {discord_timestamp}"
        else:
            channel = discord.utils.get(interaction.guild.text_channels, name="live-games")
            response = f"There is a match playing right now! head over to <#{channel.id}>"

        embed = discord.Embed(
            color=0x9C824A,
            description=response
        )

        embed.set_author(
            name=f"Next Game",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="results",
        description="Show recent results"
    )
    async def results(self, interaction: discord.Interaction):
        fixtures = parse_arsenal("results")
        body = findResults(fixtures)

        embed = discord.Embed(
            color=0x9C824A,
            description=f"```{body}```")

        embed.set_author(
            name="Last 3 results",
            icon_url="https://resources.premierleague.com/premierleague/badges/t3.png"
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(
        name="euro",
        aliases=("euros", ),
        help="Show recent results"
    )
    async def euro(self, ctx):
        body = getInternationalCup()
        await ctx.send(f"```{body}```")

    @commands.command(
        name="copa",
        aliases=("copas", ),
        help="Show results"
    )
    async def copa(self, ctx):
        body = getInternationalCup(44, 20210710)
        await ctx.send(f"```{body}```")

    @commands.command(
        name="olympic",
        aliases=("olympics", ),
        help="Show results"
    )
    async def olympic(self, ctx):
        body = getInternationalCup(66, 20210810)
        body = 'Men:\n' + body
        await ctx.send(f"```{body}```")
        body = getInternationalCup(65, 20210810)
        body = 'Women:\n' + body
        await ctx.send(f"```{body}```")

i = 0


class Match:
    def __init__(self, date, time, team, comp):
        self.date = date
        self.time = time
        self.team = team
        self.comp = comp


def getLocation(line):
    homeTeam = line[0].text.strip()
    if 'Arsenal' in homeTeam:
        return 0
    else:
        return 1


def bst_flag():
    """returns true if we are in bst"""
    date_plus_7 = datetime.utcnow().date() + timedelta(days=7)
    #BST falls between the last Sunday of march and the last sunday of october.
    if (datetime.utcnow().date()).month > 3 and (datetime.utcnow().date()).month < 11:
        return True
    #to account for that last sunday, if I add seven to the last remaining dates in march and october, i could account for that
    elif ((datetime.utcnow().date()).month) == 3 and (date_plus_7.month > 3 and date_plus_7.month < 11):
        return True
    else:
        return False

def parse_arsenal(value: str):
    url = f"https://www.arsenal.com/{value}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url,timeout=15, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    table = soup.find("div", {"class","accordions"})
    matches = table.findAll("article",attrs={'role': 'article'})
    return matches

def findFixtures(matches, number):
    fixtures = []
    body = ""
    match = matches[0].find("div",{"class","fixture-match"})
    date = matches[0].find("time").text
    time = date.split('-')[1].strip()
    date = date.split('-')[0][3:].strip()
    comp = matches[0].find("div",{"class","event-info__extra"}).text
    teams = match.findAll("div",{"class","fixture-match__team"})
    homeTeam = teams[0].find("div",{"class","team-crest__name-value"}).text
    awayTeam = teams[1].find("div",{"class","team-crest__name-value"}).text
    homeAway = getLocation(teams)
    if homeAway == 0:
        team = awayTeam + " (H)"
    else:
        team = homeTeam + " (A)"
    fixtures.append(Match(date, time, team, comp))
    if number == 0 or number > 10:
        x = 3
    else:
        x = number
    if len(matches) < x:
        x = len(matches)
    for i in range(1,x):
        match = matches[i].find("div",{"class","card__content"})
        try:
            date = matches[i].find("time").text
            time = date.split('-')[1].strip()
            date = date.split('-')[0][3:].strip()
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        except:
            time = "TBD"
            date = matches[i].find("div",class_=False, id=False).text.split(' ')
            date = (date[0][:3] + " " + date[1]).split(',')[0]
            comp = matches[i].find("div",{"class","event-info__extra"}).text
        try:
            team = match.find("span",{"class","team-crest__name-value"}).text
        except AttributeError:
            team = match.find("div",{"class","team-crest__name-value"}).text
        try:
            location = match.find("div",{"class","location-icon"})['title']
        except TypeError:
            teams = match.findAll("div",{"class","fixture-match__team"})
            homeAway = getLocation(teams)
            if homeAway == 0:
                location = "Home"
            else:
                location = "Away"
        if location == "Home":
            team = team + " (H)"
        else:
            team = team + " (A)"
        fixtures.append(Match(date, time, team, comp))
    return fixtures


def findResults(matches):
    body = ""
    for i in range(2,0,-1):
        result = ""
        try:
            match = matches[i].find("div",{"class","card__content"})
        except:
            if i == 0:
                return body
            break
        date = matches[i].find("time").text
        date = date.split('-')[0][3:].strip()
        comp = matches[i].find("div",{"class","event-info__extra"}).text
        team = match.find("span",{"class","team-crest__name-value"}).text
        location = match.find("div",{"class","location-icon"})['title']
        homeScore = match.findAll("span",{"class","scores__score"})[0].text
        awayScore = match.findAll("span",{"class","scores__score"})[1].text
        if homeScore > awayScore:
            if location == "Home":
                result += " W "
            elif location == "Neutral":
                if team == "Arsenal":
                    result += " L "
                else:
                    result += " W "
            else:
                result += " L "
        elif homeScore < awayScore:
            if location == "Home":
                result += " L "
            elif location == "Neutral":
                if team == "Arsenal":
                    result += " L "
                else:
                    result += " W "
            else:
                result += " W "
        else:
            result += " D "
        result += homeScore +" - "+awayScore
        if location == "Home":
            team = team + " (H)"
        else:
            team = team+ " (A)"
        body += "| " + date + " | " + result + " | " + team + " | " +comp+" |\n"
    result = ""
    date = matches[0].find("time").text
    date = date.split('-')[0][3:].strip()
    match = matches[0].find("div",{"class","fixture-match"})
    comp = matches[0].find("div",{"class","event-info__extra"}).text
    teams = match.findAll("div",{"class","fixture-match__team"})
    homeTeam = teams[0].find("div",{"class","team-crest__name-value"}).text
    awayTeam = teams[1].find("div",{"class","team-crest__name-value"}).text
    homeAway = getLocation(teams)
    homeScore = match.findAll("span",{"class","scores__score"})[0].text
    awayScore = match.findAll("span",{"class","scores__score"})[1].text
    if homeScore > awayScore:
        if homeAway == 0:
            result += " W "
        else:
            result += " L "
    elif homeScore < awayScore:
        if homeAway == 0:
            result += " L "
        else:
            result += " W "
    else:
        result += " D "
    result += homeScore +" - "+awayScore
    if homeAway == 0:
        team = awayTeam + " (H)"
    else:
        team = homeTeam + " (A)"
    body += "| " + date + " | " + result + " | " + team +" | " +comp+" |\n"
    return body

def getInternationalCup(leagueCode = 50, endDate = 20210711): #originally written for the euros so i have set the euros parameters as default
    """Gets the current international cup progression"""
    matches = []
    body = ""
    today = datetime.today().strftime('%Y%m%d')
    while len(matches) < 5 and int(today) < endDate:
        fixtures = fotmob.getLeague(leagueCode,"overview","league","UTC",today)
        for match in fixtures[:5]:
            matches.append(match)
            if len(matches) > 5:
                break
        today = str(int(today) + 1)
    for match in matches:
        body += match.getDate() + " | "
        if match.getKickOff():
            if match.getKickOff() == 'In Progress':
                body += match.getResult() + " | "
            else:
                body += match.getKickOff() + " | "
        else:
            body += match.getResult() + " | "
        body += match.getHomeTeam() + " v " + match.getAwayTeam() + "\n"
    return body


async def setup(bot):
    """
    Add the cog we have made to our bot.

    This function is necessary for every cog file, multiple classes in the
    same file all need adding and each file must have their own setup function.
    """
    await bot.add_cog(FixturesCog(bot))
