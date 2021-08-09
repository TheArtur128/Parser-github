from bs4 import BeautifulSoup
import requests

class User:
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    def __init__(self, URL):
        self.__URL = URL
        #Основная страница нашей жертвы
        self.__html = requests.get(self.__URL, headers=User.HEADERS)
        self.__soup = BeautifulSoup(self.__html.content, "html.parser")
        #Страница с репозиториями
        self.__html_repositories = requests.get(f"{self.__URL}?tab=repositories", headers=User.HEADERS)
        self.__soup_repositories = BeautifulSoup(self.__html_repositories.content, "html.parser")
        #Начало парсинга
        self.updata()

    #Устанавливает и\или обновляет все парс. данные
    def updata(self):
        self.__name = self.__pars_name()
        self.__repositories = self.__pars_repositories()

    def __pars_repositories(self):
        items = self.__soup_repositories.findAll("li", class_="col-12 d-flex width-full py-4 border-bottom color-border-secondary public source")
        #Названия
        names = []
        for item in items:
            names.append((item.find("h3", class_="wb-break-all")).text)
        for i in range(len(names)):
            names[i] = self.__clear(names[i])

        #Время
        time = []
        for item in items:
            time.append((item.find("relative-time", class_="no-wrap")).text)

        #Собираем все парс. данные
        repositories = []
        for i in range(len(names)):
            repositories.append({names[i]: time[i]})
        return repositories

    def __pars_name(self):
        items = self.__soup.findAll("div", class_="js-profile-editable-replace")
        #Имя
        for item in items:
            name = item.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text
        name = self.__clear(name)
        if name == "":
            name = self.__URL[19:]

        #Описание
        for item in items:
            description = item.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").text
        description = (description)

        name = {name: description}
        return name

    def __clear(self, parameter):
        return (parameter.replace(" ", "")).replace("\n", "")

    @property
    def name(self): return self.__name
    @property
    def repositories(self): return self.__repositories
