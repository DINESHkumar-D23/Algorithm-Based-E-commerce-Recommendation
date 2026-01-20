# import pandas as pd
# import numpy as np
# data = pd.read_csv('clean_data.csv')

# def process_data(data: pd.DataFrame) -> pd.DataFrame:
#     data['ProdID']=data['ProdID'].replace(-2147483648, np.nan)
#     data['ID']=data['ID'].replace(-2147483648, np.nan)

#     data['ID']=pd.to_numeric(data['ID'], errors='coerce')
#     data = data.dropna(subset=['ID'])
#     data = data.dropna(subset=['ProdID'])

#     data=data[(data['ID']!=0 ) & (data['ProdID']!=0)].copy()
#     data['ID']=data['ID'].astype(int)
#     data['ProdID']=data['ProdID'].astype(int)
#     data['ReviewCount']=pd.to_numeric(data['ReviewCount'], errors='coerce').fillna(0).astype(int)

#     if 'Unamed: 0' in data.columns:
#         data = data.drop(columns=['Unnamed: 0'])    

#     for col in ['Category', 'Brand','Description' ,'Tags']:
#         data[col] = data[col].fillna('')
#     return data

import pandas as pd
import numpy as np
data = pd.read_csv('clean_data.csv')

def process_data(data: pd.DataFrame) -> pd.DataFrame:
    data['ProdID']=data['ProdID'].replace(-2147483648, np.nan)
    data['ID']=data['ID'].replace(-2147483648, np.nan)

    data['ID']=pd.to_numeric(data['ID'], errors='coerce')
    data = data.dropna(subset=['ID'])
    data = data.dropna(subset=['ProdID'])

    data=data[(data['ID']!=0 ) & (data['ProdID']!=0)].copy()
    data['ID']=data['ID'].astype(int)
    data['ProdID']=data['ProdID'].astype(int)
    data['ReviewCount']=pd.to_numeric(data['ReviewCount'], errors='coerce').fillna(0).astype(int)

    if 'Unamed: 0' in data.columns:
        data = data.drop(columns=['Unnamed: 0'])    

    for col in ['Category', 'Brand','Description' ,'Tags']:
        data[col] = data[col].fillna('')
    return data
