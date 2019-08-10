#!/usr/bin/perl
use strict;
use warnings;
use DBI;
use Getopt::Long;
use Data::Dumper;
use Bio::DB::Taxonomy;
use Bio::Phylo::Util::Logger ':simple';

# process command line arguments
my $db;
my $infile;
GetOptions(
	'db=s' => \$db,
	'in=s' => \$infile,
);

# make connections
my $dbh     = DBI->connect( "dbi:SQLite:dbname=$db", "", "" );
my $entrez  = Bio::DB::Taxonomy->new( '-source' => 'entrez' );
my $literal = 'select * from node where name = "%s"';
my $fuzzy   = 'select * from node where name like "%s%%"';

# iterate over lines
open my $fh, '<', $infile or die $!;
my $attempts = 1;
while(<$fh>) {
	chomp;
	my ( $input, $matched ) = split /\t/, $_;
	if ( ( $attempts % 400 ) == 0 ) {
		WARN "NEED TO SLEEP A BIT";
		sleep(10);
	}
	
	# continue to next record
	if ( $matched ) {
		DEBUG "Already have $input => $matched";
		print "$input\t$matched\n";
		next;
	}
	
	# fetch canonical from NCBI
	$input =~ s/_/ /g;
	INFO "Going to query Entrez for $input";
	if ( my $taxonid = $entrez->get_taxonid($input) ) {
		$attempts++;
		$input =~ s/ /_/g;
		
		# check if not 'No hit'
		if ( $taxonid eq 'No hit' ) {
			WARN "Entrez for $input: $taxonid";	
		}
	
		else {	
			# look up canonical name
			my $taxon = $entrez->get_taxon( '-taxonid' => $taxonid );
			my $canonical = $taxon->scientific_name;
			$canonical =~ s/ /_/g;
		
			# check if literally in local DB
			my $sth = $dbh->prepare(sprintf($literal,$canonical));
			$sth->execute();
			my $row = $sth->fetchrow_hashref;
			if ( $row ) {
				ERROR "Found literal match $input => $canonical";
				print "$input\t$canonical\n";
				next;
			}
			else {
				WARN "No literal match $input => $canonical";
			}

			# check if fuzzily in local DB
			$sth = $dbh->prepare(sprintf($fuzzy,$canonical));
			$sth->execute();
			my $matches = 0;
			while ( my $row = $sth->fetchrow_hashref ) {
				my $subsp = $row->{name};
				ERROR "Found fuzzy match $input => $subsp";
				print "$input\t$subsp\n";
				$matches++;
			}
			if ( $matches ) {
				next;				
			}
			else {
				WARN "No fuzzy matches for $input";
			}
		}
	}
	WARN "No success for $input";
	print "$input\t\n";
}