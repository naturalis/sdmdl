  library(CoordinateCleaner)
  library(dplyr)
  
  # Create_taxalist function to obtain a list of species (names and filepaths) in the occurrence folder. 
  
  create_taxalist = function(dataPath)
    
  {
    lidir = list.dirs(dataPath,recursive = TRUE)
    lidir = lidir[2:length(lidir)]
    taxalist = c()
    pathlist = c()
    for (l in lidir) 
    {
      for (i in list.files(l)) 
      {
        if (grepl(".csv",i)) 
        { 
          taxalist = append(taxalist,strsplit(i,".csv")[[1]]); pathlist = append(pathlist, l) 
        }
      }
    }
    return(list(taxalist,pathlist))
  }
  
  # Num_decimals function that returns the number of decimal places of a numerical variable.
  
  num_decimals <- function(x) 
    
  {
    return(match(TRUE, round(x, 1:40) == x))
  }
  
  # Check_precision function that returns True if both coordinates have at least 2 decimal digits, and False if one (or both) have less then 2 decimal digits.
  
  check_precision = function(lat,lon) 
    
  {
    lat_prcsn = num_decimals(lat)
    lon_prcsn = num_decimals(lon)
    ifelse(lat_prcsn > 1 & lon_prcsn > 1, return(TRUE), return(FALSE))
  }
  
  # Check_boundinbox function that returns True if both coordinates fall within the valid range, and False if on (or both) fall outside of the valid range.
  
  check_boundingbox = function(lat,lon)
    
  {
    ifelse(lat < -59.5 | lat > 89.5, return(FALSE), ifelse(lon < -179.5 | lon > 179.5,return(FALSE),return(TRUE)))
  }
  
  # OccurrenceCleaner function that:
    # Finds all species in the given folder (dataPath).
    # For each species filters the occurrence table.
    # Saves the final result to a new .csv file.
  
  OccurrenceCleaner = function(dataPath) 
    
  {
    outPath = paste0(dataPath,"/data/occurrences_cleaned")
    tl = create_taxalist(paste0(dataPath,"/data/occurrences",collapse = "/"))
    dir.create(file.path(outPath), showWarnings = FALSE)
    for (each in 1:length(tl[[1]]))
    {
      filepath = paste0(tl[[2]][each],"/",tl[[1]][each],".csv")
      if (file.exists(paste0(outPath,"/",tl[[1]][each],".csv"))) {next}
      dat = read.csv(filepath, header = TRUE)
      
      dat$acceptedScientificName = gsub('_',' ',tl[[1]][each])
      
      message(paste("Cleaning",nrow(dat),sub("_"," ",tl[[1]][each],),"occurrences"))
      
      # TEST 1 - COORDINATE DECIMAL PLACES >= 2
      message("Testing coordinate precision")
      dat1 = dat[,]
      if (nrow(dat1) == 0) {message("No occurrences remaining.\n");next}
      dat1$latlon = TRUE
      for (row in 1:nrow(dat1))
      {
        dat1$latlon[row] = check_precision(dat1$decimalLatitude[row],dat1$decimalLongitude[row])
      }
      dat1 = dat1[dat1[,"latlon"] == TRUE,]
      dat1["latlon"] = NULL
      message(paste("Removed",nrow(dat)-nrow(dat1),"records."))
      
      # TEST 2 - OUT OF BOUNDS ANALYSIS [lat.max = 89.5, lat.min = -59.5, lon.max = 179.5, lon.min = 179.5]
      message("Testing bounding-box edge cases")
      dat2 = dat1[,]
      if (nrow(dat2) == 0) {message("No occurrences remaining.\n");next}
      dat2$boundbox = TRUE
      for (row in 1:nrow(dat2))
      {
        dat2$boundbox[row] = check_boundingbox(dat2$decimalLatitude[row],dat2$decimalLongitude[row])
      }
      dat2 = dat2[dat2[,"boundbox"] == TRUE,]
      dat2["boundbox"] = NULL
      message(paste("Removed",nrow(dat1)-nrow(dat2),"records."))
      
      # TEST 3 - REMOVE OVERLAPPING OCCURRENCES.
      message("Testing for overlapping occurrences")
      dat3 = dat2 %>% distinct(decimalLatitude,decimalLongitude, .keep_all= TRUE)
      if (nrow(dat3) == 0) {message("No occurrences remaining.\n");next}
      message(paste("Removed",nrow(dat2)-nrow(dat3),"records."))
      
      # TEST 4 - REMOVE GEOGRAPHIC OUTLIERS (ISOLATED FROM OTHER OCCURRENCES BY AT LEAST 1000 KM).
      dat4 = cc_outl(dat3, lon = "decimalLongitude", lat = "decimalLatitude",species="acceptedScientificName", method = "distance", tdi = 1000)
      if (nrow(dat4) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 5 - REMOVE COORDS IN VICINITY OF COUNTRY CAPITALS.
      dat5 = cc_cap(dat4,"decimalLongitude","decimalLatitude")
      if (nrow(dat5) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 6 - REMOVE COORDS IN VICINITY OF COUNTRY OR PROVINCE CENTROIDS.
      dat6 = cc_cen(dat5,"decimalLongitude","decimalLatitude")
      if (nrow(dat6) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 7 - REMOVE COORDS WITH IDENTICAL LAT/LON.
      dat7 = cc_equ(dat6,"decimalLongitude","decimalLatitude")
      if (nrow(dat7) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 8 - REMOVE COORDS IN VICINITY OF GBIF HQ.
      dat8 = cc_gbif(dat7,"decimalLongitude","decimalLatitude")
      if (nrow(dat8) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 9 - REMOVE COORDS IN VICINITY OF BIODIV INSTITUTIONS.
      dat9 = cc_inst(dat8,"decimalLongitude","decimalLatitude")
      if (nrow(dat9) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 10 - REMOVE NON-TERRESTRIAL COORDS.
      dat10 = tryCatch({cc_sea(dat9,"decimalLongitude","decimalLatitude")},
                      warning = function (warning_condition) 
                        {
                        message("Oops, something has gone wrong!")
                        message("Original warning message:")
                        message(warning_condition)
                        },
                      error = function (error_condition)
                        {
                        message("Occurrences do not overlap land, please make sure your coordinate data is correct.")
                        message("Original error message:")
                        message(error_condition)
                        })
      if (is.null(dat10)) {message("\n");next}
      if (nrow(dat10) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 11 - REMOVE INVALID LAT/LON COORDS.
      dat11 = cc_val(dat10,"decimalLongitude","decimalLatitude")
      if (nrow(dat11) == 0) {message("No occurrences remaining.\n");next}
      
      # TEST 12 - REMOVE ZERO COORDS.
      dat12 = cc_zero(dat11,"decimalLongitude","decimalLatitude")
      if (nrow(dat12) == 0) {message("No occurrences remaining.\n");next}
      
      message("Testing for NA occurrences")
      final_dat = dat12[!is.na(dat12["X"]),]
      message(paste("Removed",nrow(dat11)-nrow(final_dat),"records."))
      
      rm_records = nrow(dat) - nrow(final_dat)
      message(paste("Removed",rm_records,'of',nrow(dat),'records.\n'))
      print(tl[[1]][each])
      write.csv(final_dat,paste0(outPath,"/",tl[[1]][each],".csv"))
    }
    
    final_taxa = create_taxalist(paste0(dataPath,"/data/occurrences_cleaned",collapse = "/"))
    write(final_taxa[[1]],paste0(outPath,"/taxalist.txt"))
    
    drop_spec = setdiff(tl[[1]],final_taxa[[1]])
    write(drop_spec,paste0(outPath,"/droplist.txt"))
    
  }