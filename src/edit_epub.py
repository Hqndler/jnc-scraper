import os
import subprocess
import re
# from ebooklib import epub

def run_cmd(cmd):
    print(cmd)
    p = subprocess.run(cmd, capture_output = True, text = True, shell = True)
    if p.returncode == 0:
        return True
    print(f"`{cmd}` failed -> {p.stderr}")
    print(p.stdout)
    return False

def unzip_file(file : str) -> str:
    folder : str = file.replace(".epub", '')
    cmd = f'unzip "{file}" -d "{folder}"'
    if not run_cmd(cmd):
        return ''
    return folder

def format_chapter(string : str) -> tuple:
    name : str = string.replace("<h1>", '').replace("</h1>\n", '').strip()
    index = name.find('—')
    if  index == -1:
        id = ''.join(i for i in name.split()).strip().lower()
    else:
        id = ''.join(i for i in (name[:index]).split()).strip().lower() 
    new_line = string[:string.find('<')] + f'<h1 id="{id}">{name}</h1>\n'
    return new_line, {id : name}

def get_chapter_and_update(file : str) -> dict:
    if (not os.path.exists(file)):
        return {}
    content : list = []
    chapters : dict = {}
    with open(file, 'r', encoding="utf-8") as f:
        for line in f:
            if "h1" in line:
                new_line, chap = format_chapter(line)
                content.append(new_line)
                chapters.update(chap)
            else:
                content.append(line)
    with open(file, 'w', encoding="utf-8") as f:
        f.writelines(content)
    return chapters

def update_chapters_in_nav(nav, chapters):
    if not os.path.exists(nav):
        return 
    content : list = []
    with open(nav, 'r', encoding="utf-8") as f:
        for line in f:
            if "</ol>" in line:
                spaces = line[:line.rfind(' ')] + '   '
                content.extend([f'{spaces}<li>\n{spaces}  <a href="chap_0.xhtml#{i}">{chapters[i]}</a>\n{spaces}</li>\n' for i in chapters])
                content.append(line)
            else:
                content.append(line)
    with open(nav, 'w', encoding="utf-8") as f:
        f.writelines(content)

def zip_folder(folder, new_name):
    zipping = f"cd \"{folder}\"; zip -Xr9 ../\"{new_name}\" *; cd .."
    run_cmd(zipping)

def update_nav(folder, new_name):
    content = os.path.join(folder, os.path.join("EPUB", "chap_0.xhtml"))
    chapters = get_chapter_and_update(content)
    if chapters:    
        nav = os.path.join(folder, os.path.join("EPUB", "nav.xhtml"))
        update_chapters_in_nav(nav, chapters)

    zip_folder(folder, new_name)
    run_cmd(f'rm -rf "{folder}"')

# litteralement un .sh
def create_epub(old_file, new_file):
    old_file_copy = old_file.replace(".epub", "tmp_dir").replace(' ', '')
    unzip = f"unzip {old_file} -d {old_file_copy}"
    if not run_cmd(unzip):
        print("fail unzip")
        return False
    rm_cover = f"rm {old_file_copy}/EPUB/cover.jpg"
    if not run_cmd(rm_cover):
        print("fail rm cover")
        return False
    cp_cover = f"cp Cover.jpg {old_file_copy}/EPUB/cover.jpg"
    if not run_cmd(cp_cover):
        print("fail cp cover")
        return False
    sed = f"sed 's/<dc:language>en/<dc:language>fr/' -i {old_file_copy}/EPUB/content.opf"
    if not run_cmd(sed):
        print("fail sed")
        return False
    update_nav(old_file_copy, new_file)
    return True

def sanitize_filename(book_name):
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized_name = re.sub(invalid_chars, '', book_name)
    sanitized_name = re.sub(r'Partie (\d)(?!\d)', r'Partie 0\1', sanitized_name)
    sanitized_name = re.sub(r'Partie (\d) \[Final\]', r'Partie 0\1 [Final]', sanitized_name)
    sanitized_name = re.sub(r'\s+', ' ', sanitized_name).strip()

    return sanitized_name + ".epub"

def update_epub(epub_file_path, illustrator, trad, adap):
    print(f"{epub_file_path}, {illustrator}, {trad}, {adap}")
    book = epub.read_epub(epub_file_path)

    #https://docs.sourcefabric.org/projects/ebooklib/en/latest/_modules/ebooklib/epub.html#EpubBook.add_author
    book.add_author(illustrator, illustrator, "ill", "creator02")
    book.add_author(trad, trad, "trl", "creator03")
    book.add_author(adap, adap, "edt", "creator04")
    book.add_metadata("DC", "publisher", "JNC Nina")
    book_name = book.get_metadata('DC', "title")[0][0] #un peu abusé
    # new_name = book_name.replace(':', '').replace('?', '').replace('"', '') + ".epub"
    new_name = sanitize_filename(book_name)

    # Save the updated EPUB to a new file
    updated_epub_path = epub_file_path.replace('.epub', '_updated.epub')
    epub.write_epub(updated_epub_path, book)

    if not create_epub(updated_epub_path, new_name):
        return ""
    os.remove(updated_epub_path)
    return new_name
