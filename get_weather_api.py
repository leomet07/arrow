import requests
import json

def get_location():
    #getting the location
    send_url = "http://api.ipstack.com/check?access_key=a7c5c72da5439577d393220d2006c449"
    geo_req = requests.get(send_url)
    geo_json = json.loads(geo_req.text)
    #print(geo_json)
    con = geo_json['continent_name']
    city = geo_json['city']
    zip = geo_json['zip']
    lat = geo_json['latitude']
    long = geo_json['longitude']


    country_code = geo_json['country_code']
    return zip,country_code,con,  city, lat, long

def get_temperature():
    zip, country_code, con_name, city, lat, long = get_location()
    api_address='http://api.openweathermap.org/data/2.5/weather?zip=' + str(zip) + ',' + str(country_code) + '&appid=0c42f7f6b53b244c78a418f4f181282a&units=metric'

    url = api_address
    json_data = requests.get(url).json()
    format_add = json_data['main']['temp']

    print("Current tempature: " + str(format_add))
    return format_add

def get_weather():
    zip, country_code, con_name, city, lat, long= get_location()
    api_address='http://api.openweathermap.org/data/2.5/weather?zip=' + str(zip) + ',' + str(country_code) + '&appid=0c42f7f6b53b244c78a418f4f181282a&units=metric'

    url = api_address
    json_data = requests.get(url).json()
    weather = json_data['weather'][0]['main']
    temp = json_data['main']['temp']

    print("Current weather: " + str(weather))
    return weather,temp

get_location()