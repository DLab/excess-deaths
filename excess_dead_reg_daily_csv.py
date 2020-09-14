# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 10:46:35 2020

@author: pmaldonadol
"""


import requests
import pandas as pd
import io
import numpy as np


# Se obtienen las defunciones desde url y se transforman a dataframe
defun = requests.get('https://github.com/MinCiencia/Datos-COVID19/raw/master/output/producto32/Defunciones_std.csv').content
defun = pd.read_csv(io.StringIO(defun.decode('utf-8')))
# defun_2020 = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto32/2020-Defunciones_std.csv').content
# defun_2020 = pd.read_csv(io.StringIO(defun_2020.decode('utf-8')))
# defun=defun.append(defun_2020)


# Se obtienen las defunciones desde url y se transforman a dataframe
#defun_covid = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto14/FallecidosCumulativo_std.csv').content
#defun_covid = pd.read_csv(io.StringIO(defun_covid.decode('utf-8')),delimiter=",")
#def reg_code(data):
#    if data=="Arica y Parinacota":
#        return(15)
#    if data=="Tarapacá":
#        return(1)
#    if data=="Antofagasta":
#        return(2)
#    if data=="Atacama":
#        return(3)
#    if data=="Coquimbo":
#        return(4)
#    if data=="Valparaíso":
#        return(5)
#    if data=="O’Higgins":
#        return(6)
#    if data=="Maule":
#        return(7)
#    if data=="Biobío":
#        return(8)
#    if data=="Araucanía":
#        return(9)
#    if data=="Los Lagos":
#        return(10)
#    if data=="Aysén":
#        return(11)
#    if data=="Magallanes":
#        return(12)
#    if data=="Metropolitana":
#        return(13)
#    if data=="Los Ríos":
#        return(14)
#    if data=="Ñuble":
#        return(16)
#
#defun_covid=defun_covid[defun_covid['Region']!='Total']
#defun_covid['Codigo region'] = defun_covid['Region'].apply(reg_code)
#defun_covid['año']=pd.DatetimeIndex(defun_covid['Fecha']).year
#defun_covid['mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('M')
#defun_covid['semana-mes-año']=pd.to_datetime(defun_covid['Fecha']).dt.to_period('W')

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

#Calce de fechas
max_date=min([max(defun['Fecha']),max(defun_covid['Fecha'])])
defun=defun[defun['Fecha']<=max_date]
defun_covid=defun_covid[defun_covid['Fecha']<=max_date]

# Suma acumulativa para Nacimiento y Defunciones
defun_year=defun.groupby(['Codigo region','año']).sum()

# Plot y modelo de defunciones anuales por región
models=[]

for i in range(16):
    
    defun_2019=np.max(defun_year.iloc[
        defun_year.index.get_level_values('Codigo region')== i+1].values[
            range(9,-1,-1),1])
    x=range(2019,2009,-1)
    y=defun_year.iloc[
        defun_year.index.get_level_values('Codigo region')== i+1].values[
            range(9,-1,-1),1]
   
    mymodel = np.poly1d(np.polyfit(x, y, 1))
    models.extend([[mymodel,i+1]])
    myline=np.linspace(2020, 2010, 100)

## Proyeccion de aumetno de población diaria por región
anos=np.unique(defun['año'])
defun['dias']=0
defun['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun=defun[defun['semana']>2]

for i in anos:    
    tmp=defun[defun['año']==i]['Fecha']
    s = pd.date_range(str(i)+'-01-01', str(i)+'-01-30', freq='D').to_series()
    basedate=s[np.logical_and(s.dt.dayofweek==0, s.dt.week==3)]
    defun.loc[defun['año']==i,'dias']=(pd.to_datetime(tmp) - basedate[0]).dt.days


defun_covid['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun_covid=defun_covid[defun_covid['semana']>1]
s = pd.date_range('2020-01-01', '2020-01-30', freq='D').to_series()
basedate=s[np.logical_and(s.dt.dayofweek==0, s.dt.week==3)]
defun_covid['dias']=(pd.to_datetime(defun_covid['Fecha']) - basedate[0]).dt.days
defun_covid=defun_covid.sort_values(by=['Codigo region','dias'])
#defun_covid['Defunciones']=np.zeros(len(defun_covid['dias']))

#for i in range(16):
#    tmp=defun_covid[defun_covid['Codigo region']==i+1]['Total']
#    tmp=np.insert(np.diff(tmp),0,tmp.values[0])
#    defun_covid.loc[defun_covid['Codigo region']==i+1,'Defunciones']=tmp    
 
defun_dia=defun.groupby(['Codigo region','año','dias']).sum()
defun_covid_dia=defun_covid.groupby(['Codigo region','año','dias']).sum()    
#defun_covid_dia=defun_covid_dia.drop(['Total'], axis=1)

# Defunciones proyectadas por modelo por región semana para
dias_2020=np.array(range(max(defun_covid_dia.index.get_level_values('dias'))+1))
defun_pro=np.zeros((16,dias_2020.shape[0]))
defun_pro_min=np.zeros((16,dias_2020.shape[0]))
defun_pro_max=np.zeros((16,dias_2020.shape[0]))
defun_pro_min_1=np.zeros((16,dias_2020.shape[0]))
defun_pro_max_1=np.zeros((16,dias_2020.shape[0]))


for i in range(16):
    acum=np.zeros((10,dias_2020.shape[0]))
    for j in range(10):    
        
        y=np.array(defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2010+j,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)]['Defunciones'])
        x=np.array(defun_dia.iloc[np.logical_and(defun_dia.index.get_level_values('año') == 2010+j,
                                    defun_dia.index.get_level_values('Codigo region') == i+1)].index.get_level_values('dias'))
        ind=np.intersect1d(dias_2020,x)
        # print(y[0:d*models[i][0](2010+j)/models[i][0](2020))
        
        acum[j,ind]=y[ind]*models[i][0](2020)/models[i][0](2010+j)

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
    tmp_excess=pd.DataFrame(data=tmp_excess,columns=['Fecha','dia','Defunciones 2020',
                                                      'Defunciones Covid','Media poderanda de defunciones proyectada 2020',
                                                     'Defunciones sin causal Covid','Exceso de muertes media poderada','Exceso de muertes 2S','Exceso de muertes 1S','Exceso de muertes -1S','Exceso de muertes -2S'])
    tmp_excess['Codigo region']=i+1
    excess_dead=excess_dead.append(tmp_excess)

excess_dead.to_csv("Excces_dead_reg_daily.csv")