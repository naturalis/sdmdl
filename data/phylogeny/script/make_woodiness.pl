#!/usr/bin/perl
use strict;
use warnings;
use DBI;
use My::Taxon;
use Getopt::Long;
use Bio::Phylo::Util::Logger ':simple';
use constant { HERB => 'non-woody', TREE => 'ancestral', SECONDARY => 'derived' };

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
my $rs = $db->search({ '-or' => [
	'lens_name' => \'IS NOT NULL', 
	'woodiness' => \'IS NOT NULL', 
]});

# iterate over taxa
my $i = 1;
my $total = $rs->count;
while( my $taxon = $rs->next ) {
	my $sw_state;
	my $woodiness = $taxon->woodiness;
	my $form = $taxon->plant_growth_form;
	
	# if it's been assessed by Lens, we conclude 'derived'
	if ( $taxon->lens_name ) {
		$sw_state = SECONDARY;
	}
	
	# unambiguous 'non-woody' is only applied to herbs and grasses
	elsif ( $woodiness eq 'non-woody' ) {
		$sw_state = HERB;
	}
	
	# lump woodiness
	elsif ( $woodiness eq 'woody' ) {
		if ( not defined $form or $form =~ /^(?:tree|shrub|shrub\/tree)$/ ) {
			$sw_state = TREE;
		}
		else {
			$sw_state = HERB;
		}
	}
	
	# most difficult category
	elsif ( $woodiness eq 'non-woody/woody' ) {
		if ( defined $form and $form eq 'herb/shrub' ) {
			$sw_state = HERB;
		}
		
		# other combinations exist but in very small numbers:
		# 1. plant_growth_form = 'herb/shrub/tree' (2 records)
		# 2. plant_growth_form = NULL (3 records)
		# 3. plant_growth_form = 'shrub' (1 record)
		# ...which we will ignore here
	}
	
	# update the record
	if ( $sw_state ) {
		$taxon->update({ 'woody_state' => $sw_state });
		my $name = $taxon->allmb_name;
		INFO "updated $i/$total ($name = $sw_state)";
		$i++;
	}
}

