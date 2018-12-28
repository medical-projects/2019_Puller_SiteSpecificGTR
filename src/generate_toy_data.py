import os, gzip, argparse, sys
import numpy as np
from Bio import Phylo, AlignIO

from treetime.treeanc import TreeAnc
from treetime.gtr_site_specific import GTR_site_specific
from treetime.gtr import GTR
from treetime.seqgen import SeqGen
from treetime.seq_utils import seq2prof, profile_maps

from betatree import betatree

from filenames import *
from estimation import get_mutation_count

def save_model(gtr_model, fname):
    np.savez(fname, pi=gtr_model.Pi, mu=gtr_model.mu, W=gtr_model.W, alphabet=gtr_model.alphabet)


def save_mutation_count(T, fname):
    n_ija,T_ia,root = get_mutation_count(T, T.gtr.alphabet)
    np.savez(fname, n_ija=n_ija, T_ia=T_ia, root_sequence=root)


def load_mutation_count(fname):
    d = np.load(fname)
    return d['n_ija'], d['T_ia'], d['root_sequence']


def load_model(fname):
    d = np.load(fname)
    return GTR_site_specific.custom(alphabet=d['alphabet'], mu=d['mu'], pi=d['pi'], W=d['W'])


def simplex(params, out_prefix = None, yule=True, n_model = 5, n_seqgen=5):
    from Bio import AlignIO
    # generate a model
    T = betatree(params['n'], alpha=2.0)
    T.yule=yule
    T.coalesce()
    if out_prefix:
        Phylo.write(T.BioTree, tree_name(out_prefix, params), 'newick')

    for mi in range(n_model):
        params['model']=mi
        myGTR = GTR_site_specific.random(L=params['L'], alphabet='nuc_nogap')
        myGTR.mu*=params['m']
        if out_prefix:
            save_model(myGTR, model_name(out_prefix, params))

        for si in range(n_seqgen):
            params['seqgen']=si
            # generate sequences
            mySeq = SeqGen(gtr=myGTR, tree=T.BioTree)
            mySeq.evolve()

            if out_prefix:
                save_mutation_count(mySeq, mutation_count_name(out_prefix, params))
                with gzip.open(alignment_name(out_prefix, params), 'wt') as fh:
                    AlignIO.write(mySeq.get_aln(), fh, 'fasta')
                reconstruct_tree(out_prefix, params)


def reconstruct_tree(prefix, params):
    #call = ['iqtree', '-s', alignment_name(prefix, params), '-st', 'DNA', '-nt', '2', '-m', 'JC']
    fname =  alignment_name(prefix, params)
    call = ['gunzip -c' ,fname, '|', 'fasttree', '-nt', '>', reconstructed_tree_name(prefix, params)]
    os.system(' '.join(call))


if __name__ == '__main__':
    L=300

    prefix = '2018-12-17_simulated_data'
    if not os.path.isdir(prefix):
        os.mkdir(prefix)

    for n in [1000]:
        for mu in [0.25, 0.35, 0.5]: #[0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.35, 0.5]:
            for ti in range(3):
                params = {'L':L, 'n':n, 'm':mu, 'tree':ti}
                simplex(params, out_prefix=prefix, n_model=3, n_seqgen=3, yule=True)

