import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from scipy.signal import find_peaks
import csv, similaritymeasures
import os, math
from datetime import date, timedelta
from pymongo import MongoClient, ASCENDING
from scipy.optimize import leastsq
from scipy.interpolate import interp1d
client = MongoClient('mongodb://localhost:27017/')

db_corona = client.corona
col_system = db_corona.system_info
col_case = db_corona.corona_cases_usafacts
col_ridership = db_corona.ridership_hourly

rl_system = list(col_system.find({}))

start_date = date(2020, 3 ,16)
end_date = date(2020, 5, 11)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

dic = {}
temporal_dic = {}

for each_date in (list(daterange(start_date, end_date))):
    system_count = 0
    first_count = 0
    second_count = 0
    first_sum = 0
    second_sum = 0

    first_normal_absent_count = 0
    first_actual_absent_count = 0
    first_all_absent_count = 0

    height_relationship_change_count = 0
    each_weekday = each_date.weekday()
    today_date = each_date.strftime("%Y%m%d")
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

        if len(rl_ridership) == 0:
            continue

        try:
            temporal_dic[system_name]
        except:
            temporal_dic[system_name] = []

            
        for each_record in rl_ridership:
            if each_record["actual"] != 0:
                y.append( each_record["normal"] / each_record["actual"])
            else:
                y.append(1)
            z.append(each_record["actual"])
            w.append(each_record["normal"])
        x = list(range(len(y)))
        n = len(z)

        normal_curve = np.array([x, w])
        actual_curve = np.array([x, z])

        # Calculate Similarity: p
        # print(normal_curve)
        try:
            dic[system_name]
        except:
            dic[system_name] = []

        sum_wz = 0
        sum_z2 = 0
        for i in range(n):
            sum_wz += w[i] * z[i]
            sum_z2 += z[i] * z[i]
        p = sum_wz / sum_z2

        S = 0
        for i in range(n):
            S += (p*z[i] - w[i]) ** 2
        S = math.sqrt(S)
        dic[system_name].append(S)

        # Calculate similarity: a
        sum_w = 0
        sum_z = 0
        for i in range(n):
            sum_w += w[i]
            sum_z += z[i]
        a = (sum_z - sum_w)/n
        
        s_a =0
        for i in range(n):
            s_a += (z[i] - w[i] - a) ** 2


        df = similaritymeasures.frechet_dist(normal_curve, actual_curve)
        
        # print(system_name, ',', round(S, 8), ',', round(p, 8))

        # Find peaks
        max_decrease_times = max(y)
        normal_peaks, _ = find_peaks(w, prominence=0.05)
        actual_peaks, _2 = find_peaks(z)

        first_peak_height = 0
        second_peak_height = 0
        first_peak = -1
        second_peak = -1

        first_peak_normal = -1
        second_peak_normal = -1
        first_peak_height_normal = -1
        second_peak_height_normal = -1

        for each_peak in actual_peaks:
            actual_peak_height = z[each_peak]
            if each_peak < 12:
                if actual_peak_height > first_peak_height:
                    first_peak_height = actual_peak_height
                    first_peak = each_peak
            else:
                if actual_peak_height > second_peak_height:
                    second_peak_height = actual_peak_height
                    second_peak = each_peak

        for each_peak in normal_peaks:
            normal_peak_height = w[each_peak]
            if each_peak < 12:
                if normal_peak_height > first_peak_height_normal:
                    first_peak_height_normal = normal_peak_height
                    first_peak_normal = each_peak
            else:
                if normal_peak_height > second_peak_height_normal:
                    second_peak_height_normal = normal_peak_height
                    second_peak_normal = each_peak

        # for each_peak_index in range(len(normal_peaks)):
        #     if each_peak_index == 0:
        #         first_peak_normal = normal_peaks[each_peak_index]
        #     if each_peak_index == 1:
        #         second_peak_normal = normal_peaks[each_peak_index]
        
        # print('"' + system_name + '"',  ',', first_peak_normal, ',', first_peak, ';', second_peak_normal, ",", second_peak)

        # # Plot separately
        # the_plot = plt.plot(x, w, '-', x, z, '-')
        # plt.xlabel('x: days')
        # plt.ylabel('y: transit demand (%)')
        # plt.grid(True)
        # plt.title(system_name, fontsize=16)
        # plt.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\demand_hourly_weekend\\" + system_name + "_" + metro_area + "_" + each_date.strftime("%Y-%m-%d")
        #             + ".jpg")
        # plt.clf()

        a = True if first_peak_height > second_peak_height else False
        b = True if first_peak_height_normal > second_peak_height_normal else False

        c = a == b

        if c != True:
            height_relationship_change_count += 1

        if first_peak == -1 or first_peak_normal == -1:
            diff_first_peak = 999
            if first_peak_normal == -1:
                first_normal_absent_count += 1
                if first_peak == -1:
                    first_all_absent_count += 1
            elif first_peak == -1:
                first_actual_absent_count += 1
        else:
            diff_first_peak = first_peak - first_peak_normal
            first_count += 1 
            first_sum += diff_first_peak

        if second_peak == -1 or second_peak_normal == -1:
            diff_second_peak = 999
        else:
            diff_second_peak = second_peak - second_peak_normal
            second_count += 1
            second_sum += diff_second_peak

    print(each_date, each_weekday, height_relationship_change_count, first_all_absent_count, first_normal_absent_count, first_actual_absent_count, first_sum/first_count, second_sum/second_count)

        # print(system_name, ',', first_peak, ",", first_peak_height, ",", second_peak, ",", second_peak_height)
        # print()
        # print(actual_peaks)

        # # Plot separately
        # the_plot = plt.plot(x, w, '-', x, z, '-')
        # plt.xlabel('x: days')
        # plt.ylabel('y: transit demand (%)')
        # plt.grid(True)
        # plt.title(system_name, fontsize=16)
        # plt.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\demand_hourly\\" + system_name + "_" + metro_area + "_" + str(int(df * 100))
        #              + ".jpg")
        # plt.clf()

        # Update
        # col_system.update_one({"_id": _id}, {"$set": {"distance": S, "stretch_factor": p}})
    


    #     # Plot together
    #     the_plot = plt.plot(x, y, '.')
        
    #     plt.xlabel('x')
    #     plt.ylabel('y', rotation='horizontal')
    #     plt.grid(True)
    #     plt.title(system_name, fontsize=16)
    # plt.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\demand\\all.jpg")

# Plot collective temporal curves of different systems

average_procrustes_dis = []
std_procrustes_dis = []
count =0

for index, item in dic.items():# Update
    # print(len(item))
    if count == 0:
        average_procrustes_dis = [0] * len(item)
    # print(average_procrustes_dis, item)
    for i in range(len(item)):
        average_procrustes_dis[i] += item[i]
    
    count += 1

average_procrustes_dis = [x/ count for x in average_procrustes_dis]

print(count)
std_procrustes_dis = [0] * len(average_procrustes_dis)
for index, item in dic.items():# Update
    for i in range(len(item)):
        std_procrustes_dis[i] += (item[i] - average_procrustes_dis[i]) ** 2

std_procrustes_dis = [(x/ count)**(1/2) for x in std_procrustes_dis]

print(average_procrustes_dis, std_procrustes_dis)
    # average = 0
    # for a in item:
    #     average += a
    # average = average/len(item)
    # col_system.update_one({"name": index}, {"$set": {"average_procrustes_distance": average}})
    # print(index, item)

    # # plot
    # xx = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range(len(item))]
    # plt.plot(xx, item, '-')

xx = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range(len(average_procrustes_dis))]
print(average_procrustes_dis)
# f = interp1d(xx, average_procrustes_dis, kind='quadratic')
# y_smooth=f(xx)

xc = ["black" if (start_date + timedelta(days=i)).weekday()<=4 else "#95d0fc" for i in range(len(average_procrustes_dis))]

# plt.errorbar(xx, average_procrustes_dis, yerr=std_procrustes_dis, errorevery=1, markeredgewidth=10)
plt.scatter(xx, average_procrustes_dis, c=xc)
plt.plot(xx, average_procrustes_dis, '-')

xl = []
a = 0
for each_day in xx:
    if a % 14 == 0:
        xl.append(each_day)
    a += 1
plt.xticks(xl, xl,
       rotation=0)

plt.xlabel('x: days')
plt.ylabel('y: Procrustes distance')
# plt.ylabel('y: Stretch factor')

plt.grid(True)
# plt.title("Procrustes", fontsize=16)
plt.savefig("C:\\Users\\liu.6544\\Desktop\\coronapics\\all_procrustes_distance.jpg", dpi=500)