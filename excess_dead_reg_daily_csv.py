# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 10:46:35 2020

@author: pmaldonadol
"""


import pandas as pd
import numpy as np

# Se obtienen las defunciones desde url y se transforman a dataframe

reg_info=pd.read_json('http://192.168.2.223:5006/getStates', orient='columns')
defun_data=pd.read_json('http://192.168.2.223:5006/getAllDeathsAllStates', orient='slit')

for i in range(len(defun_data)):
    if i==0: 
        defun=pd.DataFrame(defun_data.iloc[i].values[0])
        defun['Codigo region']=i+1
        reg=reg_info.description[reg_info.id==i+1].values[0]
        defun['Region']=reg
    else:
        defun_tmp=pd.DataFrame(defun_data.iloc[i].values[0])
        defun_tmp['Codigo region']=i+1
        reg=reg_info.description[reg_info.id==i+1].values[0]
        defun_tmp['Region']=reg
        defun=defun.append(defun_tmp)

defun['Fecha']=defun['dates']
defun['Fecha']=pd.to_datetime(defun['Fecha']).dt.tz_localize(None)
defun['Defunciones']=defun['deaths']
defun=defun.drop(columns=['dates', 'deaths']) 
       

for i in range(1,17):
    if i==1:
        defun_covid=pd.read_json('http://192.168.2.223:5006/getDeathsByState?state='+str(i), orient='columns')
        defun_covid['Defunciones']=defun_covid.confirmed+defun_covid.suspected
        defun_covid['Codigo region']=i
        reg=reg_info.description[reg_info.id==i].values[0]
        defun_covid['Region']=reg
    else:
        defun_tmp=pd.read_json('http://192.168.2.223:5006/getDeathsByState?state='+str(i), orient='columns')
        defun_tmp['Defunciones']=defun_tmp.confirmed+defun_tmp.suspected
        defun_tmp['Codigo region']=i
        reg=reg_info.description[reg_info.id==i].values[0]
        defun_tmp['Region']=reg
        defun_covid=defun_covid.append(defun_tmp)

defun_covid['Fecha']=defun_covid['dates']
defun_covid['Fecha']=pd.to_datetime(defun_covid['Fecha']).dt.tz_localize(None)
defun_covid=defun_covid.drop(columns=['dates', 'confirmed', 'suspected'])



# Defunciones por periodo anual y mensual
defun['año']=pd.DatetimeIndex(defun['Fecha']).year
defun['mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('M')
defun['semana-mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('W')

defun_covid['año']=pd.DatetimeIndex(defun_covid['Fecha']).year
defun_covid['mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('M')
defun_covid['semana-mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('W')



#Calce de fechas
max_date=min([max(defun['Fecha']),max(defun_covid['Fecha'])])
defun=defun[defun['Fecha']<=max_date]
defun_covid=defun_covid[defun_covid['Fecha']<=max_date]

# Suma acumulativa para Nacimiento y Defunciones
defun_year=defun.groupby(['Codigo region','año']).sum()

# Plot y modelo de defunciones anuales por región
models=[]

for i in range(16):
    
    x=range(2019,2009,-1)
    y=defun_year.iloc[
        defun_year.index.get_level_values('Codigo region')== i+1].values[
            range(9,-1,-1)].flatten()
   
    mymodel = np.poly1d(np.polyfit(x, y, 1))
    models.extend([[mymodel,i+1]])

## Proyeccion de aumetno de población diaria por región se toma como primer día
##     
anos=np.unique(defun['año'])
defun['dias']=0
defun['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun=defun[defun['semana']>2]

for i in anos:    
    tmp=defun[defun['año']==i]['Fecha']
    s = pd.date_range(str(i)+'-01-01', str(i)+'-01-30', freq='D').to_series()
    basedate=s[np.logical_and(s.dt.dayofweek==0, s.dt.week==3)]
    defun.loc[defun['año']==i,'dias']=(pd.to_datetime(tmp) - basedate[0]).dt.days


defun_covid['semana']=pd.to_datetime(defun_covid['Fecha']).dt.week
defun_covid=defun_covid[defun_covid['semana']>1]
s = pd.date_range('2020-01-01', '2020-01-30', freq='D').to_series()
basedate=s[np.logical_and(s.dt.dayofweek==0, s.dt.week==3)]
defun_covid['dias']=(pd.to_datetime(defun_covid['Fecha']) - basedate[0]).dt.days
defun_covid=defun_covid.sort_values(by=['Codigo region','dias'])


defun_dia=defun.groupby(['Codigo region','año','dias']).sum()
defun_covid_dia=defun_covid.groupby(['Codigo region','año','dias']).sum()    


# Defunciones proyectadas por modelo por región semana para cada región
dias_2020=np.array(range(max(defun_covid_dia.index.get_level_values('dias'))+1))
defun_pro=np.zeros((16,dias_2020.shape[0]))
defun_pro_min=np.zeros((16,dias_2020.shape[0]))
defun_pro_max=np.zeros((16,dias_2020.shape[0]))
defun_pro_min_1=np.zeros((16,dias_2020.shape[0]))
defun_pro_max_1=np.zeros((16,dias_2020.shape[0]))


for i in range(16):
    acum=np.zeros((10,dias_2020.shape[0]))
    for j in range(9):    
        
        y=np.array(defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2010+j,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
        x=np.array(defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2010+j,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)].index.get_level_values('dias'))
        ind=np.intersect1d(dias_2020,x)
        acum[j,ind]=y[0:len(ind)]*models[i][0](2020)/models[i][0](2010+j)

    # print(acum)
    defun_pro[i,:]=np.mean(acum,axis=0)
    defun_pro_min[i,:]=np.mean(acum,axis=0)-2*np.std(acum,axis=0)
    defun_pro_max[i,:]=np.mean(acum,axis=0)+2*np.std(acum,axis=0)
    defun_pro_min_1[i,:]=np.mean(acum,axis=0)-1*np.std(acum,axis=0)
    defun_pro_max_1[i,:]=np.mean(acum,axis=0)+1*np.std(acum,axis=0)

excess_dead=pd.DataFrame()

for i in range(16):
        
    y=defun_pro[i,:]
    y_1s=defun_pro_max_1[i,:]
    y_2s=defun_pro_max[i,:]
    y_1sm=defun_pro_min_1[i,:]
    y_2sm=defun_pro_min[i,:]

    x=defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2020,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)].index.get_level_values('dias')
    y_2020=np.array(defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2020,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
    tmp=np.zeros(dias_2020.shape[0])
    tmp[x]=y_2020
    y_2020=tmp
    
    x_covid=defun_covid_dia.iloc[np.logical_and(defun_covid_dia.index.get_level_values('año') == 2020,  
                                    defun_covid_dia.index.get_level_values('Codigo region') == i+1)].index.get_level_values('dias')
    y_covid=np.array(defun_covid_dia.iloc[np.logical_and(defun_covid_dia.index.get_level_values('año') == 2020,
                                defun_covid_dia.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
    tmp=np.zeros(dias_2020.shape[0])
    tmp[x_covid]=y_covid
    y_covid=tmp
    
    tmp_excess=np.array([pd.date_range(basedate[0],max(pd.to_datetime(defun_covid['Fecha'])),freq='D'),dias_2020,y_2020,y_covid,y,y_2020-y_covid,y_2020-y_covid-y,y_2s,y_1s,y_1sm,y_2sm]).transpose()
    tmp_excess=pd.DataFrame(data=tmp_excess,columns=['fecha','dia','defunciones_totales',
                                                  'defunciones_covid','media',
                                                  'defunciones_no_covid','exceso_media','exceso_2S','exceso_1S','exceso_minus1S','exceso_minus2S'])
    tmp_excess['region']=str(i+1).zfill(2)
    excess_dead=excess_dead.append(tmp_excess)

excess_dead.to_csv("excess_dead_reg_daily.csv",index=False)