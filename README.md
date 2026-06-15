# Asura to html converter

## Description

This tool can convert `.asura` files (from https://asurascans.com) which can only be open in their app to a normal **web format**.  
This tool will create a folder next to the python file with a bunch of `.html` file corresponding to each chapter.

To read the **manwha** you just have to open the first `.html` file in the created folder. There's button at the **top** and **bottom** of the page to navigate to the **next** or **previous** chapter.


## Usage

Install the python modules by running `setup.bat` (on windows only) or by running `pip install -r requirements.txt`


Run the python file like this:

```powershell
python asura2html.py -f you_asura_file_here.asura
```

You can also precise the number of thread used by the program:
```powershell
python asura2html.py -f you_asura_file_here.asura -t 4
```

*/!\ Be carefull, while `more thread = higher speed`, `more thread = higher rame usage`*
