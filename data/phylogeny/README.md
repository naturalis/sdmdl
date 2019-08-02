This folder contains phylogenies for the comparative analysis of trait values
(domestication, woodiness, mycorrhiza) and niche dimensions. We currently have the
following trees:

[Tree.nex.bt.nex](Tree.nex.bt.nex)
----------------------------------

Phylogeny used in [Feijen et al.](http://doi.org/10.1038/s41598-018-28920-x). For this 
tree, the pattern of mycorrhizal association on all tips is known. 

The following domesticated taxa are in the tree:
- _Zea mays_ - no subspecies, i.e. ssp. _mexicana_ or ssp. _parviglumis_
- _Oryza sativa_, but no _O. rufipogon_ (could graft as sister)
- _Sorgum bicolor_ - no subspecies, i.e. ssp. _verticilliflorum_
- _Hordeum vulgare_, but no _H. spontaneum_ (could graft as sister)
- _Triticum aestivum_, but no _T. urartu_ or _T. turgidum_ (could graft as sisters)
- _Solanum tuberosum_, but no _S. bukasovii_ (could graft as sister)
- _Dioscorea rotundata_, but none of the other genus members
- _Musa acuminata_, but none of the other genus members
- _Fagopyrum esculentum_, but no ssp. _ancestrale_
- _Fagopyrum tataricum_, but no ssp. _potanini_
- _Arachis hypogaea_, but no _A. duranensis_, _A. ipaensis_
- _Mangifera indica_, but no _M. sylvatica_ (could graft as sister)

The following taxa are missing:
- _Eragrostis tef_, _Eragrostis pilosa_, **whole genus is missing**
- _Eleusine coracana_, _Eleusine africana_, **whole genus is missing**
- _Aegilops tauschii_, _Aegilops speltoides_, **whole genus is missing**
- _Secale cereale_, _Secale vavilovii_, **whole genus is missing**
- _Manihot esculenta_, _Manihot esculenta subsp. flabellifolia_, **whole genus is missing**
- _Ipomoea batatas_, _I. trifida_, but _Ipomoea pes caprae_ present (could graft)
- _Colocasia esculenta_, etc.: **whole genus is missing**
- _Ensete ventricosum_: **whole genus is missing**
- _Cucurbita pepo_, etc.: **whole genus is missing**
- _Artocarpus altilis_, etc.: **whole genus is missing**
- _Cocos nucifera_: **whole genus is missing**
- _Phoenix dactylifera_: **whole genus is missing**
- _Metroxylon sagu_: **whole genus is missing**

[PhytoPhylo.tre](PhytoPhylo.tre)
--------------------------------

Phylogeny used in [Qian & Yin, 2016](https://doi.org/10.1093/jpe/rtv047).

Trees from [Smith & Brown](https://doi.org/10.1002/ajb2.1019)
-------------------------------------------------------------

All these trees are from release [v0.1](https://github.com/FePhyFoFum/big_seed_plant_trees/releases/tag/v0.1)

- [ALLMB.tre](ALLMB.tre), 356,305 tips, GenBank and Open Tree of Life taxa with a 
  backbone provided by [Magallón et al. (2015)](https://doi.org/10.1111/nph.13264)
- [ALLOTB.tre](ALLOTB.tre), 353,185 tips, GenBank and Open Tree of Life taxa with a 
  backbone provided by Open Tree of Life version 9.1
- [GBMB.tre](GBMB.tre), 79,874 tips, GenBank taxa with a backbone provided by Magallón et 
  al. (2015)
- [GBOTB.tre](GBOTB.tre), 79,881 tips, GenBank taxa with a backbone provided by Open Tree 
  of Life version 9.1
- [ot_seedpruned_dated.tre](ot_seedpruned_dated.tre), The Open Tree synth release v 9.1 
  of seed plants with dates from Magallon 2015 and with non monophyletic major clades 
  removed.
- [mag2015_ot_dated.tre](mag2015_ot_dated.tre), The Magallon 2015 tree with additional 
  Open Tree taxonomy added

### Verification of [ALLMB.tre](ALLMB.tre)

Performed by indexing the tree file using `megatree-loader -i ALLMB.tre -d ALLMB.db -v`

The following domesticated taxa are in the tree:
- _Zea mays_, but no subspecies, i.e. ssp. _mexicana_ or ssp. _parviglumis_
- _Oryza sativa_ and _Oryza rufipogon_
- _Sorghum bicolor_ but not ssp. _verticilliflorum_
- _Eragrostis tef_ and _Eragrostis pilosa_
- _Eleusine coracana_ and _Eleusine africana_ (but as _Eleusine coracana subsp. africana_)
- _Hordeum vulgare_ and _Hordeum spontaneum_ (but as _Hordeum vulgare subsp. spontaneum_)
- _Triticum aestivum_, _Triticum urartu_, _Aegilops speltoides_, 
  _Triticum turgidum subsp. dicoccoides_ (but as _Triticum dicoccoides_), 
  _Aegilops tauschii_
- _Secale cereale_, _Secale vavilovii_
- _Manihot esculenta_, _Manihot esculenta subsp. flabellifolia_
- _Solanum tuberosum_ (as _Solanum tuberosum subsp. andigenum_), _Solanum bukasovii_
  (as _Solanum bukasovii f. multidissectum_)
- _Ipomoea batatas_, _Ipomoea trifida_
- _Colocasia esculenta_, _Colocasia lihengiae_, _Colocasia yunnanensis_, _Colocasia formosana_  
- _Dioscorea rotundata_ (as _Dioscorea cayennensis subsp. rotundata_), 
  _Dioscorea cayennensis_, _Dioscorea praehensilis_, _Dioscorea abyssinica_
  _Dioscorea minutiflora_, _Dioscorea alata_, _Dioscorea hamiltonii_, _Dioscorea persimilis_
  _Dioscorea polystachya_, _Dioscorea bulbifera_, _Dioscorea esculenta_, _Dioscorea dumetorum_
  _Dioscorea trifida_
- _Musa acuminata_ (in several subspecies), _Musa balbisiana_ (as _Musa balbisiana var. balbisiana_)
- _Ensete ventricosum_
- _Fagopyrum esculentum_ but not _Fagopyrum esculentum subsp. ancestrale_
- _Fagopyrum tataricum subsp. potanini_
- _Arachis hypogaea_ (in several cultivars), _Arachis duranensis_, _Arachis ipaensis_
- _Cucurbita argyrosperma_, _Cucurbita argyrosperma subsp. sororia_, _Cucurbita ficifolia_
  _Cucurbita maxima_, _Cucurbita maxima subsp. andreana_, _Cucurbita moschata_
  _Cucurbita pepo_, _Cucurbita pepo subsp. fraterna_
- _Artocarpus altilis_, _Artocarpus camansi_, _Artocarpus mariannensis_
- _Mangifera indica_, _Mangifera sylvatica_
- _Cocos nucifera_
- _Phoenix dactylifera_, _Phoenix sylvestris_
- _Metroxylon sagu_  
  
Missing:
- _Musa x paradisiaca_
- _Fagopyrum tataricum_  