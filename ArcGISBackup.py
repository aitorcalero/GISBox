""" This module creates a backup of an ArcGIS Online Organization """
import os
import shutil
from pathlib import Path
import logging
from arcgis.gis import GIS
from arcgis.gis import User

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# we open a text file where my credentials are stored
# this file must be in the same directory
URL = 'https://www.arcgis.com'
try:
    with open('credentials.txt') as f:
        USR, P, BOXDIR = f.read().split('\n')
except ValueError:
    print(ValueError)
    pass


# we connect to my arcgis account using the previous credentials
def connect_to_arcgis(_url, _usr, _pwd):
    """ Creates the connection to the ArcGIS account and returns a GIS object """
    try:
        _g = GIS(_url, _usr, _pwd)
        logging.info(f'Connected successfully to the {_g.properties.name} organization\n')
        return _g
    except ValueError:
        logging.error(ValueError.args)


GIS = connect_to_arcgis(URL, USR, P)
USER = User(GIS, USR, userdict=None)

ARCGISBOXDIR = os.path.normpath(str(Path.home()) + BOXDIR)
logging.info(ARCGISBOXDIR)

# we make sure the the arcgisbox dir do not previously exists and delete it if so
if Path(ARCGISBOXDIR).exists():
    shutil.rmtree(ARCGISBOXDIR)

os.mkdir(ARCGISBOXDIR)


# we recursively loop through each folder downloading the items type given in file_types
def create_folder_structure(_user):
    """ This function replicate the folder structure of the user account """
    flds = _user.folders
    logging.info(f"\nYou have ** {str(len(_user.folders))} ** "
                 f"folders in your ArcGIS Organization\n")
    # listing documents in the user root folder
    root_folder_items = _user.items()
    _n = 0
    logging.info(f"Total number of items in root folder: {str(len(root_folder_items))}")

    # list of supported file types to retrieve from the user folders
    # TODO Read file_types from a external file or directly form a public Esri URL
    file_types = ['CSV', 'Service Definition', 'KML', 'ZIP', 'Shapefile',
                  'Image Collection', 'PDF', 'Microsoft Excel']

    # Listing & downloading items in the root folder
    for root_folder_item in root_folder_items:
        if root_folder_item.type in file_types:
            _n += 1
            item_path = str(root_folder_item.download())
            file_extension = item_path.rsplit(".", maxsplit=1)[1]
            file_destination = os.path.normpath("".join([ARCGISBOXDIR, '/',
                                                         root_folder_item.title,
                                                         ".", file_extension]))
            os.rename(str(item_path), file_destination)
            logging.info(f"{root_folder_item.title}\t\t({root_folder_item.type})\n")

    # Listing documents inside other user folders
    for fld in flds:
        # logging.info((carpeta))
        logging.info(f"Name: {fld['title']}\n")
        os.mkdir(os.path.normpath("".join([ARCGISBOXDIR, "/", fld['title']])))
        flds = _user.items(folder=fld['title'])
        logging.info(f'You have {format(str(len(flds)))} items inside your folder\n')
        for i in flds:
            if i.type in file_types:
                _n += 1
                item_path = str(i.download())
                file_extension = item_path.rsplit(".", maxsplit=1)[1]
                file_destination = os.path.normpath("".join([ARCGISBOXDIR, "/",
                                                             fld['title'], "/", i.title,
                                                             ".", file_extension]))
                logging.info(file_destination)
                os.rename(str(item_path), file_destination)
                logging.info(f"\t\t {i.title} \t\t( {i.type} )\n")

    logging.info(f"\tDownloadable elements:\t {str(_n)}")


create_folder_structure(USER)
