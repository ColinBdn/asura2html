# Asura to HTML converter

## Description

This tool can convert `.asura` files (from https://asurascans.com) which can only be opened in their app to a normal **web format**.  
It will create a folder next to the python file with a bunch of `.html` files corresponding to each chapter.

To read the **manwha** you just have to open the first `.html` file in the created folder. There's button at the **top** and **bottom** of the page to navigate to the **next** or **previous** chapter.
It works on any web browser (mobile device included)

## Usage

Install the Python modules by running `setup.bat` (on windows only) or by running `pip install -r requirements.txt`


Run the python file like this:

```powershell
python asura2html.py -f you_asura_file_here.asura
```

You can also specify the number of threads used by the program (default is 4):
```powershell
python asura2html.py -f you_asura_file_here.asura -t 8
```

*/!\ Be carefull, while `more thread = higher speed`, `more thread = higher ram usage`*
