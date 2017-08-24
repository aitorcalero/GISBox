# GISBox

Project to create a **file synchronization service between an [ArcGIS Online](http://doc.arcgis.com/es/arcgis-online/reference/what-is-agol.htm) or [ArcGIS Enterprise](http://server.arcgis.com/es/server/latest/get-started/windows/what-is-arcgis-enterprise-.htm) account and a local-based filesystem**. 

With this tool you can easily synchronize all the content you have in your ArcGIS Organization to a local folder. This way you can easily manage documents, CSVs files, Shapefiles, etc... as you would do with other tools like [BOX](https://www.box.com), [Dropbox](https://www.dropbox.com) or [OneDrive](https://www.onedrive.com). 

This project uses the [ArcGIS API for Python](https://developers.arcgis.com/python/): 

> a Python library for working with maps and geospatial data. It provides simple and efficient tools for sophisticated vector and raster analysis, geocoding, map making, routing and directions, as well as for organizing and managing a GIS with users, groups and information items.

# Roadmap
1. Cloning the folder structure of the ArcGIS Organization account into a folder structure of the OS (Windows, Linux, MacOS)
2. Basic read-only, ie, download only syncronization script between ArcGIS and a folder structure in the OS. This process will only download meaningful file types such as PDFs, CSV, SD (Service Definition), Excel files, etc..
3. Full sychronization service whereby any new file inside a folder in the System OS, will be automatically uploaded to the ArcGIS Organization user account.
4. Publish and create ArcGIS Services using a right click pop-up menu when selecting CSVs, Excel files, KMLs or Shapefiles
