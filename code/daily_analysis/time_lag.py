import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import csv
import os
from datetime import date, timedelta
from pymongo import MongoClient, ASCENDING
from scipy.optimize import leastsq
from tqdm import tqdm
client = MongoClient('mongodb://localhost:27017/')

db_corona = client.corona
col_system = db_corona.system_info
col_case = db_corona.case_count
col_ridership = db_corona.ridership

rl_system = list(col_system.find({}))
start_date = date(2020, 1,22)
end_date = date.today()

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


for each_lag in range(15):
    positive_distance_systems = 0
    all_systems = 0
    for each_system in rl_system:
        _id = each_system["_id"]
        system_name = each_system["name"]
        metro_area = each_system["metro_area"]
        rl_ridership = col_ridership.find(
            {"system_name": system_name}).sort("date", ASCENDING)
        
        B = each_system["B"]
        k = each_system['k']
        t0 = each_system["t0"]
        b = each_system["b"]
        divergent_point = each_system["divergent_point"]
        convergent_point = each_system["convergent_point"]
        try:
            t0_corona = each_system["t0_corona"]
        except:
            continue
        if not t0_corona:
            continue
        # print(divergent_point, each_lag, t0_corona, system_name)
        distance = t0_corona -24 - each_lag - (convergent_point) # 24 is the difference of start date between two data: ridership is 2/15 and usafact cases is 1/22 
        
            
        if distance > 0:
            print(system_name, metro_area)
            positive_distance_systems += 1
        all_systems += 1

        # print(system_name, metro_area, int(divergent_point), t0_corona, each_lag)
    print(each_lag, positive_distance_systems, all_systems, positive_distance_systems/all_systems)
    # break

