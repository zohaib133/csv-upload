import os
import csv
from client.models import Country, City
from django.conf import settings

directory = settings.BASE_DIR
file = os.path.join(directory, 'client', 'countries_and_cities.csv')

with open(file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        line_count = line_count + 1
        city_ = row[0]
        country_ = row[1]

        country, created = Country.objects.get_or_create(name=country_.lower().strip())
        city, created = City.objects.get_or_create(name=city_.lower().strip(), country=country)
    print(f'Processed {line_count} lines.')
