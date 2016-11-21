#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = ( "commit.pl",
 	      "fluentd/fluent.conf",
	      "ns-manager/routes/ns_provisioning.rb",
 	      "ns-provisioning/main.rb",
	      "ns-provisioning/routes/ns.rb",
	      "ns-provisioning/helpers/ns.rb",
	      "vnf-provisioning/routes/vnf.rb",
	      "vnf-provisioning/Gemfile",
	      "vnf-provisioning/config/config.yml",
	      "vnf-provisioning/models/init.rb",
	      "vnf-provisioning/models/cachedimg.rb",
	      "vnf-provisioning/README.md",
	      "ns-provisioning/README.md"
	    );

map { system("git add $_\n"); } @files;

system("git commit -m '$name'\n");
