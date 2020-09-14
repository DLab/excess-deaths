# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 13:30:08 2020

@author: pmaldonadol
"""

import requests
import pandas as pd
import io
import numpy as np


      
# Se obtienen las defunciones desde url y se transforman a dataframe
defun = requests.get('https://github.com/MinCiencia/Datos-COVID19/raw/master/output/producto32/Defunciones_std.csv').content
defun = pd.read_csv(io.StringIO(defun.decode('utf-8')))

# Se obtienen las defunciones desde url y se transforman a dataframe

defun_covid = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto50/DefuncionesDEISPorComuna_std.csv').content
defun_covid = pd.read_csv(io.StringIO(defun_covid.decode('utf-8')))

defun_covid=defun_covid.groupby(by=['Codigo region','Region','Fecha']).sum()
defun_covid=defun_covid.drop(['Codigo comuna', 'Poblacion'],axis=1)
defun_covid.reset_index(level=0, inplace=True)
defun_covid.reset_index(level=0, inplace=True)
defun_covid.reset_index(level=0, inplace=True)


defun_covid['año']=pd.DatetimeIndex(defun_covid['Fecha']).year
defun_covid['mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('M')
defun_covid['semana-mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('W')


# Defunciones por periodo anual y mensual
defun['año']=pd.DatetimeIndex(defun['Fecha']).year
defun['mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('M')
defun['semana-mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('W')

# Calce de fechas
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
            range(9,-1,-1),1]
   
    mymodel = np.poly1d(np.polyfit(x, y, 1))
    models.extend([[mymodel,i+1]])

## Proyeccion de aumetno de población semanales por región


defun['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun_covid['semana']=pd.to_datetime(defun_covid['Fecha']).dt.week
defun_covid=defun_covid.sort_values(by=['Codigo region','semana'])

defun_week=defun.groupby(['Codigo region','año','semana']).sum()
defun_covid_week=defun_covid.groupby(['Codigo region','año','semana']).sum()

# Defunciones proyectadas por modelo por región semana para
semanas_2020=defun_week.iloc[np.logical_and(defun_week.index.get_level_values('año') == 2020,
                                    defun_week.index.get_level_values('Codigo region') == 13)].index.get_level_values('semana')
defun_pro=np.zeros((16,semanas_2020.shape[0]))
defun_pro_min=np.zeros((16,semanas_2020.shape[0]))
defun_pro_max=np.zeros((16,semanas_2020.shape[0]))
defun_pro_min_1=np.zeros((16,semanas_2020.shape[0]))
defun_pro_max_1=np.zeros((16,semanas_2020.shape[0]))


for i in range(16):
    acum=np.zeros((10,semanas_2020.shape[0]))
    for j in range(10):    
        
        y=np.array(defun_week.iloc[np.logical_and(defun_week.index.get_level_values('año') == 2010+j,
                                    defun_week.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
        # print(y[0:semanas_2020.shape[0]]*models[i][0](2010+j)/models[i][0](2020))
        acum[j,:]=y[0:semanas_2020.shape[0]]*models[i][0](2020)/models[i][0](2010+j)

    defun_pro[i,:]=np.mean(acum,axis=0)
    defun_pro_min[i,:]=np.mean(acum,axis=0)-2*np.std(acum,axis=0)
    defun_pro_max[i,:]=np.mean(acum,axis=0)+2*np.std(acum,axis=0)
    defun_pro_min_1[i,:]=np.mean(acum,axis=0)-1*np.std(acum,axis=0)
    defun_pro_max_1[i,:]=np.mean(acum,axis=0)+1*np.std(acum,axis=0)
    
excess_dead=pd.DataFrame()

for i in range(16):
        
    x=np.array(semanas_2020)
    y=defun_pro[i,:]
    y_1s=defun_pro_max_1[i,:]
    y_2s=defun_pro_max[i,:]
    y_1sm=defun_pro_min_1[i,:]
    y_2sm=defun_pro_min[i,:]
    x_covid=defun_covid_week.iloc[np.logical_and(defun_covid_week.index.get_level_values('año') == 2020,
                                    defun_covid_week.index.get_level_values('Codigo region') == i+1)].index.get_level_values('semana')

    y_2020=np.array(defun_week.iloc[np.logical_and(defun_week.index.get_level_values('año') == 2020,
                                defun_week.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
    y_covid=np.array(defun_covid_week.iloc[np.logical_and(defun_covid_week.index.get_level_values('año') == 2020,
                                defun_covid_week.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
    y_covid=np.insert(y_covid, 0, np.zeros(len(np.setdiff1d(x, x_covid))))

    tmp_excess=np.array([x,y_2020,y_covid,y,y_2020-y_covid,y_2020-y_covid-y,y_2s,y_1s,y_1sm,y_2sm]).transpose()
    tmp_excess=pd.DataFrame(data=tmp_excess,columns=['Semana','Defunciones_2020',
                                                      'Defunciones_Covid','Media_2020',
                                                     'Defunciones_no_Covid','Defunsiones_media','2S','1S','-1S','-2S'])
    tmp_excess['Codigo_region']=i+1
    tmp_excess['Region']=np.unique(defun_covid[defun_covid['Codigo region']==i+1]['Region'])[0]
    excess_dead=excess_dead.append(tmp_excess)

excess_dead.to_csv("Excces_dead_reg_weekly.csv",index=False)