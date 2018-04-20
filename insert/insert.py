import pandas as pd
from sqlalchemy import *

engine = create_engine('mysql+pymysql://crm:1umtc1@localhost:3306/crm')
df = pd.read_csv('/home/ubuntu/crm/insert/id2.csv', delimiter=';')
df.to_sql('clinic', con=engine, flavor='mysql') # replace truncates the existing table and creates a new one
