import os
import datetime
import re
import csv
import json
import xml.etree.ElementTree as ET
import sqlite3

# Record base class
class Record:
    def __init__(self):
        self.record_type = ""
        self.data = ""

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"

# News record type
class News(Record):
    def __init__(self, city, text):
        super().__init__()
        self.record_type = "News"
        self.city = city
        self.text = text
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data = f"{self.date} | {self.city} | {self.text}"

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"

# Private Ad record type
class PrivateAd(Record):
    def __init__(self, text, expiration_date):
        super().__init__()
        self.record_type = "Private Ad"
        self.text = text
        self.expiration_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%d')
        self.days_left = (self.expiration_date - datetime.datetime.now()).days
        self.data = f"{self.text} | {self.expiration_date.strftime('%Y-%m-%d')} | {self.days_left} days left"

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"

# Custom record type
class CustomRecord(Record):
    def __init__(self, record_type, custom_fields):
        super().__init__()
        self.record_type = record_type
        self.data = custom_fields

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"

# DBManager for interacting with the database
class DBManager:
    def __init__(self, db_name="news_feed.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create tables for each record type if they don't exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            city TEXT,
            text TEXT,
            UNIQUE(city, text)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS private_ad_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            expiration_date TEXT,
            days_left INTEGER,
            UNIQUE(text, expiration_date)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT,
            custom_fields TEXT,
            UNIQUE(record_type, custom_fields)
        )
        """)

        self.conn.commit()

    def insert_record(self, record):
        """Insert a record into the appropriate table."""
        if isinstance(record, News):
            if not self.check_duplicate('news_records', ['city', 'text'], [record.city, record.text]):
                self.cursor.execute("""
                INSERT INTO news_records (date, city, text) VALUES (?, ?, ?)
                """, (record.date, record.city, record.text))
                self.conn.commit()
                print(f"News record added: {record.format_record()}")
            else:
                print(f"Duplicate News record detected: {record.format_record()}")

        elif isinstance(record, PrivateAd):
            if not self.check_duplicate('private_ad_records', ['text', 'expiration_date'], [record.text, record.expiration_date]):
                self.cursor.execute("""
                INSERT INTO private_ad_records (text, expiration_date, days_left) VALUES (?, ?, ?)
                """, (record.text, record.expiration_date, record.days_left))
                self.conn.commit()
                print(f"Private Ad record added: {record.format_record()}")
            else:
                print(f"Duplicate Private Ad record detected: {record.format_record()}")

        elif isinstance(record, CustomRecord):
            if not self.check_duplicate('custom_records', ['record_type', 'custom_fields'], [record.record_type, record.data]):
                self.cursor.execute("""
                INSERT INTO custom_records (record_type, custom_fields) VALUES (?, ?)
                """, (record.record_type, record.data))
                self.conn.commit()
                print(f"Custom record added: {record.format_record()}")
            else:
                print(f"Duplicate Custom record detected: {record.format_record()}")

    def check_duplicate(self, table, fields, values):
        """Check if a record with the same fields already exists."""
        query = f"SELECT COUNT(*) FROM {table} WHERE " + " AND ".join([f"{field} = ?" for field in fields])
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0] > 0

    def close(self):
        """Close the database connection."""
        self.conn.close()

# NewsFeedManager handles the file and database integration
class NewsFeedManager:
    def __init__(self, filename="news_feed.txt", word_count_file="word-count.csv", letters_file="letters.csv"):
        self.filename = filename
        self.word_count_file = word_count_file
        self.letters_file = letters_file
        self.db_manager = DBManager()  # Initialize the DBManager here

    def write_to_file(self, record):
        # Check for duplicates in the file
        if not self.check_duplicate(record):
            with open(self.filename, "a") as file:
                file.write(record.format_record())
            print("Record added to file.")
            self.recreate_csvs()
            # Insert the record into the database
            self.db_manager.insert_record(record)
        else:
            print(f"Duplicate record detected in file: {record.format_record()}")

    def check_duplicate(self, record):
        """Check if the record already exists in the file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip() == record.format_record().strip():
                        return True
        return False

    def recreate_csvs(self):
        word_count, letter_count, total_letters = self.calculate_counts()

        with open(self.word_count_file, 'w', newline='') as word_file:
            writer = csv.writer(word_file)
            writer.writerow(["record", "word count"])
            writer.writerow(["total", word_count])
        print(f"word count csv '{self.word_count_file}' recreated.")

        with open(self.letters_file, 'w', newline='') as letters_file:
            writer = csv.writer(letters_file)
            writer.writerow(["record", "Letter count", "percentage of letters"])
            writer.writerow(["total", letter_count, f"{(letter_count / total_letters * 100) if total_letters > 0 else 0:.2f}%"])
        print(f"letters csv '{self.letters_file}' recreated.")

    def calculate_counts(self):
        word_count = 0
        letter_count = 0
        total_letters = 0

        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip().lower()
                words = re.findall(r'\w+', line)
                word_count += len(words)
                total_letters += len(line.replace(" ", ""))  
                letter_count += len([char for char in line if char.isalpha()])

        return word_count, letter_count, total_letters


class FileInputManager:
    def __init__(self, manager, default_folder="records"):
        self.manager = manager
        self.default_folder = default_folder

    def normalize_case(self, text):
        return text.lower()

    def process_file(self, file_path=None):
        if file_path is None:
            file_path = input(f"Enter the file path (default is '{self.default_folder}'): ")
            if not file_path:
                file_path = self.default_folder
        
        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist.")
            return
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            self.process_record_from_line(line)
        
        os.remove(file_path)
        print(f"File '{file_path}' processed and removed successfully.")

    def process_record_from_line(self, line):
        try:
            parts = [item.strip() for item in line.split('|')]
            record_type = self.normalize_case(parts[0])
            
            if record_type == "news":
                if len(parts) < 3:
                    print(f"Invalid News record: {line}")
                    return
                city = self.normalize_case(parts[1])
                text = self.normalize_case(parts[2])
                record = News(city, text)
                
            elif record_type == "private ad":
                if len(parts) < 3:
                    print(f"Invalid Private Ad record: {line}")
                    return
                text = self.normalize_case(parts[1])
                expiration_date = parts[2]
                record = PrivateAd(text, expiration_date)
                
            elif record_type == "custom record":
                if len(parts) < 2:
                    print(f"Invalid Custom Record: {line}")
                    return
                custom_fields = self.normalize_case(parts[1])
                record = CustomRecord(record_type, custom_fields)
                
            else:
                print(f"Unknown record type: {line}")
                return

            self.manager.write_to_file(record)
        except Exception as e:
            print(f"Error processing line '{line}': {e}")


class JsonInputManager:
    def __init__(self, manager):
        self.manager = manager

    def process_json_file(self, file_path="records.json"):
        if not os.path.exists(file_path):
            print(f"JSON file '{file_path}' does not exist.")
            return
        
        with open(file_path, 'r') as file:
            records = json.load(file)
        
        for record in records:
            record_type = record.get('type').lower()
            if record_type == "news":
                self.manager.write_to_file(News(record['city'], record['text']))
            elif record_type == "private ad":
                self.manager.write_to_file(PrivateAd(record['text'], record['expiration_date']))
            elif record_type == "custom record":
                self.manager.write_to_file(CustomRecord(record['record_type'], record['data']))
            else:
                print(f"Unknown record type: {record_type}")


class XmlInputManager:
    def __init__(self, manager):
        self.manager = manager

    def process_xml_file(self, file_path="records.xml"):
        if not os.path.exists(file_path):
            print(f"XML file '{file_path}' does not exist.")
            return
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for record in root.findall('record'):
            record_type = record.find('type').text.lower()
            if record_type == "news":
                city = record.find('city').text
                text = record.find('text').text
                self.manager.write_to_file(News(city, text))
            elif record_type == "private ad":
                text = record.find('text').text
                expiration_date = record.find('expiration_date').text
                self.manager.write_to_file(PrivateAd(text, expiration_date))
            elif record_type == "custom record":
                custom_fields = record.find('data').text
                self.manager.write_to_file(CustomRecord(record_type, custom_fields))
            else:
                print(f"Unknown record type in XML: {record_type}")


class Application:
    def __init__(self):
        self.manager = NewsFeedManager()
        self.file_input_manager = FileInputManager(self.manager)
        self.json_input_manager = JsonInputManager(self.manager)
        self.xml_input_manager = XmlInputManager(self.manager)

    def add_news_record(self):
        city = input("Enter the city: ")
        text = input("Enter the news text: ")
        record = News(city, text)
        self.manager.db_manager.insert_record(record)

    def add_private_ad_record(self):
        text = input("Enter the private ad text: ")
        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
        record = PrivateAd(text, expiration_date)
        self.manager.db_manager.insert_record(record)

    def add_custom_record(self):
        record_type = input("Enter your custom record type: ")
        custom_fields = input("Enter your custom fields (comma-separated): ")
        record = CustomRecord(record_type, custom_fields)
        self.manager.db_manager.insert_record(record)

    def import_records_from_file(self):
        self.file_input_manager.process_file()

    def import_records_from_json(self):
        self.json_input_manager.process_json_file()

    def import_records_from_xml(self):
        self.xml_input_manager.process_xml_file()

    def run(self):
        while True:
            print("\nPlease choose one of the following options:")
            print("1. Add a News Record")
            print("2. Add a Private Ad")
            print("3. Add a Custom Record")
            print("4. Import Records from File")
            print("5. Import Records from JSON File")
            print("6. Import Records from XML File")
            print("7. Exit")

            choice = input("Enter your choice (1, 2, 3, 4, 5, 6, or 7): ")

            if choice == '1':
                self.add_news_record()
            elif choice == '2':
                self.add_private_ad_record()
            elif choice == '3':
                self.add_custom_record()
            elif choice == '4':
                self.import_records_from_file()
            elif choice == '5':
                self.import_records_from_json()
            elif choice == '6':
                self.import_records_from_xml()
            elif choice == '7':
                print("Exiting...")
                self.manager.db_manager.close()
                break
            else:
                print("Invalid choice. Please, let's try again.")

if __name__ == "__main__":
    app = Application()
    app.run()
