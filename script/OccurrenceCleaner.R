library("CoordinateCleaner")

dat = read.csv("./data/maize/zea_mays_l/zea_mays_l.csv", header = TRUE)

dat$decimalLatitude <- as.numeric(dat$decimalLatitude)
dat$decimalLongitude <- as.numeric(dat$decimalLongitude)

# skip -> buffland -> Global Coastlines buffered by 1 degree

dat1 = cc_cap(dat,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country Capitals

dat2 = cc_cen(dat1,"decimalLongitude","decimalLatitude") ## Identify Coordinates in Vicinity of Country and Province Centroids

# skip -> cc_coun -> Identify Coordinates Outside their Reported Country

# skip -> cc_dupl  -> Identify Duplicated Records

dat3 = cc_equ(dat2,"decimalLongitude","decimalLatitude") ## Identify Records with Identical lat/lon

dat4 = cc_gbif(dat3,"decimalLongitude","decimalLatitude") ## Identify Records Assigned to GBIF Headquarters

dat5 = cc_inst(dat4,"decimalLongitude","decimalLatitude") ## Identify Records in the Vicinity of Biodiversity Institutions

# skip -> cc_iucn -> Identify Records Outside Natural Ranges

# dat6 = cc_outl(dat5, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions

dat6 = cc_sea(dat5,"decimalLongitude","decimalLatitude") ## Identify Non-terrestrial Coordinates

# skip  -> cc_urb  -> Identify Records Inside Urban Areas

dat7 = cc_val(dat6,"decimalLongitude","decimalLatitude") ## Identify Invalid lat/lon Coordinates

dat8 = cc_zero(dat7,"decimalLongitude","decimalLatitude") ## Identify Zero Coordinates

# skip -> cd_ddmm -> Identify Datasets with a Degree Conversion Error

# skip -> cd_round -> Identify Datasets with Rasterized Coordinates

# skip -> cf_age -> Identify Fossils with Outlier Age

# skip -> cf_equal -> Identify Fossils with equal min and max age

# skip -> cf_outl -> Identify Outlier Records in Space and Time

# skip -> cf_range -> Identify Fossils with Extreme Age Ranges

# skip -> clean_coordinates -> Geographic Cleaning of Coordinates from Biologic Collections <----- COMBINATION OF ALL/MOST CLEANING PROCEDURES IN ONE

# skip -> clean_dataset -> Coordinate Cleaning using Dataset Properties <----- TESTS FOR CONVERSION AND ROUNDING PROBLEMS

# skip -> clean_fossils -> Geographic and Temporal Cleaning of Records from Fossil Collections

dat9 = cc_outl(dat8, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions

dat8_testing = dat8[1:1000,]

dat9 = cc_outl(dat8_testing, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000) ## Identify Geographic Outliers in Species Distributions

splist <- split(dat8, f = as.character(dat8[["acceptedScientificName"]]))

thinning = FALSE

ras_create <- function(x, lat, lon,  thinning_res){
  # get data extend
  ex <- raster::extent(sp::SpatialPoints(x[, c(lon, lat)])) + thinning_res * 2
  
  # create raster
  ras <- raster::raster(x = ex, resolution = thinning_res)
  
  # set cell ids
  vals <- seq_len(raster::ncell(ras))
  ras <- raster::setValues(ras, vals)
  
  return(ras)
}

ras_dist <-  function(x, lat, lon, ras, weights){
  # x = a data.frame of point coordinates, ras = a raster with cell IDs as layer,
  #weight = logical, shall the distance matrix be weightened by the number of points per cell?
  # assign each point to a raster cell
  pts <- raster::extract(x = ras, y = sp::SpatialPoints(x[, c(lon, lat)]))
  
    # convert to data.frame
  midp <- data.frame(raster::rasterToPoints(ras))
  
  #print(midp)
  
  # retain only cells that contain points
  midp <- midp[midp$layer %in% unique(pts),]

    # order
  midp <- midp[match(unique(pts), midp$layer),]
  
  #a <- midp[, c("y")]
  
  #print(a)
  
  #b <- a < -90
  
  #print(b)
  
  #print(TRUE %in% b)


  # calculate geospheric distance between raster cells with points
  dist <- geosphere::distm(midp[, c("x", "y")], 
                           fun = geosphere::distHaversine) / 1000
  
  # set rownames and colnames to cell IDs
  dist <- as.data.frame(dist, row.names = as.integer(midp$layer))
  names(dist) <- midp$layer
  
  if(weights){
    # approximate within cell distance as half 
    # the cell size, assumin 1 deg = 100km
    # this is crude, but doesn't really matter
    dist[dist == 0] <- 100 * mean(raster::res(ras)) / 2
    
    # weight matrix to account for the number of points per cell
    ## the number of points in each cell
    cou <- table(pts)
    
    ## order
    cou <- cou[match(unique(pts), names(cou))]
    
    # weight matrix, representing the number of distances between or within the cellse (points cell 1 * points cell 2)
    wm <- outer(cou, cou)
    
    # multiply matrix elements to get weightend sum
    dist <- round(dist * wm, 0)
    
    dist <- list(pts = pts, dist = dist, wm = wm)
  }else{
    # set diagonale to NA, so it does not influence the mean
    dist[dist == 0] <- NA
    
    dist <- list(pts = pts, dist = dist)
  }
  
  return(dist)
}

flags <- lapply(splist, function(k) {
  if (nrow(k) <= 10000 & !thinning) {
    dist <- geosphere::distm(k[, c(lon, lat)], fun = geosphere::distHaversine)/1000
    dist[dist == 0] <- NA
  }
  else {
    if (thinning) {
      dist_obj <- ras_dist(x = k, lat = lat, lon = lon, 
                           ras = ras, weights = FALSE)
      pts <- dist_obj$pts
      dist <- dist_obj$dist
    }
    else {
      dist_obj <- ras_dist(x = k, lat = lat, lon = lon, 
                           ras = ras, weights = TRUE)
      pts <- dist_obj$pts
      dist <- dist_obj$dist
      wm <- dist_obj$wm
    }
  }
  if (method == "distance") {
    if (sampling_thresh > 0) {
      stop("Sampling correction impossible for method 'distance'")
    }
    mins <- apply(dist, 1, min, na.rm = TRUE)
    out <- which(mins > tdi)
  }
  else {
    if (nrow(k) >= 10000 & !thinning) {
      mins <- apply(dist, 1, sum, na.rm = TRUE)/rowSums(wm, 
                                                        na.rm = TRUE)
    }
    else {
      mins <- apply(dist, 1, mean, na.rm = TRUE)
    }
  }
  if (method == "quantile") {
    quo <- quantile(mins, c(0.25, 0.75), na.rm = TRUE)
    out <- which(mins > quo[2] + stats::IQR(mins) * mltpl)
  }
  if (method == "mad") {
    quo <- stats::median(mins, na.rm = TRUE)
    tester <- stats::mad(mins, na.rm = TRUE)
    out <- which(mins > quo + tester * mltpl)
  }
  if (nrow(k) > 10000 | thinning) {
    if (length(out) == 0) {
      ret <- NA
    }
    if (length(out) > 0) {
      ret <- rownames(k)[which(pts %in% gsub("X", "", 
                                             names(out)))]
    }
  }
  else {
    if (length(out) == 0) {
      ret <- NA
    }
    if (length(out) > 0) {
      ret <- rownames(k)[out]
    }
  }
  return(ret)
})

