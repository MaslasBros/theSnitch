def execute(validation_regex, message, payloads):

  # Search the message for the first mention of the validation point
  validation_point = validation_regex.search(message.content)
    # Loop through matched numbers in the message content to later construct a string with them
  for validation_point in validation_regex.findall(message.content):
    message_sent = f'{message.author.name}: {message.content}'


 # Append attachment URLs to the string
    for attachment in message.attachments:
      message_sent += f'\n{attachment.url}'

    # Append a link to the Discord message
    message_sent += f'\n\n> Discord: {message.jump_url}'

    # Update the payload dictionary with the issue number as the key, as to not have duplicates
    payloads.update({
      validation_point:  
      {
        'issue': {
          'notes': message_sent,
        }
      }
    })
    print("Payload being sent:", payloads)
  return validation_point, payloads