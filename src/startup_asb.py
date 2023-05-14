"""
Builds AMI-study-bot.

Requires:
    - `./bot_config.toml`: file with bot configuration
"""

### External Modules
import logging
from pathlib import Path

### Internal Modules
from asb.bot.startup_bot import run_bot


# Logging setup
logging.basicConfig(
    format="[%(asctime)s]{%(levelname)s} %(name)s: %(message)s",
    level=logging.DEBUG,
)


def run_asb():
    """
    Build and run asb application.
    """
    # build and run the bot
    run_bot(Path(__file__).with_name("bot_config.toml"))  # current path + config file

    # Program runs asynchronously inside `run_bot`


if __name__ == "__main__":
    run_asb()
