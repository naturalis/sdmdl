sdmdl — Species Distribution Modelling with Deep Learning
=========================================================

**sdmdl** is an object-oriented Python package for species distribution modelling (SDM) using deep
neural networks (DNNs). It provides a high-level interface for modelling species' environmental
preferences across many abiotic and biotic variables, training binary classification DNNs with
dropout regularisation, and generating global distribution predictions.

The package was built to maximise ease of use while still offering in-depth parameter control. The
main entry point is a single ``sdmdl`` class with four methods that cover the complete workflow:

.. code:: python

   from sdmdl.sdmdl_main import sdmdl

   model = sdmdl('/path/to/repository_root')
   model.prep()       # data preparation
   model.train()      # model training
   model.predict()    # distribution prediction
   model.clean()      # remove temporary files

Further customisation is available through a ``config.yml`` file that controls model
hyper-parameters (see `Configuration`_).

Installation
---------------------------------------------------------

Prerequisites
^^^^^^^^^^^^^

`GDAL <https://gdal.org/download.html>`_ must be installed as a system dependency, including the
GDAL Python bindings. On Ubuntu/Debian:

.. code:: bash

   sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
   sudo apt-get update
   sudo apt-get install gdal-bin libgdal-dev
   pip install GDAL==$(gdal-config --version)

Install sdmdl
^^^^^^^^^^^^^

Clone the repository and install:

.. code:: bash

   git clone https://github.com/naturalis/sdmdl.git
   cd sdmdl
   pip install .

The Python dependencies listed in ``requirements.txt`` will be installed automatically.

Input requirements
---------------------------------------------------------

To create an ``sdmdl`` object and subsequently train models, the following inputs are required:

1. **Environmental raster layers** (``.tif``) placed in the appropriate directories:

   - ``data/gis/layers/scaled/`` — layers that need to be standardised during preprocessing.
   - ``data/gis/layers/non-scaled/`` — layers that are already normalised or categorical
     (e.g. 0 = absent, 1 = present).

   Example datasets are available on Zenodo:
   `environmental rasters <https://zenodo.org/record/3460541>`_.

   .. note::

      All environmental layers **must** share the same affine transformation and resolution. This
      includes the bundled ``empty_land_map.tif`` in ``data/gis/layers/``. If you supply your own
      rasters, ensure they match the affine transformation and resolution of ``empty_land_map.tif``
      (or vice versa).

2. **Occurrence tables** (``.csv``, ``.xls``, or ``.xlsx``) placed in ``data/occurrences/``.
   Each table must contain two required columns:

   - ``decimalLatitude`` (or ``decimallatitude``) — latitude for each occurrence.
   - ``decimalLongitude`` (or ``decimallongitude``) — longitude for each occurrence.

   Coordinates must be in the WGS 84 coordinate system. Example datasets are available on Zenodo:
   `occurrence datasets <https://zenodo.org/record/3460530>`_.

   .. warning::

      Occurrence coordinates are **not** validated before data preparation. Incorrect data types
      (non-numerical values) or coordinates outside the spatial extent of the raster files will
      cause errors.

Directory layout summary:

- Scaled ``.tif`` layers → ``data/gis/layers/scaled/``
- Non-scaled ``.tif`` layers → ``data/gis/layers/non-scaled/``
- Occurrence tables → ``data/occurrences/``

Configuration
---------------------------------------------------------

A ``config.yml`` file is generated automatically on first use in the ``data/`` directory. It stores
detected raster files, detected occurrence files, and model parameters:

- **random_seed** (*int*): seed for reproducibility (default: 42).
- **pseudo_freq** (*int*): number of pseudo-absence samples (default: 2000).
- **batchsize** (*int*): training batch size (default: 75).
- **epoch** (*int*): number of training epochs (default: 150).
- **model_layers** (*list of int*): nodes per hidden layer; adding items deepens the network
  (default: ``[250, 200, 150, 100]``).
- **model_dropout** (*list of float*): dropout rate per hidden layer; 0 = no dropout, 1 = full
  dropout (default: ``[0.3, 0.5, 0.3, 0.5]``).
- **verbose** (*bool*): if ``True``, display progress bars (default: ``True``).

Data paths and detected files can also be customised in ``config.yml``.

.. note::

   Changes to ``config.yml`` are **not** picked up automatically. A new ``sdmdl`` object must be
   created for changes to take effect.

Usage example
---------------------------------------------------------

**Step 1:** Create an ``sdmdl`` object:

.. code:: python

   from sdmdl.sdmdl_main import sdmdl

   model = sdmdl('/path/to/repository_root')

**Step 2:** Prepare data (presence maps, raster stack, pseudo-absences, training and prediction
datasets):

.. code:: python

   model.prep()

**Step 3:** Train deep neural network models for each species:

.. code:: python

   model.train()

**Step 4:** Predict global species distributions:

.. code:: python

   model.predict()

**Step 5:** Remove temporary intermediate files:

.. code:: python

   model.clean()

Outputs
---------------------------------------------------------

Data preparation (``prep``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Several temporary intermediate files are created and used as inputs for training and prediction.

Training (``train``)
^^^^^^^^^^^^^^^^^^^^

- **Performance metrics** — ``results/_DNN_performance/DNN_eval.txt`` contains per-species
  accuracy, loss, AUC, true positive rate, and 95 % confidence intervals.
- **Model files** — for each species, a ``.h5`` (weights) and ``.json`` (architecture) file is
  saved under ``results/<species_name>/``.
- **Feature importance** — a SHAP-based feature impact plot (``.png``) per species, saved under
  ``results/<species_name>/``.

Prediction (``predict``)
^^^^^^^^^^^^^^^^^^^^^^^^

- **Prediction map** — a colour-mapped ``.png`` visualisation of the predicted distribution per
  species, saved under ``results/<species_name>/``.
- **Prediction raster** — a GeoTIFF (``.tif``) with the predicted probability of presence (0–1)
  per species, saved under ``results/<species_name>/``.

Package architecture
---------------------------------------------------------

The package is organised into the following modules:

- ``sdmdl.sdmdl_main`` — the main ``sdmdl`` class orchestrating the full workflow.
- ``sdmdl.sdmdl.config`` — ``Config`` class for managing ``config.yml``.
- ``sdmdl.sdmdl.occurrences`` — ``Occurrences`` class for managing occurrence data.
- ``sdmdl.sdmdl.gis`` — ``GIS`` class for managing raster layer paths and output locations.
- ``sdmdl.sdmdl.trainer`` — ``Trainer`` class for DNN training and evaluation.
- ``sdmdl.sdmdl.predictor`` — ``Predictor`` class for generating distribution predictions.
- ``sdmdl.sdmdl.data_prep`` — data preparation sub-package:

  - ``presence_map`` — creates per-species presence rasters.
  - ``raster_stack`` — stacks environmental layers into a single GeoTIFF.
  - ``presence_pseudo_absence`` — samples pseudo-absence locations.
  - ``band_statistics`` — computes band-wise mean and standard deviation.
  - ``training_data`` — prepares per-species training datasets.
  - ``prediction_data`` — prepares the global prediction dataset.

References
---------------------------------------------------------

This package implements the deep-learning SDM approach described in:

   Rademaker, M., Hogeweg, L., & Vos, R. (2019). *Modelling the niches of wild and domesticated
   Ungulate species using deep learning.* bioRxiv, 744441.
   `doi:10.1101/744441 <https://doi.org/10.1101/744441>`_

Related repositories:

- `Comparative analysis of abiotic niches in Ungulates <https://github.com/naturalis/trait-geo-diverse-ungulates>`_
  by E. Hendrix.
- `Ecological Niche Modelling Using Deep Learning <https://github.com/naturalis/trait-geo-diverse-dl>`_
  by M. Rademaker.

License
---------------------------------------------------------

This project is licensed under the `MIT License <https://opensource.org/licenses/MIT>`_.
Copyright © 2019 Naturalis Biodiversity Center.
