import bs4 as bs
import urllib.request
import logging
from rarfile import RarFile

logging.basicConfig(level=logging.INFO)

source = urllib.request.urlopen('http://www.gisandbeers.com/modelos-predictivos/')

soup = bs.BeautifulSoup(source, 'lxml')

def GetRarFiles():
    for divs in soup.find_all('div', class_='titulo'):
        for url in divs.find_all('a'):
            logging.info(url.get('href'))
            if len(str(url.get('href')).split('/ASCII/')) == 2:
                filename = str(url.get('href')).split('/ASCII/')[1]
                url_path = '/Users/aitorcalero/PycharmProjects/ArcGISBox/Examples/Rar/' + filename
                urllib.request.urlretrieve(url.get('href'), url_path)

# logging.info(RarFile.namelist())