import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import csv
import os
from datetime import date
from pymongo import MongoClient, ASCENDING
from scipy.optimize import leastsq
from scipy import stats
import statsmodels.api as sm 
import pylab
client = MongoClient('mongodb://localhost:27017/')

db_corona = client.corona
col_system = db_corona.system_info
col_case = db_corona.corona_cases_usafacts
col_ridership = db_corona.ridership

rl_system = col_system.find({})


def sigmoid(p, x):
    x0, y0, L, k = p
    y = L / (1 + np.exp(-k*(x-x0))) + y0
    return y


def residuals(p, x, y):
    return y - sigmoid(p, x)


def resize(arr, lower=0.0, upper=1.0):
    arr = arr.copy()
    if lower > upper:
        lower, upper = upper, lower
    arr -= arr.min()
    arr *= (upper-lower)/arr.max()
    arr += lower
    return arr

count = 0
total_count = 0
minimal_r_sq = 1
that = None
r_sq_list = []
for each_system in rl_system:
    _id = each_system["_id"]
    system_name = each_system["name"]
    if each_system["lat"] == None:
        continue
    metro_area = each_system["metro_area"]
    # print(system_name, metro_area)
    rl_ridership = col_ridership.find(
        {"system_name": system_name}).sort("date", ASCENDING)
    y = []
    for each_record in rl_ridership:
        y.append(each_record["demand_decrease"])
    x = list(range(len(y)))
    # print((x))

    p_guess = (int(np.median(x)), 0, 1.0, 0.5)
    p, cov, infodict, mesg, ier = leastsq(
        residuals, p_guess, args=(x, y), full_output=1)

    x0, y0, L, k = p
    results_005 = x0 - np.log(2/(0.05)-1)/k # 2.5% range
    results_095 = x0 + np.log(2/(0.05)-1)/k # 97.5% range
    
    
    xp = np.linspace(0, len(x), len(y))
    pxp = sigmoid(p, xp)

    correlation_matrix = np.corrcoef(pxp, y)
    correlation_xy = correlation_matrix[0,1]
    r_squared = correlation_xy**2

    # print("p = {:g}".format(p))
    count = count + 1
    print(system_name, r_squared)
    stats.probplot(residuals(p, x, y), dist="norm", plot=pylab)
    pylab.title(metro_area + " - " + system_name, fontsize=16)
    pylab.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\qqplots\\" + metro_area + "_" +
            system_name + ".jpg")
    pylab.clf()
    if minimal_r_sq > r_squared:
        minimal_r_sq = r_squared 
        that = system_name
    total_count += 1
    r_sq_list.append(r_squared)

print(count, total_count)
