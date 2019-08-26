[![Build Status](https://travis-ci.com/naturalis/sdmdl.svg?branch=master)](https://travis-ci.com/naturalis/sdmdl)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/naturalis/sdmdl/badge.svg?branch=master)](https://coveralls.io/github/naturalis/sdmdl?branch=master)
[![Documentation Status](https://readthedocs.org/projects/sdmdl/badge/?version=latest)](https://sdmdl.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/naturalis/sdmdl/shield.svg)](https://pyup.io/repos/github/naturalis/sdmdl/)

# sdmdl

An object-oriented python package for species distribution modelling using deep learning.
The package allows for a more intuitive and easy exploration of biodiversity patterns by 
modelling preferences for a great number of environmental variables. 

The functionality of this package and the estimates of environmental preferences it
obtains is demonstrated by way of several use cases:

* Habitat suitability predictions with which to scale visual object identifications
* Domesticated crops and their wild progenitors
* Mycorrhizal associations
* Secondary woodiness

The project builds on the previous results obtained by:

- [MAXENT modelling](https://github.com/naturalis/trait-geo-diverse-ungulates) by Elke Hendrix.
- [Deep learning](https://github.com/naturalis/trait-geo-diverse-dl) by Mark Rademaker.

### Package layout

- [CONTRIBUTING.md](CONTRIBUTING.md) - hints for how to contribute to this project
- [LICENSE](LICENSE) - the MIT license, which applies to this package
- [README.md](README.md) - the README file, which you are now reading
- [requirements.txt](requirements.txt) - prerequisites to install this package, used by pip
- [setup.py](setup.py) - installer script
- [data](data)/ - contains (some of) the data for the use cases - **marked for deletion**
- [docs](docs)/ - contains project documentation files
- [script](script)/ - contains utility scripts - **marked for deletion**
- [sdmdl](sdmdl)/ - the library code itself
- [tests](tests)/ - unit tests
