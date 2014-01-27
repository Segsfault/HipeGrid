# Copyright © 2014 California Institute of Technology, Pasadena, California.  
# Software written by Dr. Colin Borys at the Infrared Processing and Analysis
# Center (IPAC).  
# ALL RIGHTS RESERVED.  Based on Government Sponsored Research NAS7-03001.
# 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# Redistribution and use, with or without modification, are permitted provided
# that the following conditions are met:
# ·Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
# ·Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
# ·Neither the name of the California Institute of Technology (Caltech) nor the
#  names of its contributors may be used to endorse or promote products derived
#  from this software without specific prior written permission.
 
############
# Author Colin Borys (colin.borys@gmail.com)
#
# history
# 27 Jan 2014: v1.0 Initial public release
#


#!/usr/bin/env python
import MySQLdb
import sys, os
import shutil
import tempfile
import csv
import datetime
import subprocess
from mpi4py import MPI
from batchUtility import batchError,SqlConfiguration


 
class BatchProcess:
    def __init__(self,jobname):
        # keep track of how many obsids this instance has processed
        self.jobname=jobname

        self.sessionCounter=0
        try:
            rootDir=os.environ['HIPE_BATCH_ROOT']
        except KeyError:
            batchError("Environment variable HIPE_BATCH_ROOT is not set.")


        self.sql=SqlConfiguration(rootDir+'/bin/batch.cfg')
        self.templateFileName = rootDir+'/jobs/' + self.jobname+'/'+self.jobname+'.py'
        self.logDir = rootDir+'/jobs/' + self.jobname + '/log/'
        if os.path.isdir(self.logDir) == False :
            print 'LOG directory does not exist.  Creating now....'
            os.makedirs(self.logDir)
        self.outDir = rootDir+'/jobs/' + self.jobname + '/output/'
        if os.path.isdir(self.outDir) == False :
            print 'OUTPUT directory does not exist.  Creating now....'
            os.makedirs(self.outDir)

        
    def wipeTable(self):
        ''' This function will erase an entire table
        '''
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db )
        cursor = db.cursor()
        cursor.execute('DROP TABLE IF EXISTS '+self.jobname)
    
    def newTableFromBlkr(self):
        ''' This function creates a new trend analysis tracking table based on
            the original bulk-reprocessed table. 
            By default it uses ALL obsids.  To change the default, uncomment the lines below
            and edit to taste.
        '''
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db)
        cursor = db.cursor()
        try:
            cursor.execute("CREATE TABLE "+self.jobname+" AS (SELECT obsid,pipelined FROM "+self.sql.table)
            #cursor.execute("CREATE TABLE "+self.jobname+" AS (SELECT obsid,pipelined FROM "+self.sql.table + \
            #               " WHERE max_level = 'LEVEL2_PROCESSED' OR max_level='LEVEL2_5_PROCESSED')")
        except:
            batchError("Unable to create table [%s] in database [%s]" % (self.jobname,self.sql.db))  
    
        try:
            cursor.execute("UPDATE "+self.jobname+" SET pipelined=0")
            db.commit()
        except:
            batchError("Unable to clear flag in table [%s] in database [%s]" % (self.jobname,self.sql.db)) 

    def newTableFromList(self,obsidFileName):
        ''' This function creates a new processing table, based on a list of obsids
            in a csv file.
        '''
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db)
        cursor = db.cursor()
        try:
            cursor.execute("CREATE TABLE "+self.jobname+" "+\
                           "(obsid int(10) NOT NULL PRIMARY KEY, pipelined int(1) default 0)")
        except:
            batchError("Unable to create table [%s] in database [%s]" % (self.jobname,self.sql.db))  

        obsids=[]
        with open(obsidFileName,'rb') as f :
            reader=csv.reader(f)
            for row in reader :
                obsids.append(row[0])
        obsids=set(obsids)
        obsids=list(obsids)
     
        
        for obsid in obsids : # check to make sure these are #s, then add to table
            validObsid=True
            try:
                o=int(obsid)
            except:
                validObsid=False
            if validObsid :
                cursor.execute("INSERT INTO "+self.jobname+" (obsid) VALUES("+str(o)+")")
        db.commit()



      
    def getNextObsid(self):
        ''' Fetches the next available obsid from the database and sets the processed flag
            Returns None if no obsids are left.
        '''
        # Open database connection
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        # Lock table so we have exclusive access to it.
        cursor.execute("LOCK TABLE "+self.jobname+" WRITE")
            
        # Get next free obsid and set the pipelined flag.
        cursor.execute("SELECT obsid FROM "+self.jobname+" WHERE pipelined=0 ORDER BY obsid")
        result=cursor.fetchone()
        if result == None :
            obsid=None
        else:
            obsid= result[0]          
            cursor.execute("UPDATE "+self.jobname+" SET pipelined=1 WHERE obsid="+str(obsid))
            db.commit()
      
        # done with database, so unlock and close it.
        cursor.execute("UNLOCK TABLES")      
        db.close()
        return obsid    

    def reset(self):
        ''' Sets the "pipelined" value to 0 for all entries in the table.
        '''
        # Open database connection
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        cursor.execute("UPDATE "+self.jobname+" SET pipelined=0 WHERE pipelined=1")
        db.commit()   
        db.close()
 


    def run(self):
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()+1
        name = MPI.Get_processor_name()
        t0=datetime.datetime.now()
        done = False
        while not done :
            obsid=self.getNextObsid()
            if obsid==None :
                done=True
            else :   
                self.sessionCounter +=1
                tmpPalCacheDir=tempfile.mkdtemp()
                f = tempfile.NamedTemporaryFile(suffix=".py",delete=False)
                f.write('obsid='+str(obsid)+'\n')
                f.write('outDir=\"'+self.outDir+'\"\n')
                with open(self.templateFileName, 'r') as g:
                    f.write(g.read())
                f.close()
                print '.....  [Slot %d/%d on %s] [#%4i, obsid=%d] ' % (rank,size,name, self.sessionCounter,obsid)
                jyScript="hipe -properties java.vm.memory.max=2048m hcss.ia.pal.pool.cache.dir="+tmpPalCacheDir+" "+f.name  
                #jyScript="echo "+f.name  
                p = subprocess.Popen(jyScript, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
                (stdout, stderr) = p.communicate()
                os.unlink(f.name)
                shutil.rmtree(tmpPalCacheDir,ignore_errors=True)
                f=open(self.logDir+str(obsid)+'.stdout','w')
                f.write(stdout)
                f.close()
                f=open(self.logDir+str(obsid)+'.stderr','w')
                f.write(stderr)
                f.close()
        t1=datetime.datetime.now()
        deltaMinutes=(t1-t0).seconds/60.0
        print "%s SLOT %d SUMMARY: %d obsids processed in %6.1f minutes (%6.1f minutes/obsid)" % (name,rank,self.sessionCounter,deltaMinutes, deltaMinutes/self.sessionCounter)
        
           
    def status(self):
        ''' Queries the database to see how many obsids are left to process
        '''
        db = MySQLdb.connect(self.sql.host,self.sql.user,self.sql.pswd,self.sql.db )
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
            
        # Get next free obsid and set the pipelined flag.
        cursor.execute("SELECT COUNT(obsid) FROM "+self.jobname+" WHERE pipelined=1")
        result=cursor.fetchone()
        doneCount=result[0]
    
        cursor.execute("SELECT COUNT(obsid) FROM "+self.jobname)
        result=cursor.fetchone()
        allCount=result[0]
    
        print "%i of %i processed. (%3.1f %%, %i remaining)" % (doneCount, allCount, 100.0*float(doneCount)/float(allCount),allCount-doneCount)
       

                
''' This is the main program.
First we parse the config file to get the sql database parameters.
Then we parse the command and execute the relevant block of code.
'''
            

if len(sys.argv) <3 :
    sys.exit('usage: '+sys.argv[0]+ ' jobname command [obsidFileName]')
 
jobname = sys.argv[1]
command = sys.argv[2]
    
bp=BatchProcess(jobname)
if command == 'wipe' :
    bp.wipeTable()
elif command == 'new' :
    if len(sys.argv) ==3 :
        bp.newTableFromBlkr()
    else :
        bp.newTableFromList(sys.argv[3])
elif command == 'run' :
    bp.run()
elif command == 'status' :
    bp.status()
elif command =='reset' :
    bp.reset()
else :
    sys.exit('ERROR: command not recognized')
    


