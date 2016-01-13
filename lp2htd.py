#!/usr/bin/env python
#
# Copyright 2015
# Johannes K. Fichte, Vienna University of Technology, Austria
#
# lp2htd.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.  lp2htd.py is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with lp2htd.py.  If not, see <http://www.gnu.org/licenses/>.
#
from os import path as os_path
import logging
import logging.config
logging.config.fileConfig('%s/logging.conf'%os_path.dirname(os_path.realpath(__file__)))

from itertools import imap, izip
import checksum
import contextlib
import hashlib
import networkx as nx
import optparse
from os import path as os_path
import select
import sys
import timeit


import htd


if select.select([sys.stdin,],[],[],0.0)[0]:
    logging.critical("Please use file input instead of stdin.")
    exit(1)

def options():
    usage  = "usage: %prog [options] [files]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="out", type="string", help="Output file", default=None)
    opts, files = parser.parse_args(sys.argv[1:])
    if len(files)>1:
        logging.critical('Supports at most one input file.')
        exit(1)
    return opts, files[0]


@contextlib.contextmanager
def selective_output(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout
    try:
        yield fh
    finally:
        if fh:
            fh.close()

def tab(x,h,symtab):
    if symtab.has_key(x):
        return symtab[x]
    else:
        h.add_vertex()
        symtab[x]=len(symtab)+1
        return symtab[x]

def parse_and_run(filename,output):
    output.write('folder,filename,checksum,num_vertices,num_edges,width,algorithm,ordering,runtime in s\n')
    logging.info('Creating checksum')
    file_checksum=checksum.hashfile(open(filename, 'rb'), hashlib.sha256())
    start = timeit.default_timer()
    h=htd.Hypergraph(0)
    logging.info('Reading lp file and creating hypergraph...')
    symtab={}
    with open(filename) as f:
        for line in f:
            if line.startswith('edge'):
                x,y=line[5:-3].split(',')
                h.add_edge(tab(x,h,symtab),tab(y,h,symtab))
    logging.info('Determining tree decomposition...')
    ordering = htd.MinFillOrdering()
    be_decomp = htd.TDecompBE(ordering)
    decomp=be_decomp.decompose(h)
    stop = timeit.default_timer()
    #for v in decomp.vertices():
    #    print decomp.bag_content(v)
    logging.info("width=%s", decomp.width())
    logging.info('Done')
    output.write('%s,%s,%s,%i, %i, %i,%s,%s,%f\n' %(os_path.dirname(filename), os_path.basename(filename), file_checksum, h.num_vertices(), h.num_edges(), decomp.width(), 'be', 'minfill', stop-start))
    output.flush()

if __name__ == '__main__':
    opts,filename=options()
    s=None
    with selective_output(opts.out) as s:
        parse_and_run(filename,s)
    exit(0)
