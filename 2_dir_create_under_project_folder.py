# create dir for data, fig, raw, and tables 

import os 
dir_path = os.getcwd()
root_dir = os.path.dirname(dir_path)
print("Root directory: " + root_dir)
#this is my file path please adapt it to your directory


#stored raw data
#File path to the raw data. They are usually stored at a different location than the rest of the project.
raw_data_dir = os.path.join(root_dir, 'raw_data')
print("Raw data dir: "  + raw_data_dir)

#data proc
#The data directory contains all processed data and `anndata` files. 
data_dir = os.path.join(root_dir, 'data') 
if(not os.path.exists(data_dir)):
    os.mkdir(data_dir)
print("Proc data dir: " + data_dir)

#The tables directory contains all tabular data output, e.g. in `.csv` or `.xls` file format. That applies to differential expression test results or overview tables such as the number of cells per cell type.
table_dir = os.path.join(root_dir, 'tables')
if(not os.path.exists(table_dir)):
    os.mkdir(table_dir)
print("Table dir: " + table_dir)

#The default figure path is a POSIX path calles 'figures'. If you don't change the default figure directory, scanpy creates a subdirectory where this notebook is located.  
sc.settings.figdir = os.path.join(root_dir, 'figures')
if(not os.path.exists(sc.settings.figdir)):
    os.mkdir(sc.settings.figdir)
print("Fig dir: " + sc.settings.figdir.)


#When you repeat certain analyses, it might be helpful to set a date variable and add it to every figure and table (see `datetime` Python package).
import datetime
today = datetime.datetime.now().strftime('%Y%m%d') #creates a YYMMDD string of today's date
print("Today's label: " + today)
