"""Ollama Language Model, a wrapper for models running on the local machine."""

from collections.abc import Collection, Sequence
import json
import logging
import ollama
import discord
from discord.ext import commands
from collections import deque


_MAX_MULTIPLE_CHOICE_ATTEMPTS = 10
_DEFAULT_TEMPERATURE = 0.5
_DEFAULT_TERMINATORS = ()
_DEFAULT_SYSTEM_MESSAGE = (
    'Continue the user\'s sentences. Never repeat their starts. For example, '
    'when you see \'Bob is\', you should continue the sentence after '
    'the word \'is\'. Here are some more examples: \'Question: Is Jake a '
    'turtle?\nAnswer: Jake is \' should be completed as \'not a turtle.\' and '
    '\'Question: What is Priya doing right now?\nAnswer: Priya is currently \' '
    'should be completed as \'working on repairing the sink.\'. Notice that '
    'it is OK to be creative with how you finish the user\'s sentences. The '
    'most important thing is to always continue in the same style as the user.'
)

class LLM(commands.Cog, name="llm"):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.command(name="summary", description="A summary of the goings in the server.")
    async def summary(self, context: commands.Context) -> None:
        return await self.query(context, """
            Summarise the following conversation in a concise manner. Summarise in a purely 
            factual manner, without any opinions or conversation.
        """)

    
    @commands.command(name="query", description="Base command with usage.")
    async def query(self, context: commands.Context) -> None:
        """Base command with usage."""
        await context.send("Usage: !query <your_question>")

    @commands.command(name="query", description="Queries the LLM with message history.")
    async def query(self, context: commands.Context, query: str) -> None:
        """Queries the LLM with message history."""
        await context.send(embed=discord.Embed(
            title="Running LLM!"
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
                guild_cache[guild_id] = guild.name
            return guild_cache[guild_id]
        
        # llm = OllamaLanguageModel("gemma2:2b")
        llm = OllamaLanguageModel("gemma2:2b")
        message_queue = deque([
            f"{await get_user_name(message[0])} ({await get_server_name(message[1])}): {message[2]}\n"
            for message in messages
        ])
        response = llm.reduce_text(
            command = query,
            text = message_queue,
        )

        await context.send(embed = discord.Embed(
            description = response
        ))
        
    @commands.command(name="topics", description="The topics and their relevant parties.")
    async def topics(self, context: commands.Context) -> None:
        self.query(context, """
            TODO.
        """)


class OllamaLanguageModel:
    """Language Model that uses Ollama LLM models."""

    def __init__(
        self,
        model_name: str,
        *,
        system_message: str = _DEFAULT_SYSTEM_MESSAGE,
    ) -> None:
        """Initializes the instance.

        Args:
            model_name: The language model to use. For more details, see
                https://github.com/ollama/ollama.
            system_message: System message to prefix to requests when prompting the
                model.
            measurements: The measurements object to log usage statistics to.
            channel: The channel to write the statistics to.
        """
        self._model_name = model_name
        self._client = ollama.Client()
        self._system_message = system_message
        self._terminators = []

        logging.basicConfig(level = logging.INFO, format = "[%(levelname)s] %(asctime)s :: %(message)s")
        logging.info("Setup")

    def sample_text(
        self,
        prompt: str,
        *,
        max_tokens: int = 4096,
        terminators: Collection[str] = _DEFAULT_TERMINATORS,
        temperature: float = _DEFAULT_TEMPERATURE,
        timeout: float = -1,
        seed: int | None = None,
    ) -> str:
        del max_tokens, timeout, seed, temperature  # Unused.

        logging.info(f"Sent prompt, {len(prompt)} characters, beginning: \"{prompt[:32]}\".")

        prompt_with_system_message = f'{self._system_message}\n\n{prompt}'

        terminators = self._terminators + list(terminators)

        response = self._client.generate(
            model=self._model_name,
            prompt=prompt_with_system_message,
            options={'stop': terminators},
            keep_alive='10m',
        )
        result = response['response']

        logging.info(f"-> Generated response, {len(result)} characters, beginning: \"{result[:32]}\".")
        return result

    def reduce_text(
        self,
        command: str,
        text: deque[str],
        *,
        max_tokens: int = 4096,
        terminators: Collection[str] = _DEFAULT_TERMINATORS,
        temperature: float = _DEFAULT_TEMPERATURE,
        timeout: float = -1,
        seed: int | None = None,
    ) -> str:
        chunk = ""
        command_length = len(command)

        while len(text) > 1:
            message = text.popleft()
            if len(chunk) + len(message) > max_tokens - command_length:
                response = self.sample_text(
                    command + chunk, 
                    max_tokens = max_tokens,
                    terminators = terminators, 
                    temperature = temperature,
                    timeout = timeout,
                    seed = seed,
                )
                text.append(response)
                chunk = message
            else:
                chunk += message
        
        assert len(text) == 1
        return text.pop()


async def setup(bot) -> None:
    await bot.add_cog(LLM(bot))


