'''
Created on 19 févr. 2017

@author: home
'''
import unittest
import logging
import os
import logchecker


class TestLogChecker(unittest.TestCase):

    def setUp(self):
        if os.path.isfile("app1.log"):
            open("app1.log", 'w').close()
        if os.path.isfile("app2.log"):
            open("app2.log", 'w').close()

    def tearDown(self):
        pass

    def test_1checkNewError(self):
        log1.error("checkNewError1")
        log1.error("checkNewError11")        
        log2.error("checkNewError2")
        log1.info("an info")
        log2.info("an other info")
        
        lc = logchecker.LogChecker("./")
        lc.compare()
        log2.error("checkNewError3")
        log2.error("checkNewError4")

        keys = lc.compare()
        self.assertEqual(len(keys), 2, "New error test success")
                
    def tst_11sendEmail(self):
        log1.error("checkNewError1")
        lc = logchecker.LogChecker("./")
        lc.compare()
        log2.error("checkNewError3")
        log2.error("checkNewError4")
        log2.error("checkNewError5")
        logchecker.main("./")

    def test_2checkNoError(self):
        lc = logchecker.LogChecker("./")
        lc.compare()
        keys = lc.compare()
        self.assertEqual(len(keys), 0, "No error test success")

    def test_3checkNoNewError(self):
        log1.error("checkNewError1")
        log1.error("checkNewError11")        
        log2.error("checkNewError2")
        log1.info("an info")
        lc = logchecker.LogChecker("./")
        lc.compare()
        keys = lc.compare()
        self.assertEqual(len(keys), 0, "No new error test success")    

    def test_4checkLessError(self):
        log1.error("checkLessError1")
        log1.error("checkLessError11")
        log2.error("checkLessError2")
        lc = logchecker.LogChecker("./")
        lc.compare()
        open("app2.log", 'w').close()
        keys = lc.compare()
        self.assertEqual(len(keys), 0, "Less error test success")

    def test_5checkNewAndLessError(self):
        log1.error("checkLessError1")
        log2.error("checkLessError2")
        lc = logchecker.LogChecker("./")
        lc.compare()
        open("app2.log", 'w').close()
        log1.error("checkLessError11")
        keys = lc.compare()
        self.assertEqual(len(keys), 1, "New and Less error test success")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log1 = logging.getLogger('app1')
    log1.setLevel(logging.INFO)
    hd1 = logging.FileHandler('app1.log')
    hd1.setLevel(logging.INFO)
    hd1.setFormatter(fmt)
    log1.addHandler(hd1)
    
    log2 = logging.getLogger('app2')
    log2.setLevel(logging.INFO)
    hd2 = logging.FileHandler('app2.log')
    hd2.setLevel(logging.INFO)
    hd2.setFormatter(fmt)
    log2.addHandler(hd2)

    unittest.main()