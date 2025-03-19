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
        id_to_key = {
            'auteur': 'author',
            'auteurs': 'author',
            'illustrateur': 'illustrator',
            'illustrateurs': 'illustrator',
            'traduction': 'translator',
            'traductions': 'translator',
            'adaptation': 'adapt',
            'adaptations': 'adapt',
            'th-mes': 'themes'
        }
        result = {key : [] for key in id_to_key}
        section = soup.find('div', class_='fcoxyrb')
        current_key = None

        for child in section.find_all(['div'], recursive=False):
            if 'text' in child.get('class', []) and 'normal' in child.get('class', []):
                header_div = child.find('div', class_='header')
                if header_div:
                    current_key = header_div.get('id')
                    if current_key in id_to_key:
                        result[id_to_key[current_key]] = []
                    else:
                        current_key = None
            elif 'aside-buttons' in child.get('class', []):
                text_div = child.find('div', class_='text')
                if text_div and current_key:
                    result[id_to_key[current_key]].append(text_div.get_text(strip=True))

        for key in result:
            result[key] = ', '.join(result[key]) if result[key] else 'Inconnu'

        self.author = result.get("author", "Auteur inconu")
        self.illustrator = result.get("illustrator", "Illustrateur inconnu")
        self.translator = result.get("translator", "Traducteur inconnu")
        self.adapt = result.get("adapt", "Adaptateur inconnu")
        self.themes = result.get("themes", "Pas de thèmes") # 86 REALLY ?

        self.cover_url = self.get_cover(soup)
        if self.cover_url is not None:
            cover = requests.get(self.cover_url)
            open("Cover.jpg", "wb").write(cover.content) #replace the previous if already exist

    def __str__(self) -> str:
        return f"Auteur : {self.author}\n Illustrateur : {self.illustrator}\n Traduction : {self.translator}\n Adaptation : {self.adapt}\n Themes : {self.themes}"
