#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = ( "commit.pl",
	      "hot-generator/helpers/hot.rb",
	      "hot-generator/models/neutron/router.rb",
	      "hot-generator/routes/hot.rb",
	      "ns-provisioning/helpers/ns.rb",
	      "ns-provisioning/helpers/vim.rb",
 	      "vnfd-validator/assets/schemas/*",
	      "ns-manager/helpers/*.rb",
	      "ns-manager/routes/*.rb",
	      "ns-manager/*.rb",
	      "ns-provisioning/helpers/*.rb",
	      "ns-provisioning/routes/*.rb",
	      "ns-provisioning/*.rb",
	      "vnf-provisioning/helpers/*.rb",
	      "vnf-provisioning/routes/*.rb",
	      "vnf-provisioning/models/*.rb",
	      "vnf-provisioning/Gemfile",
	      "vnf-provisioning/*.rb",
	      "vnf-provisioning/README.md",
	      "ns-provisioning/README.md"
	    );

map { system("git add $_\n"); } @files;

system("git commit -m '$name'\n");
