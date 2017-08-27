from arcgis.gis import GIS
from arcgis.gis import User
import os
import shutil
from pathlib import Path

# we open a text file where my credentials are stored
# this file must be in the same directory
with open('credentials.txt') as f:
    url, usr, p, arcgisboxdir = f.read().split('\n')  # or similar


# we connect to my arcgis account using the previous credentials
def connect_to_arcgis(_url, _usr, _pwd):
    gis = GIS(_url, _usr, _pwd)
    print('Connected successfully to the [' + gis.properties.name + '] organization\n')
    return gis


gis = connect_to_arcgis(url, usr, p)

user = User(gis, usr, userdict=None)

# we make sure the the arcgisbox dir do not previously exists and delete it if so
if Path(arcgisboxdir).exists():
    shutil.rmtree(arcgisboxdir)

os.mkdir('Box')


# we recursively loop through each folder downloading the items type given in file_types
def CreateFolderStructure(_user):
    flds = _user.folders
    print('\nYou have **' + str(len(_user.folders)) + '** folders in your ArcGIS Organization\n')
    # listing documents in the user root folder
    root_folder_items = _user.items()
    n = 0
    print("Total number of items in root folder: " + str(len(root_folder_items)))

    # list of supported file types to retrieve from the user folders
    file_types = ['CSV', 'Service Definition', 'KML', 'ZIP', 'Shapefile', 'Image Collection']

    # Listing & downloading items in the root folder
    for root_folder_item in root_folder_items:
        if root_folder_item.type in file_types:
            n += 1
            item_path = str(root_folder_item.get_data())
            file_extension = item_path.split(".")[1]
            os.rename(str(item_path), arcgisboxdir + root_folder_item.title + "." + file_extension)
            print(root_folder_item.title + '\t\t(' + root_folder_item.type + ')\n')

    # Listing documents inside other user folders
    for fld in flds:
        # print((carpeta))
        print('Name: ' + fld['title'] + '\n')
        os.mkdir(arcgisboxdir + fld['title'])
        flds = _user.items(folder=fld['title'])
        print('You have ' + str(len(flds)) + ' items inside your folder\n')
        for i in flds:
            if i.type in file_types:
                n += 1
                item_path = str(i.get_data())
                file_extension = item_path.split(".")[1]
                os.rename(str(item_path), arcgisboxdir + fld['title'] + "/" + i.title + "." + file_extension)
                print('\t\t' + i.title + '\t\t(' + i.type + ')\n')

    print('\tDownloadable elements:\t' + str(n))


CreateFolderStructure(user)
