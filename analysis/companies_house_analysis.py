# for analysis of companies house data

# overlaps with some of the work in 'visualise' - perhaps consolidate

# in venn diagram of the three sources, 
# how are there organisations in CH2014 and CH2023 but not in that scraped from the api? 
# Does this change according the the base download used (Jan, June, Oct)
# Are 'dormant' companies not in the api scrape?

# other analysis of companies house data?

import csv

def load_uid_sets(sources_list):
    uid_sets_per_source = {}
    for s in sources_list:
        new_set = set()
        with open(s,'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_set.add(row['uid'])

            print(f'source {s} has {len(new_set)} unique uids')
        uid_sets_per_source[s]=new_set
    return uid_sets_per_source

def source_intersections(sources_list):

    uid_sets_per_source = load_uid_sets(sources_list)
    source_index = 0
    while source_index < len(sources_list):
        current_source = sources_list[source_index]
        set_1 = uid_sets_per_source[current_source]
        remaining_sources = sources_list[source_index+1:]

        for pairing in remaining_sources:
            set_2 = uid_sets_per_source[pairing]
            print(f'sources {current_source} and {pairing} intersect with {len(set.intersection(set_1,set_2))} identical uids')
        source_index += 1


def source_differences(sources_list):

    uid_sets_per_source = load_uid_sets(sources_list)
    source_index = 0
    while source_index < len(sources_list):
        current_source = sources_list[source_index]
        set_1 = uid_sets_per_source[current_source]
        remaining_sources = sources_list[source_index+1:]

        for pairing in remaining_sources:
            set_2 = uid_sets_per_source[pairing]
            print(f'sources {current_source} and {pairing} differ with {len(set.difference(set_1,set_2))} uids')
        source_index += 1



if __name__ == '__main__':
    a = '../spine_data/CH_2014.spine.csv'		
    Oct ='../spine_data/CH_Oct_2023.spine.csv'	
    c= '../spine_data/CH_gap_decade.spine.csv'
    June ='../spine_data/June_data/CH_June_2023.spine.csv'

    source_intersections([a,June,c,Oct])
    source_differences([a,June,c,Oct])

    # interested in the identities of organisations which are no longer in the bulk download

    bulk_download_sets = load_uid_sets([June,Oct])
    in_June_not_Oct = bulk_download_sets[June].difference(bulk_download_sets[Oct])
    in_Oct_not_June = bulk_download_sets[Oct].difference(bulk_download_sets[June])

    print(f'{len(in_June_not_Oct)} uids in June, not Oct bulk download - have these dissolved?')
    print(f'{len(in_Oct_not_June)} uids in Oct, not June bulk download - have these just been incorporated?')