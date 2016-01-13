#!/usr/bin/env python
#
# Copyright 2015
# Johannes K. Fichte, Vienna University of Technology, Austria
#
# gml2htd.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.  gml2htd.py is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public
# License along with gml2htd.py.  If not, see
# <http://www.gnu.org/licenses/>.
#
from os import path as os_path
import logging
import logging.config
logging.config.fileConfig('%s/logging.conf'%os_path.dirname(os_path.realpath(__file__)))

from itertools import imap, izip
import contextlib
import networkx as nx
import optparse
import sys

#import htd
import sys
sys.path.append('./')
import htd

def options():
    usage  = "usage: %prog [options] [files]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="out", type="string", help="Output file", default=None)
    opts, files = parser.parse_args(sys.argv[1:])
    if len(files)>1:
        raise ValueError('Supports at most one input file.')
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

def write_htdecomp(G,output):
    logging.warning('Creating hypergraph')
    h=htd.Hypergraph()
    num_edges=G.number_of_edges()
    symtab={x: y+1 for x,y in izip(G.nodes_iter(), xrange(G.number_of_nodes()))}
    logging.warning('Adding edges')
    for e,i in izip(G.edges_iter(),xrange(num_edges)):
        #print symtab[e[0]],symtab[e[1]]
        print symtab[e[0]],symtab[e[1]]
        h.add_edge(symtab[e[0]],symtab[e[1]])
        #print edge list
        #print 'e(%s,%s).' %(symtab[e[0]],symtab[e[1]])

    logging.warning('Determine tree decomposition')
    ordering = htd.MinFillOrdering()
    be_decomp = htd.TDecompBE(ordering)
    decomp=be_decomp.decompose(h)
    size = []
    for v in decomp.vertices():
        size.append(len(decomp.bag_content(v)))
        #print decomp.bag_content(v)
    #print size
    print 'treewidth=', max(size)
    #print size
    #L = {s:0 for s in size}
    #print '='*80
    #for s in size:
    #    print s, ", ",
    #    L[s]+=1 
    #print L

def parse_and_run(filename,output):
    logging.info('Reading gml file...')
    G=nx.read_gml(filename)
    logging.info('Reading done')
    logging.info('Exporting Graph to htdecomp format')
    write_htdecomp(G,output)

if __name__ == '__main__':
    opts,filename=options()
    s=None
    with selective_output(opts.out) as s:
        parse_and_run(filename,s)
    exit(1)
