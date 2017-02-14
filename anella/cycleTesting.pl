#!/usr/bin/perl

use strict;

while ( 1 ) {
  print "Testing ...\n";
  system("python orchestrator_tests.py");
  print "Sleeping ...\n";
  sleep(240);
  system("perl cleanvim.pl localhost");
  sleep(30);
}
