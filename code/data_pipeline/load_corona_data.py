import csv, os
from datetime import date
from pymongo import MongoClient, ASCENDING

client = MongoClient('mongodb://localhost:27017/')

db_case = client.corona
col_case = db_case.case_count

data_location = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "\data\COVID19_case_count\COVID19_US_countylevel.csv"
print(data_location)
col_case.drop()
with open(data_location) as the_file:
    the_reader = csv.reader(the_file, delimiter=',')
    line_count = 0
    field_names = []
    records = []

    for row in the_reader:
        if line_count == 0:
            for each_item in row:
                date_list = each_item.split("-")
                if len(date_list) < 3:
                    field_names.append(each_item)
                    continue
                else:
                    field_names.append(date(int(date_list[2]), int(date_list[0]), int(date_list[1]))) 

        else:
            numbers = row

            for index in range(len(numbers)):
                item = numbers[index]
                if index == 0:
                    state = item
                elif index == 1:
                    county = item
                elif index == 2:
                    lat = item
                elif index == 3:
                    lon = item
                else:
                    # print(field_names[index])
                    insertion = {
                        "state": state,
                        "county": county,
                        "lat": float(lat),
                        "lon": float(lon),
                        "date": field_names[index].strftime("%Y%m%d"),
                        "case": int(item)
                    }
                    records.append(insertion)
        line_count += 1
    
    col_case.insert_many(records)
    col_case.create_index([("date", 1), ("state", 1), ("county", 1)])