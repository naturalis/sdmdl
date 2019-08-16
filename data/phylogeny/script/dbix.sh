#!/bin/bash
perl -MDBIx::Class::Schema::Loader=make_schema_at,dump_to_dir:./lib -e 'make_schema_at("My::Taxon", { debug => 1 }, [ "dbi:SQLite:dbname=/Users/rutger.vos/Dropbox/documents/projects/dropbox-projects/trait-geo-diverse-angiosperms/sqlite/taxa.db","sqlite" ])'

