import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
api_Key=os.getenv("WEATHER_API_KEY")

class weather_report:
    def __init__(self,api_key,database_name="weather_report.db"):
        self.api_key=api_key
        self.url="http://api.weatherapi.com/v1/current.json"
        self.con=sqlite3.connect(database_name)
        self.cur=self.con.cursor()
        self.create_Table()

    def create_Table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                location TEXT PRIMARY KEY,
                country TEXT NOT NULL,
                time TEXT,
                temperature_in_celsius REAL,
                condition TEXT
        )''')

        self.con.commit()

    def get_record_from_db(self,city_name):
        self.cur.execute('''SELECT * FROM weather_data WHERE location = ?''',(city_name.lower(),))
        result=self.cur.fetchone()
        return result
    
    def set_record_in_db(self,city_name,data):
        self.cur.execute('''INSERT INTO weather_data VALUES (?,?,?,?,?)''',(
            city_name.lower(),
            data["location"]["country"],
            data["location"]["localtime"],
            data["current"]["temp_c"],
            data["current"]["condition"]["text"]
            ) #Data To be inserted using API (The data will be in this format the one we are using)
        )
        self.con.commit()

    def get_weather_report(self,city_name):
        city_name=city_name.lower()

        if_stored=self.get_record_from_db(city_name)

        if (if_stored):
            print("The data was Already in our database no need to fetch from API!!")

            return { #Returning the answer or response in dictionary format for better understanding
                "Location":if_stored[0],
                "Country":if_stored[1],
                "Time":if_stored[2],
                "Temperature_In_Celsius":if_stored[3],
                "Condition":if_stored[4]
            }
        
        params={
            "key":self.api_key,
            "q":city_name.lower()
        }

        try:
            response=requests.get(self.url,params=params)
            response.raise_for_status()
            data=response.json() #To make data readable for the user, since the format of the data send through API can wary so we use this json method
            print("Data Fetched From the API!!")
            self.set_record_in_db(city_name,data)

            return{
                "Location":data["location"]["name"],
                "Country":data["location"]["country"],
                "Time":data["location"]["localtime"],
                "Temperature_In_Celsius":data["current"]["temp_c"],
                "Condition":data["current"]["condition"]["text"]
            }
        
        except requests.exceptions.RequestException as e:
            print(f"The error : {e}")
            return {}
        
def main():
    print("*"*75)
    while True:
        print("Welcome to our Weather Forecast : ")
        user_response=input("Please enter your city you want to know the report about : ")
        
        if (user_response.lower()=="exit"):
            break

        else:
            weather_ans=weather_report(api_Key)
            ans=weather_ans.get_weather_report(user_response)
            if ans:
                print(f"The Weather of the Provided city {user_response} is : -------------")
                print(f"City : {ans["Location"]}")
                print(f"Country : {ans["Country"]}")
                print(f"Time : {ans["Time"]}")
                print(f"Temperature In Celsius : {ans["Temperature_In_Celsius"]}")
                print(f"Condition : {ans["Condition"]}")

            else:
                print("The App couldn't find your location and weather information, sorry")

            print("*"*75)


if __name__=="__main__":
    main()