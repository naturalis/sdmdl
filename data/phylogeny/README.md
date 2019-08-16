# Obtaining an optimal set of taxa

## What is the problem we're facing?

The complete SDM-DL workflow is *costly*, specifically the following steps:

1. **Fetching occurrence data sets from GBIF**. In the special case of the Ungulates
   (i.e. Artiodactyla+Perissodactyla) it was possible to fetch the entire higher
   taxon - something that GBIF facilitates - and then filter the occurrences
   locally. This is not feasible for the plants because it would be a dataset 
   that is about 1000x larger. Hence, we have to fetch the occurrences per 
   selected species through GBIF's programmable API. 
2. **Cleaning the occurrences**. Even with the rather good CoordinateCleaner package
   this still takes some time. Hundres of species, or a thousand, is doable in 
   reasonable time. Above that becomes dicy.
3. **Doing the actual DL**. Training the models takes a long time and a lot of CPU
   (or GPU). Again, this ought to be doable for up to a thousand species but it
   looks difficulat to scale beyond that.

## How can we limit this problem?

We have three use cases:

1. Switches between mycorrhizal assocation, which we assume to be connected to
   shifts in niche dimensions.
2. Switches between forms of woodiness, which we assume to be adaptations to
   certain environmental conditions.
3. Preadaptations of staple crops, which we assume to be related at least in
   part to climate.
   
For each of these we have states that we are interested in (e.g. secondarily
woody, or domesticated) and 'background' states. We expect identifiable differences 
in certain niche dimensions between those (spoiler alert: to be identified using
AIC variable selection and then modelled under phyloglm on the tree of Smith
& Brown) but to detect these we need sufficient numbers of shifts between
the interesting foreground state and the background state. It would be 
opportunistic of the foreground taxa for one use case could be the background
taxa for another use case so that we limit the problem described above. This means
coming up with some optimal intersection between taxon sets for the different
use cases.

## What might be the approach?

1. Reconcile the different data sets with a common taxonomy/phylogeny. The backbone
   we've selected for this is the ALLMB phylogeny (v0.1) by Smith & Brown. This is
   a tree whose backbone constraint is the tree from Magallon et al., enriched with
   sequence data from GenBank. This tree has branch lengths that are supposedly
   proportional to time (the root is 325,050,492 MYA, which is 325,048,473 years 
   before Christ). The tips are labelled using the NCBI taxonomy. We thus match against
   this using i) literal string matches, ii) substring matches (sometimes only a
   sequence for a subspecies is deposited while other data sets have the species),
   iii) fuzzy and synonym matches via the Entrez web service. This results in two
   SQLite databases:
   - **ALLMB.db**, which is the Smith and Brown tree, indexed for somewhat fast 
     traversal and pruning using 
     [Bio::Phylo::Forest::DBTree](https://metacpan.org/pod/Bio::Phylo::Forest::DBTree)
   - **taxa.db**, which is like a giant character state matrix where one column
     maps back to the tips in ALLMB.db and others contain information about the
     taxonomic name reconciliations (i.e. the name variants as we encounter them in 
     the various data sources) and the data themselves, i.e.:
     - data on derived woodiness vetted by Lens and general woodiness and habit from TRY
     - data on mycorrhizal associations from data sets by Steidinger et al., Werner
       et al. and Maherali et al.
     - data on major crop species from SCCS
2. Take the intersection between the taxon sets, identify the taxa that are 'redundant'
   in the sense that they participate in a clade with other taxa that have the same
   combination of states, and from these select the one with the most occurrences.
   All this is easier said than done because the switches that are relevant for the
   different use cases happen at different taxonomic depths. For now the approach is
   going to be to do some data exploration to see how well the overlap pans out, whether
   the generic filtering approach introduces serious biases or whether specific clades
   (e.g. families) jump out as of special interest.

### So what is in this directory?

- [data](data)/ contains input data in tab-separated format, for ingestion in the taxa.db
  database
- [script](script)/ contains utility scripts to do the ingestion
- [lib](lib)/ a simple object-relational mapping between the schema of taxa.db and
  the Perl programming language, generated using 
  [DBIx::Class](https://metacpan.org/pod/DBIx::Class)
