import os
import datetime

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
    def __init__(self, filename="news_feed.txt"):
        self.filename = filename

    def write_to_file(self, record):
        with open(self.filename, "a") as file:
            file.write(record.format_record())
        print("Record added successfully.")

    def display_menu(self):
        print("\nPlease choose one of the following options:")
        print("1. Add a News Record")
        print("2. Add a Private Ad")
        print("3. Add a Custom Record")
        print("4. Import Records from File")
        print("5. Exit")


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
        
        # If file processed successfully, delete it
        os.remove(file_path)
        print(f"File '{file_path}' processed and removed successfully.")

    def process_record_from_line(self, line):
        try:
            # Format: Type|City|Text|ExpirationDate 
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

            # Write to the file using the existing manager
            self.manager.write_to_file(record)
        
        except Exception as e:
            print(f"Error processing line '{line}': {e}")


class Application:
    def __init__(self):
        self.manager = NewsFeedManager()
        self.file_input_manager = FileInputManager(self.manager)

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

    def run(self):
        while True:
            self.manager.display_menu()


            choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

            if choice == '1':
                self.add_news_record()
            elif choice == '2':
                self.add_private_ad_record()
            elif choice == '3':
                self.add_custom_record()
            elif choice == '4':
                self.import_records_from_file()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please, let's try again.")


if __name__ == "__main__":
    app = Application()
    app.run()
