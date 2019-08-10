#!/usr/bin/perl
use strict;
use warnings;
use JSON;
use My::Taxon;
use Getopt::Long;
use Data::Dumper;
use LWP::UserAgent;
use Bio::Phylo::Util::Logger ':simple';

# URL templates for web service calls
my $base = 'http://api.gbif.org/v1/';
my $url_match = $base . 'species/match?name=%s';
my $url_data  = $base . 'occurrence/search?isGeoreferenced=true&speciesKey=%d';

# process command line arguments
my $db;
my $verbosity = WARN;
GetOptions(
	'db=s'     => \$db,
	'verbose+' => \$verbosity,
);

# instantiate/configure objects
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity );
my $tdb = My::Taxon->connect( $db );
my $sql = \'IS NULL';
my $trs = $tdb->resultset('Taxon')->search({ is_gbif_tnrs => $sql });
my $num = $trs->count;

# start iterating over records without species keys
my $count = 0;
TAXON: while( my $taxon = $trs->next ) {
	my $name = $taxon->ncbi_name;
	
	# log every 100 records
	if ( not ++$count % 100 ) {
		INFO "Processing $count/$num - $name";
	}	
	
	# skip non-identified specimens
	if ( $name =~ /^[A-Z][a-z]+_sp\._.+/ ) {
		DEBUG "Skipping unidentified specimen $name";
		next TAXON;
	}	
	
	# do taxon query, returns hashref or undef
	if ( my $res = do_query( sprintf( $url_match, $name ) ) ) {
		my $update = {
			'is_gbif_tnrs' => 1,
		};
	
		# check result - no speciesKey probably means only a genus match
		if ( my $key = $res->{'speciesKey'} ) {
			
			# we can update at least the GBIF name and speciesKey
			$update->{'gbif_name'} = $res->{'canonicalName'};
			$update->{'gbif_species_key'} = $key;
			
			# do occurrence query, returns hashref or undef
			if ( my $occ = do_query( sprintf( $url_data, $key ) ) ) {
			
				# count could be undef or 0; we want neither
				unless ( $update->{'num_occurrences'} = $occ->{'count'} ) {
					DEBUG "Occurrence count for $name: " . $update->{'num_occurrences'};
				}
			}
			else {
				ERROR "No occurrence query result for $name";
			}			
		}
		else {
			WARN "No species match for $name";
		}
		
		# update the taxon record
		$taxon->update($update);		
	}
	else {
		ERROR "No species query result for $name";
	}
}


# performs a generic HTTP/GET => JSON API call
sub do_query {
	my $url = shift;
	my $ua  = LWP::UserAgent->new;
	my $res = $ua->get($url);
	if ( $res->is_success ) {
		my $json = JSON->new;
		my $obj;
		eval { $obj = $json->decode( $res->decoded_content ) };
		if ( $@ ) {
			ERROR "Problem decoding JSON: $@";
			return undef;
		}
		else {
			return $obj;
		}
	}
	else {
		ERROR "Problem with $url\n" . $res->status_line;
		return undef;
	}
}