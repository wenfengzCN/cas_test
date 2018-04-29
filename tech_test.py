import logging
import threading
import json
import pandas as pd
file = pd.read_csv('/home/wenfeng/vlis/testset/jetty1710_test.csv',encoding='ISO-8859-1').assign(pmd=None)
file.to_csv('/home/wenfeng/jetty_test.csv',index=False)