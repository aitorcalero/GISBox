from arcgis.gis import GIS

csv_path = r"/Users/aitorcalero/PycharmProjects/ArcGISBox/Box/test.csv"
csv_properties={'title':'Impactos de meteoritos',
                'description':'Impactos de meteoritos registrados en diferentes partes del mundo',
                'tags':'csv, meteoritos, impactos'}

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

earthquake_csv_item = gis.content.add(item_properties=csv_properties, data=csv_path)
earthquake_feature_layer_item = earthquake_csv_item.publish()

print('The ['+earthquake_csv_item['title'] +'] layer has been sucessfully published')