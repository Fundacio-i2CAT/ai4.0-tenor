#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = (
	     "Gemfile",
	     "./anella/Vagrantfile",
	     "./anella/dcs.json",
	     "./anella/chunkUploader/repoServer.py",
	     "./anella/chunkUploader/send.pl",
	     "./anella/chunkUploader/requirements.txt",
	     "./anella/chunkUploader/static/index.html",
	     "./anella/chunkUploader/static/*.js",
	     "./anella/aux/shtemplating.sh",
	     "./anella/config.cfg",
	     "./anella/.gitignore",
	     "./anella/orchestrator_tests.py",
	     "./anella/commit.pl",
	     "./anella/tenor_client/README.md",
	     "./anella/tenor_client/*.py",
	     "./anella/start.py",
	     "./anella/requirements.txt",
	     "./anella/tenor_client/samples/*.json",
	     "./anella/tenor_client/samples/*.md",
	     "./anella/tenor_client/templates/*.json",
	     "./anella/tenor_client/templates/*.md",
	     "./anella/README.md",
 	     "commit.pl",
	     "invoker.ini",
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
