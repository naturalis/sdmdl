This folder structure holds the input data for the SDM analyses.

### Occurrences

The substructure will include a folder ([filtered](filtered)) with files with 
occurrences, one file per species. The files are formatted as per
[this](https://github.com/naturalis/trait-geo-diverse-ungulates/blob/master/data/filtered/Aepyceros_melampus.csv)
example. The data are collected from GBIF as DarwinCore archives 
(store the DOI for each query!) from which we retain the following columns:

1. gbif_id
2. taxon_name
3. decimal_latitude
4. decimal_longitude

### GIS data

There will also be a folder ([GIS](GIS)) with GIS layers as input for the niche 
modelling. The resolution will be 5 arcminutes. Which layers is to be determined.
