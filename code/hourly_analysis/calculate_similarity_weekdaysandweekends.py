import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from scipy.signal import find_peaks
import csv, similaritymeasures
import os, math
from datetime import date, timedelta, datetime
from pymongo import MongoClient, ASCENDING
from scipy.optimize import leastsq
client = MongoClient('mongodb://localhost:27017/')

db_corona = client.corona
col_system = db_corona.system_info
col_case = db_corona.corona_cases_usafacts
col_ridership = db_corona.ridership_hourly

rl_system = list(col_system.find({}))

start_date = date(2020, 3 ,16)
end_date = date(2020, 5, 10)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

dic = {}

for each_date in (list(daterange(start_date, end_date))):
    system_count = 0
    first_count = 0
    second_count = 0
    first_sum = 0
    second_sum = 0
    each_weekday = each_date.weekday()

    if each_weekday != 2 and each_weekday != 6:
        continue

    today_date = each_date.strftime("%Y%m%d")
    try:
        dic[today_date]
    except:
        dic[today_date] = {}


    for each_system in rl_system:
        _id = each_system["_id"]
        system_name = each_system["name"]
        metro_area = each_system["metro_area"]
        rl_ridership = list(col_ridership.find(
            {"name": system_name, "day": each_date.strftime("%Y%m%d")}).sort("time", ASCENDING))
        y = []
        z = []
        w = []
        x = []

        try:
            dic[today_date][system_name]
        except:
            dic[today_date][system_name] = {}
            dic[today_date][system_name]["normal"] = []
            dic[today_date][system_name]["actual"] = []

        if len(rl_ridership) == 0:
            continue
            
        for each_record in rl_ridership:
            if each_record["actual"] != 0:
                y.append( each_record["normal"] / each_record["actual"])
            else:
                y.append(1)
            z.append(each_record["actual"])
            w.append(each_record["normal"])
        
        dic[today_date][system_name]['actual'] = z
        dic[today_date][system_name]['normal'] = w
        
weekday_item = []
for each_date, each_item in dic.items():
    each_date = datetime.strptime(each_date, "%Y%m%d")
    each_weekday = each_date.weekday()

    if each_weekday == 2:
        weekday_item = each_item
        continue
    else:
        weekend_item = each_item
        for each_system in ((rl_system)):
            system_name = each_system["name"]
            metro_area = each_system["metro_area"]
            weekday_normal = weekday_item[system_name]["normal"]
            weekend_normal = weekend_item[system_name]['normal']
            n = len(weekday_normal)
            

            sum_wz = 0
            sum_z2 = 0
            for i in range(n):
                sum_wz += weekend_normal[i] * weekday_normal[i]
                sum_z2 += weekday_normal[i] * weekday_normal[i]
            if sum_z2 != 0:
                p_normal = sum_wz / sum_z2
            else:
                print(system_name, 'wrong')
                # print(weekday_item)
                continue
            

            S = 0
            for i in range(n):
                S += (p_normal*weekday_normal[i] - weekend_normal[i]) ** 2
            S_normal = math.sqrt(S)
            

            weekday_actual = weekday_item[system_name]["actual"]
            weekend_actual = weekend_item[system_name]['actual']
            n = len(weekday_actual)
            

            sum_wz = 0
            sum_z2 = 0
            for i in range(n):
                sum_wz += weekend_actual[i] * weekday_actual[i]
                sum_z2 += weekday_actual[i] * weekday_actual[i]
            if sum_z2 != 0:
                p_actual = sum_wz / sum_z2
            else:
                print(system_name, 'wrong')
                continue

            S = 0
            for i in range(n):
                S += (p_actual*weekday_actual[i] - weekend_actual[i]) ** 2
            S_actual = math.sqrt(S)
            
            print(system_name, S_actual - S_normal)