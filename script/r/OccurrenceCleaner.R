library("CoordinateCleaner")

create_taxalist = function(dataPath)
  
{
  
  lidir = list.dirs(dataPath,recursive = TRUE)
  lidir = lidir[2:length(lidir)]
  
  taxalist = c()
  pathlist = c()
  
  for (l in lidir) {
    for (i in list.files(l)) {
      if (grepl(".csv",i)) { taxalist = append(taxalist,strsplit(i,".csv")[[1]]); pathlist = append(pathlist, l) }
    }
  }
  
  return(list(taxalist,pathlist))
  
}

num.decimals <- function(x) {
  stopifnot(class(x)=="numeric")
  x <- sub("0+$","",x)
  x <- sub("^.+[.]","",x)
  nchar(x)
}

check.precision = function(lat,lon) 
  
{
  lat_prcsn = num.decimals(lat)
  lon_prcsn = num.decimals(lon)
  
  ifelse(lat_prcsn > 1 & lon_prcsn > 1, return(TRUE), return(FALSE))
}

check.boundingbox = function(lat,lon)
  
{
  
  ifelse(lat < -89.0 | lat > 89.0, return(FALSE), ifelse(lon < -179.0 | lon > 179.0,return(FALSE),return(TRUE)))
  
}

OccurenceCleaner = function(dataPath,outPath) {

tl = create_taxalist(dataPath)

dir.create(file.path(outPath), showWarnings = FALSE)

for (each in 1:length(tl[[1]]))
  
{

filepath = paste0(tl[[2]][each],"/",tl[[1]][each],".csv")

dat = read.csv(filepath, header = TRUE)

message(paste("Cleaning",nrow(dat),sub("_"," ",tl[[1]][each],),"occurrences"))

message("Testing coordinate precision")

dat$latlon = TRUE

dat1 = dat

for (row in 1:nrow(dat1))
  
{
  
  dat1$latlon[row] = check.precision(dat1$decimalLatitude[row],dat1$decimalLongitude[row])
  
}

dat1 = dat1[dat1[,"latlon"] == TRUE,]

dat1["latlon"] = NULL

message(paste("Removed",nrow(dat)-nrow(dat1),"records."))

dat1$boundbox = TRUE

message("Testing bounding-box edge cases")

dat2 = dat1

for (row in 1:nrow(dat2))
  
{

    dat2$boundbox[row] = check.boundingbox(dat2$decimalLatitude[row],dat2$decimalLongitude[row])
  
}

dat2 = dat2[dat2[,"boundbox"] == TRUE,]

dat2["boundbox"] = NULL

message(paste("Removed",nrow(dat1)-nrow(dat2),"records."))

message("Testing for overlapping occurrences")

dat3 = dat2[row.names(unique(dat2[,c("decimalLatitude", "decimalLongitude")])),]

message(paste("Removed",nrow(dat2)-nrow(dat3),"records."))

dat4 = cc_cap(dat3,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country Capitals
dat5 = cc_cen(dat4,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country and Province Centroids
dat6 = cc_equ(dat5,"decimalLongitude","decimalLatitude") ## Identify Records with Identical lat/lon
dat7 = cc_gbif(dat6,"decimalLongitude","decimalLatitude") ## Identify Records Assigned to GBIF Headquarters
dat8 = cc_inst(dat7,"decimalLongitude","decimalLatitude") ## Identify Records in the Vicinity of Biodiversity Institutions
dat9 = cc_sea(dat8,"decimalLongitude","decimalLatitude") ## Identify Non-terrestrial Coordinates
dat10 = cc_val(dat9,"decimalLongitude","decimalLatitude") ## Identify Invalid lat/lon Coordinates
dat11 = cc_zero(dat10,"decimalLongitude","decimalLatitude") ## Identify Zero Coordinates
dat12 = cc_outl(dat11, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions

removed_records = nrow(dat) - nrow(dat12)
message("")
message(paste("Removed",removed_records,'of',nrow(dat),'records.'))
message()

write.csv(dat12,paste0(outPath,"/",tl[[1]][each],".csv"))

}

write(tl[[1]],paste0(outPath,"/taxalist.txt"))

}