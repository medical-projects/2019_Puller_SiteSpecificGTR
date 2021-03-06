import os, glob
from datetime import date
from math import ceil

def make_chunks(d, n=1):
    chunks = []
    chunk_size = ceil(len(d)/n)
    for i in range(n):
        chunks.append(d[i*chunk_size:(i+1)*chunk_size])

    return chunks

if __name__ == '__main__':

    L=1000
    muvals =  [0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.35, 0.5]

    import argparse
    parser = argparse.ArgumentParser(description = "", usage="generate_toy_data")
    parser.add_argument("--nvals", nargs='+', type=int,  help="number of taxa")
    parser.add_argument("--muvals", nargs='+', default=muvals, type=float,  help="number of taxa")
    parser.add_argument("--submit", action='store_true', help="submit")
    parser.add_argument("--date", type=str,  help="date prefix")
    args=parser.parse_args()

    date_prefix = args.date or date.today().strftime('%Y-%m-%d')

    for pc in [0.01, 0.1, 0.5, 1.0]:
        for alpha, rate_alpha, JC, aa in [(1.0, 3.0, False, False)]: #[(1.0, 1.5, False, False), (0.0, 1.5, True, False), (0.2, 1.5, False, True), (0.5, 1.5, False, True)]:
            dirname = f'{date_prefix}_simulatedData_L{L}_ratealpha{rate_alpha:1.1f}_freqalpha{alpha:1.1f}_{"aa" if aa else "nuc"}' + ("_JC" if JC else "")

            for n in args.nvals:
                submit_script = "submit.sh" if n>200 else "submit_small.sh"
                for mu in args.muvals:
                    aln_mask = os.path.join(dirname, f"L{L}_n{n}_m{mu}_*.fasta.gz")
                    files = glob.glob(aln_mask)
                    if len(files):
                        chunks = make_chunks(files, n=ceil(n/100))
                        for ci,chunk in enumerate(chunks):
                            output = os.path.join(dirname+f"_results", f"L{L}_n{n}_m{mu}_c{pc:1.2f}_chunk{ci:02d}.tsv")
                            cmd = f'sbatch {submit_script} src/reconstruct_toy_data.py --files {" ".join(chunk)} --output {output} {"--aa" if aa else ""} --pc {pc}'
                            print(cmd)
                            if args.submit:
                                os.system(cmd)

