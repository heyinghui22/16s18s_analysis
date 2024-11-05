#! /usr/bin/env python3
import os
import re
import sys
import string
import optparse
import fasta
import math

def format(seq, N=60):
    nseg = int(math.ceil(len(seq) / float(N)))
    return '\n'.join([seq[i*N:(i+1)*N] for i in range(nseg)])

parser = optparse.OptionParser(version="%prog ")

parser.add_option("-i", "--input", dest="input_fasta", action="store",
        help="name of input file in fasta format")
parser.add_option("-L", "--LibHmm", dest="hmm_path", action="store",
        default="HMM3", help="path of hmm database")
parser.add_option("-o", "--output", dest="out_fname", action="store",
        help="name of output file")
parser.add_option("-k", "--kingdoms", dest="kingdoms", action="store",
        default="arc,bac,euk", help="kingdom used")
parser.add_option("-m", "--moltypes", dest="moltypes", action="store",
        default="lsu,ssu,tsu", help="molecule type detected")
parser.add_option("-e", "--Evalue", dest="evalue", action="store", type="float",
        default=0.01, help="evalue cut-off for hmmsearch")

try:
    (options, args) = parser.parse_args()
except:
    parser.print_help()
    sys.exit(1)

if options.input_fasta is None or options.hmm_path is None:
    parser.print_help()
    sys.exit(1)

out_fname = os.path.abspath(options.out_fname)
out_dir = os.path.dirname(out_fname)
fname = os.path.abspath(options.input_fasta)

tr = str.maketrans("gatcryswkmbdhvnGATCRYSWKMBDHVN", "ctagyrswmkvhdbnCTAGYRSWMKVHDBN")

def rev_record(record):
    return ">" + record.header + "|rev\n" + format(record.sequence[::-1].translate(tr))

records = [rec for rec in fasta.fasta_itr(fname)]
headers = [[rec.header, len(rec.sequence)] for rec in records]

with open(out_fname + '.fa', 'w') as ff:
    for i, rec in enumerate(records):
        ff.write('>s' + str(i) + '\n' + format(rec.sequence) + '\n')
        ff.write('>s' + str(i) + '|rev\n' + format(rec.sequence[::-1].translate(tr)) + '\n')

def parse_hmmsearch(kingdom, moltype, src):
    resu = []
    with open(src) as f:
        data = f.readlines()
    inds = [-1  ] + [i for i, x in enumerate(data[2]) if x == " "]
    inds = [(inds[j]+1, inds[j+1]) for j in range(len(inds)-1)]
    data = [line for line in data if line[0] != "#"]
    for line in data:
        if not len(line.strip()):
            continue
        elements = line.split()[:21]
        dom_iEvalue = float(elements[12])
        if dom_iEvalue < options.evalue:
            resu.append("\t".join([elements[3], elements[16], elements[17], elements[0], elements[12]]))
    return resu

hmm_resu = []
for kingdom in options.kingdoms.split(','):
    for moltype in options.moltypes.split(','):
        hmm_out_fname = f"{out_fname}.{kingdom}_{moltype}.out"
        dom_out_fname = f"{out_fname}.{kingdom}_{moltype}.dom"
        cmd = f'hmmsearch --cpu 10 -o {hmm_out_fname} --domtblout {dom_out_fname} -E {options.evalue} {os.path.abspath(options.hmm_path)}/{kingdom}_{moltype}.hmm {out_fname}.fa'
        #print(cmd)
        os.system(cmd)
        hmm_resu += parse_hmmsearch(kingdom, moltype, dom_out_fname)
        os.remove(hmm_out_fname)
        os.remove(dom_out_fname)

dict_read2kingdom = {}
for line in hmm_resu:
    feature_type, r_start, r_end, read, evalue = line.strip().split('\t')
    read = read.split('|')[0]
    evalue = float(evalue)
    kingdom = feature_type.split('_')[0]
    if read in dict_read2kingdom:
        if evalue < dict_read2kingdom[read][1]:
            dict_read2kingdom[read] = [kingdom, evalue]
    else:
        dict_read2kingdom[read] = [kingdom, evalue]

header = ['##seq_name', 'method', 'feature', 'start', 'end', 'evalue', 'strand', 'gene']
with open(out_fname + ".coord", "w") as ff:
    dict_rRNA = {
        'arc_lsu': 'Archaeal:23S_rRNA', 'arc_ssu': 'Archaeal:16S_rRNA', 'arc_tsu': 'Archaeal:5S_rRNA',
        'bac_lsu': 'Bacterial:23S_rRNA', 'bac_ssu': 'Bacterial:16S_rRNA', 'bac_tsu': 'Bacterial:5S_rRNA',
        'euk_lsu': 'Eukaryotic:28S_rRNA', 'euk_ssu': 'Eukaryotic18S_rRNA', 'euk_tsu': 'Eukaryotic:8S_rRNA'
    }

    ff.write('\t'.join(header) + '\n')
    for line in hmm_resu:
        feature_type, r_start, r_end, read, evalue = line.strip().split('\t')
        if dict_read2kingdom[read.split('|')[0]][0] != feature_type.split('_')[0]:
            continue
        feature_type = dict_rRNA[feature_type]
        if read.endswith('|rev'):
            strand = '-'
            tmp = list(map(int, [r_start, r_end]))
            pos = int(read[1:-4])
            header = headers[pos][0]
            L = headers[pos][1]
            r_end, r_start = [str(L+1-x) for x in tmp]
        else:
            strand = '+'
            pos = int(read[1:])
            header = headers[pos][0]
        ff.write('\t'.join([header.split()[0], 'rna_hmm3', 'rRNA', r_start, r_end, evalue, strand, feature_type]) + '\n')

os.remove(out_fname + '.fa')

rRNA_dict = {}
for line in open(out_fname + ".coord").readlines()[1:]:
    line = line.strip().split()
    if rRNA_dict.get(line[0], None) is None:
        rRNA_dict[line[0]] = []
    rRNA_dict[line[0]].append((int(line[3]), int(line[4]), line[6], line[7]))

with open(out_fname + '.mask', "w") as f_mask, open(out_fname + '.seq', "w") as f_seq:
    for rec in fasta.fasta_itr(options.input_fasta):
        header = rec.header.split()[0]
        seq = rec.sequence[:]
        tno = 1
        for start, end, strand, rRNA_type in rRNA_dict.get(header, []):
            seq = seq[:(start-1)] + 'N' * (end-start+1) + seq[end:]
            f_seq.write(f">{header}.{tno} /start={start} /end={end} /strand={strand} {rRNA_type}\n")
            if strand == "+":
                f_seq.write(format(rec.sequence[(start-1):end]) + "\n")
            else:
                f_seq.write(format(rec.sequence[(start-1):end][::-1].translate(tr)) + "\n")
            tno += 1
        f_mask.write(">" + rec.header + "\n")
        f_mask.write(format(seq) + "\n")