import pandas as pd
import numpy as np

def process_data(data: pd.DataFrame) -> pd.DataFrame:
    # Fix corrupted integer values
    data['ProdID'] = data['ProdID'].replace(-2147483648, np.nan)
    data['ID'] = data['ID'].replace(-2147483648, np.nan)

    data['ID'] = pd.to_numeric(data['ID'], errors='coerce')
    data['ProdID'] = pd.to_numeric(data['ProdID'], errors='coerce')

    data = data.dropna(subset=['ID', 'ProdID'])
    data = data[(data['ID'] != 0) & (data['ProdID'] != 0)].copy()

    data['ID'] = data['ID'].astype(int)
    data['ProdID'] = data['ProdID'].astype(int)

    data['ReviewCount'] = (
        pd.to_numeric(data['ReviewCount'], errors='coerce')
        .fillna(0)
        .astype(int)
    )

    # ImageURL cleanup
    if 'ImageURL' in data.columns:
        data['ImageURL'] = data['ImageURL'].astype(str)
        data['ImageURL'] = data['ImageURL'].str.split('|').str[0]
        data = data[~data['ImageURL'].str.lower().isin(
            ['nan', 'none', 'null', 'undefined']
        )]
        data = data[data['ImageURL'].str.strip().ne('')]
        data = data[data['ImageURL'].str.match(r'^https?://.+')]

    if 'Unnamed: 0' in data.columns:
        data = data.drop(columns=['Unnamed: 0'])

    for col in ['Category', 'Brand', 'Description', 'Tags']:
        data[col] = data[col].fillna('')

    return data.reset_index(drop=True)
