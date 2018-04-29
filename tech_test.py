import logging
import threading
import json
#
# class Pmd():
#     def __init__(self,name,logger):
#         self.name = name
#         self.logger = logger
#
#
# class Mythread(threading.Thread):
#     def __init__(self,func,name,logger):
#         threading.Thread.__init__(self)
#         self.func = func
#         self.name = name
#         self.logger = logger
#
#     def run(self):
#         self.func(self.name,self.logger)
#
# def test(name,logger):
#     pmd = Pmd(name,logger)
#     pmd.logger.info(name)
#
#
# if __name__ == '__main__':
#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)
#     logger.addHandler(logging.FileHandler('test.log'))
#     thread1 = Mythread(test,'thread1',logger)
#     thread2 = Mythread(test,'thread2',logger)
#     thread1.start()
#     thread2.start()
#
config = json.load(open('./pmd_config.json'))
pmd_path = config['PMD_PATH']
print (pmd_path)