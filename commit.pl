#!/usr/bin/perl

use strict;

my $name = shift @ARGV || die "\nLack of commit name\n\n";

map { $name .= " $_"; } @ARGV;

my @files = (
	     ".gitignore",
	     "Gemfile",
	     "./anella/stress/vnfd.json",
	     "./anella/stress/stress.pl",
	     "./anella/stress/superstress.pl",
	     "./anella/cleanvim.pl",
	     "./anella/Vagrantfile",
	     "./anella/dcs.json",
	     "./anella/aux/wsockets/templates/own.html",
	     "./anella/aux/wsockets/static/index.html",
	     "./anella/aux/wsockets/static/ws.js",
	     "./anella/aux/wsockets/ioServer.py",
	     "./anella/aux/wsockets/requirements.txt",
	     "./anella/aux/chunkUploader/repoServer.py",
	     "./anella/aux/chunkUploader/send.pl",
	     "./anella/aux/chunkUploader/requirements.txt",
	     "./anella/aux/chunkUploader/static/index.html",
	     "./anella/aux/chunkUploader/static/*.js",
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
	     "ns-catalogue/routes/*.rb",
	     "vnf-catalogue/routes/*.rb",
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
