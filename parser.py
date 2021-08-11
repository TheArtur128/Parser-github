from bs4 import BeautifulSoup
from win32api import GetSystemMetrics as my_win
from random import randint as random
import requests
from math import ceil
import tkinter

debug_mode = True

class User:
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    def __init__(self, URL):
        if debug_mode: print("loading...")
        self.__URL = URL
        #Основная страница нашей жертвы
        self.__html = requests.get(self.__URL, headers=User.HEADERS)
        self.__soup = BeautifulSoup(self.__html.content, "html.parser")
        #Страница с репозиториями
        self.__html_repositories = requests.get(f"{self.__URL}?tab=repositories", headers=User.HEADERS)
        self.__soup_repositories = BeautifulSoup(self.__html_repositories.content, "html.parser")
        #Начало парсинга
        self.update()

    #Устанавливает и\или обновляет все парс. данные
    def update(self):
        self.__data = self.__pars_data()
        self.__repositories = self.__pars_repositories()
        if debug_mode: print("Completed!")

    def __pars_repositories(self):
        if debug_mode: print("Parsing repositories...")
        items = self.__soup_repositories.findAll("div", class_="UnderlineNav width-full box-shadow-none")
        #Парсим кол. репозиториев и вычесляем кол. страниц
        for item in items:
            if item.find("span", class_="Counter") is None:
                repositories_sum = 0
            else:
                #Количество репозиториев
                repositories_sum = int(item.find("span", class_="Counter").text.strip())
                #Количество страниц
                page = ceil(repositories_sum / 30)

        #Парсим данные репозиториев
        names = []
        description = []
        language = [] #<span class="ml-0 mr-3">
        time = []
        for i in range(page):
            for q in range(2):
                #Устанавливаем классы, и из-за того что их два на github'е мы парсим репозитории не по порядку
                if q == 0:
                    items = self.__soup_repositories.findAll("li", class_="col-12 d-flex width-full py-4 border-bottom color-border-secondary public source")
                elif q == 1:
                    items = self.__soup_repositories.findAll("li", class_="col-12 d-flex width-full py-4 border-bottom color-border-secondary public fork")

                #Названия репозитория
                for item in items:
                    names.append((item.find("h3", class_="wb-break-all")).text.strip())

                #Описания
                for item in items:
                    if item.find("p", class_="col-9 d-inline-block color-text-secondary mb-2 pr-4") is None:
                        description.append(None)
                    else:
                        description.append((item.find("p", class_="col-9 d-inline-block color-text-secondary mb-2 pr-4")).text.strip())

                #Последнее время взаимодействия
                for item in items:
                    time.append((item.find("relative-time", class_="no-wrap")).text)

                #Язык разработки
                for item in items:
                    language.append((item.find("div", class_="f6 color-text-secondary mt-2")).text.strip().replace("\n", "")[:10].strip()) #<span class="ml-0 mr-3">


            #Устанавливаем след. страничку для парсинга если их больше 1
            if page > 1 and i != page - 1:
                items = self.__soup_repositories.findAll("div", class_="BtnGroup")
                for item in items:
                    next_link = (item.find("a", class_="btn btn-outline BtnGroup-item")).get("href")

                self.__html_repositories = requests.get(next_link, headers=User.HEADERS)
                self.__soup_repositories = BeautifulSoup(self.__html_repositories.content, "html.parser")

        #Собираем все парс. данные
        repositories = []
        for i in range(len(names)):
            repositories.append({names[i]: [description[i], language[i], time[i]]})

        #Устанавливаем страницу по умолчанию для устранения ошибок при парсинге более одной странице
        self.__html_repositories = requests.get(f"{self.__URL}?tab=repositories", headers=User.HEADERS)
        self.__soup_repositories = BeautifulSoup(self.__html_repositories.content, "html.parser")

        return repositories

    def __pars_data(self):
        if debug_mode: print("Parsing data...")
        #Парсинг
        items = self.__soup.findAll("div", class_="js-profile-editable-replace")
        for item in items:
            #Имя
            name = item.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text
            if name is None or name.strip() == "": name = self.__URL[19:]
            else: name = item.find("span", class_="p-name vcard-fullname d-block overflow-hidden").text.strip()
            #Самоописание
            description = item.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").txet
            if description is None or description == "": description = "Unknown"
            description = description.strip()
            #Указанное место жительства
            home = item.find("span", class_="p-label")
            if home is None or home == "": home = "Unknown"
            else: home = item.find("span", class_="p-label").txet.strip()
            #Аватар
            avatar = item.find("img", class_="avatar avatar-user width-full border color-bg-primary").get("src")

        #Оформляем даннные и возврощаем в атрибут
        try:
            data = {name: [description, home, avatar]}
            return data
        except UnboundLocalError:
            raise Exception ("Github is not responding")

    @property
    def data(self): return self.__data
    @property
    def repositories(self): return self.__repositories


#FRONT

c = { #colors
    "fone": "#BAD4FF",
    "button": "#2F36FF",
    "text": "#031129",
    "White": "White"
}

#Оформления окна
win = tkinter.Tk()
win.title("Parser-github")
win.config(bg=c["fone"])

#Геометрия окна
display = [my_win(0)//4, my_win(1)//2]
win.geometry(f"{display[0]}x{display[1]}") #I have 341x384!
win.resizable(False, False)

#Логика
#Заполняем все колонны
win.grid_columnconfigure(0, minsize=display[0]//6)

#Команды
def return_in_data():
    Participant = User(Entry_URL.get())
    Entry_URL.delete(0, "end")

    print(f"\n{Participant.data}")
    for i in range(0, len(Participant.repositories)):
        print(Participant.repositories[i])

#Подгоняем под шаблон github'а
def URL_set():
    if Entry_URL.get() != "https://github.com/":
        Entry_URL.insert(0, "https://github.com/")

#Брашура
tkinter.Label(win, text=f"URL:",
    bg=c["button"], fg=c["White"],
    font=("Lucida Sans Unicode",10),
    width=7, height=1,
    relief=tkinter.RAISED,
    bd=0
).grid(row=0, column=0, stick="nwe")

#Система ввода URL
Entry_URL = tkinter.Entry(win, relief=tkinter.RAISED, bd=0)
Entry_URL.grid(row=0, column=1, stick="news")

#Кнопка return
tkinter.Button(win, text="return URL",
    command=return_in_data,
    bg=c["White"], fg=c["button"],
    activebackground=c["button"],
    font=("Lucida Sans Unicode",10),
    relief=tkinter.RAISED,
    bd=1
).grid(row=1, column=0, stick="nswe", columnspan=2)

#Подгонка под адрес github'а
tkinter.Button(win, text="pattern",
    command=URL_set,
    bg=c["White"], fg=c["button"],
    activebackground=c["button"],
    font=("Lucida Sans Unicode",10),
    relief=tkinter.RAISED,
    bd=1
).grid(row=0, column=2, stick="nsew", rowspan=2)

#Update
win.mainloop()
