# Makefile for source rpm: e2fsprogs
# $Id$
NAME := e2fsprogs
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
