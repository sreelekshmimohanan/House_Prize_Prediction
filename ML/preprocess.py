
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd 


# In[2]:


data=pd.read_csv('Bengaluru_House_Data.csv')
data.head()


# In[3]:


data.info()


# In[4]:


data.columns


# In[5]:


data.dropna(inplace=True)
data.head()


# In[6]:


"""data.reset_index(inplace=True)
data.drop(["index"],axis=1,inplace)
data"""


# In[7]:


data.shape


# In[8]:


data['size'].unique()


# In[9]:


data['BHK']=data['size'].apply(lambda x: int(x.split(' ')[0]))


# In[10]:


data.head()


# In[11]:


data['HALL_KITCHEN']=data['size'].apply(lambda x: str(x.split(' ')[1]))


# In[12]:


data.HALL_KITCHEN.unique()


# In[13]:


def isfloat(x):
    try:
        float(x)
    except:
        return False
    return True


# In[14]:


data[~data['total_sqft'].apply(isfloat)].head()


# In[15]:


def convert_sqft_tonum(x):
    token=x.split('-')
    if len(token)==2:
        return (float(token[0])+float(token[1]))/2
    try:
        return float(x)
    except:
        return None


# In[16]:


data=data.copy()
data['total_sqft']=data['total_sqft'].apply(convert_sqft_tonum)


# In[17]:


data.head()


# In[18]:


data1=data.copy()
data1['price_per_sqft']=data1['price']*1000000/data1['total_sqft']
data1.head()


# In[19]:


data1.location=data1.location.apply(lambda x: x.strip())
location_stats=data1.groupby('location')['location'].agg('count').sort_values(ascending=False)
location_stats.head()


# In[20]:


locationlessthan10=location_stats[location_stats<=10]
len(locationlessthan10)


# In[21]:


location_new=[]
for ind in data1.index:
    #print(data1['location'][ind])
    if str(data1['location'][ind]) in locationlessthan10:
        location_new.append("other")
    else:
        location_new.append(str(data1['location'][ind]))
#data1.location=data1.location.apply(lambda x: 'other' if x in locationlessthan10 else x)
#len(data1.location.unique())
len(location_new)


# In[22]:


data1['location_new']=location_new


# In[23]:


data1.head()


# In[24]:


data1[data1.total_sqft/data1.BHK<300].head()


# In[25]:


data2=data1[~(data1.total_sqft/data1.BHK<300)]
data2.head()


# In[26]:


data2.shape


# In[27]:


data2["price_per_sqft"].describe().apply(lambda x:format(x,'f'))


# In[28]:


def remove_pps_outliers(df):
    df_out=pd.DataFrame()
    for key,subdf in df.groupby('location'):
        m=np.mean(subdf.price_per_sqft)
        st=np.std(subdf.price_per_sqft)
        reduced_df=subdf[(subdf.price_per_sqft>(m-st))& (subdf.price_per_sqft<(m+st))]
        df_out=pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out
data3=remove_pps_outliers(data2)
data3.shape


# In[29]:


def remove_bhk_outliers(df):
    exclude_indices=np.array([])
    for location, location_df in df.groupby('location'):
        bhk_sats={}
        for BHK,BHK_df in location_df.groupby('BHK'):
            bhk_sats[BHK]={
                'mean':np.mean(BHK_df.price_per_sqft),
                'std':np.std(BHK_df.price_per_sqft),
                'count':BHK_df.shape[0]
            }
        for BHK,BHK_df in location_df.groupby('BHK'):
            stats=bhk_sats.get(BHK-1)
            if stats and stats['count']>5:
                exclude_indices=np.append(exclude_indices,BHK_df[BHK_df.price_per_sqft<(stats['mean'])].index.values)
    return df.drop(exclude_indices,axis='index')

data4=remove_bhk_outliers(data3)
data4.shape


# In[30]:


data5=data4[data4.bath<data4.BHK+2]
data5.shape


# In[48]:


data6=data5.drop(['size','price_per_sqft'],axis='columns')
data6.head()


# In[51]:


data6.HALL_KITCHEN.unique()


# In[52]:


data6['HALL_KITCHEN'].replace({'Bedroom':'B','RK':'BK'},inplace=True)


# In[53]:


print(data6.HALL_KITCHEN.unique())
data6.head()


# In[54]:


from datetime import date
m={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
d0 = date(2008, 1, 1)
availability_days=[]
for ind in data6.index:
    #print(data6['availability'][ind])
    if data6['availability'][ind]=='Ready To Move':
        availability_days.append(0)
    else:
        dt=str(data6['availability'][ind]).split('-')
        dy=int(dt[0])
        mn=int(m[str(dt[1])])
        d1 = date(2008, mn, dy)
        dys = d1 - d0
        availability_days.append(int(dys.days))


# In[55]:


data6['availability_days']=availability_days
data6.head()


# In[56]:


data6.area_type.unique()


# In[40]:


#data6.location_new.unique()


# In[41]:


#data6.to_csv("final_data.csv")


# In[57]:


data6.drop(["location","availability"],axis=1,inplace=True)
data6.head()


# In[59]:


#data.total_sqft.unique


# In[39]:


from datetime import date

d0 = date(2008, 8, 18)
d1 = date(2008, 9, 12)
delta = d1 - d0
print(delta.days)

