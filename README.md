[![Build Status](https://travis-ci.com/naturalis/trait-geo-diverse-angiosperms.svg?branch=master)](https://travis-ci.com/naturalis/trait-geo-diverse-angiosperms)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/naturalis/trait-geo-diverse-angiosperms/badge.svg?branch=master)](https://coveralls.io/github/naturalis/trait-geo-diverse-angiosperms?branch=master)
[![Updates](https://pyup.io/repos/github/naturalis/trait-geo-diverse-angiosperms/shield.svg)](https://pyup.io/repos/github/naturalis/trait-geo-diverse-angiosperms/)

# sdmdl

An object-oriented python package for species distribution modelling using deep learning.
The package allows for a more intuitive and easy exploration of biodiversity patterns by 
modelling preferences for a great number of environmental variables. 

The functionality of this package and the estimates of environmental preferences it
obtains is demonstrated by way of three use cases:

* Domesticated crops and their wild progenitors
* Mycorrhizal associations
* Secondary woodiness

The project builds on the previous results obtained by:

- [MAXENT modelling](https://github.com/naturalis/trait-geo-diverse-ungulates) by Elke Hendrix.
- [Deep learning](https://github.com/naturalis/trait-geo-diverse-dl) by Mark Rademaker.

### Package layout

- [LICENSE](LICENSE) - the MIT license, which applies to this package
- [README.md](README.md) - the README file, which you are now reading
- [requirements.txt](requirements.txt) - prerequisites to install this package, used by pip
- [setup.py](setup.py) - installer script
- [data](data)/ - contains (some of) the data for the use cases
- [docs](docs)/ - contains project documentation files
- [script](script)/ - contains utility scripts
- [sdmdl](sdmdl)/ - the library code itself
- [tests](tests)/ - unit tests
