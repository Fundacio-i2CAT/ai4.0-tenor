#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = ( "commit.pl",
 	      "vnfd-validator/assets/schemas/*",
	      "ns-manager/helpers/*.rb",
	      "ns-manager/routes/*.rb",
	      "ns-manager/routes/ns_provisioning.rb",
	      "ns-provisioning/routes/ns.rb",
	      "ns-provisioning/helpers/ns.rb",
	      "vnf-provisioning/helpers/hot.rb",
	      "vnf-provisioning/helpers/vnf.rb",
	      "vnf-provisioning/routes/vnf.rb",
	      "vnf-provisioning/Gemfile",
	      "vnf-provisioning/main.rb",
	      "vnf-provisioning/models/init.rb",
	      "vnf-provisioning/models/cachedimg.rb",
	      "vnf-provisioning/README.md",
	      "ns-provisioning/README.md"
	    );

map { system("git add $_\n"); } @files;

system("git commit -m '$name'\n");
