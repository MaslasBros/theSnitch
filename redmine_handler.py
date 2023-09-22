import re
import requests
import json
import random

async def process_message_for_redmine(config, message, channel_id, correct_format_reaction, incorrect_format_reaction):

  redmine_request = config["requests"]["redmine"]
  # Define the verb which will be used for the communication with the Redmine API 
  redmine_request_verb = redmine_request.get("verb")
  # Define the headers for making requests to the Redmine API
  redmine_headers = config["headers"]["redmine_headers"]
  # Create the template of the url which will be used for the communication with the Redmine API
  redmine_request_url_template = redmine_request.get("url_template")

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
  redmine_payloads = config.get("redmine_payloads", {})

  regex_pattern = config["regex_pattern"]

   # Define a regular expression to find numbers following hashtags
  issue_number_regex = re.compile(regex_pattern)

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
    await message.add_reaction(correct_format_reaction)
    await message.clear_reaction(incorrect_format_reaction)
      
    if random.randint(1,4096) == 1:
      await message.add_reaction('🌟')

    
  else:
    # Message has the incorrect format, add a thumbs down reaction and remove potential thumbs up
    await message.add_reaction(incorrect_format_reaction)
    await message.clear_reaction(correct_format_reaction)

  # Send the payloads to the Redmine API with PUT requests
  for key, value in redmine_payloads.items():
    print("Issue number: ", key)
    print("Redmine payload: ", value)

    #Assign the number of the key to the url format to complete the url
    url = redmine_request_url_template.format(key = key)

    response = requests.put(
      url, 
      json=value, 
      headers=redmine_headers)
    
    print(f'\n{redmine_request_verb} {url}\n',
      json.dumps(indent=4, obj=value), 
      redmine_headers,
      response.status_code, 
      response.text, 
      sep='\n')