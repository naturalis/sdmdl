import pandas as pd

def load_taxa_list (path):
    
    # Load the taxa list.
    
    taxa=pd.read_csv(path+"/data/occurrences_cleaned/taxalist.txt",header=None)
    taxa.columns=["taxon"]
    
    # initiate and build species dictionary.
    
    species_occ_dict={}
    
    for i in taxa["taxon"]:
        taxon_data = pd.read_csv(path+"/data/occurrences_cleaned/%s.csv"%i)
        species_occ_dict["%s"%i] = taxon_data  
    
    #check whether all species have been included and inspect dictionary
    
    #if len(species_occ_dict.keys())==len(taxa["taxon"]):
        #print("All species dataframes now in dictionary")
    #else:
        #print("Error: not all species dataframe included")
        
    return(taxa,species_occ_dict)