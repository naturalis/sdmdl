library("CoordinateCleaner")

OccurenceCleaner <- function(filepath) {

dat = read.csv(filepath, header = TRUE)

dat1 = cc_cap(dat,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country Capitals
dat2 = cc_cen(dat1,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country and Province Centroids
dat3 = cc_equ(dat2,"decimalLongitude","decimalLatitude") ## Identify Records with Identical lat/lon
dat4 = cc_gbif(dat3,"decimalLongitude","decimalLatitude") ## Identify Records Assigned to GBIF Headquarters
dat5 = cc_inst(dat4,"decimalLongitude","decimalLatitude") ## Identify Records in the Vicinity of Biodiversity Institutions
#??? = cc_sea(dat5,"decimalLongitude","decimalLatitude") ## Identify Non-terrestrial Coordinates
dat6 = cc_val(dat5,"decimalLongitude","decimalLatitude") ## Identify Invalid lat/lon Coordinates
dat7 = cc_zero(dat6,"decimalLongitude","decimalLatitude") ## Identify Zero Coordinates
#??? = cc_outl(dat8, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions

file_name = paste0(strsplit(strsplit(filepath,"/")[[1]][length(strsplit(filepath,"/")[[1]])],".csv"),"_clean.csv")
file_location = paste(strsplit(filepath,"/")[[1]][1:(length(strsplit(filepath,"/")[[1]])-1)],collapse='/')
output_location = paste(c(file_location,file_name),collapse="/")

removed_records = nrow(dat) - nrow(dat7)
message("")
message(paste("Removed",removed_records,'of',nrow(dat),'records.'))
message()

write.csv(dat7,output_location)

}