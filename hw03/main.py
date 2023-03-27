
from pathlib import Path
from threading import Thread
import logging
import sys
import re
import shutil



img_files =[]
videos_files =[]
documents_files =[]
music_files =[]
archives_files =[]
other_files =[]

images =['.png' ,'.jpg' ,'.jpeg' ,'.svg'],
videos =['.avi', '.mp4', '.mov', '.mkv'],
documents =['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
music =['.mp3', '.ogg', '.wav', '.amr'],
archives =['.zip', '.gz', '.tar' ,'.rar']



FOLDERS =[]

# ! cловник для розширень і сортування файлів
FILE_TYPES = {
    tuple(['png', 'jpg', 'jpeg', 'svg']): img_files,
    tuple(['avi', 'mp4', 'mov', 'mkv']): videos_files,
    tuple(['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx']): documents_files,
    tuple(['mp3', 'ogg', 'wav', 'amr']): music_files,
    tuple(['zip', 'gz', 'tar', 'rar']): archives_files,
}

FILE_TAGS = {
    'images': img_files,
    'videos': videos_files,
    'documents': documents_files,
    'music': music_files,
    'archives': archives_files,
}

# ! словник для перекладу
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

for k, v in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(k)] = v
    TRANS[ord(k.upper())] = v.upper()


# ! парсинг файлів
def get_extension(filename: str) -> str:
    return Path(filename).suffix[1:]


def scanning(folder: Path) -> None:
    def scan(item):
        logging.debug(f"Start scanning folder: {item}")
        if item.is_dir():
            if item.name not in ['images', 'videos', 'documents', 'archives', 'music']:
                FOLDERS.append(item)
                scanning(item)
        ext = get_extension(item.name)
        fullname = folder / item.name
        for k, v in FILE_TYPES.items():
            if ext in k:
                v.append(fullname)
        logging.debug(f"End scanning folder: {item}")

    for item in folder.iterdir():
        th = Thread(target=scan,args=(item,))
        


# ! нормалізація файлів
def normalize(name: str) -> str:
    ext = ''
    try:
        ext, t_name = name.split('.')[::-1]
    except:
        t_name = name.translate(TRANS)
    finally:
        t_name = t_name.translate(TRANS)
        t_name = re.sub(r'\W', '_', t_name)
        t_name = t_name + '.' + ext
    return t_name



def sorting(path,type):
    logging.debug(f"Start sorting: {type}")
    for file in FILE_TAGS.get(type):
        handle_standart(file, path /type)
    logging.debug(f"End sorting: {type}")

# ! cтворення та переміщення файлів у папки


def handle_standart(filename: Path, path: Path):
    path.mkdir(exist_ok=True, parents=True)
    filename.replace(path / normalize(filename.name))


def handle_archives(filename: Path, path: Path):
    path.mkdir(exist_ok=True, parents=True)
    archive_folder = path / normalize(filename.name.replace(filename.suffix, ''))

    archive_folder.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        print(f"It isn't archive: {filename.name}")
        archive_folder.rmdir()
    filename.unlink()


def handle_folder(path: Path):
    try:
        path.rmdir()
    except:
        print(f"Не вдалось видалити папку {path}")


# ! основний скрипт
def main1(path: Path):
    scanning(path)
    for file in FILE_TAGS.get('images'):
        handle_standart(file, path / 'images')
    for file in FILE_TAGS.get('videos'):
        handle_standart(file, path / 'videos')
    for file in FILE_TAGS.get('documents'):
        handle_standart(file, path / 'documents')
    for file in FILE_TAGS.get('music'):
        handle_standart(file, path / 'music')
    for file in FILE_TAGS.get('archives'):
        handle_archives(file, path / 'archives')

    for file in FOLDERS[::-1]:
        handle_folder(path)

def main(path:Path):
    scanning(path)
    logging.basicConfig(level=logging.DEBUG, format='')
    logging.debug('Start sorting')
    th_images=Thread(target=sorting,args=(path,'images'),)
    th_videos=Thread(target=sorting,args=(path,'videos'),)
    th_documents=Thread(target=sorting,args=(path,'documents'),)
    th_music=Thread(target=sorting,args=(path,'music'),)
    th_archives=Thread(target=sorting,args=(path,'archives'),)
    threads=[th_images,th_videos,th_documents,th_music,th_archives]
    for t in threads:
        t.start()
    [el.join() for el in threads]
    logging.debug('End sorting')

if __name__ == '__main__':
    dir_scan = Path(sys.argv[1])
    main(dir_scan.resolve())


