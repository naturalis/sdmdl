def read_config(path):
    
    config = '/data/config.txt'
    
    cnfg = open(path + config)
    cnfg = cnfg.read()
    cnfg = cnfg.split("\n")
    
    for row in cnfg:
        if row != '' and not row.startswith('#'):
            if row.split('=')[0].replace(' ','') == 'path':
                root = row.split('=')[-1].replace(' ','')[1:-1]
            if row.split('=')[0].replace(' ','') == 'verbose':
                verbose = row.split('=')[-1].replace(' ','')[1:-1]
    return(root,verbose)
            