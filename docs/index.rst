SDMDL - species distribution modelling with deep learning
=========================================================

This toolkit was built to maximize ease of use while still offering in-depth parameter control for deep learning models.
As such this package offers only a single class and a handful of functions. If further customization of these models is 
required it comes with a config.yml file that can be edited in order to change important model hyper parameters. 

the SDMDL package works as follows:

.. code:: python

 model = sdmdl('path')
 model.prep()
 model.train()
 model.predict()

To create an sdmdl object and subsequently train deep learning models a few requirements need to be met.

1. Several input files (simply obtainable by copying the git repo).
2. A number of .tif files which will serve as the source of data for the deep learning process. 
   This project distinguishes between two types of environmental layers:
   i. Scaled layers, that need to be scaled during the process of preparing the data. 
   ii. Non-scaled layers, that are already normalized or are categorical (0 = not present while 1 = present).
   Note: all environmental layers need to have the same affine projection and coordinate system to be usable for analysis.
3. A set of occurrences (.csv or .xls) that will serve as training examples of where the species currently occurs.
   To be detectable as occurrence files, these tables need to have two required columns:
   i. 'decimalLatitude' or 'decimallatitude' holding the latitude for each occurrence.
   ii. 'decimalLongitude' or 'decimalLongitude', holding the longitude for each occurrence.

Before running the tool a few important details should be taken into account:

1. Scaled tif layers should be inserted into the ''root/data/gis/layers/scaled''
2. Non-scaled tif layers should be inserted into the ''root/data/gis/layers/non-scaled''
3. Occurrences should be inserted into the ''root/data/occurrences''

If these locations are not convenient it is possible to change these locations using the config.yml file in data/root.
Config.yml is created the first time an sdmdl object is created. And holds any relevant information on:
1. The detected environmental layers 
2. the detected occurrence files
3. Important hyperparameters for running the deep learning model are:
    i. Epoch or the number of training itterations.
    ii. Random seed to make random processes repeatable.
    iii. Model nodes & Model dropout, that allow the architecture of the model to be changed.
Note: changes to the config file are not updated automatically (yet!) so for these changes to take effect a new sdmdl objects needs to be created.

Once these steps are completed the model is ready for analysis:

Step 1: create a sdmdl object: ''model = sdmdl(location_of_repo)''
        or with additional parameters: ''model = sdmdl(location_of_repo, location_of_data, location_of_occurrences)''

Step 2: perform data pre-processing using: ''model.prep()''

Step 3: train the model using: ''model.train()''

Step 4: predict global distribution using: ''model.predict()''



