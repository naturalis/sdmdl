import pandas as pd

class taxa_list():
    
    def __init__(path):
        

def load_taxa_list (path):
      
    taxa=pd.read_csv(path+"/data/occurrences_cleaned/taxalist.txt",header=None)
    taxa.columns=["taxon"]

    species_occ_dict={}
    
    for i in taxa["taxon"]:
        taxon_data = pd.read_csv(path+"/data/occurrences_cleaned/%s.csv"%i)
        species_occ_dict["%s"%i] = taxon_data  
        
    return(taxa,species_occ_dict)