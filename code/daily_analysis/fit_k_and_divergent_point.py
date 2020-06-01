import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import csv
import os
from datetime import date
from pymongo import MongoClient, ASCENDING
from datetime import date, timedelta, datetime
from scipy.optimize import leastsq
client = MongoClient('mongodb://localhost:27017/')

db_corona = client.corona
col_system = db_corona.system_info
col_case = db_corona.corona_cases_usafacts
col_ridership = db_corona.ridership

rl_system = col_system.find({}).sort("divergent_point", 1)


def sigmoid(p, x):
    a, b, d = p
    # return a*x**3 + b*x**2 + c*x + d
    return a/(x - b) + d

    # return a*np.exp(x-b) + c
    # print(x)
    # y = []
    # for xi in x:
    #     yi = a*xi*xi + b*xi + c
    #     y.append(yi)
    # return y


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


rl_ridership = col_system.find({})
y = []
x = []
for each_record in rl_ridership:
    y.append(each_record["k"])
    # x.append(each_record["divergent_point"])
    x.append(each_record["divergent_point"])

y = np.array(y)
x = np.array(x)
# print((x), y)

p_guess = (-3.66, 30, 0)
p, cov, infodict, mesg, ier = leastsq(
    residuals, p_guess, args=(x, y), full_output=1)

# p = np.polyfit(x, y, deg = 2)

print(p)

a0, b0, d0 = p
print('''\
a = {a0}
b = {b0}
d = {d0}
'''.format(a0=a0, b0=b0, d0=d0))

p = p_guess
xp = np.array(list(range(-5, (30))))
pxp = sigmoid(p, xp)
# print(pxp)
start_date = datetime.strptime("20200215", "%Y%m%d")
# xx = [(start_date + timedelta(days=int(i))).strftime("%Y%m%d") for i in x]
# print(xx)
xl = []
xll = []
a = 0
for each_day in xp:
    if a % 7 == 0:
        xl.append(each_day)
        xll.append(
            (start_date + timedelta(days=int(each_day))).strftime("%Y%m%d"))
    a += 1
plt.xticks(xl, xll,
           rotation=0)

# Plot separately
the_plot = plt.plot(x, y, '.', xp, pxp, '-')
plt.xlabel('x: Cliff point')
plt.ylabel('y: Decay rate', rotation='vertical')
plt.grid(True)
# plt.title("Decay rate - divergent point", fontsize=16)
plt.savefig(
    "C:\\Users\\liu.6544\\Desktop\\coronapics\\k_and_cliff_scatter.jpg")
plt.clf()


#     # Plot together
#     the_plot = plt.plot(x, y, '.')

#     plt.xlabel('x')
#     plt.ylabel('y', rotation='horizontal')
#     plt.grid(True)
#     plt.title(system_name, fontsize=16)
# plt.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\demand\\all.jpg")
