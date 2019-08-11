#!/usr/bin/perl
use strict;
use warnings;
use JSON;
use My::Taxon;
use Getopt::Long;
use LWP::UserAgent;
use Text::CSV 'csv';
use Bio::Phylo::Util::Logger ':simple';

# URL templates for web service calls
my $base = 'http://api.gbif.org/v1/';
my $url_match = $base . 'species/match?name=%s';
my $url_data  = $base . 'occurrence/search?isGeoreferenced=true&speciesKey=%d';

# process command line arguments
my $verbosity = WARN;
my $dbfile;
my $infile;
GetOptions(
	'verbose+' => \$verbosity,
	'dbfile=s' => \$dbfile,
	'infile=s' => \$infile,
);

# instantiate/configure objects
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity );
my $db = My::Taxon->connect( $dbfile )->resultset( 'Taxon' );

# start reading file
for my $r ( @{ csv( 'in' => $infile, 'headers' => 'auto', 'sep_char' => "\t" ) } ) {

	# check if name exists
	my $name = $r->{allmb_name};
	if ( my $taxon = $db->search({ allmb_name => $name })->single ) {
		INFO "Have literal match for $name";
		$taxon->update({ domestication => $r->{domestication} });
	}
	else {
		WARN "No literal match for $name";
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