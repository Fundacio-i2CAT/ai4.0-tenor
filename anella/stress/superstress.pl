#!/usr/bin/perl

use strict;
use threads ('yield',
 	     'stack_size' => 64*4096,
 	     'exit' => 'threads_only',
 	     'stringify');

BEGIN { $| = 1 };

my $server = shift @ARGV || die "\nLack of server\n\n";
my $nthreads = shift @ARGV || die "\nLack of nthreads\n\n";
my $ntimes = shift @ARGV || die "\nLack of ntimes\n\n";

my @threads = ();

foreach my $thread ( 0..$ntimes ) {
  if ( scalar @threads < $nthreads ) {
    push(@threads,threads->create( sub { fire(); } ));
  } else {
    map { $_->join() } @threads;
    system("perl cleanvim.pl $server");
    @threads = ();
    push(@threads,threads->create( sub { fire(); } ));
  }
}

map { $_->join() } @threads;

sub fire {
  system("python orchestrator_tests.py");
}
