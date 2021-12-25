import json

from bs4 import BeautifulSoup
import requests


class ParseEntity:
    """Parses and encapsulates this data"""
    show_the_process = True

    def __init__(self, url: str):
        self.url = url
        self.update()

    def update(self) -> None:
        pass

    def parse(self) -> dict:
        pass

    def parse_main_page(self) -> dict:
        pass

    def _get_html_from(self, url: str, method: str = "lxml") -> BeautifulSoup:
        if self.show_the_process: print(f"parse {url}")
        return BeautifulSoup(
            requests.get(
                url,
                headers=self.headers
            ).content,
            method
        )

    @property
    def headers(self):
        return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
  

class GithubUser(ParseEntity):
    """Parses account data"""

    def update(self) -> None:
        parsing_data = self.parse()
        self.fullname = parsing_data["fullname"]
        self.username = parsing_data["username"]
        self.description = parsing_data["description"]
        self.link_to_avatar = parsing_data["link to avatar"]
        self.repositories = parsing_data["links to repositories"]

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return f"{self.username}: {self.description}"

    def parse(self) -> dict:
        return {
            **self.parse_main_page(),
            **self.parse_repositories_page()
        }

    def parse_main_page(self) -> dict:
        content = self._get_html_from(self.url)
        return {
            "fullname": content.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text.strip(),
            "username": content.find("span", class_="p-nickname vcard-username d-block").text.strip(),
            "description": content.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").text.strip(),
            "link to avatar": content.find("a", itemprop="image").get("href")
        }

    def parse_repositories_page(self) -> dict:
        content = self._get_html_from(f"{self.url}?tab=repositories")

        number_of_repositories = int(content.find("span", class_="Counter").text)
        data = {
            "links to repositories": []
        }

        while True:
            for line in content.find_all("a", itemprop="name codeRepository"):
                data["links to repositories"].append(f'https://github.com{line.get("href")}')

            number_of_repositories -= 30 #maximum amount that can be on a page

            if number_of_repositories > 0:
                content = self._get_html_from(
                    content.find_all("a", class_="btn btn-outline BtnGroup-item")[-1].get("href")
                )
            else:
                return data


class Repository(ParseEntity):
    pass


class Converter:
    """An abstract base class for saving data to a file in a directory"""
    show_the_process = True

    def __init__(self, directory: str = None):
        self.directory = f"{directory}\\" if directory is not None else ""

    def save(self, object: object, filename: str) -> None:
        pass


class JSONConverter(Converter):
    def save(self, object: object, filename: str = None) -> None:
        directory = f"{self.directory}{filename if filename is not None else f'{object}.json'}"
        with open(directory , "w") as file:
            json.dump(object.__dict__, file, indent=2)

        if self.show_the_process:
            print(f"{object} data saved in {directory}")


if __name__ == "__main__":
    user = GithubUser("https://github.com/TheArtur128")
    JSONConverter().save(user)
    print("parsing data:")
    for key, values in user.__dict__.items():
        print(f"  {key}: {values}")
    
