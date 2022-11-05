"""Classes for retrieving, parsing, and writing CC2 C2M files."""
import requests
from bs4 import BeautifulSoup

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc2/"

class C2MHandler:
    """Class for retrieving, parsing, and writing CC2 C2M files."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        try:
            # Retrieve the list of all available CC1 sets from Gliderbot.
            soup = BeautifulSoup(
                requests.get(
                    GLIDERBOT_URL,
                    timeout=10).text,
                "html.parser")

            # Ignore the first link, it is a link to parent directory.
            self.available_sets = [a.text for a in soup.find_all("a")[1:]]
        except Exception as ex:
            raise f"Error retrieving list of sets from Gliderbot: {ex}"

        # Cache results as we retrieve sets to minimize HTTP requests.
        self.cache = {}

    def fetch(self, levelset):
        """Fetches a CC2 levelset from Gliderbot."""

    class Parser:
        """Class that parses raw bytes in C2M format."""
        def __init__(self):
            pass

    class Writer:
        """Writes to C2M format."""
        def __init__(self):
            pass
