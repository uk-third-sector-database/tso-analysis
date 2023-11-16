import csv
import pandas
import sys

from tqdm import tqdm

class ThirdSectorOrg:

    def __init__(self,uuid:str,names:set,matched_uids:set) -> None:
#        print('(TSO init: ',uuid,matched_uids,names,')')

        # remove original uid from matchlist
        
        l = set(matched_uids)
        l.discard(uuid)

        self.uuid = uuid
        self.names = set(names)
        self.matched = l
        
    def __eq__(self, other) -> bool:
        if not isinstance(other,ThirdSectorOrg):
            return False
        if self.uuid != other.uuid:
            print('uuid does not match: self %s and other %s'%(self.uuid,other.uuid))
            return False

        if not (self.names == other.names):
            print('names do not match: self %s and other %s (uuid = %s)'%(self.names,other.names,self.uuid))
            return False
        if not (self.matched == other.matched):
            print('matched uids do not match: self %s and other %s (uuid = %s)'%(self.matched,other.matched,self.uuid))
            return False
        return True
    
    
    def sort_sets(self):
        '''for format_row: return sorted lists as strings for uid linkages and names'''
        l = list(self.matched)
        l.sort()

        n = list(self.names)
        n.sort()

        return(' - '.join(l), ' - '.join(n))

    def add_matched_uids(self,items):
        '''make sure that self.matched never includes self.uuid'''
        self.matched = set.union(self.matched,items)
        self.matched.discard(self.uuid)


def update_all_TSO_objects(match_list,names,uid_dictionary):
    '''if key already in dictionary, it was part of another match.
    We want the names and ids that this org was already matched to to be updated
    with the names and ids for this current match
    All in list matched_list need to be updated with all the info, whether or not they've already
    been entered in the dictionary'''

    previous_matches = set(match_list)
    previous_names = set(names)
    
    for id in match_list:
        if id in uid_dictionary.keys():
            previous_names.update(i for i in uid_dictionary[id].names)
            previous_matches.update(i for i in uid_dictionary[id].matched)

    for id in previous_matches:
        if id in uid_dictionary.keys():
            uid_dictionary[id].add_matched_uids(previous_matches)
            uid_dictionary[id].names = set.union(uid_dictionary[id].names,previous_names)
        else:
            uid_dictionary[id] = ThirdSectorOrg(id,previous_names,previous_matches)
    return uid_dictionary



def load_file_as_csv(input_csv_filename:str):
    '''given file in spine format, create dictionary of {'uid':ThirdSectorOrg_object}
    e.g. orgs a1 and b2 match : their combined uid is a1_b2
    Dictionary will be {'a1':TSO1, 'b2':TSO2} where TSO1.uuid = 'a1', TSO1.names=['name'], TSO1.matched = ['b2']'''
    
    d={}

    print('loading file ',input_csv_filename,' into dictionary format (function analysis.base.load_file_as_csv)')
    with open(input_csv_filename, mode='r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        if 'normalisedname' in csvreader.fieldnames:

            for row in csvreader:
                row_uid = row['uid'].strip()
                row_name = row['normalisedname'].strip()
                d[row_uid] = {row_name} if row_uid not in d else d[row_uid] | {row_name}

            memory_usage = sys.getsizeof(d)
            print(f"Memory usage of dictionary 1 (uids and names loaded from csv): {memory_usage} bytes")

            d_uuids={}
            for matched_uid in tqdm(d.keys()):
            
                matched_list = set(matched_uid.strip().split('_'))
                names = d[matched_uid] # set of names 

                # add key:TSO object to dictionary for each part of the uid
                for original_uid in matched_list:
                    if original_uid in d_uuids.keys():
                        d_uuids = update_all_TSO_objects(matched_list,names,d_uuids)
                    else:
                        d_uuids[original_uid] = ThirdSectorOrg(original_uid,names,matched_list)

            memory_usage = sys.getsizeof(d_uuids)
            print(f"Memory usage of dictionary 2 (original uids and names loaded from dictionary 1): {memory_usage} bytes")
            return d_uuids

        elif 'linkages' in csvreader.fieldnames:
            d_uuids = {}
            rowid=0
            try:
                for row in csvreader:
                    rowid +=1
                    original_uid = row['uid'].strip()
                    matched_list = set(row['linkages'].split(' - '))
                    names = set(row['names'].split(' - '))
                    if original_uid in d_uuids.keys():
                        d_uuids = update_all_TSO_objects(matched_list,names,d_uuids)
                    else:
                        d_uuids[original_uid] = ThirdSectorOrg(original_uid,names,matched_list)
                    
            except Exception as e:
                print(f'exception for rowid {rowid}: {e}')
                
            

            memory_usage = sys.getsizeof(d_uuids)
            print(f"Memory usage of dictionary 2 (original uids and names loaded from dictionary 1): {memory_usage} bytes")
            return d_uuids



def format_row(dict1:dict,dict2:dict,key:str):
    new_row = {}
    tso1 = ''
    tso2 = ''
    new_row["uid"] = key
    try:
        tso1 = dict1[key]
        new_row['linkages_file1'], new_row['names_file1'] = tso1.sort_sets()
    except KeyError:
        pass
    try:
        tso2 = dict2[key]
        new_row['linkages_file2'], new_row["names_file2"] = tso2.sort_sets()
    except KeyError:
        pass
    new_row['agree'] = 0
    if tso1 and tso2:
        if tso1.matched == tso2.matched:
            new_row['agree'] = 1
    

    return new_row


def compare_linkages(file1:str,file2:str,outputfile, use_tso_object=False):
    '''given two files with linked organisations (using 'spine' syntax), process all linkages
    and output a csv for analysis'''

    fields = ['uid', 'linkages_file1', 'names_file1', 'linkages_file2', 'names_file2', 'agree']
    first_line = ['n/a',file1,'n/a',file2,'n/a','n/a']

    
    dict1 = load_file_as_csv(file1)
    dict2 = load_file_as_csv(file2)

    all_keys = set(list(dict1.keys()) + list(dict2.keys())) 
#    #print('keys: ',all_keys)
    all_keys = list(all_keys)
    all_keys.sort()
#    #print('sorted keys: ',all_keys)

    with open(outputfile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerow({fields[i]: first_line[i] for i in range(len(fields))}  )

        for key in all_keys:
            if key:
                new_row = format_row(dict1,dict2,key)
                writer.writerow(new_row)

    print('Completed comparison. Output written to ',outputfile)


def linkage_stats(linkages_filename,ofile):
    df=pandas.read_csv(linkages_filename)
    out = open(ofile,'w+')

    # find the row of the csv which contains the filenames behind the linkage
    row_with_uid_na = df[df['uid'].isnull()]
    if not row_with_uid_na.empty:
        linkage_file1 = row_with_uid_na['linkages_file1'].iloc[0]
        linkage_file2 = row_with_uid_na['linkages_file2'].iloc[0]
    else:
        linkage_file1 = None
        linkage_file2 = None
    #print(linkage_file1,'\n',linkage_file2)
    #print(df.shape)
    df_agree=df[df['agree']==1]
    df_disagree=df[df['agree']==0]
    df_disagree_not_null = df_disagree[df_disagree['linkages_file1'].notnull() & df_disagree['linkages_file2'].notnull()]
    df_agree_not_null = df_agree[df_agree['linkages_file1'].notnull() & df_agree['linkages_file2'].notnull()]
    #print(df.columns)
    total = df.shape[0]
    
    out.write('Dataset has %s unique uids'%total)
    out.write('\n\nORGANSIATION WITH NO LINKAGES IN ONE OR BOTH SETS\n')
    data = df[df['linkages_file1'].isnull() & df['linkages_file2'].isnull()].shape[0]
    perc = 100*data/total
    out.write('\n%d (%.2f%%) organisations have no linkage in either file'%(data,perc))
    data = df[df['linkages_file1'].isnull() & df['linkages_file2'].notnull()].shape[0]
    perc = 100*data/total
    out.write('\n%d (%.2f%%) organisations have no linkage in %s, but have some linkage in %s'%(data,perc,linkage_file1,linkage_file2))
    data = df[df['linkages_file1'].notnull() & df['linkages_file2'].isnull()].shape[0]
    perc = 100*data/total
    out.write('\n%d (%.2f%%) organisations have some linkage in %s, but have no linkage in %s'%(data,perc,linkage_file1,linkage_file2))
    
    out.write('\n\n\nLINKAGES MADE IN BOTH SETS\n')
    data1 = df[df['linkages_file1'].isnull() & df['linkages_file2'].isnull()].shape[0]
    perc = 100*data1/total
    out.write('\n%d (%.2f%%) organisations have no linkage in either file'%(data1,perc))
    data = df_agree_not_null.shape[0]
    perc = 100*data/total
    out.write('\n%d (%.2f%%) organisations have the same not null linkage in both files'%(data,perc))
    data2=data1+data
    perc = 100* data2/total
    out.write('\n==> in total the two algorithms match in %d (%.2f%%) organisations'%(data,perc))
    
    out.write('\n\n\nORGANISATIONS WITH LINKAGES WHICH DIFFER IN THE TWO SOURCES\n')
    data = df_disagree_not_null.shape[0]
    perc = 100*data/total
    a=data
    out.write('\n%d (%.2f%%) organisations have linkages in both datasets, but linkages differ by algorithm'%(data,perc))
    data = df[df['linkages_file1'].isnull() & df['linkages_file2'].notnull()].shape[0]
    perc = 100*data/total
    a+=data
    out.write('\n%d (%.2f%%) organisations have no linkage in %s, but have some linkage in %s'%(data,perc,linkage_file1,linkage_file2))
    data = df[df['linkages_file1'].notnull() & df['linkages_file2'].isnull()].shape[0]
    perc = 100*data/total
    a+=data
    out.write('\n%d (%.2f%%) organisations have some linkage in %s, but have no linkage in %s'%(data,perc,linkage_file1,linkage_file2))
    perc = 100*a/total
    out.write('\n==> in total the two algorithms differ for %d (%.2f%%) organisations'%(a,perc))



def extract_linkages(src,output):
    d = load_file_as_csv(src)

    with open(output, 'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['uid', 'linkages', 'names'], extrasaction='ignore')
        writer.writeheader()

        for key, tso in d.items():
            new_row = {'uid': key, 'linkages': ' - '.join(tso.matched), 'names': ' - '.join(tso.names)}
            writer.writerow(new_row)

    print(f'Reformatted data from {src} written to {output}')

