"""Classes for retrieving DAT files from Gliderbot."""
import requests
from bs4 import BeautifulSoup

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc1/"


class DATHandler:
    """Class for retrieving DAT files from Gliderbot"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        try:
            # Retrieve the list of all available CC1 sets from Gliderbot.
            soup = BeautifulSoup(requests.get(GLIDERBOT_URL, timeout=10).text, "html.parser")

            # Ignore the first link, it is a link to parent directory.
            self.available_sets = [a.text for a in soup.find_all("a")[1:]]
        except Exception as ex:
            raise f"Error retrieving list of sets from Gliderbot: {ex}"

        # Cache results as we retrieve sets to minimize HTTP requests.
        self.cache = {}

    def fetch(self, levelset):
        """Retrieve a binary levelset by name from Gliderbot."""
        if levelset in self.cache:
            return self.cache[levelset]
        if levelset not in self.available_sets:
            raise Exception(f"{levelset} was not found on gliderbot.")
        resp = requests.get(GLIDERBOT_URL + levelset, timeout=10)

        if resp.status_code < 300:
            print(f"Successfully retrieved {GLIDERBOT_URL + levelset}.")
            self.cache[levelset] = resp.content
            return resp.content

        raise Exception(
            f"Failed to retrieve {GLIDERBOT_URL + levelset}. {resp.status_code}: {resp.reason}")
