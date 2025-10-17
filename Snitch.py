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
# Get the reactions
reactions = config.get("reactions", {})
correct_format_reaction = reactions.get("upvote").strip()
incorrect_format_reaction = reactions.get("downvote").strip()

def is_valid_reaction(reaction_string):
  # Check if the string consists of valid Unicode emoji characters
  return all(ord(char) <= 0x1F64F for char in reaction_string)

if (
  not is_valid_reaction(correct_format_reaction)
  ):
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

# Event handler for when a message is sent in a channel
async def process_message(message):

 try:

  request = config["requests"]
  # Define the verb which will be used for the communication with the Redmine API 
  request_verb = request.get("verb")
  # Define the headers for making requests to the Redmine API
  headers = config["headers"]
  # Create the template of the url which will be used for the communication with the Redmine API
  request_url_template = request.get("url_template")
  
  # Print the original message content
  logger.info(f'''Original message content: %s {message.content}''')

# Emojis can be classed as characters with an ID exceeding 0xA9; the following removes such characters from the message's raw text.
  filtered_content = "" 
  for character in message.content:
    if ord(character) > 0x00A9:
      continue
    filtered_content += character
  message.content = filtered_content

# Print the filtered message content
  logger.info(f'''Filtered message content: {message.content}''')

# Get the dictionary from the config file to store payloads for Redmine
  payloads = {}

  regex_pattern = config["regex_pattern"]

   # Define a regular expression to find numbers following hashtags
  validation_regex = re.compile(regex_pattern)

  # Define the validation point which will be used for the validation of the format of the messages
  validation_point = None

  # Call the method responsible for the building of the payload
  validation_point, payloads = module.execute(validation_regex, message, payloads)

  if validation_point:
    # Message has the correct format, add a thumbs up reaction and remove potential thumbs down
    if correct_format_reaction and incorrect_format_reaction:
      await message.add_reaction(correct_format_reaction)
      await message.clear_reaction(incorrect_format_reaction)
      
    if random.randint(1,4096) == 1:
      await message.add_reaction('🌟')
 
  else:
    # Message has the incorrect format, add a thumbs down reaction and remove potential thumbs up
    if correct_format_reaction and incorrect_format_reaction:
      await message.add_reaction(incorrect_format_reaction)
      await message.clear_reaction(correct_format_reaction)

  # Send the payloads to the Redmine API with PUT requests
  for key, value in payloads.items():
   # logger.info(f'''Issue number: {key}''')
    #logger.info(f'''Payload: {value}''')

    #Assign the number of the key to the url format to complete the url
    url = request_url_template.format(key = key)

    response = requests.put(
      url, 
      json=value, 
      headers=headers)
    
    logger.info("Request: %s %s\nPayload: %s\nHeaders: %s\nResponse: %s %s", request_verb, url,
      json.dumps(indent=4, obj=value), 
      headers,
      response.status_code, 
      response.text
      )
    
 except InvalidConfigurationException as e:
    logger.error(f"Configuration error: {e}") 

# Event handler for when the bot is ready
@client.event
async def on_ready():
  logger.info("Bot is ready!")

# Check to see if the bot is in the correct channel
@client.event
async def on_message(message):
  await process_message(message)


# Function responsible for the editing of a posted message
@client.event
async def on_message_edit(before, after):
    # Process the edited message using the common logic
    await process_message(after)    

# Start the bot with the provided token
client.run(token)


