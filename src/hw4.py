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
        print("\nSelect a record type to add:")
        print("1. News")
        print("2. Private Ad")
        print("3. Custom Record")
        print("4. Exit")


class Application:
    def __init__(self):
        self.manager = NewsFeedManager()

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

    def run(self):
            while True:
                self.manager.display_menu()
                print("\nPlease choose one of the following options:")
                print("1. Add a News Record: This allows you to add a news item with city and description.")
                print("2. Add a Private Ad: This allows you to add a private ad with expiration date and description.")
                print(  "3. Add a Custom Record: This allows you to create your own record with a custom type and fields.")
                print("4. Exit: Quit the application.")

                choice = input("Enter your choice (1, 2, 3, or 4): ")

                if choice == '1':
                    self.add_news_record()
                elif choice == '2':
                    self.add_private_ad_record()
                elif choice == '3':
                    self.add_custom_record()
                elif choice == '4':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please, let's try again.")


if __name__ == "__main__":
    app = Application()
    app.run()

