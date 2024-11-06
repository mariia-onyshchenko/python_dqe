import math
import sqlite3

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

class CityCoordinatesDB:
    def __init__(self, db_name="city_coordinates.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_name TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL
        )
        """)
        self.conn.commit()

    def insert_city(self, city_name, latitude, longitude):
        self.cursor.execute("""
        INSERT OR REPLACE INTO cities (city_name, latitude, longitude)
        VALUES (?, ?, ?)
        """, (city_name, latitude, longitude))
        self.conn.commit()

    def get_coordinates(self, city_name):
        self.cursor.execute("SELECT latitude, longitude FROM cities WHERE city_name = ?", (city_name,))
        result = self.cursor.fetchone()
        return result

    def close(self):
        self.conn.close()

class CityDistanceTool:
    def __init__(self):
        self.db = CityCoordinatesDB()

    def get_city_coordinates(self, city_name):
        coordinates = self.db.get_coordinates(city_name)
        if coordinates:
            return coordinates
        else:
            print(f"Coordinates for {city_name} not found in the database.")
            lat = float(input(f"Please enter the latitude for {city_name}: "))
            lon = float(input(f"Please enter the longitude for {city_name}: "))
            self.db.insert_city(city_name, lat, lon)
            print(f"Coordinates for {city_name} have been saved.")
            return lat, lon

    def calculate_distance(self):
        city1 = input("Enter the name of the first city: ").strip()
        city2 = input("Enter the name of the second city: ").strip()
        
        lat1, lon1 = self.get_city_coordinates(city1)
        lat2, lon2 = self.get_city_coordinates(city2)
        
        distance = haversine(lat1, lon1, lat2, lon2)
        print(f"The straight-line distance between {city1} and {city2} is {distance:.2f} km.")

    def run(self):
        while True:
            print("\nCity Distance Tool")
            print("1. Calculate distance between two cities")
            print("2. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.calculate_distance()
            elif choice == '2':
                print("Exiting the tool.")
                self.db.close()
                break
            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":
    tool = CityDistanceTool()
    tool.run()
