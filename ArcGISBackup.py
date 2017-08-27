from arcgis.gis import GIS
from arcgis.gis import User
import os
import getpass

url = 'https://geogeeks.maps.arcgis.com'
usr = 'aitor.calero.masquemapas'
directorio = os.getcwd()
#p = getpass.getpass()
p = 'EkE4HEhpmRE8'


def connnect_to_arcgis(_url, _usr, _pwd):
    gis = GIS(_url, _usr, _pwd)
    print('Connected successfully to the [' + gis.properties.name + '] organization\n')
    return gis


gis = connnect_to_arcgis(url, usr, p)

m = gis.map()
user = User(gis, usr, userdict=None)
os.mkdir('Box')


def CreateFolderStructure():

    flds = user.folders
    print('\nYou have **' + str(len(user.folders)) + '** folders in your ArcGIS Organization\n')
    # listing documents in the user root folder
    root_folder_items = user.items()
    n = 0
    print("Total number of items in root folder: " + str(len(root_folder_items)))

    # list of supported file types to retrieve from the user folders
    file_types = ['CSV', 'Microsoft Excel', 'KML', 'PDF', 'ZIP', 'Service Definition']

    # Listing items in the root folder
    for root_folder_item in root_folder_items:
        if (root_folder_item.type in file_types):
            n += 1
            print(root_folder_item.title + '\t\t(' + root_folder_item.type + ')\n')

    # Listing documents inside other user folders
    for fld in flds:
        # print((carpeta))
        print('Name: ' + fld['title'] + '\n')
        os.mkdir("Box/" + fld['title'])
        flds = user.items(folder=fld['title'])
        print('You have ' + str(len(flds)) + ' items inside your folder\n')
        for i in flds:
            if i.type in file_types:
                n += 1
                print('\t\t' + i.title + '\t\t(' + i.type + ')\n')

    print('\tDownloadable elements:\t' + str(n))


def CreateFolder():
    print(os.getcwd())

CreateFolderStructure()