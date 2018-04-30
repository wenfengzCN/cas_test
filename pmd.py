#!/usr/bin/python3
import threading
import subprocess
import json
import time
import logging
import pandas as pd
import xml.etree.ElementTree as ET

config = json.load(open('./pmd_config.json'))
BASIC_PATH = config['BASIC_PATH']
PMD_PATH = config['PMD_PATH']

class MyThread(threading.Thread):
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)

class Pmd():
    """
    get pmd result

    """

    SHOW_CMD = 'git show {!s}:{!s} > {!s}'
    PMD_CMD= PMD_PATH + 'bin/run.sh pmd -d {!s} -f xml -r  {!s} -rulesets  category/java/codestyle.xml,' \
              'category/java/bestpractices.xml,category/java/documentation.xml,category/java/errorprone.xml,category/java/multithreading.xml,' \
              'category/java/performance.xml,category/java/design.xml -cache {!s}'
    RM_CMD = 'rm {!s} {!s}'
    MAX_LINE = 10000

    def __init__(self,repo_id,time_logger):
        self.repo_id = repo_id
        self.java_tmp = BASIC_PATH + 'cas_test/tmp/tmp_' + repo_id + '.java'
        self.xml_tmp = './tmp/tmp_' + repo_id + '.xml'
        self.cache_tmp = './tmp/cache_' + repo_id
        self.repo_dir = BASIC_PATH + 'cas_vlis/ingester/CASRepos/git/' + repo_id
        self.test_csv = BASIC_PATH + 'testset/' +repo_id+'_test'
        # init log
        self.basic_logger = logging.getLogger(repo_id+' log')
        self.basic_logger.setLevel(logging.INFO)
        self.basic_logger.addHandler(logging.FileHandler("./log/" + repo_id + '.log'))
        self.time_logger = time_logger


    def parse_xml(self, commit, file_name, xml_file):
        tree = ET.ElementTree(file=xml_file)
        pmd_result = {}
        for elem in tree.iter('{http://pmd.sourceforge.net/report/2.0.0}file'):
            for violation in elem.iter(tag='{http://pmd.sourceforge.net/report/2.0.0}violation'):
                begin = violation.get('beginline')
                priority=  violation.get('priority')
                key = commit + '_' + file_name + '_' + str(begin)
                if key in pmd_result:
                    if pmd_result[key] > priority:
                        pmd_result[key] = priority
                else:
                    pmd_result[key] = priority
        return pmd_result


    # get the modified files after the commit
    def get_pmd(self,commit, file):
        try:
            subprocess.call(self.SHOW_CMD.format(commit,file,self.java_tmp), shell=True,cwd=self.repo_dir)
        except:
            pass
        p = subprocess.Popen(self.PMD_CMD.format(self.java_tmp, self.xml_tmp,self.cache_tmp), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        self.basic_logger.info(stdout)
        self.basic_logger.info(stderr)
        pmd_result = self.parse_xml(commit,file,self.xml_tmp)
        subprocess.call(self.RM_CMD.format(self.java_tmp,self.xml_tmp),shell=True)
        return pmd_result

    def pmdMain(self):
        process_start = time.process_time()
        print (self.repo_id,'Begining to analyze!')
        file = pd.read_csv(self.test_csv+'.csv',encoding='ISO-8859-1').assign(pmd=None)
        d_row = file.duplicated(['commit_hash','file_new'],'first')
        pmd_reslut = {}

        for index, row in file.iterrows():
            if d_row[index] == False:
                # a new version of file and start pmd program
                pmd_reslut = self.get_pmd(row['commit_hash'],row['file_new'])

            test = row['commit_hash'] + '_' + row['file_new'] + '_' + str(row['line_num'])
            if test in pmd_reslut:
                file.loc[index,'pmd'] = pmd_reslut[test]
            else:
                file.loc[index, 'pmd'] = 0
        file.to_csv(self.test_csv+'_pmd.csv',index=False)
        process_end = time.process_time()
        cost_time = (process_end-process_start)/60
        print (self.repo_id, ': analyzing finished! using time(min:)', cost_time)
        self.time_logger.info(self.repo_id + " analyzing finished! using time(min):" + str(cost_time))

def loop(repo_id,time_logger):
    pmd = Pmd(repo_id,time_logger)
    pmd.pmdMain()

def main(repos):
    time_logger = logging.getLogger('time_consuming')
    time_logger.setLevel(logging.INFO)
    time_logger.addHandler(logging.FileHandler("./log/time_consuming.log" ))
    threads = []
    for repo in repos:
        t = MyThread(loop,(repo,time_logger))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__=='__main__':
    repos = []
    # while(True):
    #     x = input("Please input the repo to analyze('End' to finish input):")
    #     if x == 'End':
    #         print ("Begining to analyze!")
    #         break
    #     else:
    #         repos.append(x)
    main(repos)