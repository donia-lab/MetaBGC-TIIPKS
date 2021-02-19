import click
import logging
from time import time
import os
from metabgc.src.metabgcbuild import mbgcbuild
from metabgc.src.metabgcidentify import mbgcidentify
from metabgc.src.metabgcquantify import mbgcquantify
from metabgc.src.metabgccluster import mbgccluster
from metabgc.src.metabgcanalytics import mbgcanalytics
from metabgc.src.metabgcsynthesize import mbgcsynthesize
from metabgc.src.metabgcfindTP import mbgcfindtp

__version__ = "2.0.0"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--prot_alignment',required=True,
              type=click.Path(exists=True,file_okay=True,readable=True),
              help="Alignment of the protein homologs in FASTA format.")
@click.option('--tp_genes_nucl', required=True,
              type=click.Path(exists=True,file_okay=True,readable=True),
              help="Multi-FASTA with the nucleotide sequence of the true positive genes.")
@click.option('--f1_thresh', required=True,
              type=click.FLOAT, help="F1 score threshold.")
@click.option('--prot_family_name', required=True,
              help="Name of the protein family.")
@click.option('--cohort_name', required=True,
              help="Name of the sample/cohort.")
@click.option('--nucl_seq_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with synthetic read files of the cohort.")
@click.option('--prot_seq_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with translated synthetic read files of the cohort. Computed if not provided.")
@click.option('--seq_fmt', required=True,
              type=click.Choice(['fasta', 'fastq'],case_sensitive=False),
              help="Sequence file format and extension.")
@click.option('--pair_fmt', required=True,
              type=click.Choice(['single', 'split', 'interleaved'],case_sensitive=False),
              help="Sequence pair format.")
@click.option('--r1_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R1 reads. Not specified for single or interleaved reads.")
@click.option('--r2_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R2 reads. Not specified for single or interleaved reads.")
@click.option('--blastn_search_directory', required=False,
              type=click.Path(exists=False,dir_okay=True,readable=True),
              help="Directory with BLAST search of the synthetic read files against the TP genes. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--blast_db_directory_map_file', required=False,
              type=click.Path(exists=True,dir_okay=False,readable=True),
              help="Path to 2 column comma seperated mapping file with (sample_name,blast_database_path). The BLAST databases are computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--hmm_search_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with HMM searches of the synthetic read files against all the spHMMs. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--output_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help="Directory to save results.")
@click.option('--cpu', required=False,
              type=click.INT,default=4,
              help="Number of threads. Def.: 4")
def build(prot_alignment,prot_family_name,cohort_name,
          nucl_seq_directory,prot_seq_directory,seq_fmt,pair_fmt,r1_file_suffix,
          r2_file_suffix,tp_genes_nucl,blast_db_directory_map_file,blastn_search_directory,hmm_search_directory,f1_thresh,
          output_directory,cpu):
    click.echo('Invoking MetaBGC Build...')
    t0 = time()
    logging.basicConfig(filename=os.path.join(output_directory, 'metabgc.log'), level=logging.INFO)
    hp_hmm_directory = mbgcbuild(prot_alignment,prot_family_name,cohort_name,
          nucl_seq_directory,prot_seq_directory,seq_fmt,pair_fmt,r1_file_suffix,
          r2_file_suffix,tp_genes_nucl,blast_db_directory_map_file,blastn_search_directory,hmm_search_directory,f1_thresh,
          output_directory,cpu)
    print('High performance SpHMMS saved here: '+hp_hmm_directory)
    t1 = time() - t0
    logging.info("Time elapsed: " + str(t1))

@cli.command()
@click.option('--sphmm_directory', required=True, help= "High performance spHMM directory generated by Build.")
@click.option('--prot_family_name', required=True,
              help="Name of the protein family.")
@click.option('--cohort_name', required=True,
              help="Name of the sample/cohort.")
@click.option('--nucl_seq_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with synthetic read files of the cohort.")
@click.option('--prot_seq_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with translated synthetic read files of the cohort. Computed if not provided.")
@click.option('--seq_fmt', required=True,
              type=click.Choice(['fasta', 'fastq'],case_sensitive=False),
              help="Sequence file format and extension.")
@click.option('--pair_fmt', required=True,
              type=click.Choice(['single', 'split', 'interleaved'],case_sensitive=False),
              help="Sequence pair format.")
@click.option('--r1_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R1 reads. Not specified for single or interleaved reads.")
@click.option('--r2_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R2 reads. Not specified for single or interleaved reads.")
@click.option('--hmm_search_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with HMM searches of the synthetic read files against all the spHMMs. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--output_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help="Directory to save results.")
@click.option('--cpu', required=False,
              type=click.INT,default=4,
              help="Number of threads. Def.: 4")
def identify(sphmm_directory,cohort_name,nucl_seq_directory,prot_seq_directory,
             seq_fmt,pair_fmt,r1_file_suffix,r2_file_suffix,
             prot_family_name, hmm_search_directory, output_directory,cpu):
    click.echo('Invoking MetaBGC Identify...')
    ident_reads_file = mbgcidentify(sphmm_directory, cohort_name, nucl_seq_directory,prot_seq_directory,
                 seq_fmt, pair_fmt, r1_file_suffix, r2_file_suffix,
                 prot_family_name, hmm_search_directory, output_directory, cpu)
    print('Identified reads: ' + ident_reads_file)

@cli.command()
@click.option('--identify_fasta', required=True,
              type=click.Path(exists=True,file_okay=True,readable=True),
              help= "Path to the file produced by MetaBGC-Identify.")
@click.option('--prot_family_name', required=True,
              help="Name of the protein family.")
@click.option('--cohort_name', required=True,
              help="Name of the sample/cohort.")
@click.option('--nucl_seq_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with synthetic read files of the cohort.")
@click.option('--seq_fmt', required=True,
              type=click.Choice(['fasta', 'fastq'],case_sensitive=False),
              help="Sequence file format and extension.")
@click.option('--pair_fmt', required=True,
              type=click.Choice(['single', 'split', 'interleaved'],case_sensitive=False),
              help="Sequence pair format.")
@click.option('--r1_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R1 reads. Not specified for single or interleaved reads.")
@click.option('--r2_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R2 reads. Not specified for single or interleaved reads.")
@click.option('--blastn_search_directory', required=False,
              type=click.Path(exists=False,dir_okay=True,readable=True),
              help="Directory with BLAST search of the synthetic read files against the TP genes. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--blast_db_directory_map_file', required=False,
              type=click.Path(exists=True,dir_okay=False,readable=True),
              help="Path to 2 column comma seperated mapping file with (sample_name,blast_database_path). The BLAST databases are computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--output_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help="Directory to save results.")
@click.option('--cpu', required=False,
              type=click.INT,default=4,
              help="Number of threads. Def.: 4")
def quantify(identify_fasta,prot_family_name,cohort_name,nucl_seq_directory,
             seq_fmt,pair_fmt,r1_file_suffix,r2_file_suffix,blastn_search_directory,blast_db_directory_map_file,
             output_directory,cpu):
    click.echo('Invoking MetaBGC Quantify...')
    abund_file, abund_wide_table = mbgcquantify(identify_fasta, prot_family_name, cohort_name, nucl_seq_directory,
             seq_fmt, pair_fmt, r1_file_suffix, r2_file_suffix,blast_db_directory_map_file,blastn_search_directory,
             output_directory, cpu)
    print('Reads abundance file: ' + abund_file)


@cli.command()
@click.option("--table",required=True,type=click.Path(exists=True,file_okay=True,readable=True),
              help="Path of tab-delimited abundance table.")
@click.option("--table_wide",required=True,type=click.Path(exists=True,file_okay=True,readable=True),
              help="Path of tab-delimited abundance wide file.")
@click.option('--identify_fasta', required=True,
              type=click.Path(exists=True,file_okay=True,readable=True),
              help= "Path to the file produced by MetaBGC-Identify.")
@click.option("--max_dist", type=float, default=0.1,help="Maximum Pearson distance between two reads to be in the same cluster. Default is 0.1")
@click.option("--min_samples", type=float, default=1,help="Minimum number of samples required for a cluster. " \
                                                          "If min_samples > 1, noise are labelled as -1")
@click.option("--min_reads_bin", type=float, default=10,help="Minimum number of reads required in a bin to be considered in analytics output files.")
@click.option("--min_abund_bin", type=float, default=10,help="Minimum total read abundance required in a bin to be considered in analytics output files.")
@click.option("--cpu", type=int, default=1,help="Number of threads.")
def cluster(table,table_wide,identify_fasta,max_dist,min_samples,min_reads_bin,min_abund_bin,cpu):
    click.echo('Invoking MetaBGC Cluster...')
    summary_file, cluster_file = mbgccluster(table,table_wide, identify_fasta, max_dist, min_samples,min_reads_bin, min_abund_bin, cpu)
    click.echo('Cluster summary file: ' + summary_file)
    click.echo('Cluster detail file: ' + cluster_file)


@cli.command()
@click.option('--sphmm_directory', required=True, help= "High performance spHMM directory generated by Build.")
@click.option('--prot_family_name', required=True,
              help="Name of the protein family.")
@click.option('--cohort_name', required=True,
              help="Name of the sample/cohort.")
@click.option('--nucl_seq_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with synthetic read files of the cohort.")
@click.option('--prot_seq_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with translated synthetic read files of the cohort. Computed if not provided.")
@click.option('--seq_fmt', required=True,
              type=click.Choice(['fasta', 'fastq'],case_sensitive=False),
              help="Sequence file format and extension.")
@click.option('--pair_fmt', required=True,
              type=click.Choice(['single', 'split', 'interleaved'],case_sensitive=False),
              help="Sequence pair format.")
@click.option('--r1_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R1 reads. Not specified for single or interleaved reads.")
@click.option('--r2_file_suffix', required=False,
              help="Suffix including extension of the file name specifying R2 reads. Not specified for single or interleaved reads.")
@click.option("--max_dist", type=float, default=0.1,help="Maximum Pearson distance between two reads to be in the same cluster. Default is 0.1")
@click.option("--min_samples", type=float, default=1,help="Minimum number of samples required for a cluster. " \
                                                          "If min_samples > 1, noise are labelled as -1")
@click.option("--min_reads_bin", type=float, default=10,help="Minimum number of reads required in a bin to be considered in analytics output files.")
@click.option("--min_abund_bin", type=float, default=10,help="Minimum total read abundance required in a bin to be considered in analytics output files.")
@click.option('--hmm_search_directory', required=False,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help="Directory with HMM searches of the synthetic read files against all the spHMMs. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--blastn_search_directory', required=False,
              type=click.Path(exists=False,dir_okay=True,readable=True),
              help="Directory with BLAST search of the synthetic read files against the TP genes. Computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--blast_db_directory_map_file', required=False,
              type=click.Path(exists=True,dir_okay=False,readable=True),
              help="Path to 2 column comma seperated mapping file with (sample_name,blast_database_path). The BLAST databases are computed if not provided. To compute seperately, please see job_scripts in development.")
@click.option('--output_directory', required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help="Directory to save results.")
@click.option('--cpu', required=False,
              type=click.INT,default=4,
              help="Number of threads. Def.: 4")
def search(sphmm_directory,prot_family_name,cohort_name,
            nucl_seq_directory,prot_seq_directory,seq_fmt,pair_fmt,
            r1_file_suffix,r2_file_suffix,max_dist,min_samples,min_reads_bin,min_abund_bin,
            hmm_search_directory, blastn_search_directory, blast_db_directory_map_file, output_directory,cpu):
    logging.basicConfig(filename=os.path.join(output_directory,'metabgc.log'), level=logging.INFO)
    logging.info('Invoking MetaBGC search...')
    click.echo('Invoking MetaBGC search...')
    t0 = time()
    ident_reads_file = mbgcidentify(sphmm_directory, cohort_name, nucl_seq_directory,prot_seq_directory,
                                    seq_fmt, pair_fmt, r1_file_suffix, r2_file_suffix,
                                    prot_family_name, hmm_search_directory, output_directory, cpu)

    abund_file, abund_wide_table = mbgcquantify(ident_reads_file, prot_family_name, cohort_name, nucl_seq_directory,
             seq_fmt, pair_fmt, r1_file_suffix, r2_file_suffix,blast_db_directory_map_file,blastn_search_directory,
             output_directory, cpu)

    summary_file, cluster_file = mbgccluster(abund_file,abund_wide_table, ident_reads_file, max_dist, min_samples,min_reads_bin, min_abund_bin, cpu)
    click.echo('Cluster summary file: ' + summary_file)
    click.echo('Cluster detail file: ' + cluster_file)
    logging.info('Cluster summary file: ' + summary_file)
    logging.info('Cluster detail file: ' + cluster_file)
    t1 = time() - t0
    logging.info("Time elapsed: " + str(t1))
    logging.info("MetaBGC search complete...")
    click.echo("MetaBGC search complete...")

@cli.command()
@click.option('--metabgc_output_dir',
              required=True,
              type=click.Path(exists=True, dir_okay=True, writable=True),
              help= "Output directory of a successful metabgc search run.")
@click.option('--cohort_metadata_file',
              required=True,
              type=click.Path(exists=True,dir_okay=False,readable=True),
              help= "Cohort metadata file.")
@click.option('--assembly_metadata_file',
              required=True,
              type=click.Path(exists=True,dir_okay=False,readable=True),
              help= "CSV file with sample assembly paths.")
@click.option('--output_directory',
              required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help= "Directory to save results.")
@click.option('--cpu', required=False,
              type=click.INT,default=4,
              help="Number of threads. Def.: 4")
def analytics(metabgc_output_dir,cohort_metadata_file,assembly_metadata_file,output_directory,cpu):
    mbgcanalytics(metabgc_output_dir,cohort_metadata_file,assembly_metadata_file,output_directory,cpu)

@cli.command()
@click.option('--indir1','-i1',required=True,
              type=click.Path(exists=True, dir_okay=True,readable=True),
              help= "Input directory of background fasta files for simulation.")
@click.option('--indir2','-i2',required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help= "Input directory protein family positive fasta files for simulation.")
@click.option('--system', '-ss',required=True,
              help= "Illumina sequencing system (HS10, HS25, MSv3, etc.). Same options as -ss in art_illumina.")
@click.option('--length', '-l', required=True,
              type=click.INT, help="Read length in bp.")
@click.option('--mflen', '-fl', required=True,
              type=click.INT, help="Mean fragment size in bp.")
@click.option('--mflensd', '-sd', required=True,
              type=click.INT, help="Standard dev of fragment size in bp.")
@click.option('--num_reads', '-nr',required=True,
              type=click.INT, help="Total number of read pairs.")
@click.option('--samples', '-ns', required=True,
              type=click.INT, help=" Number of samples to generate.")
@click.option('--prop', '-p', required=True,
              type=click.FloatRange(0,1), help="Proportion of organisms to draw for each metagenomic sample. Should be between 0 and 1.")
@click.option('--output_directory', '-o',required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help= "Directory to save results.")
@click.option('--base_name', '-b', required=False,
              default='S', help="Prefix of sample name (Def.='S')")
@click.option('--cpu', '-t',required=False,
              type=click.INT, default=1,
              help="Number of threads. Def.: 1")
@click.option('--seed','-rs', required=False,
              type=click.INT, default=915,
              help="Random seed. Def.: 915")
def synthesize(indir1, indir2, system, length, mflen, mflensd, num_reads,
               samples, prop, output_directory, base_name, cpu, seed):
    mbgcsynthesize(indir1, indir2, system, length, mflen, mflensd, num_reads,
                   samples, prop, output_directory, base_name, cpu, seed)

@cli.command()
@click.option('--aln_file',required=True,
              type=click.Path(exists=True, file_okay=True,readable=True),
              help= "Input protein family sequences in a fasta format or a MUSCLE alignment. If it is a FASTA file then set --do_alignment 1.")
@click.option('--prot_seq_directory',required=True,
              type=click.Path(exists=True,dir_okay=True,readable=True),
              help= "Input directory with the protein family positive fasta files used for simulation.")
@click.option('--output_directory', '-o',required=True,
              type=click.Path(exists=True,dir_okay=True,writable=True),
              help= "Directory to save results.")
@click.option('--do_alignment',required=True,
              type=click.BOOL, help="Set it up to do an alignment if the --alnFile is a FASTA.")
def findtp(aln_file, prot_seq_directory, output_directory, do_alignment):
    mbgcfindtp(aln_file, prot_seq_directory, output_directory, do_alignment)

def main():
    cli()
