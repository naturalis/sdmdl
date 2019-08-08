use utf8;
use DBI;
package My::Taxon;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

use strict;
use warnings;

use base 'DBIx::Class::Schema';

__PACKAGE__->load_namespaces;
my ( $SINGLETON, $DBH );

sub connect {
	my $class = shift;
	my $file  = shift;
	if ( not $SINGLETON ) {
		
		# create if not exist
		if ( not -e $file ) {
			$class->create($file);
		}
	
		# fuck it, let's just hardcode it here - Yeehaw!
		my $dsn  = "dbi:SQLite:dbname=$file";
		$DBH = DBI->connect($dsn,'','');
		$DBH->{'RaiseError'} = 1;
		$SINGLETON = $class->SUPER::connect( sub { $DBH } );
	}
	return $SINGLETON;
}


# Created by DBIx::Class::Schema::Loader v0.07049 @ 2019-08-06 12:43:00
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:psodCSidgElRIT/3B1fDzw


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;
