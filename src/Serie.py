import requests
import lxml
from bs4 import BeautifulSoup

class Serie:
    def __init__(self, soup) -> None:
        self.author : str = str()
        self.illustrator : str = str()
        self.translator : str = str()
        self.adapt : str = str()
        self.themes : list = list()
        self.cover_url : str = str()
        self.get_everything(soup)

    @staticmethod
    def get_cover(soup) -> str:
        novels = soup.find_all("div", class_="f1vdb00x novel")
        imgs = list()
        for novel in novels:
            if novel.find_all("div", "fz7z7g5"):
                imgs.append(novel.find('img').get('src'))
        if imgs:
            return imgs[-1].replace("/240/", "/1200/") #to get the best res
        return None

    def get_everything(self, soup):
        divs = soup.find_all('div', class_=['f3gc1kc text normal', 'aside-buttons'])
        side_elems = ["author", "illustrator", "translator", "adapt", "themes"]
        index = -1
        tmp_dict = dict()

        for div in divs:
            if div['class'] == ['aside-buttons']:
                if tmp_dict.get(side_elems[index]):
                    tmp_dict.update({side_elems[index] : tmp_dict[side_elems[index]] + ", " + div.text})
                else:
                    tmp_dict[side_elems[index]] = div.text

            if div['class'] == ['f3gc1kc', 'text', 'normal']:
                index += 1

            elif side_elems[index] == "themes":
                tmp_dict["themes"] = [i.text for i in div]
                break

        self.author = tmp_dict["author"]
        self.illustrator = tmp_dict["illustrator"]
        self.translator = tmp_dict["translator"]
        self.adapt = tmp_dict["adapt"]
        self.themes = tmp_dict["themes"]

        self.cover_url = self.get_cover(soup)
        if self.cover_url is not None:
            cover = requests.get(self.cover_url)
            open("Cover.jpg", "wb").write(cover.content) #replace the previous if already exist

    def __str__(self) -> str:
        return f"Auteur : {self.author}\n Illustrateur : {self.illustrator}\n Traduction : {self.translator}\n Adaptation : {self.adapt}\n Themes : {self.themes}"
