from arcgis.gis import GIS
import urllib.request

url = r"https://datos.madrid.es/egob/catalogo/208223-7605484-trafico-intensidad-tramas.kml"

urllib.request.urlretrieve(url,"C:\\Users\\aitor.calero\\Downloads\\trafico-intensidad.kml")

item_path = r"C:\\Users\\aitor.calero\\Downloads\\trafico-intensidad.kml"
item_properties={'title':'Intensidad de Tráfico',
                'description':'Intensidad de tráfico de Madrid actualizada cada 5 min',
                'tags':'tráfico, madrid, intensidad',
                'type':'KML'
                }


# gis = connect_to_arcgis("https://www.arcgis.com", usr, p)
gis = GIS(profile='geogeeks')

try:
    search_item = gis.content.search('Intensidad de Tráfico')
    item_for_deletion = gis.content.get(search_item[0].id)
    item_for_deletion.delete()
    print("El elemento \"{}\" ha sido borrado".format(search_item['title']))
except:
    print("Error al borrar")

try:
    item = gis.content.add(item_properties=item_properties, data=item_path)
    print('La capa \"{}\" se ha publicado con éxito'.format(item['title']))
except RuntimeError:
    print('Se ha encontrado un error')
