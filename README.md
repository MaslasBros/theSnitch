# TheSnitch
TheSnitch is a Discord bot that helps manage issue tracking integration and provides additional functionality for your Discord server.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Installation

To install TheSnitch, follow these steps:

1. Clone this repository: `git clone https://github.com/MaslasBros/TheSnitch.git`
2. Configure the bot by editing `config.json`.
3. Run the bot: `python Snitch.py`
4. (Optionally, you can add your own custom python script with a custom workflow; this script must have a specific format, which is analysed in the `Configuration` section)

## Usage

TheSnitch offers the following features:

- **Immediate Redmine Integration:** Post Discord messages as Redmine issues by following a specific format (Redmine is set up as the default API)
- **Custom Reactions:** Add custom reactions to messages with emoji responses.
- **Configuration for different REST APIs :** The bot can be configured to support a variety of different REST APIs

If Redmine integration is assumed, to create an issue from a discord message, the following format is used:

```
#123 Issue Title

Description of the issue. 
```

## Configuration

To configure TheSnitch, edit the `config.json` file. You can set up API details, reactions, and other discord-specific bot settings.

Here's an example of the `config.json` file:

```{
    "channel_id": "YOUR_DISCORD_CHANNEL_ID",
    "requests": 
    {
        "verb": "YOUR_REST_API_VERB",
        "url_template": "https://YOUR_URL_TEMPLATE.COM"
    },
    "token": "YOUR_DISCORD_BOT_TOKEN",
    "regex_pattern": "YOUR_REGEX_PATTERN",
    "headers":
    {
        "X-Redmine-API-Key": "YOUR_API_KEY",
        "Content-Type": "THE_TYPE_OF_THE_CONTENT"
    },
    "reactions":
    {
        "upvote": "YOUR_REACTION_TO_CORRECT_MESSAGE",
        "downvote": "YOUR_REACTION_TO_INCORRECT_MESSAGE"
    },
    "module": "YOUR_MODULE_NAME"
}
```
Furthermore, to import a custom python script which is responsible for a connection using other REST APIs, that script must have the following format:
An `exetute()` function which takes the parameters of `validation_regex, message, payloads`;

* `validation_regex`: The regex which will be used to validate the format of the messages   that are posted on discord
*  `message`: The actual message posted on discord
* `payloads`: The format of the message that is to be sent to the server 

This function must return two things to the main script of the bot: 
* `validation_point`: The point which will be used for the validation of the format of the messages
* `payloads`


## Contributing

We welcome contributions from the community. If you'd like to contribute to TheSnitch, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them with clear messages.
4. Push your changes to your fork: `git push origin feature/your-feature-name`.
5. Open a pull request on the main repository.

## License

TheSnitch is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- We thank the Discord.py and Redmine Python libraries for their valuable contributions.
- Special thanks to Kryall for building the base of the code this final version of the bot is based on. 
- Finally, we thank to our contributors and users for their feedback and support.