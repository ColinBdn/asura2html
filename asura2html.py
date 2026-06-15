import typing
from PIL import Image 
from io import BytesIO
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import argparse
from tqdm import tqdm
import sys
from pathlib import Path


OFF_SIZE = 4
CHAPTER_OFFSET = 6
PANE_OFFSET = 10


def getNbChapter(f: typing.IO):
    totalChapter = 0

    f.seek(0, os.SEEK_END)
    size = f.tell()

    f.seek(size-200)
    data: bytes = f.read(150)
    pagesOffset = data.find(b"pages/")

    f.seek(size-200+pagesOffset+CHAPTER_OFFSET)
    totalChapter = int(f.read(3).decode())

    return totalChapter



def getPane(targetChapter, targetPane, f: typing.IO):
    found = False
    currentOffset = 0
    goodOffset = 0
    goodSize = 0
    while not found:
        f.seek(currentOffset)
        data: bytes = f.read(100)
        pagesOffset = data.find(b"pages/")
        startOffset = pagesOffset+19

        if pagesOffset<0:
            break

        f.seek(currentOffset+pagesOffset+CHAPTER_OFFSET)
        chapterFound = int(f.read(3).decode())

        f.seek(currentOffset+pagesOffset+PANE_OFFSET)
        paneFound = int(f.read(4).decode())

        f.seek(currentOffset+startOffset+OFF_SIZE)
        size = int.from_bytes(f.read(4), "little")

        if (chapterFound==targetChapter and paneFound==targetPane):
            found = True
            goodOffset = currentOffset+startOffset
            goodSize = size+8
        else:
            currentOffset += startOffset+size+8

    if found:
        f.seek(goodOffset)
        return f.read(goodSize)
    else:
        return b""




def getAllPanes(f: typing.IO):
    currentOffset = 0
    panesData = []
    totalPane = 0
    totalChapter = 0
    while True:
        f.seek(currentOffset)
        data: bytes = f.read(100)
        pagesOffset = data.find(b"pages/")
        startOffset = pagesOffset+19

        if pagesOffset<0:
            break

        f.seek(currentOffset+pagesOffset+CHAPTER_OFFSET)
        lastChapterFound = chapterFound
        chapterFound = int(f.read(3).decode())
        if lastChapterFound > chapterFound:
            totalChapter += 1
        elif lastChapterFound < chapterFound:
            print("WTFFFF")
            exit(1)

        f.seek(currentOffset+pagesOffset+PANE_OFFSET)
        paneFound = int(f.read(4).decode())
        totalPane+=1

        f.seek(currentOffset+startOffset+OFF_SIZE)
        size = int.from_bytes(f.read(4), "little")

        goodOffset = currentOffset+startOffset
        goodSize = size+8
        f.seek(goodOffset)
        panesData.append(f.read(goodSize))
        currentOffset += startOffset+size+8

    return panesData



def getPanesOfChapter(targetChapter, f: typing.IO):
    currentOffset = 0
    panesData = []
    totalPane = 0
    while True:
        f.seek(currentOffset)
        data: bytes = f.read(100)
        pagesOffset = data.find(b"pages/")
        startOffset = pagesOffset+19

        if pagesOffset<0:
            break

        f.seek(currentOffset+pagesOffset+CHAPTER_OFFSET)
        chapterFound = int(f.read(3).decode())

        f.seek(currentOffset+startOffset+OFF_SIZE)
        size = int.from_bytes(f.read(4), "little")

        if chapterFound == targetChapter:
            found = True
            goodOffset = currentOffset+startOffset
            goodSize = size+8
            f.seek(goodOffset)
            panesData.append(f.read(goodSize))
            totalPane+=1
        elif chapterFound > targetChapter:
            break

        currentOffset += startOffset+size+8

    return panesData



def image2base64(img):
    buffer = BytesIO()
    img.save(buffer, format="jpeg", quality=85)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"









def process_task(chapter_num, chapter_panes, nbChapter, outFolder):
    images = []
    for pane in chapter_panes:
        images.append(Image.open(BytesIO(pane)))

    min_width = 9999999999
    for image in images:
        if image.width<min_width:
            min_width = image.width

    for i, image in enumerate(images):
        if image.width>min_width:
            images[i] = image.resize((min_width, int(image.height*min_width/image.width)))

    prev_disabled = ""
    next_disabled = ""
    if chapter_num==0:
        prev_disabled = "disabled"
    elif chapter_num==nbChapter-1:
        next_disabled = "disabled"
        
    prev_chapter = f"chapter_{chapter_num-1}.html"
    next_chapter = f"chapter_{chapter_num+1}.html"
    nav = f'<div class="nav"><a class="btn {prev_disabled}" href="{prev_chapter}">Previous</a><a class="btn {next_disabled}" href="{next_chapter}">Next</a></div>'
    img_tags = "\n".join( f'<img src="{image2base64(img)}">' for img in images)

    html = f"<!DOCTYPEhtml>\n<html>\n<head>\n<metacharset=\"utf-8\">\n<title>Webtoon</title>\n<style>\nhtml,body{{margin:0;padding:0;background:#121212;}}\nbody{{display:flex;flex-direction:column;align-items:center;}}\nimg{{display:block;margin:0;padding:0;max-width:100%;height:auto;}}\n.nav{{top:0;width:100%;display:flex;justify-content:space-between;gap:10px;padding:12px;box-sizing:border-box;background:rgba(18,18,18,0.6);backdrop-filter:blur(10px);}}\n.btn{{flex:1;text-align:center;padding:10px 14px;border-radius:999px;background:linear-gradient(135deg,#2b2b2b,#1a1a1a);color:#eaeaea;text-decoration:none;font-weight:600;letter-spacing:0.3px;box-shadow:0 2px 10px rgba(0,0,0,0.4);transition:all 0.2s ease;}}\n.btn:hover{{transform:translateY(-2px);background:linear-gradient(135deg,#3a3a3a,#222);box-shadow:0 6px 18px rgba(0,0,0,0.6);}}\n.btn:active{{transform:translateY(0px);}}\n.btn.disabled{{pointer-events:none;color:#3d3d3d;}}\n</style>\n</head>\n<body>\n{nav}\n{img_tags}\n{nav}\n</body>\n</html>"

    output_file = Path(f"./{outFolder}/chapter_{chapter_num}.html")
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with output_file.open('w', encoding="utf-8") as f:
        f.write(html)










def main(fileName, nbThread):
    chapter_list = []
    outFolder = Path(fileName).stem.replace(" ", "_")

    with open(fileName, "rb") as inputFile:
        nbChapter = getNbChapter(inputFile)
        print(f"Found {nbChapter} chapters !")
        print("Reading every panes...")
        for chapter in tqdm(range(nbChapter+1)):
            chapter_list.append(getPanesOfChapter(chapter, inputFile))

    print("Converting to html...")
    with ThreadPoolExecutor(max_workers=nbThread) as executor:
        futures = [executor.submit(process_task, i, chapter, nbChapter, outFolder) for i, chapter in enumerate(chapter_list)]

        try:
            for future in tqdm(as_completed(futures), total=nbChapter):
                future.result() 
        except Exception as e:
            print(f"\nError occurred: {e}")
            for f in futures:
                f.cancel()




class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\033[31m{self.prog}: error: {message}\033[0m", file=sys.stderr)
        print()
        self.print_help()
        raise SystemExit(2)


if __name__ == '__main__':
    # parser = CustomParser(description="Convert .asura file to a folder of .html file corresponding to each chapter")
    # requiredGroup = parser.add_argument_group("Required arguments")
    # requiredGroup.add_argument("-f", "--file", dest="input_file", type=str, required=True, help="asura file name")
    # optionalGroup = parser.add_argument_group("Optional arguments")
    # optionalGroup.add_argument("-t", "--thread", dest="nb_threads", type=int, required=False, default=4, help="/!\\ more thread = higher speed but higher ram usage")
    # args = parser.parse_args()
    main("the-margrave-s-worthless-mage.asura", 1)