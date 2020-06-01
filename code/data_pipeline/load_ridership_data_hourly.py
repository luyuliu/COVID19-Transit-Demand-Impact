import csv, os, time
from datetime import date, datetime
from pymongo import MongoClient, ASCENDING
from tqdm import tqdm

client = MongoClient('mongodb://localhost:27017/')

db_case = client.corona
col_case = db_case.case_count

col_system = db_case.system_info

col_ridership = db_case.ridership_hourly
col_other_ridership = db_case.other_ridership_hourly
col_agg = db_case.aggregated_ridership_hourly

data_location = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "\\data\\transit_demand\\ridership_hourly.csv"
print(data_location)
col_ridership.drop()
col_other_ridership.drop()
col_agg.drop()

with open(data_location) as the_file:
    the_reader = csv.reader(the_file, delimiter=',')
    line_count = 0
    field_names = []
    US_records = []
    other_records = []
    city_county_records = []

    for row in tqdm(the_reader):
        # print(row)
        if line_count == 0:
            for each_item in row:
                field_names.append(each_item)
        else:
            numbers = row
            insertion = {}
            for index in range(len(numbers)):
                key = field_names[index]
                value = numbers[index]
                insertion[key] = value

            insertion["name"] = insertion["name"].strip()
            insertion["time"] = float(insertion["time"])
            insertion["actual"] = float(insertion["actual"].strip("%"))/100
            insertion["week_ago"] = float(insertion["week_ago"].strip("%"))/100
            insertion["normal"] = float(insertion["normal"].strip("%"))/100
            insertion["day"] = datetime.strptime(insertion["day"], "%Y-%m-%d").strftime("%Y%m%d")
            if insertion["name"] == "Metro Transit" and insertion["metro_area"] == "St. Louis":
                insertion["name"] = "Metro Transit St Louis"
            
            rl_query = col_system.find_one({"name": insertion["name"]})
            if rl_query == None:
                if insertion["metro_area"] == "":
                    city_county_records.append(insertion)
                else:
                    other_records.append(insertion)
                
            else:   
                US_records.append(insertion)
            # print(insertion)
        line_count += 1
    
    col_ridership.insert_many(US_records)
    col_other_ridership.insert_many(other_records)
    col_agg.insert_many(city_county_records)
    col_ridership.create_index([("name", 1)])