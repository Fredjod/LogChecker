#!/usr/local/bin/python3.5
# encoding: utf-8
'''
Created on 16 févr. 2017

@author: FredJod
The purpose is to grep "ERROR" (case insensitive) string in a given directory of .log files.
If any new Error has been logged since the last LogChecker execution, a report is sent by email.
Between 2 executions, the grep result is stored in a .check_error.json file in the same directory than the script
This script takes into account the case of some errors are removed from logs between 2 executions
The .check_error.json data structure is
    { "md5line" : { "file_name" : "file.log" , "log_line" : "2016-12-12T20:30:12:ERROR:Balances integrity testing failded" }, .. }

'''
import os,sys
import hashlib
import re
import json
import parameters

class LogChecker():

    def __init__(self, logdir):
        self.__grep_error =  {}
        self.__logdir = logdir
    
    def getErrorLine(self, key_md5):
        return self.__grep_error.get(key_md5)
        
    def saveErrorLogs(self):
        try:
            with open('.check_error.json', 'w') as outfile:
                json.dump(self.__grep_error, outfile)
        finally:
                outfile.close()
    
    def parseLogsForError(self):
        grep_error={}
        files = [f for f in os.listdir(self.__logdir) if re.match(r'.*\.log', f)]
        for f in files:
            try:
                fd = open(os.path.join(self.__logdir, f), 'r')
                for line in fd:
                    if re.search('error', line, re.IGNORECASE):
                        record = {}
                        record.update({'file_name': f, 'log_line': line.strip( '\n' )})
                        grep_error[self.md5(line)] = record
            finally:
                fd.close()
        self.__grep_error = grep_error
        return grep_error       
    
    def loadPreviousErrorLogs(self):
        json_data = None
        json_file = '.check_error.json'
        if os.path.isfile(json_file):
            with open(json_file) as json_fd:
                json_data = json.load(json_fd)
        return json_data
    
    def compare(self):
        previous_json = self.loadPreviousErrorLogs()
        current_json = self.parseLogsForError()
        new_errors = {}
        if previous_json != None:
            new_errors = set(current_json.keys()) & set(previous_json.keys()) ^ set(current_json.keys())
        self.saveErrorLogs()
        return new_errors
    
    def md5(self, line):
        return hashlib.md5(line.encode('utf-8')).hexdigest()
    
    def sendmail(self, body):
        import smtplib
        import email.mime.multipart
        import email.mime.text
     
        fromaddr = parameters.MAILING_FROM
        toaddr = parameters.MAILING_LIST
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = parameters.MAILING_SUBJECT
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
     
        try:
            server = smtplib.SMTP(parameters.SMTP_SERVER)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
        except smtplib.SMTPException as e:
            raise e

def main(logdir):
    lc = LogChecker(logdir)
    error_keys = lc.compare()
    if len(error_keys) > 0:
        body = "New errors reported in "+logdir+"\n"
        for k in error_keys:
            body += lc.getErrorLine(k).get('file_name')+": "+lc.getErrorLine(k).get('log_line')+'\n'
        lc.sendmail(body)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        print ("Usage: logchecker /dir/of/logs/")
