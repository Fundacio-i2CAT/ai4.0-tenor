#!/usr/bin/perl

use strict;

use LWP::UserAgent;
use HTTP::Request;
use JSON::Parse 'parse_json';;

my $ua = LWP::UserAgent->new;
my $server = shift @ARGV || die "\nLack of orchestrator\n\n";

die "NOOO" if $server =~ m/dev/gi;

print "Cleaning $server\n";

my $url = "http://$server:8082/orchestrator/api/v0.1/service/instance";

my $req = HTTP::Request->new("GET",$url);
my $res = $ua->request($req);

die "\nOrchestrator unreacheable\n" unless ( $res->is_success );

my $instances = parse_json($res->decoded_content);

foreach my $instance ( @{$instances} ) {
  my $delete = HTTP::Request->new("DELETE","$url/" . $instance->{"service_instance_id"});
  my $resp = $ua->request($delete);
  if ( $resp->is_success ) {
    print "Successfully deleted:\t";
    print $instance->{"service_instance_id"} . "\t";
    print $instance->{"state"} . "\n";
  } else {
    print "Problems with $instance->{service_instance_id}\n";
  }
}
