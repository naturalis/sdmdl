use utf8;
package My::Taxon::Result::Taxon;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

My::Taxon::Result::Taxon

=cut

use strict;
use warnings;

use base 'DBIx::Class::Core';

=head1 TABLE: C<taxon>

=cut

__PACKAGE__->table("taxon");

=head1 ACCESSORS

=head2 taxon_id

  data_type: 'integer'
  is_auto_increment: 1
  is_nullable: 0

=head2 ncbi_name

  data_type: 'text'
  is_nullable: 1

=head2 myco_name

  data_type: 'text'
  is_nullable: 1

=head2 lens_name

  data_type: 'text'
  is_nullable: 1

=head2 gbif_name

  data_type: 'text'
  is_nullable: 1

=head2 is_domesticated

  data_type: 'boolean'
  is_nullable: 1

=head2 has_ascomycota

  data_type: 'boolean'
  is_nullable: 1

=head2 has_basidiomycota

  data_type: 'boolean'
  is_nullable: 1

=head2 has_glomeromycotina

  data_type: 'boolean'
  is_nullable: 1

=head2 has_mucoromycotina

  data_type: 'boolean'
  is_nullable: 1

=head2 has_mycorrhiza

  data_type: 'boolean'
  is_nullable: 1

=head2 is_sw

  data_type: 'boolean'
  is_nullable: 1

=head2 habit

  data_type: 'text'
  is_nullable: 1

=head2 distribution

  data_type: 'text'
  is_nullable: 1

=head2 island_occurrence

  data_type: 'boolean'
  is_nullable: 1

=head2 island_endemic

  data_type: 'boolean'
  is_nullable: 1

=head2 num_occurrences

  data_type: 'integer'
  is_nullable: 1

=head2 gbif_species_key

  data_type: 'integer'
  is_nullable: 1

=head2 is_gbif_tnrs

  data_type: 'integer'
  is_nullable: 1
  
=cut

__PACKAGE__->add_columns(
  "taxon_id",
  { data_type => "integer", is_auto_increment => 1, is_nullable => 0 },
  "ncbi_name",
  { data_type => "text", is_nullable => 1 },
  "myco_name",
  { data_type => "text", is_nullable => 1 },
  "lens_name",
  { data_type => "text", is_nullable => 1 },
  "gbif_name",
  { data_type => "text", is_nullable => 1 },
  "is_domesticated",
  { data_type => "boolean", is_nullable => 1 },
  "has_ascomycota",
  { data_type => "boolean", is_nullable => 1 },
  "has_basidiomycota",
  { data_type => "boolean", is_nullable => 1 },
  "has_glomeromycotina",
  { data_type => "boolean", is_nullable => 1 },
  "has_mucoromycotina",
  { data_type => "boolean", is_nullable => 1 },
  "has_mycorrhiza",
  { data_type => "boolean", is_nullable => 1 },
  "is_sw",
  { data_type => "boolean", is_nullable => 1 },
  "habit",
  { data_type => "text", is_nullable => 1 },
  "distribution",
  { data_type => "text", is_nullable => 1 },
  "island_occurrence",
  { data_type => "boolean", is_nullable => 1 },
  "island_endemic",
  { data_type => "boolean", is_nullable => 1 },
  "num_occurrences",
  { data_type => "integer", is_nullable => 1 },
  "gbif_species_key",
  { data_type => "integer", is_nullable => 1 },
  "is_gbif_tnrs",
  { data_type => "integer", is_nullable => 1 },  
);

=head1 PRIMARY KEY

=over 4

=item * L</taxon_id>

=back

=cut

__PACKAGE__->set_primary_key("taxon_id");


# Created by DBIx::Class::Schema::Loader v0.07049 @ 2019-08-06 12:43:00
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:w/1s9SjFQewI7qELaMdpvQ


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;
