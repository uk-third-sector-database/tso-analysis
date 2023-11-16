import click
import csv


#from analysis.base import compare_linkages, load_file_as_df
from analysis.analysis_base import compare_linkages,linkage_stats, extract_linkages
from analysis.FTC_data_wrangling import wrangle_findthatcharity_data_csv




@click.group()
def cli():
    ...




@cli.command()
@click.argument("src1", type=click.File("r", encoding='UTF8'))#, nargs=1)
@click.argument("src2", type=click.File("r", encoding='UTF8'))#, nargs=1)
#@click.argument("sources", type=str, nargs=2)
@click.option("-o", "--output", default="linkages.out.csv", type=str)#show_default=True, type=click.File("w", encoding='UTF8'))
def analyse_linkages(src1,src2,output):
    '''Compare linkages in two input source files. Inputs must contain the fields uid and normalisedname.
    Output is a file comparing the linkages, with field for agreement, plus file <output>.stats containing simple comparisons'''

    #src1,src2 = [source.name for source in sources]
    print(src1.name,src2.name)
    compare_linkages(src1.name,src2.name,output,True)
    linkage_stats(output,output+'.stats')



@cli.command()
@click.argument("src", type=click.File("r", encoding='UTF8'))#, nargs=1)
#@click.argument("sources", type=str, nargs=2)
@click.option("-o", "--output", default="sort_linkages.out.csv", type=str)#show_default=True, type=click.File("w", encoding='UTF8'))
def sort_linkage_data(src,output):
    '''Input file has fields in matched spine format; output has individual-uid : linkages : normalised-names.
     Used to then analyse linkages '''

    #src1,src2 = [source.name for source in sources]
    print(src.name)
    extract_linkages(src.name,output)

    

@cli.command()
@click.argument("src1", type=click.File("r", encoding='UTF8'))
@click.option("-o", "--output", default="linkages.out.csv", type=str)
def wrangle_ftc(src1,output):
    '''take FTC data and transform to our 'spine' format (<output>.tmp) and then linkage format (<output>) for comparison '''

    print(src1.name)
    interim_ofile = '%s.tmp'%output
    wrangle_findthatcharity_data_csv(src1.name,interim_ofile)
    extract_linkages(interim_ofile,output)


@cli.command()
@click.argument("src1", type=click.File("r", encoding='UTF8'))
@click.option("-o", "--output", default="linkage_stats.out.csv", type=str)
def get_linkage_stats(src1,output):
    '''compare linkages (output to terminal) in file produced by analyse-linkages '''

    print(src1.name)
    linkage_stats(src1.name,output)



if __name__ == "__main__":
    cli()
