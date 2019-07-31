library("CoordinateCleaner")

dat = read.csv("./data/maize/zea_mays_l/zea_mays_l_test.csv", header = TRUE)

dat1 = cc_cap(dat,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country Capitals

dat2 = cc_cen(dat1,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country and Province Centroids

dat3 = cc_equ(dat2,"decimalLongitude","decimalLatitude") ## Identify Records with Identical lat/lon

dat4 = cc_gbif(dat3,"decimalLongitude","decimalLatitude") ## Identify Records Assigned to GBIF Headquarters

dat5 = cc_inst(dat4,"decimalLongitude","decimalLatitude") ## Identify Records in the Vicinity of Biodiversity Institutions

dat6 = cc_sea(dat5,"decimalLongitude","decimalLatitude") ## Identify Non-terrestrial Coordinates

dat7 = cc_val(dat6,"decimalLongitude","decimalLatitude") ## Identify Invalid lat/lon Coordinates

dat8 = cc_zero(dat7,"decimalLongitude","decimalLatitude") ## Identify Zero Coordinates

# dat9 = cc_outl(dat8, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions