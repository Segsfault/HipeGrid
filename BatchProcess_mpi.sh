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


#!/bin/csh -f
mpirun -hostfile  ${HIPE_BATCH_ROOT}/bin/hostfile BatchProcess.py $1 run 
