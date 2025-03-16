import os, json, time, requests, shutil, asyncio
from typing import List
from bs4 import BeautifulSoup
from .edit_epub import update_epub
from .Serie import Serie
from .jncep_launcher import jncep_launcher
from .mega_upload import up_to_mega
from .webhook_send import send_webhook

JNCNINA = r"https://jnc-nina.eu"
json_file = "shared/series_status.json"

class JNCScrapper:


    def __init__(self) -> None:
        self.series : list = list()
        self.json_data : dict = dict()
        self.files : dict = dict()
        #check the json file to understand how json_data works

    def load_json(self) -> None:
        self.json_data = dict()
        self.files = dict()
        if not os.path.exists(json_file): #skip if json_file does not exist
            return
        if os.stat(json_file).st_size == 0: #skip if json_file is empty (will crash otherwise)
            return
        with open(json_file, 'r') as file:
            self.json_data = json.load(file)

    def update_json(self):
        with open(json_file, 'w') as file:
            json.dump(self.json_data, file)

    @staticmethod
    def get_parts_serie(soup) -> list:
        parts = soup.find_all('a', class_=lambda class_list: class_list and all(cls in class_list for cls in ['link', 'block', 'f1ppn23n', 'available'])) # get every available link
        return [(JNCNINA + part['href']) for part in parts]

    @staticmethod
    def get_series_links(soup) -> list:
        links = soup.find_all("a", class_="link f122npxj block") # get every link with this class
        return [(JNCNINA + link["href"]) for link in links if "series/" in link["href"]] # filter the results to only have what we want

    @staticmethod
    def get_key(url : str) -> str:
        key = url.replace(JNCNINA + "/fr/series/", "")
        if key.endswith("-fr"):
            key = key[:-3]
        return key

    @staticmethod
    def get_key_with_part(part : str, key : str) -> str:
        return part[part.rfind("/") + 1 + len(key) + 1:]

    @staticmethod
    def move_to_done(old : str, new : str) -> None:
        if not os.path.exists("done/"):
            os.mkdir("done")
        os.remove(old)
        try:
            shutil.move(new, "done")
        except shutil.Error:
            os.remove(new)

    def get_this_part(self, part : str, serie_infos : Serie, key : str):
        epub = jncep_launcher(part)
        if not epub:
            print(f"`{part}` skipped after launcher")
            self.json_data[key].update({self.get_key_with_part(part, key) : False})
            return
        time.sleep(1)
        new_name = update_epub(epub, serie_infos.illustrator, serie_infos.translator, serie_infos.adapt)
        if new_name:
            self.json_data[key].update({self.get_key_with_part(part, key) : True})
            self.move_to_done(epub, new_name)
            
            if self.files.get(serie_infos.cover_url) is None:
                self.files[serie_infos.cover_url] = list()
            self.files[serie_infos.cover_url].append(os.path.join("done", new_name))

        else:
            os.remove(epub)
            print(f"`{part}` skipped after edit")

    def every_parts(self, parts : str, key : str, serie_infos : Serie):
        self.json_data[key] = dict()
        print(f"every part : parts = {parts}, key = {key}")
        for part in parts:
            print("getting the part")
            self.get_this_part(part, serie_infos, key)

    def remaining_parts(self, parts : str, key : str, serie_infos : Serie):
        def already_scrappe(part_list : List[dict], part):
            for p in part_list:
                if p == part:
                    return part_list[part]
            return False

        for part in parts:
            if already_scrappe(self.json_data[key], self.get_key_with_part(part, key)):
                print(f"`{part}` skipped because already dl")
                continue
            self.get_this_part(part, serie_infos, key)
            

    def load_serie(self, url : str):
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        series_props = Serie(soup)
        print(series_props)
        parts = self.get_parts_serie(soup)

        key = self.get_key(url)

        serie_parts = self.json_data.get(key)
        print(f"serie_parts = {serie_parts}")
        if serie_parts is None:
            self.every_parts(parts, key, series_props)
        else:
            self.remaining_parts(parts, key, series_props)

    def prepare_to_upload(self):
        files = list()
        covers = list()
        for key in self.files:
            for _ in range(len(self.files[key])):
                covers.append(key)
            files.extend(self.files[key])
        print(files)
        print(covers)

        if ((len(covers) != len(files)) and (len(covers) < len(files))):
            print("Unmatch files and cover len, something's gonna break somewhere")
            last = covers[-1]
            for _ in range(len(files)):
                covers.append(last)

        links = up_to_mega(files)
        print(links)
        if (len(links) != len(files) and (len(links) < len(files))):
            last = links[-1]
            print("Unmatch files and links len, something's gonna break somewhere")
            for _ in range(len(files)):
                links.append(last)

        asyncio.run(send_webhook(links, files, covers))
        if (os.path.exists("done/") and os.path.isdir("done/")):
            shutil.rmtree("done/")

    @staticmethod
    def get_range_ongoing(soup):
        """
        Permet de récupérer toutes les séries dispo si +10 séries (max 10 séries sur une page)
        """
        res = soup.find("span", class_="f182sjpl").find_all("b")[-1].text
        try:
            nb_pages = int(res)
        except ValueError:
            return 1
        return nb_pages // 10 + (1 if nb_pages % 10 != 0 else 0)

    def JNCNina_series(self):
        """
        Regarde toutes les séries dispo sur JNC Nina (https://jnc-nina.eu/fr/series)
        Regarde ensuite dans toutes les séries trouvée si une nouvelle partie est sortie
        """
        url = JNCNINA + "/fr/series"
        response = requests.get(url)
        nb_pages = self.get_range_ongoing(BeautifulSoup(response.text, 'lxml'))
        series = list()

        for i in range(nb_pages):
            url = JNCNINA + "/fr/series?status=ongoing&page=" + str(i + 1)
            response  = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            series.extend(self.get_series_links(soup))

        self.load_json()
        for serie in series:
            self.load_serie(serie)
            time.sleep(0.1)

        self.update_json()
        self.prepare_to_upload()