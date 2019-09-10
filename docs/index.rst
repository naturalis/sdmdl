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

1. Several input files (simply obtainable by copying or cloning the git repo).
2. `A set of environmental rasters <https://link.to.rasters/>`_ (.tif) which will serve as the source of data for the deep learning process.
   This project distinguishes between two types of environmental layers:

   i. Scaled layers, that need to be scaled during the process of preparing the data.
   ii. Non-scaled layers, that are already normalized or are categorical (0 = not present while 1 = present).

   **Note:**
   all environmental layers need to have the same affine transformation and resolution to be usable for analysis.
   This includes the file 'empty_land_map.tif' that is included in the git repo. This entails that the spatial extent
   and resolution of 'empty_land_map.tif' need to be copied, or that this file must be edited to match spatial extent
   and resolution of the other raster files.

3. `A set of occurrences <https://link.to.rasters/>`_ (.csv or .xls) that will serve as training examples of where the species currently occurs.
   To be detectable as occurrence files, these tables need to have two required columns:

   i. 'decimalLatitude' or 'decimallatitude' holding the latitude for each occurrence.
   ii. 'decimalLongitude' or 'decimalLongitude', holding the longitude for each occurrence.

   **Note:**
   The occurrence coordinates are currently not checked before starting data preparations. So be aware that any
   obviously wrong values will cause an error. This includes any values of the wrong datatype (anything that is not
   numerical) and coordinates that are outside the spatial extent of the provided raster files.

**Before running the tool a few important details should be taken into account:**

1. Scaled tif layers should be inserted into the ''root/data/gis/layers/scaled''
2. Non-scaled tif layers should be inserted into the ''root/data/gis/layers/non-scaled''
3. Occurrences should be inserted into the ''root/data/occurrences''

If these locations are not convenient it is possible to change these locations using the config.yml file in "root/data".
Config.yml is initiated the first time an sdmdl object is created. And holds any relevant information on:

1. Detected raster files.
2. Detected occurrence files
3. Parameters for running the deep learning model are:
    a. **integer** random_seed, makes random processes repeatable.
    b. **integer** pseudo_freq: number of sampled (pseudo) absences.
    c. **integer** batchsize: number of data points given to the model during training at once.
    d. **integer** epoch: number of (training) iterations over the whole data set.
    e. **integer** model_layers: number of nodes per layer. Adding extra items to the list makes the model deeper.
    f. **float** model_dropout: dropout deactivates a percentage of nodes during training (0 = no nodes are turned off and 1 = all nodes are turned off)
    g. **boolean** Verbose: if True prints progress bars

**Note:** changes to the config file are not updated automatically
so any changes are not detected by the sdmdl object, for changes to take effect a new sdmdl objects needs to be created.

Once these steps are completed the model is ready for analysis:

**Step 1:** create a sdmdl object:

.. code:: python

 model = sdmdl(location_of_repo)

 or

 model = sdmdl(location_of_repo, location_of_data, location_of_occurrences)

**Step 2:** prepare data:

.. code:: python

 model.prep()

**Step 3:** train the model(s):

.. code:: python

 model.train()

**Step 4:** predict global distribution:

.. code:: python

 model.predict()



