from bs4 import BeautifulSoup
import requests
import json
import os

#Класс уверенного юзера github'а
class User:
    Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    #Версия самого парсера и его json файлов.
    #При не соответсвии версий при парсинге из json'ов выдаёт ошибку
    VERSION = "0.1.0"

    #По умолчанию url нужно вводить для парсинга страницы, но если вы захотите спарить все данные с json'a то он спарситься от-туда
    def __init__(self, url=None, load=False, save=True, exception=False):
        #Упоменания место парсинга
        if url is not None:
            print(f"Parsing from {url}...")
        elif load:
            print(f"Parsing from Github-users/{load}.json...")

        self.__parser_version = User.VERSION
        self.__URL = url
        self.parsing(load=load, exception=exception, save=save)

    #При парсинге json'a данные само сабой заного в json не сахроняються
    #По умолчанию парсим данные и сохраняем их в json. Также можем загрузить данные из json'а и отключить save
    #load принимает не True а название json файла в катологе юзеров без расширения
    #Также save лучьше трогать лишь в исключительные моменты
    #Для пролёта ошибки с версией при парсинге json укажите exception=True
    def parsing(self, load=False, exception=False, save=True):
        #Парсим данные и сохраняем их или не сахроняем
        if not load:
            self.__parsing_data()
            self.__parsing_repositories()
            if save:
                self.save()

        #Загружаем уже напарсированые данные из католога
        elif load:
            book = json.loads(open(f"Github-users/{load}.json", "r").read())
            if book["_User__parser_version"] == User.VERSION or exception:
                self.__dict__ = book
                open(f"Github-users/{load}.json").close()
            else:
                raise ImportError (f"{book['_User__parser_version']} is no longer served. If you still want to parse then specify exception=True")

    #Сохраняем __dict__ нашего экземпляра в файл json что в каталоге
    def save(self):
        #Создаём каталог пользователей если он отсутсвует
        try:
            os.mkdir("Github-users")
        except FileExistsError: pass

        #Создаём json-файл под конкретного юзера
        with open(f"Github-users/{self.__vacancy['name']}.json", "w") as file:
            json.dump(self.__dict__, file, indent=4)

    #Парсинг данных с основной страницы
    def __parsing_data(self):
        #Контент основной страницы
        page = requests.get(self.__URL, headers=User.Headers)
        content = BeautifulSoup(page.content, "lxml")

        #Имя. при не удачной попытки парсинга берёт чать URL'a
        name = content.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text.strip()
        if name == "":
            name = content.find("span", class_="p-nickname vcard-username d-block").text.strip()

        #Самоописание
        description = content.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").text
        if description == "":
            description = "Unknown"

        #Время регимтрации
        time = content.find("relative-time", class_="no-wrap").text

        #Аватарка как ссылка на картинку
        avatar = content.find("img", alt="Avatar").get("src")

        #Собираем все данные вместе
        self.__vacancy = {"name": name, "description": description, "creation time": time, "avatar": avatar}

    #Парсинг страницы с репозиториями
    def __parsing_repositories(self):
        #Получаем контент страницы с репами
        page = requests.get(f"{self.__URL}?tab=repositories", headers=User.Headers)
        content = BeautifulSoup(page.content, "lxml")

        #Парсим количества репозиториев
        summing_repositories = content.find("span", class_="Counter")
        #Если репозиториев нет то новый атрибут у обьекта не появиться
        if summing_repositories is None or summing_repositories == "":
            repositories_on_page = 0
        else:
            repositories_on_page = int(summing_repositories.get("title"))

        #Вся напарсированая информация
        repositories_names = []
        repositories_links = []
        repositories_language = []
        repositories_time = []
        repositories_description = []

        #Все карточки репозиториев
        block = content.find_all("li", itemprop="owns")

        #Начинаем парсить репозитории если они есть
        while repositories_on_page > 0:
            #Парсинг карточки
            for item in block:
                #Имя
                repositories_names.append(item.find("h3", class_="wb-break-all").text.strip())

                #Ссылка
                repositories_links.append(f"https://github.com/{item.find('a', itemprop='name codeRepository').get('href')}")

                #Язык пограмирования
                language = item.find("span", itemprop="programmingLanguage")
                if language is None:
                    repositories_language.append("Unknown")
                else:
                    repositories_language.append(language.text)

                #Последнее время обновления
                time = item.find("relative-time", class_="no-wrap")
                if time is None:
                    repositories_time.append("Unknown")
                else:
                    repositories_time.append(time.text)

                #Описание
                description = item.find("p", class_="col-9 d-inline-block color-text-secondary mb-2 pr-4")
                if description is None:
                    repositories_description.append("Unknown")
                else:
                    repositories_description.append(description.text.strip())

            #Отнимаем от количества репозиториев сумму всех репов на странице
            repositories_on_page -= 30

            #Переходим на след. страницу парсить уже те репозитории или собираем все данные в кучу
            if repositories_on_page > 0:
                #Получаем ссылку на следующию страницу
                new_page = content.find("a", class_="btn btn-outline BtnGroup-item").get("href")

                #Получаем контент страницы с репами
                page = requests.get(new_page, headers=User.Headers)
                content = BeautifulSoup(page.content, "lxml")

                #Все карточки репозиториев
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
        return self.__vacancy["name"]

    @property
    def vacancy(self): return self.__vacancy
    @property
    def repositories(self): return self.__repositories
    @property
    def parser_version(self): return self.__parser_version
