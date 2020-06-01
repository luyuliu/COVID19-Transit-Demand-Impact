import csv, os, time
from datetime import date, datetime
from pymongo import MongoClient, ASCENDING
from tqdm import tqdm

client = MongoClient('mongodb://localhost:27017/')

db_case = client.corona
col_case = db_case.case_count

col_ridership = db_case.ridership
col_other_ridership = db_case.other_ridership

data_location = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "\\data\\transit_demand\\ridership.csv"
print(data_location)
col_ridership.drop()
col_other_ridership.drop()
with open(data_location) as the_file:
    the_reader = csv.reader(the_file, delimiter=',')
    line_count = 0
    field_names = []
    US_records = []
    other_records = []

    for row in (the_reader):
        # print(row)
        if line_count == 0:
            for each_item in row:
                date_list = each_item.split("-")
                if len(date_list) < 2:
                    field_names.append(each_item)
                    continue
                else:
                    field_names.append(datetime.fromtimestamp(time.mktime(time.strptime("2020-"+each_item, "%Y-%d-%b"))))

        else:
            numbers = row

            for index in range(len(numbers)):
                item = numbers[index]
                if index == 0:
                    system_name = item
                elif index == 1:
                    metro_area = item
                    location_list = metro_area.split(", ")
                    if len(location_list) < 2:
                        city = None
                        country = None
                    else:
                        city = location_list[0]
                        country = location_list[1][0:2]
                else:
                    if item == "":
                        continue
                    if country != "US":
                        insertion = {
                            "system_name": system_name,
                            "city": city,
                            "country": country,
                            "date": field_names[index].strftime("%Y%m%d"),
                            "demand_decrease": float(item.strip('%')) / 100.0
                        }
                        other_records.append(insertion)
                    else:
                        insertion = {
                            "system_name": system_name,
                            "city": city,
                            "country": country,
                            "date": field_names[index].strftime("%Y%m%d"),
                            "demand_decrease": float(item.strip('%')) / 100.0
                        }
                        # print(insertion)
                        US_records.append(insertion)
        line_count += 1
        # print(line_count, len(US_records))
    
    col_ridership.insert_many(US_records)
    col_other_ridership.insert_many(other_records)
    col_ridership.create_index([("system_name", 1)])