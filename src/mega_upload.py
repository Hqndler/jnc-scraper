from mega import Mega
import os

def up_to_mega(epubs : list) -> list:
    if not epubs:
        return []
    print("Uploading to mega")
    email = os.environ.get("MEGA_EMAIL")
    password = os.environ.get("MEGA_PASSWORD")

    mega = Mega()
    session = mega.login(email, password)
    folder = session.find("JNC-Nina")[0]
    links = list()
    for epub in epubs:
        file = session.upload(epub, folder)
        links.append(session.get_upload_link(file))
    return links