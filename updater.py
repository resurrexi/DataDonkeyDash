import sys
import pyodbc
import config
import pandas as pd

### RUN THIS MONTHLY ON THE 30TH OF EVERY MONTH ###
filepath = sys.path[0]
filename = sys.path[0] + "\\" + sys.argv[0]
cnnx = pyodbc.connect('DRIVER={IBM DB2 ODBC DRIVER - DB2COPY1};DBALIAS=EDW5P1;UID=' + config.usr + ';PWD=' + config.fbpass)

print "Running {0}".format(filename)

query = """
select last_day(max(MDLX_RTGP_END_DT)) as MAX_DATE
from EDWPVW.EDW_HD_CNSR_CND
"""

result = pd.read_sql_query(query, cnnx)

cnnx.close()

result.to_csv(filepath + '/static/data/HD_Max_Date.csv', index=False)