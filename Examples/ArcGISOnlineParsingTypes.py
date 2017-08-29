import bs4 as bs
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)

def GetFileExtensions(_url):
    source = urllib.request.urlopen(_url)
    soup = bs.BeautifulSoup(source, 'lxml')
    _ListTypes = []
    for divs in soup.find_all('span', class_='usertext'):
        _ListTypes.append(divs.text)
    return _ListTypes

def GetFileTypes(_url):
    source = urllib.request.urlopen(_url)
    soup = bs.BeautifulSoup(source, 'lxml')
    _ListTypes = []
    for divs in soup.find_all('li'):
        _ListTypes.append(divs.text)
    return _ListTypes


ListExtensionTypes = GetFileExtensions(
    'http://doc.arcgis.com/en/arcgis-online/reference/supported-items.htm')

ListFileTypes = GetFileTypes(
    'http://doc.arcgis.com/en/arcgis-online/reference/supported-items.htm')

for type in ListFileTypes:
    logging.info('\t'+type)

ListExtensionTypes = list(set(ListExtensionTypes))

for type in ListExtensionTypes:
    logging.info('\t'+type)


logging.info('There are {} different types of elements that you can store in ArcGIS Online'
    .format(len(ListExtensionTypes),'\t'))