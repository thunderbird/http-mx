#!/usr/bin/perl
use strict;
use warnings FATAL => 'all';

use Net::DNS qw(mx);
use List::Util qw(min);
use HTTP::Date qw(time2str);
use HTTP::Status qw(:constants status_message);

use constant TIMEOUT => 10;

#Keep on one line to keep CPAN and friends happy
our $VERSION = "0.02";

my %headers = (
               'Content-type'  => 'text/plain',
               'Cache-Control' => 'public',
               'X-Powered-by'  => "DNS-MX/$VERSION",
              );

# Strip the initial '/' then let Net::DNS handle data validation
(my $domain = $ENV{PATH_INFO}) =~ s[^/][]g;

my @mx = lookup_mx($domain);

if (my $ttl = min map { $_->ttl } @mx) {
    $headers{'Cache-Control'} .= ", max-age=$ttl";
    $headers{'Expires'} = time2str(time + $ttl);
}

send_headers(\%headers);

# Sort MXes in preference order before alphabetical, so results for a given query are reproducible
foreach my $mx (sort { $a->preference <=> $b->preference || $a->exchange cmp $b->exchange } @mx) {
    print $mx->exchange, "\n";
}

sub send_headers {
    my $h = shift;
    foreach my $header (sort keys %$h) {
        print "$header: $h->{$header}\n";
    }
    print "\n";
}

sub lookup_mx {
    my $domain = shift;
    my @mx;
    my $status = HTTP_NOT_FOUND;
    
    eval {
    	local $SIG{ALRM} = sub { die "alarm\n" };
        alarm TIMEOUT;
        @mx = mx($domain);
	alarm 0;
    };
    
    if ($@ and $@ eq "alarm\n") {
	@mx = ();
	$status = HTTP_GATEWAY_TIMEOUT;
    }
    
    unless (@mx) {
        warn "No MX data for $domain";
	print "Status: $status " , status_message($status), "\r\n\r\n";
        print "No MX data for $domain\n";
        exit;
    }
    return @mx;
}
