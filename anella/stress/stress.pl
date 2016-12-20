#!/usr/bin/perl

use strict;
use HTTP::Request;
use JSON::Parse 'parse_json';;
use LWP::UserAgent;
use Time::HiRes qw(usleep nanosleep);

my $server = shift @ARGV || die "\nLack of server\n\n";
my $number = shift @ARGV || die "\nLack of number\n\n";

open(JSON,"vnfd.json");
my $vnfd = "";
map { $vnfd .= $_; } <JSON>;
close(JSON);

my $url = "http://$server:8082/orchestrator/api/v0.1/vnf";
my $req = HTTP::Request->new( 'POST', $url );
$req->header( 'Content-Type' => 'application/json' );
$req->content( $vnfd );

my $ua = LWP::UserAgent->new;
$number--;
my $fails = 0;
my $vnfFails = 0;
foreach my $i ( 0..$number ) {
  my $res = $ua->request($req);
  # usleep(1000*int(rand(1000)));
  if ( $res->status_line !~ m/\A200/gi ) {
    print $res->decoded_content;
    $vnfFails++;
  }
  my $data = parse_json($res->decoded_content);
  my $vnf_id = $data->{vnf_id};
  my $nsurl = "http://$server:8082/orchestrator/api/v0.1/ns";
  my $nsreq = HTTP::Request->new( 'POST', $nsurl );
  $nsreq->header( 'Content-Type' => 'application/json' );
  $nsreq->content( "{\"vnf_id\": $vnf_id, \"name\": \"stress\"}" );
  my $nsres = $ua->request($nsreq);
  if ( $nsres->status_line !~ m/\A200/gi ) {
    print $nsres->decoded_content;
    $fails++;
  }
  print "$vnf_id\n";
  my $perc = sprintf("%1.1f",100.0*$fails/$number);
  my $vnfPerc = sprintf("%1.1f",100.0*$vnfFails/$number);
  print "Fails til now:\t$perc %\t$vnfPerc %\n";;
}
