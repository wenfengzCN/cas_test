#!/usr/bin/python3
import subprocess
import time
import pandas as pd
from orm.commit import *
import xml.etree.ElementTree as ET

show_cmd = file_cmd = 'git show {!s}:{!s} > {!s}'
pmd_cmd = '/opt/pmd-bin-6.1.0/bin/run.sh pmd -d {!s} -f xml -r  {!s} -rulesets  category/java/codestyle.xml,' \
          'category/java/bestpractices.xml,category/java/documentation.xml,category/java/errorprone.xml,category/java/multithreading.xml,' \
          'category/java/performance.xml,category/java/design.xml -cache /home/wenfeng/vlis/cas_test/file_tmp/cachefile'
rm_cmd = 'rm {!s} {!s}'
file_tmp = '/home/wenfeng/vlis/cas_test/file_tmp/tmp.java'
xml_tmp = '/home/wenfeng/vlis/cas_test/file_tmp/tmp.xml'
repo_id = 'jetty1710'
repo_dir='/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git/' + repo_id
MAX_LINE = 10000
pmd_dict = {}



def parse_xml(commit, file_name, xml_file):
    results  = []
    tree = ET.ElementTree(file=xml_file)
    for elem in tree.iter('{http://pmd.sourceforge.net/report/2.0.0}file'):
        for violation in elem.iter(tag='{http://pmd.sourceforge.net/report/2.0.0}violation'):
            begin = violation.get('beginline')
            priority=  violation.get('priority')
            key = commit + '_' + file_name + '_' + str(begin)
            if key in pmd_dict:
                if pmd_dict[key] > priority:
                    pmd_dict[key] = priority
            else:
                pmd_dict[key] = priority


# get the modified files after the commit
def get_pmd(commit, files):
    for file in files:
        try:
            subprocess.call(show_cmd.format(commit,file,file_tmp), shell=True,cwd=repo_dir)
        except:
            continue
        p = subprocess.Popen(pmd_cmd.format(file_tmp,xml_tmp), shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        stdout,stderr = p.communicate()


        parse_xml(commit,file,xml_tmp)
        subprocess.call(rm_cmd.format(file_tmp,xml_tmp),shell=True)

def main(repoId):
    add_csv = '/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/diff/' + repo_id + '/'+repo_id+'_add'

    # get commit hash
    session = Session()
    commits = (session.query(Commit).filter((Commit.repository_id==repoId))
               .order_by( Commit.author_date_unix_timestamp.desc()).all())
    # get pmd rank
    for commit in commits:
        files_tmp = commit.fileschanged.split(',CAS_DELIMITER,')
        files = []
        for item in files_tmp:
            name = item.strip(',CAS_DELIMITER')
            if name.endswith('.java'):
                files.append(name)
        if files != []:
            get_pmd(commit.commit_hash,files)

    # add new attribute in add.csv
    file = pd.read_csv(add_csv+'.csv')
    file['pmd'] = None
    for index, row in file.iterrows():
        test = row['commit_hash']+'_'+row['file_new'] + '_' + str(row['line_num'])
        if test in pmd_dict:
            file.loc[index,'pmd'] = pmd_dict[test]
        else:
            file.loc[index, 'pmd'] = 0
    file.to_csv(add_csv+'_pmd.csv',index=False)

    session.commit()
    session.close()
main(repo_id)
