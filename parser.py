from bs4 import BeautifulSoup
import requests

#Класс уверенного юзера github'а
class User:
    Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    def __init__(self, url):
        print(f"Parsing from {url}...")
        self.__URL = url
        #Парсинг на практике
        self.parsing()

    #Запускает все парсеры-методы. Может вызван что-бы обновить данные
    def parsing(self):
        self.__parsing_data()
        self.__parsing_repositories()

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

        #Аватарка как ссылка на картинку
        avatar = content.find("img", alt="Avatar").get("src")

        #Собираем все данные вместе
        self.__vacancy = {name: [description, avatar]}

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
                    self.__repositories.append({repositories_names[i]: [repositories_description[i], repositories_language[i], repositories_time[i], repositories_links[i]]})

    def __repr__(self):
        return self.__vacancy

    @property
    def vacancy(self): return self.__vacancy
    @property
    def repositories(self): return self.__repositories

Arthur = User("https://github.com/TheArtur128")
