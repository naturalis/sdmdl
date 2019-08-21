Code review
===========

Probleem: hard coderen van paden op veel locaties
-------------------------------------------------

Op heel veel plekken los van elkaar worden dezelfde paden hard gecodeerd in de code.
(Voorbeeld: `/data/GIS/layers/...` komt heel vaak terug in de code). Dat is een probleem 
omdat we hierdoor vanaf nu getrouwd zijn met bepaalde locaties die vrijwel niet meer te 
wijzigen zijn. Wat als ik mijn mapje `gis` in plaats van `GIS` wil noemen?

Niet alleen is dat een probleem voor onszelf, maar nog veel erger voor eventuele 
gebruikers (=Wouter), die hun TIF layers op exact de juiste (niet-gedocumenteerde) plek, 
met de juiste naam, in een specifieke nesting moeten zetten. Dat gaat ze nooit lukken.

Hard gecodeerde paden en duplicatie zijn een symptoom van een fragiel, moeilijk te 
onderhouden ontwerp: http://wiki.c2.com/?OnceAndOnlyOnce

Een iets betere optie zou zijn dat zo'n pad maximaal op **een** plek staat, namelijk 
binnen de code van een configuratie-object (of andere abstractie) die paden beheert. De 
kennis over de paden is dan geconcentreerd op een plek en hoeft dus alleen daar aangepast 
te worden. Nog beter is als die kennis op **nul** plekken in de code staat, en volledig 
afhankelijk is van een configuratiebestand.

Hier zijn voorbeelden van het probleem:
https://github.com/naturalis/sdmdl/search?l=Python&q=%27%2Fdata%2FGIS%2F%27
https://github.com/naturalis/sdmdl/blob/master/script/python/train.py#L3

Gerelateerd hier aan is ook het probleem dat hard gecodeerd getest wordt op `.tif`, 
terwijl de bestands-extensie in werkelijkheid niet case sensitive hoeft te zijn (dus 
`.TIF` is ook een valide naam), en zelfs ook iets anders zou kunnen zijn (nl. `.tiff` of 
`.TIFF`).

**Oplossing**: paden laten beheren via een configuratie abstractie

Probleem: te lange methods
--------------------------

Elke method (of functie) moet ongeveer een scherm vol zijn: ±40 regels. Als dat onmogelijk
lijkt dan probeert de method dus te veel te doen en moet opgesplitst worden:
http://wiki.c2.com/?LongMethodSmell

**Oplossing**: methods opsplitsen

Probleem: hard gecodeerde dictionary keys
-----------------------------------------

Op een aantal plekken in de code zijn kolomnamen van de DarwinCore archives hard 
gecodeerd, en laten dan een mix zien van CamelCase en underscore_case. Dit is een 
probleem omdat we hierdoor getrouwd zijn met hele specifieke (en custom) structuren
voor onze data. Als Wouter met de data van observation.org aan de slag wil dan heeft
hij vast andere namen voor de kolommen. Wat er moet gebeuren is dat er een Occurrence
class is (of iets dergelijks) die dit intern beheert zodat de rest van de code de 
specifieke details van de databestanden niet hoeft te weten. Als dan blijkt dat het in 
observation.org decimal_latitude in plaats van decimalLatitude us dan hoeft er maar op 
een plek iets aangepast te worden. Bijkomend voordeel is dat je zo ook geen typefouten 
in de code kan krijgen (bijvoorbeeld, per ongeluk data["decima1Latitude"]).

**Oplossing**: een aparte class voor DarwinCore records, idealiter als subclass van een
al bestande DarwinCore library

Probleem: niet (goed) testbare code
-----------------------------------

Een verzameling losse scripts is niet hetzelfde als een hebruikbare, testbare API. Het
moet mogelijk zijn om elk stukje van de code via een unit test te verifieren. Dat kan
eigenlijk alleen maar (of althans, op een veel meer voor de hand liggende manier) als
de code bestaat uit classes die door de unit test suite geimporteerd kunnen worden om
zo de functionaliteit van elke method te testen. Het doel is dat de coverage om en
nabij de 100% wordt.

**Oplossing**: toch echt wel een daadwerkelijke OO API. Het doel is om dus van de
huidige 0% coverage (https://coveralls.io/github/naturalis/trait-geo-diverse-angiosperms?branch=master)
tot een ruim voldoende/goed te komen

Probleem: geen goede documentatie van de methods
------------------------------------------------

Het moet zo zijn dat we uiteindelijk automatisch goede documentatie kunnen genereren
(bijvoorbeeld op readthedocs). 

Voorbeeld van goed gedocumenteerde code:
https://github.com/BelgianBiodiversityPlatform/python-dwca-reader/blob/master/dwca/read.py

Automatisch gegenereerde documentatie:
https://python-dwca-reader.readthedocs.io/en/latest/api.html

**Oplossing**: code zodanig documenteren dat het readthedocs knopje op groen komt te
staan: https://readthedocs.org/projects/sdmdl/

Probleem: hard gecodeerde 'magic numbers'
-----------------------------------------

Voorbeelden:
- random number seed ("42")
- aantal pseudo absences ("2000")
- parameters voor plots (palet e.d.)

**Oplossing**: moeten allemaal via de configuratie beheerd worden (met defaults)

Probleem: print() statements voor debugging
-------------------------------------------

**Oplossing**: vervangen door log4py

Suggesties voor de API
======================

Aan de collecties van scripts kan je in grote lijnen zien hoe de API er uit zou moeten
zien. De namen die ik hier hanteer dienen even als voorbeeldjes:

- **config** - een class die de configuratiebestanden (e.g. YAML) inleest en de waardes
  via methods beschikbaar maakt aan de rest. Is verantwoordelijk voor het aanleveren
  van defaults (dus niet via magic numbers elders in de code), het construeren van 
  locaties van invoer- en uitvoerbestanden.
- **model_trainer** - een class die de training van het model aanstuurt, d.w.z. de 
  input parameters vanuit de configuratie ophaalt en overdraagt aan keras, vervolgens
  de voortgang / het succes van de training evalueert, en het model kan opslaan
- **model_predictor** - gegeven een getraind model (eventueel in te lezen van een bestand)
  zorgt deze class dat er voorspellingen gedaan worden
- **gis_handler** - weet alles van het inlezen, croppen, rescalen, plotten, wegschrijven 
  van GIS data
- **occurrence_handler** - weet alles van het inlezen, filteren, converteren, wegschrijven 
  van DarwinCore (-achtige) data

