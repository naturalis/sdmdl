#!/usr/bin/perl
use strict;
use warnings;
use My::Taxon;
use Getopt::Long;
use Text::CSV 'csv';
use Bio::Phylo::Util::Logger ':simple';

# process command line arguments
my $dbfile;
my $infile;
my $column;
my $verbosity = WARN;
GetOptions(
	'infile=s' => \$infile,
	'dbfile=s' => \$dbfile,
	'column=s' => \$column,
	'verbose+' => \$verbosity,
);	
	
# configure services
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity );
my $db  = My::Taxon->connect( $dbfile )->resultset( 'Taxon' );
my $tsv = csv( 'in' => $infile, 'sep' => "\t", 'headers' => 'auto');
my $n   = scalar( @{ $tsv } );

# iterate over TSV records
my $i = 1;
for my $in ( @{ $tsv } ) {

	# clean record by removing 'family' field
	delete $in->{'family'};
	my $name = $in->{$column};
	INFO "Processing $name (".$i++."/$n)";
	
	# find matching taxon in database
	my $taxon_rs = $db->search( { $column => $name } );
	while ( my $taxon = $taxon_rs->next ) {
	
		# check any existing fields and note a conflict if there's a mismatch
		KEY: for my $key ( keys %{ $in } ) {
			next KEY if $key eq $column;
			if ( $in->{$key} eq '' ) {
				delete $in->{$key};
				next KEY;
			}
			if ( defined( my $val = $taxon->$key ) ) {
				$in->{'has_myco_conflict'} = 1 if $val != $in->{$key};			
			}
		}
		WARN "Conflict for $name" if $in->{'has_myco_conflict'};
		$taxon->update($in);
	}
}
	
	