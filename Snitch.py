import discord
import os
import requests
import re
import json

# Change the working directory to the location of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Define the bot's intents, including all privileged intents
bot_intents = discord.Intents.all()

# Create a Discord client instance with the specified intents
client = discord.Client(intents=bot_intents)

# Define the headers for making requests to the Redmine API
redmine_headers = {"X-Redmine-API-Key": "4a2121484a69ce17c67d6654c1e60301181a5dce",
               "Content-Type": "application/json"}

# Event handler for when a message is sent in a channel
@client.event
async def process_message(message):

  # Check if the message is in the specified channel
  if message.channel.id != 1152230135244791818:
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

# Create a dictionary to store payloads for Redmine
  redmine_payloads = {}

   # Define a regular expression to find numbers following hashtags
  issue_number_regex = re.compile(r'(?<=\s#)\d+|(?<=^#)\d+')

  issue_number = None

# Loop through matched numbers in the message content to later construct a string with them
  for issue_number in issue_number_regex.findall(message.content):
    redmine_message = f'{message.author.name}: {message.content}'



 # Append attachment URLs to the string
    for attachment in message.attachments:
      redmine_message += f'\n{attachment.url}'

    # Append a link to the Discord message
    redmine_message += f'\n\n> Discord: {message.jump_url}'

    # Update the payload dictionary with the issue number as the key, as to not have duplicates
    redmine_payloads.update({
      issue_number:  
      {
        'issue': {
          'notes': redmine_message,
        }
      }
    })
    print("Redmine Payload being sent:", redmine_payloads)

  if issue_number:
    # Message has the correct format, add a thumbs up reaction and remove potential thumbs down
    await message.add_reaction("\U0001F44D")
    await message.clear_reaction("\U0001F44E")
    
  else:
    # Message has the incorrect format, add a thumbs down reaction and remove potential thumbs up
    await message.add_reaction("\U0001F44E")
    await message.clear_reaction("\U0001F44D")

  # Send the payloads to the Redmine API with PUT requests
  for key, value in redmine_payloads.items():
    print("Issue number: ", key)
    print("Redmine payload: ", value)
    response = requests.put(
      f"https://project.maslasbros.com/issues/{key}.json", 
      json=value, 
      headers=redmine_headers)
    
    print(f'\nPUT https://project.maslasbros.com/issues/{key}.json\n',
      json.dumps(indent=4, obj=value), 
      redmine_headers,
      response.status_code, 
      response.text, 
      sep='\n')

# Event handler for when the bot is ready
@client.event
async def on_ready():
  print("Bot is ready!")


@client.event
async def on_message(message):
  if message.channel.id != 1152230135244791818:
    return
  
  await process_message(message)

@client.event
async def on_message_edit(before, after):
    if after.channel.id != 1152230135244791818:
        return

    # Process the edited message using the common logic
    await process_message(after)    

# Read the bot token from a file
with open('token.txt', 'r') as f:
  token = f.read()

# Start the bot with the provided token
client.run(token)


