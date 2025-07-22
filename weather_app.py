import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")

class Weather_Class:
    def __init__(self,api_key,db_name="weather_report.db"):
        self.api_key=api_key
        self.base_url="http://api.weatherapi.com/v1/current.json"
        self.con=sqlite3.connect(db_name)
        self.cur=self.con.cursor()
        self.create_table()

    def get_record(self):
        self.cur.execute('''select * from weather_forecast''')
        for row in self.cur.fetchall():
            print(row)

    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                Location TEXT PRIMARY KEY,
                Country TEXT,
                Time TEXT,
                Temperature_Celsius REAL,
                Condition TEXT
            )
        ''')
        self.con.commit()

    def get_weather_record(self,city):
        self.cur.execute('''select * from weather_forecast where Location=?''',(city.lower(),))
        record=self.cur.fetchone()
        return record
    
    def set_weather_record(self,city,data):
        self.cur.execute('''insert into weather_forecast values(?,?,?,?,?)''',(city.lower(),data["location"]["country"],data["location"]["localtime"],data["current"]["temp_c"],data["current"]["condition"]["text"]))
        self.con.commit()

    def get_weather(self,city):

        city=city.lower()
        record = self.get_weather_record(city)
        if (record):
            print("Found data from our database!!!")
            return {
                "Location":record[0],
                "Country":record[1],
                "Time":record[2],
                "Temperature_(In Celsius)":record[3],
                "Condition":record[4]
            }

        params ={
                    "key":self.api_key,
                    "q":city.lower()
                }
        
        try:
                response=requests.get(self.base_url,params=params)
                response.raise_for_status() #We Use this function here to check whether the response was succesfull or not so that we won't get any problems regarding the error, it will create an error if the connection or request fails
                data=response.json()
                print("New data stored in our database!!!")
                self.set_weather_record(city,data)
                return{
                    "Location":data["location"]["name"],
                    "Country":data["location"]["country"],
                    "Time":data["location"]["localtime"],
                    "Temperature_(In Celsius)":data["current"]["temp_c"],
                    "Condition":data["current"]["condition"]["text"]
                    # "Cloud":data["cloud"],
                    # "Feels_Like_(In Celsius)":data["feelslike_c"]
                }
        
        except requests.exceptions.RequestException as e:
            print(f"Error : {e}")
            return {}


    
print('*'*70)
print("Welcome to the Weather Forecast | Please Enter your location for the weather Information")
city=input("Enter the City : ")
weather_object=Weather_Class(api_key)

weather=weather_object.get_weather(city)

# weather_object.get_record()

if weather:
    print(f"The Weather of {city} is------ ")
    print(f"Location : {weather["Location"]}, {weather["Country"]}")
    print(f"Time : {weather["Time"]}")
    print(f"Temperature (In Celsius): {weather["Temperature_(In Celsius)"]}")
    print(f"Condtion : {weather["Condition"]}")

else:
    print("The App couldn't find your Location and fetch the info about the weather, sorry")


