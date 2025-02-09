import discord
from discord.ext import commands
import spacy
import matplotlib.pyplot as plt
from collections import Counter
import io

class Analysis(commands.Cog, name="analysis"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="scrape", description="Scrape all messages in channel!")
    async def analyze(self, context: commands.Context) -> None:
        await context.send(embed=discord.Embed(
            title="Scraping messages!"
        ))

        async for message in context.channel.history(limit=1024, before=context.message):
            await self.bot.database.add_msg(message.author.id, message.guild.id, message.content)

        await context.send(embed=discord.Embed(
            title="Done!"
        ))

    @commands.command(name="dump", description="Dump all messages!")
    async def dump(self, context: commands.Context) -> None:
        """Dump the data"""

        await context.send(embed=discord.Embed(
            title="Dumping messages!"
        ))

        messages = await self.bot.database.get_msgs(context.guild.id)
        user_cache = {}
        guild_cache = {}

        async def get_user_name(user_id):
            if user_id not in user_cache:
                user = await self.bot.fetch_user(user_id)
                user_cache[user_id] = user.name
            return user_cache[user_id]

        async def get_server_name(guild_id):
            if guild_id not in guild_cache:
                guild = await self.bot.fetch_guild(guild_id)
                guild_cache[guild_id] = guild
            return guild_cache[guild_id]

        message_chunks = []
        current_chunk = ""

        for message in messages:
            message_content = f"{await get_user_name(message[0])} ({await get_server_name(message[1])}): {message[2]}\n"
            if len(current_chunk) + len(message_content) > 4096:
                message_chunks.append(current_chunk)
                current_chunk = message_content
            else:
                current_chunk += message_content

        if current_chunk:
            message_chunks.append(current_chunk)

        for chunk in message_chunks:
            await context.send(embed=discord.Embed(
                title="Messages",
                description=chunk
            ))

    @commands.command(name="frequency", description="Analyze the frequency of words in the channel!")
    async def frequency(self, context: commands.Context) -> None:
        await context.send(embed=discord.Embed(
            title="Frequency Analysis"
        ))

        messages = await self.bot.database.get_msgs(context.guild.id)
        all_text = " ".join([message[2] for message in messages])

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(all_text)
        words = [token.text for token in doc if token.is_alpha]
        word_freq = Counter(words)

        common_words = word_freq.most_common(10)
        labels, values = zip(*common_words)

        plt.figure(figsize=(10, 5))
        plt.bar(labels, values)
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.title('Top 10 Most Common Words')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        file = discord.File(buf, filename="frequency.png")
        embed = discord.Embed(title="Word Frequency Analysis")
        embed.set_image(url="attachment://frequency.png")
        await context.send(file=file, embed=embed)

    @commands.command(name="topUsers", description="Show most active users by message count")
    async def top_users(self, context: commands.Context) -> None:
        messages = await self.bot.database.get_msgs(context.guild.id)
        counter = Counter(msg[0] for msg in messages)
        top_10 = counter.most_common(10)
        
        result = []
        for user_id, count in top_10:
            user = await self.bot.fetch_user(user_id)
            result.append(f"{user.name}: {count}")
        
        await context.send(embed=discord.Embed(
            title="Top 10 Active Users",
            description="\n".join(result)
        ))

async def setup(bot) -> None:
    await bot.add_cog(Analysis(bot))
