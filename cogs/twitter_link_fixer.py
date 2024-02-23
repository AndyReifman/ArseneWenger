import re
from urllib.parse import urlparse

from discord.ext import commands


class TwitterLinkFixerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def rewrite_url(self, message):
        parse_url = urlparse(message)
        return parse_url._replace(netloc="fxtwitter.com").geturl()

    def find_twitter_urls(self, message):
        twitter_or_x_pattern = re.compile(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/\S+')
        return re.findall(twitter_or_x_pattern, message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Limit fixing Tweets to first found link, to prevent potential spam
        try:
            twitter_url = self.find_twitter_urls(message.content.lower())[0]
        except IndexError:
            return
        if twitter_url:
            await message.edit(suppress=True)
            await message.reply(f"Fx'ed that for you! {self.rewrite_url(twitter_url)}", mention_author=False)
async def setup(bot):
    await bot.add_cog(TwitterLinkFixerCog(bot))
