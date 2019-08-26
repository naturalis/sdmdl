''SDMDL'' or species distribution modelling with deep learning is a tool that as the name suggests allows for modelling of the distribution of any (terrestrial) species.

This tool was built to maximize ease of use while still offering in depth parameter control for deep learning model. 
As such this package offers only a single class and a handful of functions. If further customization of these models is required it comes with a config.yml file that can be edited in order change important model hyper parameters. 

the SDMDL package works as follows:

''model = sdmdl('path')
model.prep()
model.train()
model.predict()''

To create an sdmdl object and subsequently train deep learning models a few requirements need to be met.

1. Several input files (simply obtainable by copying the git repo)
2. A number of .tif files which will serve as the source of data for the deep learning process. This project distinguishes between two types of environmental layers:
a. Scaled layers, that need to be scaled during the process of preparing the data. 
b. Non-scaled layers, that are already normalized or are categorical (0 = not present while 1 = present).
3. A set of occurrences (.csv or .xls) that will serve as training examples of where the species currently occurs.

Before running the tool a few important details should be taken into account:

1. Scaled tif layers should be inserted into the ''root/data/gis/layers/scaled''
2. Non-scaled tif layers should be inserted into the ''root/data/gis/layers/non-scaled''
3. Occurrences should be inserted into the ''root/data/occurrences''

If these locations are not convenient it is possible to change these locations using the config.yml file in root.

Once these steps are completed the model is ready for analysis:

Step 1: create a sdmdl object ''model = sdmdl(location_of_repo)

Step 2: perform data pre-processing using ''model.prep()''

Step 3: train the model using ''model.train()''

Step 4: predict global distribution using ''model.predict()''



