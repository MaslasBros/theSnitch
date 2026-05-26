import discord
import os
import requests
import re
import json
import random
import importlib
import logging

with open('config.json', 'r' ) as config_file:
  config = json.load(config_file)

class InvalidConfigurationException(Exception):
  pass

module_path = config["module"]
module = importlib.import_module(module_path)

# Define the token the functionality of the bot
token = config["token"]
# Retreave the logging variables from the json file
logging_config = config.get("logging", {})
logging_enabled = logging_config.get("enabled")
log_level = logging_config.get("log_level")
log_path = logging_config.get("log_path")
log_file = logging_config.get("log_file")

#
# Rest API
#

# Define the headers for making requests to the Redmine API
headers = config["headers"]
# Create the template of the url which will be used for the communication with the Redmine API
request_url = config["url"]

#
# Regex Patterns
#

# Retreave and compile the configured regex patterns
regex_patterns = config.get("regex_patterns", {})


# Validates the compiled regular expressions
def is_valid_regex(pattern: str) -> bool:
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False
    
pattern = regex_patterns["update"].strip()

if not is_valid_regex(pattern): 
  raise InvalidConfigurationException("Invalid update regex pattern configuration in config.json")

update_regex = re.compile(pattern)

pattern = regex_patterns["list"].strip()

if not is_valid_regex(pattern):
  raise InvalidConfigurationException("Invalid list regex pattern configuration in config.json")

list_regex = re.compile(pattern)

pattern = regex_patterns["closed"].strip()

if not is_valid_regex(pattern):
  raise InvalidConfigurationException("Invalid list regex pattern configuration in config.json")

closed_regex = re.compile(pattern)

pattern = regex_patterns["report"].strip()

if not is_valid_regex(pattern): 
  raise InvalidConfigurationException("Invalid report regex pattern configuration in config.json")

report_regex = re.compile(pattern)
#
# Reactions
#
reactions = config.get("reactions", {})
correct_format_reaction = reactions.get("upvote").strip()
incorrect_format_reaction = reactions.get("downvote").strip()

# Validates the retreaved reactions
def is_valid_reaction(reaction_string):
  # Check if the string consists of valid Unicode emoji characters
  return all(ord(char) <= 0x1F64F for char in reaction_string)

if not is_valid_reaction(correct_format_reaction):
    raise InvalidConfigurationException("Invalid reaction configuration in config.json")

if not is_valid_reaction(incorrect_format_reaction):
  raise InvalidConfigurationException("Invalid reaction configuration in config.json")

if not log_path:
  raise InvalidConfigurationException("Invalid log path in config.json") 

# Check if logging is enabled and find the log file  
if logging_enabled:
  logging.basicConfig(
    filename=os.path.join(log_path, log_file), 
    level=getattr(logging, log_level.upper()),
    format="%(asctime)s - %(levelname)s - %(message)s")
  
logger = logging.getLogger("discord")

# Change the working directory to the location of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Define the bot's intents, including all privileged intents
bot_intents = discord.Intents.all()

# Create a Discord client instance with the specified intents
client = discord.Client(intents=bot_intents)

##
# Methods
##

# Check if the bot is mentioned into the message sent
async def is_itself(message):
  if message.author.bot:
    return True
  
  return False


# Based on the message content it should decide the action that the bot shall execute.
async def select_command(message):
  content = message.content

  if report_regex.search(content):
    logger.info(f"Report: {content}")
    await report_issue(message)
  elif list_regex.search(content):
    logger.info(f"List: {content}")
    await list_issues(message)
  elif closed_regex.search(content):
    logger.info(f"List Closed: {content}")
    await list_closed_issues(message)
  else:
    logger.info(f"Update: {content}")
    await update_issue(message)


async def report_issue(message):
  if await is_itself(message):
    logger.warning(f"Report: Ignoring message from bot")
    return
  
  response = module.report(report_regex, message, discord, requests, request_url, headers)

  if response:
    await message.add_reaction(correct_format_reaction)
    await message.channel.send(embed=response)
    logger.info(f"Report {correct_format_reaction}: {response}")
  else:
    await message.add_reaction(incorrect_format_reaction)
    logger.warning(f"Report {incorrect_format_reaction}")

async def list_issues(message):
  if await is_itself(message):
    logger.warning(f"List: Ignoring message from bot")
    return
  
  project_id = config["project_id"]
  response = module.list(list_regex, message, project_id, "open", requests, request_url, headers)
  
  if response:
    await message.add_reaction(correct_format_reaction)
    await message.channel.send(response)
    logger.info(f"List {correct_format_reaction}: {response}")
  else:
    await message.add_reaction(incorrect_format_reaction)
    logger.warning(f"List {incorrect_format_reaction}")

async def list_closed_issues(message):
  if await is_itself(message):
    logger.warning(f"List: Ignoring message from bot")
    return
  
  project_id = config["project_id"]
  response = module.list_closed(list_regex, message, project_id, "closed", requests, request_url, headers)
  
  if response:
    await message.add_reaction(correct_format_reaction)
    await message.channel.send(response)
    logger.info(f"List Closed {correct_format_reaction}: {response}")
  else:
    await message.add_reaction(incorrect_format_reaction)
    logger.warning(f"List Closed {incorrect_format_reaction}")

# Update the history of an issue with the following message.
async def update_issue(message):
  if await is_itself(message):
    logger.warning(f"Update: Ignoring message from bot")
    return

  # Emojis can be classed as characters with an ID exceeding 0xA9; the following removes such characters from the message's raw text.
  filtered_content = "" 
  for character in message.content:
    if ord(character) > 0x00A9:
      continue
    filtered_content += character
  message.content = filtered_content

  # Get the dictionary from the config file to store payloads for Redmine
  payloads = {}

  # Define the validation point which will be used for the validation of the format of the messages
  validation_point = None

  # Call the method responsible for the building of the payload
  validation_point, payloads = module.update(update_regex, message, payloads)

  if validation_point:
    # Message has the correct format, add a thumbs up reaction and remove potential thumbs down
    if correct_format_reaction and incorrect_format_reaction:
      await message.add_reaction(correct_format_reaction)
      await message.clear_reaction(incorrect_format_reaction)
      logger.info(f"Update {correct_format_reaction}")
      
    if random.randint(1,4096) == 1:
      await message.add_reaction('🌟')
 
  else:
    # Message has the incorrect format, add a thumbs down reaction and remove potential thumbs up
    if correct_format_reaction and incorrect_format_reaction:
      await message.add_reaction(incorrect_format_reaction)
      await message.clear_reaction(correct_format_reaction)
      logger.warning(f"Update {incorrect_format_reaction}")

  # Send the payloads to the Redmine API with PUT requests
  for key, value in payloads.items():
    logger.info(f'''Issue number: {key}''')
    #logger.info(f'''Payload: {value}''')
    url = f"{request_url}/issues/{key}.json"

    response = requests.put(
      url, 
      json=value, 
      headers=headers)

# Event handler for when the bot is ready
@client.event
async def on_ready():
  logger.info("Bot is ready!")

# Check to see if the bot is in the correct channel
@client.event
async def on_message(message):
  await select_command(message)


# Function responsible for the editing of a posted message
@client.event
async def on_message_edit(before, after):
    # Process the edited message using the common logic
    await update_issue(after)    

# Start the bot with the provided token
client.run(token)


