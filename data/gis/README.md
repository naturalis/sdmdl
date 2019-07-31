# GIS datasets 
## Climate 
Both the [Bioclim](http://worldclim.org/version2) dataset and the [ENVIREM](https://deepblue.lib.umich.edu/data/concern/data_sets/gt54kn05f) dataset are used as climatic variables. 
![](images/bioclim.PNG)
### Datasets Bioclim 
1. BIO1 Annual Mean Temperature
2. BIO2 Mean Diurnal Range (Mean of monthly (max temp - min temp))
3. BIO3 Isothermality (BIO2/BIO7) (* 100)
4. BIO4 Temperature Seasonality (standard deviation *100)
5. BIO5 Max Temperature of Warmest Month
6. BIO6 Min Temperature of Coldest Month
7. BIO7 Temperature Annual Range (BIO5-BIO6)
8. BIO8 Mean Temperature of Wettest Quarter
9. BIO9 Mean Temperature of Driest Quarter
10. BIO10 Mean Temperature of Warmest Quarter
11. BIO11 Mean Temperature of Coldest Quarter
12. BIO12 Annual Precipitation
13. BIO13 Precipitation of Wettest Month
14. BIO14 Precipitation of Driest Month
15. BIO15 Precipitation Seasonality (Coefficient of Variation)
16. BIO16 Precipitation of Wettest Quarter
17. BIO17 Precipitation of Driest Quarter
18. BIO18 Precipitation of Warmest Quarter
19. BIO19 Precipitation of Coldest Quarter

### Datasets ENVIREM 
1. annualPET Annual potential evapotranspiration
2. aridityIndexThornthwaite Thornthwaite aridity index
3. climaticMoistureIndex Metric of relative wetness and aridity
4. continentality Average temp. of warmest and coldest month
5. embergerQ Emberger’s pluviothermic quotient
6. growingDegDays0 Sum of months with temperatures greater than 0 degrees
7. growingDegDays5 Sum of months with temperatures greater than 5 degrees
8. maxTempColdestMonth Maximum temp. of the coldest month
9. minTempWarmestMonth Minimum temp. of the warmest month
10. monthCountByTemp10 Sum of months with temperatures greater than 10 degrees
11. PETColdestQuarter Mean monthly PET of coldest quarter
12. PETDriestQuarter Mean monthly PET of driest quarter
13. PETseasonality Monthly variability in potential evapotranspiration
14. PETWarmestQuarter Mean monthly PET of warmest quarter
15. PETWettestQuarter Mean monthly PET of wettest quarter
16. thermInd Compensated thermicity index

## Topography
Median elevation variables were extracted from the [Harmonized World Soil Database ](http://www.fao.org/soils-portal/soil-survey/soil-maps-and-databases/harmonized-world-soil-database-v12/en/) and have a spatial resolution of 30 arcseconds. The topographic wetness index and the terrain roughness index are extracted from the [ENVIREM](https://deepblue.lib.umich.edu/data/concern/data_sets/gt54kn05f) dataset and have a spatial resolution of 30 arcseconds. 
### Datasets 
1. Slope
2. Aspect
![](images/slope.PNG)
## Soil 
The soil characteristics are extracted from the [Land-Atmosphere Interaction Research Group](http://globalchange.bnu.edu.cn/research/soilw) with a spatial resolution of 5 arcminutes. 

1. Bulk density
2. Clay percentage
3. pH CaCL
4. Organic carbon 

![](images/ph.PNG)

## Ecoregions
Separate raster maps representing the world's terrestrial ecoregions were created from the [The Nature Conservancy's](http://maps.tnc.org/gis_data.html) world ecoregion's shapefile.
1. Boreal Forests and Taiga
2. Deserts and Xeric Shrublands
3. Flooded Grasslands and Savannas
4. Inland Water
5. Mangroves
6. Meditteranean Forests, Woodlands and Scrubs
7. Montane Grasslands and Shrublands
8. Rock and Ice
9. Temperature Broadleaf  and Mixed Forests
10. Temperature Conifer Forests
11. Temperate Grasslands, Savannas and Shurblands
12. Tropical and Subtropical Coniferous Forests
13. Tropical and Subtropical Dry Broadleaf Forests
14. Tropical and Subtropical Grasslands, Savannas and Shrublands
15. Tropical and Subtropical Moist Broadleaf Forests
16. Tundra

## Ecoregion attributes
Additional attribute metrics per ecoregion from the The World Atlas of Conservation extracted as shapefiles from [Databasin](https://databasin.org/maps/new#datasets=43478f840ac84173979b22631c2ed672) and rasterized.
1. Habitat fragmentation
2. Human accessibility
3. Human appropriation
4. Mammal species richness
5. Plant species richness

## Species co-occurrence.
Species occurrence raster maps created for 124 species, list of species can be found in [Taxa list](https://github.com/naturalis/trait-geo-diverse-dl/blob/master/data_GIS_extended/data/SQL_filtered_gbif/taxa_list.txt)


# Stacked raster datasets
## env_stacked
The [env_stacked](env_stacked) folder contains the environmental variable rasters stacked into a single GeoTiff, the file itself is not uploaded on Github as it's size is too large. Next to this, the folder contains a text file containing the variable descriptions for each of the 186 bands in the GeoTiff.

## stacked raster clips
A clip was made of the GeoTiff for each species, based on its IUCN range.
However, this clip was not uploaded to Github as file sizes were too large.
