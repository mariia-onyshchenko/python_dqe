import os
import datetime
import re
import csv
import json
import xml.etree.ElementTree as ET

class Record:
    def __init__(self):
        self.record_type = ""
        self.data = ""

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"


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


class CustomRecord(Record):
    def __init__(self, record_type, custom_fields):
        super().__init__()
        self.record_type = record_type
        self.data = custom_fields

    def format_record(self):
        return f"{self.record_type} | {self.data}\n"


class NewsFeedManager:
    def __init__(self, filename="news_feed.txt", word_count_file="word-count.csv", letters_file="letters.csv"):
        self.filename = filename
        self.word_count_file = word_count_file
        self.letters_file = letters_file

    def write_to_file(self, record):
        with open(self.filename, "a") as file:
            file.write(record.format_record())
        print("Record added successfully.")
        self.recreate_csvs()

    def display_menu(self):
        print("\nPlease choose one of the following options:")
        print("1. Add a News Record")
        print("2. Add a Private Ad")
        print("3. Add a Custom Record")
        print("4. Import Records from File")
        print("5. Import Records from JSON File")
        print("6. Import Records from XML File")  
        print("7. Exit")

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
    def __init__(self, manager, default_folder="records"):
        self.manager = manager
        self.default_folder = default_folder

    def process_json_file(self, file_path=None):
        if file_path is None:
            file_path = input(f"Enter the JSON file path (default is '{self.default_folder}'): ")
            if not file_path:
                file_path = self.default_folder
        
        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist.")
            return

        with open(file_path, 'r') as file:
            try:
                records = json.load(file)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format.")
                return
        
        for record in records:
            self.process_record(record)

        os.remove(file_path)
        print(f"File '{file_path}' processed and removed successfully.")

    def process_record(self, record):
        record_type = record.get("type", "").strip().lower()
        
        try:
            if record_type == "news":
                city = record.get("city", "").strip()
                text = record.get("text", "").strip()
                if city and text:
                    news_record = News(city, text)
                    self.manager.write_to_file(news_record)
                else:
                    print(f"Invalid News record: {record}")

            elif record_type == "private ad":
                text = record.get("text", "").strip()
                expiration_date = record.get("expiration_date", "").strip()
                if text and expiration_date:
                    private_ad_record = PrivateAd(text, expiration_date)
                    self.manager.write_to_file(private_ad_record)
                else:
                    print(f"Invalid Private Ad record: {record}")

            elif record_type == "custom record":
                custom_fields = record.get("custom_fields", "").strip()
                if custom_fields:
                    custom_record = CustomRecord(record_type, custom_fields)
                    self.manager.write_to_file(custom_record)
                else:
                    print(f"Invalid Custom Record: {record}")

            else:
                print(f"Unknown record type: {record}")

        except Exception as e:
            print(f"Error processing record '{record}': {e}")


class XmlInputManager:
    def __init__(self, manager, default_folder="records"):
        self.manager = manager
        self.default_folder = default_folder

    def process_xml_file(self, file_path=None):
        if file_path is None:
            file_path = input(f"Enter the XML file path (default is '{self.default_folder}'): ")
            if not file_path:
                file_path = self.default_folder
        
        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist.")
            return

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError:
            print("Error: Invalid XML format.")
            return
        
        for record in root.findall('record'):
            record_type = record.get('type', '').strip().lower()
            self.process_record(record_type, record)

        os.remove(file_path)
        print(f"File '{file_path}' processed and removed successfully.")

    def process_record(self, record_type, record):
        try:
            if record_type == "news":
                city = record.find('city').text.strip()
                text = record.find('text').text.strip()
                if city and text:
                    news_record = News(city, text)
                    self.manager.write_to_file(news_record)
                else:
                    print(f"Invalid News record: {ET.tostring(record, encoding='unicode')}")

            elif record_type == "private ad":
                text = record.find('text').text.strip()
                expiration_date = record.find('expiration_date').text.strip()
                if text and expiration_date:
                    private_ad_record = PrivateAd(text, expiration_date)
                    self.manager.write_to_file(private_ad_record)
                else:
                    print(f"Invalid Private Ad record: {ET.tostring(record, encoding='unicode')}")

            elif record_type == "custom record":
                custom_fields = record.find('custom_fields').text.strip()
                if custom_fields:
                    custom_record = CustomRecord(record_type, custom_fields)
                    self.manager.write_to_file(custom_record)
                else:
                    print(f"Invalid Custom Record: {ET.tostring(record, encoding='unicode')}")

            else:
                print(f"Unknown record type: {record_type}")

        except Exception as e:
            print(f"Error processing record '{ET.tostring(record, encoding='unicode')}': {e}")


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
        self.manager.write_to_file(record)

    def add_private_ad_record(self):
        text = input("Enter the private ad text: ")
        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
        record = PrivateAd(text, expiration_date)
        self.manager.write_to_file(record)

    def add_custom_record(self):
        record_type = input("Enter your custom record type: ")
        custom_fields = input("Enter your custom fields (comma-separated): ")
        record = CustomRecord(record_type, custom_fields)
        self.manager.write_to_file(record)

    def import_records_from_file(self):
        self.file_input_manager.process_file()

    def import_records_from_json(self):
        self.json_input_manager.process_json_file()

    def import_records_from_xml(self):
        self.xml_input_manager.process_xml_file()

    def run(self):
        while True:
            self.manager.display_menu()

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
                break
            else:
                print("Invalid choice. Please, let's try again.")


if __name__ == "__main__":
    app = Application()
    app.run()
