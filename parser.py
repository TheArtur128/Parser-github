from bs4 import BeautifulSoup
import requests

class User:
    TOKEN = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    def __init__(self, URL):
        self.__URL = URL
        #Откладочная информация
        self.response = requests.get(self.URL, headers=User.TOKEN)
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        #Спарсированные данные
        self.__name = self.__name()
        self.__repositories = self.__repositories()

    def __repr__(self):
        return self.__URL

    def update(self, URL):
        self.__init__(URL)

    def info(self):
        return (f"{self.__name}: {self.__URL}\nRepositories: {self.__repositories}")

    def __name(self):
        items = self.soup.findAll("div", class_="vcard-names-container float-left js-profile-editable-names col-12 py-3 js-sticky js-user-profile-sticky-fields")
        for item in items:
            name = item.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text

        return (name.replace(" ", "")).replace("\n", "") #Удаляет из парсированого имени все пробелы

    def __repositories(self):
        items = self.soup.findAll("div", class_="UnderlineNav width-full box-shadow-none")
        for item in items:
            repositories = item.find("span", class_="Counter").text

        return repositories

    @property
    def URL(self): return self.__URL
    @property
    def name(self): return self.__name
    @property
    def repositories(self): return self.__repositories

#Artur = User("https://github.com/TheArtur128")
LoveSy = User("https://github.com/yujincheng08")

print(LoveSy.info())
