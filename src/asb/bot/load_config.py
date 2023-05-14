"""
Module used to work with bot's configurations.
"""

# module for working w/ toml files
import logging
import toml


class BotConfig:
    """
    Class representing configuration of a bot.

    #### Attributes:

        token (:obj:`str`): Token of the bot.
    """

    def __init__(self, token: str):
        self.token: str = token

    @classmethod
    def from_file(cls, config_file_path: str):
        """
        Create an instance of BotConfig using a filepath.

        Filepath should point to a valid `bot_config.toml` file.

        #### Arguments:

            config_file_path (:obj:`str`): Path to the config file.

        """

        # open file w/ bot config
        try:
            with open(
                config_file_path,  # current file path + name
                "r",  # read-only config
            ) as config_file:
                # load the toml config object
                config_toml = toml.load(config_file)

                # load the token and throw an exception if cannot
                try:
                    token: str = config_toml["bot"]["token"]
                except Exception:  # failed to get token from toml
                    raise AttributeError(
                        f'Config file "{config_file_path}" does not have token properly defined.'
                    )

                # return new bot config instance
                logging.debug(f'Loaded bot config from "{config_file_path}".')
                return cls(token)
        except:  # failed to open the file
            raise OSError(
                f'Couldn\'t open the bot config file at "{config_file_path}".'
            )
