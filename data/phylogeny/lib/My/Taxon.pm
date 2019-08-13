use utf8;
package My::Taxon;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

use strict;
use warnings;

use base 'DBIx::Class::Schema';

__PACKAGE__->load_namespaces;


# Created by DBIx::Class::Schema::Loader v0.07049 @ 2019-08-13 10:52:51
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:7S7h1kbCHFRQTjpBvzY1tA


# Helper function to create a SQLite handle to the input file and wrap
# that inside the object-relational mapping classes.
use DBI;
my ( $SINGLETON, $DBH );
sub connect {
	my $class = shift;
	my $file  = shift;
	if ( not $SINGLETON ) {
		my $dsn  = "dbi:SQLite:dbname=$file";
		$DBH = DBI->connect($dsn,'','');
		$DBH->{'RaiseError'} = 1;
		$SINGLETON = $class->SUPER::connect( sub { $DBH } );
	}
	return $SINGLETON;
}

1;
