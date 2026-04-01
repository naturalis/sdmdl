[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/naturalis/sdmdl/badge.svg?branch=master)](https://coveralls.io/github/naturalis/sdmdl?branch=master)
[![Documentation Status](https://readthedocs.org/projects/sdmdl/badge/?version=latest)](https://sdmdl.readthedocs.io/en/latest/?badge=latest)

# sdmdl — Species Distribution Modelling with Deep Learning

An object-oriented Python package for species distribution modelling (SDM) using deep neural
networks (DNNs). The package provides an intuitive, high-level interface for exploring biodiversity
patterns by modelling species' environmental preferences across a large number of abiotic and biotic
variables.

Traditional SDM approaches such as [MaxEnt](https://biodiversityinformatics.amnh.org/open_source/maxent/)
have well-known limitations in handling correlated input features and incorporating species
interactions. **sdmdl** addresses these limitations by using deep learning, which can learn complex,
non-linear relationships between environmental predictors and species occurrences. The package
trains binary classification DNNs with dropout regularisation, evaluates model performance using AUC
and bootstrapped confidence intervals, and estimates variable importance using
[SHAP](https://github.com/slundberg/shap) values.

## Features

- **Data preparation** — Automatically creates presence maps, raster stacks, pseudo-absence
  samples, band statistics, and training/prediction datasets from occurrence tables and
  environmental raster layers.
- **Model training** — Trains multiple DNN replicates per species and retains the best-performing
  model (highest AUC). Computes feature importance via SHAP.
- **Prediction** — Generates global species distribution maps as GeoTIFF rasters and PNG
  visualisations.
- **Configuration** — All key hyper-parameters (batch size, epochs, layer sizes, dropout, random
  seed, pseudo-absence sample size) are controlled through a single `config.yml` file.

## Installation

### Prerequisites

[GDAL](https://gdal.org/download.html) must be installed separately as a system dependency,
including the GDAL Python bindings. On Ubuntu/Debian:

```bash
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)
```

### Install sdmdl

Clone the repository and install in your Python environment:

```bash
git clone https://github.com/naturalis/sdmdl.git
cd sdmdl
pip install .
```

The Python dependencies listed in [`requirements.txt`](requirements.txt) will be installed
automatically.

## Quick start

```python
from sdmdl.sdmdl_main import sdmdl

# Step 1: Create an sdmdl object pointing to the repository root
model = sdmdl('/path/to/sdmdl')

# Step 2: Prepare data (presence maps, raster stack, pseudo-absences, training & prediction data)
model.prep()

# Step 3: Train deep neural network models for each species
model.train()

# Step 4: Predict global species distributions
model.predict()

# Step 5: Remove temporary intermediate files
model.clean()
```

### Input requirements

1. **Environmental raster layers** (`.tif`) placed in:
   - `data/gis/layers/scaled/` — layers that require standardisation during preprocessing.
   - `data/gis/layers/non-scaled/` — layers that are already normalised or categorical.

   All raster layers (including the bundled `empty_land_map.tif`) must share the same affine
   transformation and resolution.

2. **Occurrence tables** (`.csv` or `.xls`/`.xlsx`) placed in `data/occurrences/`. Each table must
   contain columns named `decimalLatitude` (or `decimallatitude`) and `decimalLongitude` (or
   `decimallongitude`) with WGS 84 coordinates.

### Configuration

A `config.yml` file is generated automatically on first use in the `data/` directory. It controls:

| Parameter        | Type    | Description                                                  |
|------------------|---------|--------------------------------------------------------------|
| `random_seed`    | int     | Seed for reproducibility                                     |
| `pseudo_freq`    | int     | Number of pseudo-absence samples                             |
| `batchsize`      | int     | Training batch size                                          |
| `epoch`          | int     | Number of training epochs                                    |
| `model_layers`   | list    | Nodes per hidden layer (length sets network depth)           |
| `model_dropout`  | list    | Dropout rate per hidden layer                                |
| `verbose`        | bool    | If `True`, display progress bars                             |

Changes to `config.yml` take effect the next time an `sdmdl` object is created.

### Outputs

- **Performance metrics** — `results/_DNN_performance/DNN_eval.txt` with per-species accuracy,
  loss, AUC, TPR, and confidence intervals.
- **Trained models** — Per-species `.h5` (weights) and `.json` (architecture) files under
  `results/<species_name>/`.
- **Feature importance** — SHAP-based feature impact plots (`.png`) per species.
- **Prediction maps** — GeoTIFF rasters and colour-mapped PNG visualisations of predicted
  distributions per species.

## Documentation

Full documentation is available on [Read the Docs](https://sdmdl.readthedocs.io/) and in
[`docs/index.rst`](docs/index.rst).

## Background and references

This package implements the deep-learning SDM approach described in the following preprint:

> Rademaker, M., Hogeweg, L., & Vos, R. (2019). *Modelling the niches of wild and domesticated
> Ungulate species using deep learning.* bioRxiv, 744441.
> [https://doi.org/10.1101/744441](https://doi.org/10.1101/744441)

A copy of the preprint is included in this repository at [`docs/744441.full.pdf`](docs/744441.full.pdf).

### Related repositories

- [Comparative analysis of abiotic niches in Ungulates](https://github.com/naturalis/trait-geo-diverse-ungulates)
  by E. Hendrix — the MaxEnt-based comparative analysis that preceded this work.
- [Ecological Niche Modelling Using Deep Learning](https://github.com/naturalis/trait-geo-diverse-dl)
  by M. Rademaker — the original proof-of-concept DL-SDM implementation.

### Case study data

The raw results of a case study on domesticated crops and their wild progenitors are available on
Zenodo:
- [Environmental raster layers](https://zenodo.org/record/3460541)
- [Occurrence datasets](https://zenodo.org/record/3460530)
- [Case study results](https://zenodo.org/record/3460718)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on
submitting bug reports, feature requests, and pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

Copyright © 2019 Naturalis Biodiversity Center.
