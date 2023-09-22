import discord
import os
import requests
import re
import json
import random
import importlib

with open('config.json', 'r' ) as config_file:
  config = json.load(config_file)

module_path = config["module"]
module = importlib.import_module(module_path)

# Define the token the functionality of the bot
token = config["token"]
# Define the channel which the bot will watch and get the messages from
channel_id = config["channel_id"]
# Get the reactions
reactions = config.get("reactions", {})
correct_format_reaction = reactions.get("upvote")
incorrect_format_reaction = reactions.get("downvote")

# Change the working directory to the location of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Define the bot's intents, including all privileged intents
bot_intents = discord.Intents.all()

# Create a Discord client instance with the specified intents
client = discord.Client(intents=bot_intents)

# Event handler for when a message is sent in a channel
async def process_message(message):

  request = config["requests"]
  # Define the verb which will be used for the communication with the Redmine API 
  request_verb = request.get("verb")
  # Define the headers for making requests to the Redmine API
  headers = config["headers"]
  # Create the template of the url which will be used for the communication with the Redmine API
  request_url_template = request.get("url_template")

  # Check if the message is in the specified channel
  if message.channel.id != channel_id:
    return
  
  # Print the original message content
  print("Original message content:", message.content)

# Emojis can be classed as characters with an ID exceeding 0xA9; the following removes such characters from the message's raw text.
  filtered_content = "" 
  for character in message.content:
    if ord(character) > 0x00A9:
      continue
    filtered_content += character
  message.content = filtered_content

# Print the filtered message content
  print("Filtered message content:", message.content)

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
    await message.add_reaction(correct_format_reaction)
    await message.clear_reaction(incorrect_format_reaction)
      
    if random.randint(1,4096) == 1:
      await message.add_reaction('🌟')
 
  else:
    # Message has the incorrect format, add a thumbs down reaction and remove potential thumbs up
    await message.add_reaction(incorrect_format_reaction)
    await message.clear_reaction(correct_format_reaction)

  # Send the payloads to the Redmine API with PUT requests
  for key, value in payloads.items():
    print("Issue number: ", key)
    print("Payload: ", value)

    #Assign the number of the key to the url format to complete the url
    url = request_url_template.format(key = key)

    response = requests.put(
      url, 
      json=value, 
      headers=headers)
    
    print(f'\n{request_verb} {url}\n',
      json.dumps(indent=4, obj=value), 
      headers,
      response.status_code, 
      response.text, 
      sep='\n')

# Event handler for when the bot is ready
@client.event
async def on_ready():
  print("Bot is ready!")

# Check to see if the bot is in the correct channel
@client.event
async def on_message(message):
  if message.channel.id != channel_id:
    return
  await process_message(message)


# Function responsible for the editing of a posted message
@client.event
async def on_message_edit(before, after):
    if after.channel.id != channel_id:
        return 
    # Process the edited message using the common logic
    await process_message(after)    

# Start the bot with the provided token
client.run(token)


