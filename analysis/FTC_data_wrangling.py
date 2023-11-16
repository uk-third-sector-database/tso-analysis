
import csv
import string

''' normalizer is in spine/wrangling, but importing from here wasn't working - to fix 
For now just copying the function here since FTC work is not critical'''
def normalizer(name, norm_dict=None):
    ''' normalise entity names with manually curated dict'''
    norm_dict={}
    if isinstance(name, str):
        name = name.upper()
        for key, value in norm_dict.items():
            name = name.replace(key, value)
        name = name.replace(r"\(.*\)", "")  # remove brackets
        name = "".join(l for l in name if l not in string.punctuation) # keep text other than punctuation
        name = ' '.join(name.split()) # remove additional spaces
        name = name.strip() # remove trailing spaces
        return name
    return None

def iter_csv_rows(filename):
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row

def transform_row(row):
    res = set()
    row_orgid = row['org_id']
    all_orgs = row['orgIDs'].strip('"').strip('[]').split(',')
    for o in all_orgs:
        res.add(o.replace('"','').replace("'",'').strip())
    uid = '_'.join(sorted(set(res)))
    if not row_orgid in res:
        print(f'unexpected row: orgid {row_orgid} not in orgIDs')
    names = [row['name'],row['alternateName']]
    new_rows=[]
    for name in names:
        name = normalizer(name)
        if name: 
            d = {}
            d['uid'] = uid
            d['normalisedname'] = name
            new_rows.append(d)

    return new_rows


def wrangle_findthatcharity_data_csv(infile:str,ofile:str):  
    processed_rows = 0
    fields = ['uid','normalisedname']

    with open(ofile, "w+", encoding='UTF8', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for new_row in iter_csv_rows(infile):
            #print(new_row)
            processed_rows += 1
            writer.writerows(transform_row(new_row))
    
    print("File %s processed, %d lines written to %s\n"%(infile,processed_rows,ofile))


if __name__=='__main__':
    ftc_infile = '../raw_data/FindThatCharity_matches.csv'
    ftc_ofile = '../processed_data/FindThatCharity_matches_processed.csv'

    wrangle_findthatcharity_data_csv(ftc_infile,ftc_ofile)