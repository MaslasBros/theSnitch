def update(update_regex, message, payloads):
  # Search the message for the first mention of the validation point
  validation_point = update_regex.search(message.content)
    # Loop through matched numbers in the message content to later construct a string with them
  for validation_point in update_regex.findall(message.content):
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
  return validation_point, payloads

##
# Lists from the Redmine REST API all the issue numbers of a specific user.
###
def list(list_regex, message, project_id, requests, url, headers):
  list = None
  match = list_regex.search(message.content)

  if not match:
    return list

  # The parameters
  trackers = ["1", "12"]  # or numeric IDs if needed
  limit = 5000    

  params = {
    "project_id": project_id,
    "tracker_id": ",".join(trackers),
    "status_id": "open",
    "sort": "created_on:desc",
    "limit": limit
}
  
  discord_username = message.author.display_name

  url = f"{url}/issues.json"
  response = requests.get(url, headers=headers, params=params)

   # No API response
  if response.status_code != 200:
      return list
  
  data = response.json()
  issues = data.get("issues", [])
  filtered_issues = []

  # Role restrictions
  roles = message.author.roles

  if any(role.name == "Beta Tester" for role in roles) and len(roles) == 1:
    limit = 5

  i = 0

  for issue in issues:
    for field in issue.get("custom_fields", []):
        if field.get("name") == "Discord Name" and field.get("value") == discord_username:
            filtered_issues.append(issue)
            i += 1
            break
        
    # Applies the Role restriction limit
    if limit == i:
       break

  if not filtered_issues:
    list = "📋 You have no open bugs and/or suggestions at the moment."
    return list

  # Build message with issue numbers and subjects
  issues_list = [f"#{issue['id']} – {issue['subject']}" for issue in filtered_issues]
  list = "📋 Your bugs and/or suggestions:\n" + "\n".join(issues_list);

  return list

##
# Returns details from the Redmine REST API regarding a specific issue.
###
def report(report_regex, message, discord, requests, url, headers):
  embed = None
  match = report_regex.search(message.content)

  if not match:
     return embed
  
  issue_id = match.group(1)

  url = f"{url}/issues/{issue_id}.json"
  response = requests.get(url, headers=headers)

  # No API response
  if response.status_code != 200:
      return embed

  data = response.json()
  issue = data.get("issue")

  # Issue not found response
  if not issue:
    return embed
  
  tracker = issue.get("tracker")

  # Ignores trakcers other than Bugs and/or Suggentions
  if tracker.get("id") != 1 and tracker.get("id") != 12:
     return embed

  tracker_name = tracker.get("name", "No tracker")
  subject = issue.get("subject", "No subject")
  status = issue.get("status", {}).get("name", "Unknown")
  #priority = issue.get("priority", {}).get("name", "Unknown")

  custom_fields = issue.get("custom_fields", [])
  beta_tester = None
  for field in custom_fields:
      if field["name"] == "Discord Name":
          beta_tester = field["value"]
          break

  description = issue.get("description", "").split("## Description", 1)[1]

  embed = discord.Embed(
      title=f"#{issue_id}: {subject}",
      color=0xff0000
  )

  embed.add_field(name="Type", value=tracker_name, inline=True)
  embed.add_field(name="Status", value=status, inline=True)
  #embed.add_field(name="Priority", value=priority, inline=True)

  if beta_tester:
      embed.add_field(name="Submitted", value=beta_tester, inline=False)

  if description:
      embed.add_field(name="Description", value=description, inline=False)

  return embed