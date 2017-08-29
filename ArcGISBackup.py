import logging

from arcgis.gis import GIS
from arcgis.gis import User
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )


# we open a text file where my credentials are stored
# this file must be in the same directory
with open('credentials.txt') as f:
    url, usr, p, boxdir = f.read().split('\n')

arcgisboxdir = str(Path.home())+ boxdir
logging.info(arcgisboxdir)

# we connect to my arcgis account using the previous credentials
def connect_to_arcgis(_url, _usr, _pwd):
    gis = GIS(_url, _usr, _pwd)
    logging.info('Connected successfully to the {} organization\n'.format(gis.properties.name))
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
    logging.info('\nYou have ** {} ** folders in your ArcGIS Organization\n'.format(str(len(_user.folders))))
    # listing documents in the user root folder
    root_folder_items = _user.items()
    n = 0
    logging.info("Total number of items in root folder: {}".format(str(len(root_folder_items))))

    # list of supported file types to retrieve from the user folders
    #TODO Read file_types from a external file or directly form a public Esri URL 
    file_types = ['CSV', 'Service Definition', 'KML', 'ZIP', 'Shapefile', 'Image Collection','PDF','Microsoft Excel']

    # Listing & downloading items in the root folder
    for root_folder_item in root_folder_items:
        if root_folder_item.type in file_types:
            n += 1
            item_path = str(root_folder_item.download())
            file_extension = item_path.rsplit(".",maxsplit=1)[1]
            os.rename(str(item_path), arcgisboxdir + root_folder_item.title + "." + file_extension)
            logging.info('{}\t\t({})\n'.format(root_folder_item.title,root_folder_item.type))

    # Listing documents inside other user folders
    for fld in flds:
        # logging.info((carpeta))
        logging.info('Name: {}\n'.format(fld['title']))
        os.mkdir(arcgisboxdir + fld['title'])
        flds = _user.items(folder=fld['title'])
        logging.info('You have {} items inside your folder\n'.format(str(len(flds))))
        for i in flds:
            if i.type in file_types:
                n += 1
                item_path = str(i.download())
                file_extension = item_path.split(".")[1]
                os.rename(str(item_path), arcgisboxdir + fld['title'] + "/" + i.title + "." + file_extension)
                logging.info('\t\t {} \t\t( {} )\n'.format(i.title,i.type))

    logging.info('\tDownloadable elements:\t {}'.format(str(n)))


CreateFolderStructure(user)
