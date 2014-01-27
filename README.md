HIFI/HIPE Batch processing framework.
Written by Colin Borys, borys@caltech.edu
**********************************************
The Herschel Interactive Processing Environment (HIPE) is a data analysis package written in Java, scriptable with Python, and developed using an Agile philosophy.  
It is tailored for the large data volume collected by the Herschel Space Telescope.  The software is an international collaboration with >100 contributors.  
To obtain HIPE, go to: http://herschel.esac.esa.int/HIPE_download.shtml
While great at interactive processing of single observations, it is not as straightforward to run it in an unattended batch mode.

The software in this repository allows the user to apply a script to Herschel data in batch mode, utilizing any number of computers to speed up processing.
HIFI is a spectrometer on the Herschel Space Telescope, and requires the HIPE application to process data from.  For an overview, you can read the following blog post:
http://segsfault.com/blog/?p=1


A MySQL database is used to keep track of obsids to process, and can optionally be used to store the output of a analysis.
Other SQL variants can be used with appropriate modifications to the codebase.

example usage:
1. Setup a new job where ALL obsids will be processed:
BatchProcess.py testRun new

The result will be a new subdirectory called 'jobs/testRun' in the root directory of the installation.  Also, a new SQL table named 'testRun' will be created.

2. Setup a new job where only certain obsids will be processed:
BatchProcess.py testRun new myObsids.txt

The result is the same as in (1).  The text file has a list of obsids, one per line.

3. Reset a failed run.
BatchProcess.py testRun reset

This sets the 'pipelined' column in the 'testRun' SQL to zeros.

4. Initiate a batch run using a single instance of HIPE.
BatchProcess.py testRun run

Result: HIPE will be loaded once per obsid. It will execute the script, then exit.  When all obsids are process, the task will complete.

5. Get status of a run:
BatchProcess.py testRun status

Result: Text indicating how many obsids have been processed.

6. Initiate a run across multiple HIPE sessions
BatchProcess_mpi.sh testRun

Result: using the 'hostfile', the script will spawn the BatchProcess.py 'run' command on multiple computers via openMPI, allowing for parallelized execution of the script.  This is the preferred (and much faster) option.




PREQUISITES:
For all computers that will execute a script, the following needs to be installed:

1. The mysql-connector jar file must be installed as part of the classpath.
   - http://dev.mysql.com/downloads/connector/j/
2. Python hooks for MySQL must be installed:
   - http://mysql-python.sourceforge.net/
3. OpenMPI must be installed and in the path.
   - http://www.open-mpi.org/
4. Python hooks for openMPI must be installed:
   - http://mpi4py.scipy.org/
5. HIPE must be installed and in the path.
   - http://herschel.esac.esa.int/HIPE_download.shtml


A NOTE ON DIRECTORIES:
The code was setup assuming the following:

A 'root' directory where the executables and output from jobs is stored.
This needs to be defined as an environment variable (see below)

In my particular setup, I have the following:
HIPE_BATCH_ROOT/
   bin/
      BatchProcess.py
      BatchProcess_mpi.sh
      batch.cfg
      batchUtility.py
      hostfile
      readme.txt    
   jobs/
      testRun/
         testRun.py
         log/
         output/
   lib/
      mysql-connector-java-5.1.22-bin.jar

ENVIRONMENT VARIABLES:
here is a BASH version of my setup:

export HIPE_BATCH_ROOT=/hifi/batchProcessing/
# setup mysql/jython class file.
mysqljar=$HIPE_BATCH_ROOT/lib/mysql-connector-java-5.1.22-bin.jar
if [ -z $CLASSPATH ]; then
   export CLASSPATH=$mysqljar 
else
   export CLASSPATH=$mysqljar:${CLASSPATH}
fi
unset mysqljar

export PATH=$HIPE_BATCH_ROOT/bin:$PATH



The batch.cfg configuration file:

[sql]
host      = mysqlserver.mydomain.edu
user      = hipeuser
pswd      = sqlpasswd
db        = blkr
table     = v11_1
     
The config file 'table' should refer to the master SQL table where all obsids are stored.

The hostfile (for openMPI execution).  In this example, 15 HIPE sessions will be run simultaneously

#Example host file for OpenMPI processing.

# Run 2 HIPEs on the local machine:
localhost slots=2 max_slots=2

# Run 10 instances on a remote high-compute server (30 cores):
myremote1.ipac.caltech.edu slots=10 max_slots=10

# Run 3 instances on a remote quad-core computer:
myremote1.ipac.caltech.edu slots=3 max_slots=3


Finally, an SQL dump of the complete list of HIFI observations is provided.  It is 
based on the HIPE 11.1 pipeline.

