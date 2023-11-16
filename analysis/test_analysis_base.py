
from .analysis_base import load_file_as_csv, ThirdSectorOrg, compare_linkages


def assert_files_basically_same(a,b,ignore=False):
    def filter_na_lines(line):
        return not line.startswith('n/a')

    a_lines = a.split('\n')
    b_lines = b.split('\n')

    if ignore:
        compare_pairs = [(a_line,b_line) for a_line,b_line in zip(filter(filter_na_lines,a_lines),filter(filter_na_lines,b_lines))]
    else:
        compare_pairs = zip(a.split('\n'),b.split('\n'))
    for a_line, b_line in compare_pairs:
        assert a_line.strip() == b_line.strip()


def test_load_file__csv__multiple_names_no_matches():
    '''test file, containing fields uid, normalised name
    load_file should create a dictionary indexed by original (separate) uids, with ThirdSectorOrg
    objects as values
    '''
    f_data = '''uid,normalisedname
    a1,NAME1
    a1,NAME2'''

    name_list = {'NAME1','NAME2'}
    uuid = 'a1'
    matches = []

    a1_tso = ThirdSectorOrg(uuid,name_list,matches)
    expected = {'a1':a1_tso}

    #f1_io = io.StringIO(f_data)
    f1_file = 'tmp.test_base.out'
    f1_io = open(f1_file,'w')
    f1_io.write(f_data)
    f1_io.close()

    assert load_file_as_csv(f1_file) == expected


def test_load_file__csv__multiple_names_with_matches():
    '''test file, containing fields uid, normalised name
    load_file should create a dictionary indexed by original (separate) uids, with ThirdSectorOrg
    objects as values
    '''
    f_data = '''uid,normalisedname
    a1,NAME1
    a1,NAME2
    b2_b3_b4,NAME3
    b3_b100,NAME30'''

    name_list = {'NAME1','NAME2'}
    matches = []

    
    a1_tso = ThirdSectorOrg('a1',name_list,matches)
    b2_tso = ThirdSectorOrg('b2',{'NAME3','NAME30'},{'b3','b4','b100'})
    b3_tso = ThirdSectorOrg('b3',{'NAME3','NAME30'},{'b2','b4','b100'})
    b4_tso = ThirdSectorOrg('b4',{'NAME3','NAME30'},{'b2','b3','b100'})
    b100_tso = ThirdSectorOrg('b100',{'NAME3','NAME30'},{'b3','b2','b4'})
    expected = {'a1':a1_tso,
                'b2':b2_tso,
                'b3':b3_tso,
                'b4':b4_tso,
                'b100':b100_tso}

    #f1_io = io.StringIO(f_data)
    f1_file = 'tmp.test_base1.out'
    f1_io = open(f1_file,'w')
    f1_io.write(f_data)
    f1_io.close()

    print(expected)
    
    assert load_file_as_csv(f1_file) == expected



def test_load_file_with_matches_linkage_fmt():
    '''test file, containing fields uid, linkages, names
    load_file should create a dictionary indexed by original (separate) uids, with ThirdSectorOrg
    objects as values
    '''
    f_data = '''uid,linkages,names
    a1,,NAME1 - NAME2
    b2,b3 - b4 - b100,NAME3 - NAME30
    b3,b2 - b4 - b100,NAME3 - NAME30
    b4,b2 - b3 - b100,NAME3 - NAME30
    b100,b3 - b2 - b4,NAME3 - NAME30'''

    
    a1_tso = ThirdSectorOrg('a1',{'NAME1','NAME2'},{''})
    print(a1_tso.uuid,a1_tso.matched,a1_tso.names)
    b2_tso = ThirdSectorOrg('b2',{'NAME3','NAME30'},{'b3','b4','b100'})
    b3_tso = ThirdSectorOrg('b3',{'NAME3','NAME30'},{'b2','b4','b100'})
    b4_tso = ThirdSectorOrg('b4',{'NAME3','NAME30'},{'b2','b3','b100'})
    b100_tso = ThirdSectorOrg('b100',{'NAME3','NAME30'},{'b3','b2','b4'})
    expected = {'a1':a1_tso,
                'b2':b2_tso,
                'b3':b3_tso,
                'b4':b4_tso,
                'b100':b100_tso}

    #f1_io = io.StringIO(f_data)
    f1_file = 'tmp.test_base1.out'
    f1_io = open(f1_file,'w')
    f1_io.write(f_data)
    f1_io.close()

    print(expected)
    d = load_file_as_csv(f1_file)
    print('d:',d)

    assert load_file_as_csv(f1_file) == expected


def test_compare_linkages():
    link1 = '''uid,normalisedname
    a1_b2,NAME1
    a4,NAME2
    a3_b3,NAME3'''
    link2 = '''uid,normalisedname
    a1_b2,NAME1
    a4_CC,NAME2
    a3_b3_B4,NAME3'''
# ['B4', 'CC', 'a1', 'a3', 'a4', 'b2', 'b3']
    expected = '''uid,linkages_file1,names_file1,linkages_file2,names_file2,agree
    B4,,,a3 - b3,NAME3,0
    CC,,,a4,NAME2,0
    a1,b2,NAME1,b2,NAME1,1
    a3,b3,NAME3,B4 - b3,NAME3,0
    a4,,NAME2,CC,NAME2,0
    b2,a1,NAME1,a1,NAME1,1
    b3,a3,NAME3,B4 - a3,NAME3,0'''

    f1_file = 'tmp.test_base1.out'    
    f2_file = 'tmp.test_base2.out'
    f1_io = open(f1_file,'w')
    f1_io.write(link1)
    f1_io.close()
    f2_io = open(f2_file,'w')
    f2_io.write(link2)
    f2_io.close()

    ofile = 'test_base.tmp.out'#io.StringIO()
    compare_linkages(f1_file,f2_file,ofile)
    written_data = open(ofile,'r').read()
    print('ofile.read:\n',written_data)
    assert_files_basically_same(written_data,expected,ignore=True)

def test_tso_object():
    matches = ['a','b','c']
    names=['name1']
    a=ThirdSectorOrg('a',names,matches)
    print(a.sort_sets)

    assert a.matched == {'b','c'}

    a.add_matched_uids('b')
    print(a.sort_sets)
    assert a.matched == {'b','c'}

    a.add_matched_uids('a')
    print(a.sort_sets)
    assert a.matched == {'b','c'}


