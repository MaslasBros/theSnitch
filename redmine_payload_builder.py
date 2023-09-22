def build_redmine_payload(validation_regex, message, redmine_payloads):

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
    redmine_payloads.update({
      validation_point:  
      {
        'issue': {
          'notes': message_sent,
        }
      }
    })
    print("Redmine Payload being sent:", redmine_payloads)
  return validation_point, redmine_payloads