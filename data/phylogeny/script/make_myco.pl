#!/usr/bin/perl
use strict;
use warnings;
use My::Taxon;
use Getopt::Long;
use Bio::Phylo::Util::Logger ':simple';

# state mapping, will look up 0/1 coordinates from DB
my $state = [
	[ 'neither',    'ecto' ],
	[ 'arbuscular', 'both' ]
];

# process command line arguments
my $dbfile;
my $verbosity = WARN;
GetOptions(
	'dbfile=s' => \$dbfile,
	'verbose+' => \$verbosity,
);	
	
# configure services
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity );
my $db = My::Taxon->connect( $dbfile )->resultset( 'Taxon' );
my $rs = $db->search({
	'has_am'  => \'IS NOT NULL',
	'has_ecm' => \'IS NOT NULL',
	'has_myco_conflict' => \'IS NULL',
});

# iterate over records
while( my $taxon = $rs->next ) {
	my $am = $taxon->has_am;
	my $ec = $taxon->has_ecm;
	my $ms = $state->[$am]->[$ec];
	my $an = $taxon->allmb_name;
	$taxon->update({ 'myco_state' => $ms });
	INFO "$an: $ms";
}
