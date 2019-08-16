#!/usr/bin/perl
use strict;
use warnings;
use My::Taxon;
use Getopt::Long;
use Bio::Phylo::Forest::DBTree;
use Bio::Phylo::Util::Logger ':simple';

# process command line arguments
my $datafile;
my $treefile;
my $column;
my $verbosity = WARN;
GetOptions(
	'datafile=s' => \$datafile,
	'treefile=s' => \$treefile,
	'column=s'   => \$column,
	'verbose+'   => \$verbosity,
);
	
# setup services
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity, '-class' => 'main' );
my $data = My::Taxon->connect( $datafile )->resultset( 'Taxon' );
my $tree = Bio::Phylo::Forest::DBTree->connect( $treefile);
my $root = $tree->get_root;
my $n = $data->search( { $column => \'IS NOT NULL' } )->count;

# we have to do two passes, first postorder to label the nodes:
INFO "Attaching states to $n nodes by postorder traversal";
my $i = 1;
$root->visit_depth_first(
	'-post' => sub {
		my $node = shift;
		
		# here we just label the tips
		if ( $node->is_terminal ) {
			my $id = $node->get_id;
			my $rs = $data->search( { 'allmb_id' => $id } );
			while( my $r = $rs->next ) {
				if ( my $state = $r->$column ) {
					$node->set_generic( $column => { $state => [$r] } );
					DEBUG "Attached $column => $state to tip $i/$n";
					$i++;
				}
			}
		}
		
		# here we merge the tip states
		else {
			my %state;
			for my $child ( @{ $node->get_children } ) {
				if ( my $cache = $child->get_generic($column) ) {
					for my $key ( keys %$cache ) {
						$state{$key} = [] if not $state{$key};
						push @{ $state{$key} }, @{ $cache->{$key} };
					}
				}
			}
			$node->set_generic( $column => \%state );
		}
	}
);

# second we do a pre-order traversal to fetch the earliest monotypic node
INFO "Going to find synapomorphy exemplars by pre-order traversal";
my @header = ( qw(allmb_name gbif_species_key num_occurrences), $column );
print join("\t",@header), "\n";
$root->visit_depth_first(
	'-pre' => sub {
		my $node = shift;
		
		# check if node is annotated: might not be if none of the subtended tips had data
		if ( my $cache = $node->get_generic($column) ) {
		
			# if there is only one key the subtended clade is monotypic
			if ( scalar(keys(%$cache)) == 1 ) {
				DEBUG "Found monotypic internal node";
				
				# sort by num occurrences (desc) using Schwartzian transform
				my ($tips) = values %$cache;
				my ($most_occurrences) = map { $_->[1] } 
				                        sort { $b->[0] <=> $a->[0] }
				                         map { [ $_->num_occurrences || 0, $_ ] } @$tips;
				my @values = map { $most_occurrences->$_ } @header;
				print join("\t",@values), "\n";
				
				# unset all the descendents
				my $desc_rs = $node->get_descendants_rs;
				while( my $desc = $desc_rs->next ) {
					$desc->set_generic( $column => undef );
				}
			}
		}
	}
);
	



