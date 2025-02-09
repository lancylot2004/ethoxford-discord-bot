# Discord Analysis Bot

## Overview
A discord bot that uses an LLM to process and output conclusions about the message history of the server its in.

##Relevant Bot Commands
Analysis 
!scrape - Scrape all messages in channel!
!dump - Dump all messages!
!frequency - Analyze the frequency of words in the channel!
!topUsers - Show most active users by message count
LLM
!summary - A summary of the goings in the server.
!query - Queries the LLM with message history.
!topics - The topics and their relevant parties.

## Set-up
1.	Clone the repository from https://github.com/lancylot2004/ethoxford-discord-bot.
2.	CD into the project directory and run in the command line: pip install -r requirements.txt
3.	Download Ollama: https://ollama.com/download 
4.	Download the ollama model: gemma2:2b. You can do this in the terminal by: ollama run gemma2:2b
5.	Download spaCy package with: python -m spacy download en_core_web_sm
6.	Invite the bot to your discord server with: https://discord.com/oauth2/authorize?&client_id=1337704412881354772&scope=bot+applications.commands&permissions=10240
7.	Run the bot with: python bot.py

## Usage
1.	Use the command !scrape to first get the message history of the server.
2.	The relevant bot commands will use this history when returning.

## Templated Bot Commands

Below are a list of bot commands that came with the template we’ve used (https://github.com/kkrypt0nn/Python-Discord-Bot-Template) and their uses.
Moderation
!kick - Kick a user out of the server. 
!nick - Change the nickname of a user on a server. 
!ban - Bans a user from the server. 
!purge - Delete a number of messages.
!hackban - Bans a user without the user having to be in the server. 
!archive - Archives in a text file the last messages with a chosen limit of messages.
Fun
!randomfact - Get a random fact. 
!coinflip - Make a coin flip, but give your bet before. 
!rps - Play the rock paper scissors game against the bot.
General
!help - List all commands the bot has loaded.
!botinfo - Get some useful (or not) information about the bot.
!serverinfo - Get some useful (or not) information about the server.
!ping - Check if the bot is alive.
!invite - Get the invite link of the bot to be able to invite it.
!server - Get the invite link of the discord server of the bot for some support.
!8ball - Ask any question to the bot.
!bitcoin - Get the current price of bitcoin.
