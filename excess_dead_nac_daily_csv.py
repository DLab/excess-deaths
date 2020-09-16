# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 10:30:34 2020

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
defun=defun.groupby(['Fecha']).sum()
defun=defun.drop(columns=['deaths','Codigo region']) 
defun.reset_index(inplace=True)      

for i in range(1,17):
    if i==1:
        defun_covid_N=pd.read_json('http://192.168.2.223:5006/getDeathsByState?state='+str(i), orient='columns')
        defun_covid_N['Defunciones']=defun_covid_N.confirmed+defun_covid_N.suspected
        defun_covid_N['Codigo region']=i
        reg=reg_info.description[reg_info.id==i].values[0]
        defun_covid_N['Region']=reg
    else:
        defun_tmp=pd.read_json('http://192.168.2.223:5006/getDeathsByState?state='+str(i), orient='columns')
        defun_tmp['Defunciones']=defun_tmp.confirmed+defun_tmp.suspected
        defun_tmp['Codigo region']=i
        reg=reg_info.description[reg_info.id==i].values[0]
        defun_tmp['Region']=reg
        defun_covid_N=defun_covid_N.append(defun_tmp)

defun_covid_N['Fecha']=defun_covid_N['dates']
defun_covid_N['Fecha']=pd.to_datetime(defun_covid_N['Fecha']).dt.tz_localize(None)
defun_covid_N=defun_covid_N.groupby(['Fecha',]).sum()
defun_covid_N=defun_covid_N.drop(columns=['confirmed', 'suspected','Codigo region'])
defun_covid_N.reset_index(inplace=True)


# Defunciones por periodo anual y mensual
defun['año']=pd.DatetimeIndex(defun['Fecha']).year
defun['mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('M')
defun['semana-mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('W')

defun_covid_N['año']=pd.DatetimeIndex(defun_covid_N['Fecha']).year
defun_covid_N['mes-año']=pd.to_datetime(defun_covid_N['Fecha']).dt.to_period('M')
defun_covid_N['semana-mes-año']=pd.to_datetime(defun_covid_N['Fecha']).dt.to_period('W')


#Calce de fechas
max_date=min([max(defun['Fecha']),max(defun_covid_N['Fecha'])])
defun=defun[defun['Fecha']<=max_date]
defun_covid_N=defun_covid_N[defun_covid_N['Fecha']<=max_date]


# Modelos nacional
defun_year_all=defun.groupby(['año']).sum()
y=defun_year_all['Defunciones'].iloc[range(9,-1,-1)].values
x=range(2019,2009,-1)
anual_model_l = np.poly1d(np.polyfit(x, y, 1))
anual_model_c = np.poly1d(np.polyfit(x, y, 2))
myline=np.linspace(2020, 2010, 100)

## Proyeccion de aumetno de población semanales totales

defun['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun_covid_N['semana']=pd.to_datetime(defun_covid_N['Fecha']).dt.week

defun_week=defun.groupby(['año','semana']).sum()
defun_covid_week=defun_covid_N.groupby(['año','semana']).sum()
# defun_covid_week=defun_covid_week[defun_covid_week.index.get_level_values('semana')!=23]


anos=np.unique(defun['año'])
defun['dias']=0
for i in anos:    
    tmp=defun[defun['año']==i]['Fecha']
    basedate=pd.to_datetime(str(i)+'-01-01')
    defun.loc[defun['año']==i,'dias']=(pd.to_datetime(tmp) - basedate).dt.days

defun_dia=defun.groupby(['año','dias']).sum()

basedate=pd.to_datetime('2020-01-01')
defun_covid_N['dias']=(pd.to_datetime(defun_covid_N['Fecha']) - basedate).dt.days
defun_covid_N=defun_covid_N.sort_values(by=['dias'])
#defun_covid_N['Defunciones']=np.zeros(len(defun_covid_N['dias']))


#tmp=defun_covid_N['Total']
#tmp=np.insert(np.diff(tmp),0,tmp.values[0])
#defun_covid_N['Defunciones']=tmp    
# 

# Defunciones proyectadas por modelo lineal pais dia
dias_2020=np.array(range(max(defun_covid_N['dias'])+1))


acum=np.zeros((10,dias_2020.shape[0]))
for j in range(10):    
            

        
    y=np.array(defun_dia.iloc[defun_dia.index.get_level_values('año') == 2010+j]['Defunciones'])
    x=np.array(defun_dia.iloc[defun_dia.index.get_level_values('año') == 2010+j].index.get_level_values('dias'))
    # print(y[0:semanas_2020.shape[0]]*models[i][0](2010+j)/models[i][0](2020))
    ind=np.intersect1d(dias_2020,x)          
    acum[j,ind]=y[ind]*anual_model_l(2020)/anual_model_l(2010+j)

# print(acum)
defun_pro=np.mean(acum,axis=0)
defun_pro_min=np.mean(acum,axis=0)-2*np.std(acum,axis=0)
defun_pro_max=np.mean(acum,axis=0)+2*np.std(acum,axis=0)
defun_pro_max_1=np.mean(acum,axis=0)+1*np.std(acum,axis=0)
defun_pro_min_1=np.mean(acum,axis=0)-1*np.std(acum,axis=0)


x=np.array(dias_2020)
x_2020=np.array(defun_dia.iloc[defun_dia.index.get_level_values('año') == 2020].index.get_level_values('dias'))
x_covid=np.array(defun_covid_N['dias'])

y=defun_pro
y_1s=defun_pro_max_1
y_2s=defun_pro_max
y_1sm=defun_pro_min_1
y_2sm=defun_pro_min

y_2020=np.array(defun_dia.iloc[defun_dia.index.get_level_values('año') == 2020]['Defunciones'])
tmp=np.zeros(len(x))
tmp[x_2020]=y_2020
y_2020=tmp

y_covid=np.array(defun_covid_N['Defunciones'])
tmp=np.zeros(len(x))
tmp[x_covid]=y_covid
y_covid=tmp


excess_dead=pd.DataFrame()
tmp_excess=np.array([pd.date_range(basedate,max(pd.to_datetime(defun_covid_N['Fecha'])),freq='D'),dias_2020,y_2020,y_covid,y,y_2020-y_covid,y_2020-y_covid-y,y_2s,y_1s,y_1sm,y_2sm]).transpose()
tmp_excess=pd.DataFrame(data=tmp_excess,columns=['fecha','dia','defunciones_totales',
                                                  'defunciones_covid','media',
                                                  'defunciones_no_covid','exceso_media','exceso_2S','exceso_1S','exceso_minus1S','exceso_minus2S'])
excess_dead=excess_dead.append(tmp_excess)

excess_dead.to_csv("excess_dead_nac_daily.csv",index=False)