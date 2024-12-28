import pandas as pd
import numpy as np
import sqlite3



fh = pd.read_csv('marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv')

print('Columns before cleaning:',fh.columns.size)
print('Rows before cleaning:', fh.shape[0])
fh = fh.replace("", pd.NA)

for column in fh.columns.values:
    if fh[column].isnull().sum() >= (fh.shape[0] * 87 /100):
        fh = fh.drop(column, axis=1)
        
fh =fh.drop(['Variants', 'Product Url', 'Shipping Weight', 'Category', 'Model Number', 
             'Is Amazon Seller', 'Technical Details', 'Product Specification'], axis=1)
fh.columns = fh.columns.str.replace(' ', '_').str.lower()
fh = fh[fh['selling_price'].str.len() <= 6]
fh['selling_price'] = fh['selling_price'].str.replace('$', '').str.replace('.','').str.replace(' ', '')
fh['selling_price'] = fh['selling_price'].str.replace(',', '')
fh = fh.dropna()
fh['selling_price'] = fh['selling_price'].astype(int)
fh['about_product'] = fh['about_product'].str.replace('Make sure this fits by entering your model number. | ','')
conn = sqlite3.connect('product.db')

random_numbers = np.random.choice([35, 40, 45, 50], size=len(fh))
random_review_count = np.random.randint(1,1000,size=len(fh))
fh['rating'] =  random_numbers
fh['review_count'] = random_review_count
fh.to_sql('product',conn, if_exists='replace', index=False)
conn.close()

# fh300.to_csv('new.csv',index=False)
print('Columns after cleaning:', fh.shape[1])
print('Rows after cleaning:', fh.shape[0])
