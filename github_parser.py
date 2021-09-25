import json
import os

from bs4 import BeautifulSoup
import requests

Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}


class Github_User:
    def __init__(self, url=None):
        self.__URL = url
        self.parsing()

    def parsing(self):
        print(f"Parsing from {self.__URL}...")
        self.__parsing_main_page()
        self.__parsing_repositories_page()

    def save_instances(self):
        try: os.mkdir("Github-users")
        except FileExistsError: pass

        #Создаём json-файл под конкретного юзера
        with open(f"Github-users/{self.__info['name']}.json", "w") as file:
            print(f"Saving {self.__info['name']}'s github data to json")
            json.dump(self.__dict__, file, indent=2)

    def __parsing_main_page(self):
        #Контент основной страницы
        page = requests.get(self.__URL, headers=Headers)
        content = BeautifulSoup(page.content, "lxml")

        name = content.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text.strip()
        if name == "":
            name = content.find("span", class_="p-nickname vcard-username d-block").text.strip()

        description = content.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").text
        if description == "":
            description = "Unknown"

        try: creation_time = content.find("relative-time", class_="no-wrap").text
        except AttributeError: creation_time = "Unknown"

        avatar = content.find("img", alt="Avatar").get("src")
        #Собираем все данные вместе
        self.__info = {"name": name, "description": description, "creation time": creation_time, "avatar": avatar}

    def __parsing_repositories_page(self):
        #Получаем контент страницы с репами
        page = requests.get(f"{self.__URL}?tab=repositories", headers=Headers)
        content = BeautifulSoup(page.content, "lxml")

        #Парсим количества репозиториев
        summing_repositories = content.find("span", class_="Counter")
        #Если репозиториев нет то новый атрибут у обьекта не появиться
        if summing_repositories is None or summing_repositories == "":
            repositories_on_page = 0
        else:
            repositories_on_page = int(summing_repositories.get("title"))

        #Хранилище для напарсированной информации
        repositories_names = []
        repositories_links = []
        repositories_language = []
        repositories_time = []
        repositories_description = []

        block = content.find_all("li", itemprop="owns")

        while repositories_on_page > 0:
            for item in block:
                repositories_names.append(item.find("h3", class_="wb-break-all").text.strip())

                repositories_links.append(f"https://github.com/{item.find('a', itemprop='name codeRepository').get('href')}")

                language = item.find("span", itemprop="programmingLanguage")
                if language is None:
                    repositories_language.append("Unknown")
                else:
                    repositories_language.append(language.text)

                time = item.find("relative-time", class_="no-wrap")
                if time is None:
                    repositories_time.append("Unknown")
                else:
                    repositories_time.append(time.text)

                description = item.find("p", class_="col-9 d-inline-block color-text-secondary mb-2 pr-4")
                if description is None:
                    repositories_description.append("Unknown")
                else:
                    repositories_description.append(description.text.strip())

            #Отнимаем от количества репозиториев сумму всех репов на странице
            repositories_on_page -= 30

            #Переходим на следующий цикл итерации если остались репозитории
            if repositories_on_page > 0:
                new_page = content.find("a", class_="btn btn-outline BtnGroup-item").get("href")
                page = requests.get(new_page, headers=Headers)
                content = BeautifulSoup(page.content, "lxml")
                block = content.find_all("li", itemprop="owns")
            else:
                self.__repositories = []
                for i in range(len(repositories_names)):
                    self.__repositories.append({
                        "name": repositories_names[i],
                        "description": repositories_description[i],
                        "language": repositories_language[i],
                        "interaction time": repositories_time[i],
                        "link": repositories_links[i]
                    })

    def __repr__(self):
        return self.__info["name"]
