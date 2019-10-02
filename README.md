[![Build Status](https://travis-ci.com/naturalis/sdmdl.svg?branch=master)](https://travis-ci.com/naturalis/sdmdl)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/naturalis/sdmdl/badge.svg?branch=master)](https://coveralls.io/github/naturalis/sdmdl?branch=master)
[![Documentation Status](https://readthedocs.org/projects/sdmdl/badge/?version=latest)](https://sdmdl.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/naturalis/sdmdl/shield.svg)](https://pyup.io/repos/github/naturalis/sdmdl/)

# sdmdl

An object-oriented python package for species distribution modelling using deep learning.
The package allows for a more intuitive and easy exploration of biodiversity patterns by 
modelling preferences for a great number of environmental variables.

Instructions for installing and using the sdmdl package can be found [here](docs/index.rst).

### Case study

The functionality of this package and the estimates of environmental preferences it
obtains is demonstrated by way of a use case on domesticated crops and their wild progenitors.

The raw uninterpreted results of this case study can be found [here](https://zenodo.org/record/3460718#.XYuBJEYzaCo). 

### Acknowledgments

- [Comparative analysis of abiotic niches in Ungulates](https://github.com/naturalis/trait-geo-diverse-ungulates) by E. Hendrix.
- [Ecological Niche Modelling Using Deep Learning](https://github.com/naturalis/trait-geo-diverse-dl) by M. Rademaker.

### Package layout

- [CONTRIBUTING.md](CONTRIBUTING.md) - hints for how to contribute to this project
- [LICENSE](LICENSE) - the MIT license, which applies to this package
- [README.md](README.md) - the README file, which you are now reading
- [requirements.txt](requirements.txt) - prerequisites to install this package, used by pip
- [setup.py](setup.py) - installer script
- [data](data)/ - contains some files that are (currently) required for data preprocessing - **marked for deletion**
- [docs](docs)/ - contains documentation on package installation and usage
- [sdmdl](sdmdl)/ - the library code itself
- [tests](tests)/ - unit tests
