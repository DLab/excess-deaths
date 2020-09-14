# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 10:30:34 2020

@author: pmaldonadol
"""
import requests
import pandas as pd
import io
import numpy as np



# Se obtienen las defunciones desde url y se transforman a dataframe
defun = requests.get('https://github.com/MinCiencia/Datos-COVID19/raw/master/output/producto32/Defunciones_std.csv').content
defun = pd.read_csv(io.StringIO(defun.decode('utf-8')))

# Defunciones por periodo anual y mensual
defun['año']=pd.DatetimeIndex(defun['Fecha']).year
defun['mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('M')
defun['semana-mes-año']=pd.to_datetime(defun['Fecha']).dt.to_period('W')

# Se obtienen las defunciones covid nacionales desde url y se transforman a dataframe
# defun_covid_N = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto5/TotalesNacionales_std.csv').content
# defun_covid_N = pd.read_csv(io.StringIO(defun_covid_N.decode('utf-8')),delimiter=",")

# defun_covid_N = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto14/FallecidosCumulativo_std.csv').content
# defun_covid_N = pd.read_csv(io.StringIO(defun_covid_N.decode('utf-8')),delimiter=",")

defun_covid_N = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto50/DefuncionesDEISPorComuna_std.csv').content
defun_covid_N = pd.read_csv(io.StringIO(defun_covid_N.decode('utf-8')))

defun_covid_N=defun_covid_N.groupby(by=['Fecha']).sum()
defun_covid_N=defun_covid_N.drop(['Codigo region', 'Codigo comuna', 'Poblacion'],axis=1)
defun_covid_N.reset_index(level=0, inplace=True)
# defun_covid_N = defun_covid_N[defun_covid_N.Dato=='Fallecidos']
# defun_covid_N = defun_covid_N[defun_covid_N.Region=='Total']
# d_covid=np.diff(defun_covid_N['Total'])
# defun_covid_N['Defunciones']=np.insert(d_covid,0,1)
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

## Proyeccion de aumetno de población semanales totales

defun['semana']=pd.to_datetime(defun['Fecha']).dt.week
defun_covid_N['semana']=pd.to_datetime(defun_covid_N['Fecha']).dt.week

defun_week=defun.groupby(['año','semana']).sum()
defun_covid_week=defun_covid_N.groupby(['año','semana']).sum()
# defun_covid_week=defun_covid_week[defun_covid_week.index.get_level_values('semana')!=23]


# Defunciones proyectadas por modelo lineal pais semana
semanas_2020=defun_week.iloc[defun_week.index.get_level_values('año') == 2020].index.get_level_values('semana')
defun_pro=np.zeros(semanas_2020.shape[0])
defun_pro_min=np.zeros(semanas_2020.shape[0])
defun_pro_max=np.zeros(semanas_2020.shape[0])


acum=np.zeros((10,semanas_2020.shape[0]))
for j in range(10):    
    
    y=np.array(defun_week.iloc[defun_week.index.get_level_values('año') == 2010+j]['Defunciones'])
    # print(y[0:semanas_2020.shape[0]]*models[i][0](2010+j)/models[i][0](2020))
    acum[j,:]=y[0:semanas_2020.shape[0]]*anual_model_l(2020)/anual_model_l(2010+j)

# print(acum)
defun_pro=np.mean(acum,axis=0)
defun_pro_min=np.mean(acum,axis=0)-2*np.std(acum,axis=0)
defun_pro_max=np.mean(acum,axis=0)+2*np.std(acum,axis=0)
defun_pro_max_1=np.mean(acum,axis=0)+1*np.std(acum,axis=0)
defun_pro_min_1=np.mean(acum,axis=0)-1*np.std(acum,axis=0)




x=np.array(semanas_2020)
x_cov=np.array(defun_covid_week.iloc[defun_covid_week.index.get_level_values('año') == 2020].index.get_level_values('semana'))
y=defun_pro
y_1s=defun_pro_max_1
y_2s=defun_pro_max
y_1sm=defun_pro_min_1
y_2sm=defun_pro_min

y_2020=np.array(defun_week.iloc[defun_week.index.get_level_values('año') == 2020]['Defunciones'])
y_covid=np.array(defun_covid_week.iloc[defun_covid_week.index.get_level_values('año') == 2020]['Defunciones'])
y_covid=np.insert(y_covid, 0, np.zeros(len(np.setdiff1d(x, x_cov))))


excess_dead=pd.DataFrame()
tmp_excess=np.array([x,y_2020,y_covid,y,y_2020-y_covid,y_2020-y_covid-y,y_2s,y_1s,y_1sm,y_2sm]).transpose()
tmp_excess=pd.DataFrame(data=tmp_excess,columns=['Semana','Defunciones_2020',
                                                      'Defunciones_Covid','Media_2020',
                                                      'Defunciones_no_Covid','Defunsiones_media','2S','1S','-1S','-2S'])
tmp_excess['Codigo_region']=0
tmp_excess['Region']='Nacional'
excess_dead=excess_dead.append(tmp_excess)

# excess_dead.to_excel("Excces_dead_nac_weekly.xls")


excess_dead.to_csv("Excces_dead_nac_weekly.csv")