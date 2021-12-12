# **OSWAS** <sup><sub><sup><sub><sup>**IAP491_G3**</sup></sub></sup></sub></sup>

## **Overview**
OSWAS (Optimized Solutions for WebApp Scanners) is a Capstone Project for FPT University. OSWAS aims to provide intergrated methods to web crawling & web vulnerability testing using Selenium Framework.

## **Requirements**
* Python 3.9+
* Works on Linux

## **Folder Structure**
```
/oswas
|   README.md
|   .env.local
|   .gitignore
|   setup.py
|
├───/app
|   |   __main__.py
|   |   __init__.py
|   |
|   ├───/lib
|   |   |   __init__.py
|   |   |   burpsuite.py
|   |   |   constants.py
|   |   |   db.py
|   |   |   dirsearch.py
|   |   |   form_spider.py
|   |   |   options.py
|   |   |   project.py
|   |   |   report.py
|   |   |   save_response.py
|   |   |   scanner.py
|   |   |   sitemap.py
|   |   |   utils.py
|   |   |   web_element.py
|   |
|   └───/ui
|   
└───/bin
    |   oswas   # shell script file
    └───/burp
```

## **Setup & Installation**
Install pip3, Nodejs, npm, qterminal (Ubuntu, Debian):
```
sudo apt-get install python3-venv python3-pip nodejs npm qterminal
```

Install Python dependencies:
```
sudo pip3 install selenium pymongo pymongo[srv] python-dotenv requests exrex bson colorama mitmproxy bs4
```

Set up enviromnent:
```
cp .env.local .env
nano .env
```
Assign MONGO_URI with your MongoDB URI then hit CTRL-X + Y + Enter to save .env file.

Then, download burploader and Burp Suite from [this link](https://drive.google.com/drive/folders/1vu9Am2yAezt9cYgs7j-_ojQbCHFYORuU?usp=sharing), extract and move the extracted files to `bin/burp` directory. Go to `bin/burp` directory, edit file `burp-rest-api.sh`:
```shell
# edit line 4
# put your absulute path to burploader.jar into <burploader.jar>

java -noverify -javaagent:<burploader.jar> -cp "$CLASSPATH" org.springframework.boot.loader.JarLauncher $@
```

## **Running**
Start running OSWAS by running:
```
cd bin/
./oswas
```