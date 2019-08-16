#!/usr/bin/perl
use strict;
use warnings;
use DBI;
use My::Taxon;
use Getopt::Long;
use Data::Dumper;
use Bio::DB::Taxonomy;
use Bio::Phylo::Util::Logger ':simple';

# Usage:
# $o -d <sqlite.db> -i <table.tsv> -c <col in tsv and db> \
# 	-u <actually do updates> \
# 	-m <check if myco data from new source matches existing record>
# 	-s <separator, e.g. _>
# 	-v [-v]

# process command line arguments
my $match;
my $dbfile;
my $infile;
my $column;
my $update;
my $sep = '_';
my $verbosity = WARN;
GetOptions(
	'sep=s'    => \$sep,
	'match'    => \$match,
	'update'   => \$update,
	'dbfile=s' => \$dbfile,
	'infile=s' => \$infile,
	'column=s' => \$column,
	'verbose+' => \$verbosity,
);

# make connections
Bio::Phylo::Util::Logger->VERBOSE( '-level' => $verbosity );
my $db = My::Taxon->connect( $dbfile )->resultset( 'Taxon' );
my $entrez = Bio::DB::Taxonomy->new( '-source' => 'entrez' );

# iterate over lines
open my $fh, '<', $infile or die $!;
my $attempts = 1;
my @header;
NAME: while(<$fh>) {
	
	# preprocess records into hashes
	chomp;
	my @line = split /\t/, $_;
	if ( not @header ) {
		@header = @line;
		next NAME;
	}
	my %record = map { $header[$_] => $line[$_] } 0 .. $#header;
	delete $record{'family'}; # XXX is not in database, so we delete it here for the ORM
	for my $k ( keys %record ) {
	
		# don't match or insert NULL records
		delete $record{$k} if not defined $record{$k} or $record{$k} eq '';
	}	
	
	# the input that has the taxon name
	my $input = $record{$column};
	
	# XXX skip existing
	if ( $db->search({ $column => $input })->single ) {
		print "already done $input\n";
		next NAME;
	}
	
	# need to go easy on Entrez API: sleep 10 seconds every 400 queries
	if ( ( $attempts % 400 ) == 0 ) {
		WARN "NEED TO SLEEP A BIT";
		sleep(10);
	}
	
	# check if literally in local DB
	my $sanitized = $input;
	$sanitized =~ s/\Q$sep\A/_/g; # local DB has underscores	
	next NAME if db_check($sanitized, \%record);	
	
	# fetch canonical from NCBI
	$input =~ s/\Q$sep\A/ /g; # NCBI has spaces
	INFO "Going to query Entrez for $input";
	my $taxonid;
	eval { $taxonid = $entrez->get_taxonid($input) };
	if ( $@ ) {
		ERROR "Couldn't Entrez query $input: $@";
		next NAME;
	}	
	if ( $taxonid ) {
		$attempts++;
		$input =~ s/ /$sep/g;
		
		# check if not 'No hit'
		if ( $taxonid eq 'No hit' ) {
			WARN "Entrez for $input: $taxonid";	
			next NAME;
		}
	
		# look up canonical name
		my $taxon;
		eval { $taxon = $entrez->get_taxon( '-taxonid' => $taxonid ) };
		if ( $@ ) {
			ERROR "Couldn't Entrez fetch $taxonid: $@";
			next NAME;
		}
		my $canonical = $taxon->scientific_name;
		$canonical =~ s/ /_/g;
		WARN "No match for Entrez TNRS $input => $canonical" unless db_check($canonical, \%record);		
	}
}

sub db_check {
	my ( $name, $record ) = @_;
	if ( my $allmb = $db->search({ 'allmb_name' => $name })->single ) {
		INFO "Found literal match $name";
		match( $record, $allmb, $name ) if $match;
		$allmb->update($record) if $update;		
		return 1;
	}

	# check if fuzzily in local DB
	my $matches = 0;
	my $allmb = $db->search({ 'allmb_name' => { '-like' => $name.'%' } });
	while ( my $fuzzy = $allmb->next ) {
		my $subsp = $fuzzy->allmb_name;
		INFO "Found fuzzy match $name => $subsp";
		match( $record, $fuzzy, $subsp ) if $match;
		$fuzzy->update($record) if $update;		
		$matches++;
	}
	return $matches;
}

sub match {
	my ( $update, $record, $name ) = @_;
	my @keys = grep { $_ ne $column } keys %$update;
	for my $k ( @keys ) {
		next unless defined $update->{$k};
		my ( $new, $old ) = ( $update->{$k}, $record->$k );
		next unless defined $old;
		next if "$new" eq "$old";
		ERROR "mismatch in ${name}.${k}: $new != $old (new, old)";
		return 0;
	}
	return 1;
}