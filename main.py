from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Це обов'язкове поле, воно не може бути пустим.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен складатися з рівно 10 цифр.")
        super().__init__(value)
    
    def __eq__(self, other):
        if isinstance(other, Phone):
            return self.value == other.value
        return False
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Введіть дату в форматі DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone) 
    
    def remove_phone(self, phone_number):
        phone = Phone(phone_number)
        try:
            self.phones.remove(phone)
        except ValueError:
            return(f"Номер {phone_number} не знайдено.")

    def edit_phone(self, old_phone_number, new_phone_number):
        old_phone = Phone(old_phone_number)  
        new_phone = Phone(new_phone_number)
        for i, phone in enumerate(self.phones):
            if phone == old_phone:
                self.phones[i] = new_phone
                return
        raise ValueError(f"Не знайдено запису для {old_phone_number}")
    
    def find_phone(self, phone_number):
        phone = Phone(phone_number)
        for ph in self.phones:
            if ph == phone:
                return ph
        return None
    
    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def __str__(self):
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "не вказаний"
        return f"Ім'я контакту: {self.name.value}, Номери: {'; '.join(p.value for p in self.phones)}, День народження: {birthday_str}"

    def __repr__(self):
        return self.__str__()

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        if name in self.data:
            return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if record.birthday:  
                birthday = record.birthday.value
                current_year_birthday = birthday.replace(year=today.year)
                days_until_birthday = (current_year_birthday - today).days

                if 0 <= days_until_birthday <= 7:
                    days_ahead = 7 - current_year_birthday.weekday() if current_year_birthday.weekday() >= 5 else 0
                    congrats_date = current_year_birthday + timedelta(days=days_ahead)
                    upcoming_birthdays.append(f"Ім'я: {record.name.value} День народження: {birthday} Дата привітання: {congrats_date.strftime('%Y.%m.%d')}")
        if upcoming_birthdays:
            return upcoming_birthdays
        else:
            return "Не має днів народжень в наступні 7 днів."

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())
    
def save_data(contacts, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(contacts, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Контакт не знайдено."
        except IndexError:
            return "Введіть всю необхідну інформацію."
        except AttributeError as e:
            return str(e)
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts):
    if len(args) < 2:
        raise IndexError
    name, phone = args
    record = contacts.find(name)
    if not record:
        record = Record(name)
        contacts.add_record(record)
    record.add_phone(phone)
    return "Contact added."

@input_error
def change_contact(args, contacts):
    if len(args) < 3:
        raise IndexError
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError

@input_error
def show_phone(args, contacts):
    if len(args) < 1:
        raise IndexError
    name = args[0]
    record = contacts.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    else:
        raise KeyError

@input_error
def show_all(contacts):
    if contacts:
        return str(contacts)
    else:
        return "No contacts available."

@input_error
def add_birthday(args, contacts):
    if len(args) < 2:
        raise IndexError
    name, birthday = args
    record = contacts.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError

@input_error
def show_birthday(args, contacts):
    if len(args) < 1:
        raise IndexError
    name = args[0]
    record = contacts.find(name)
    if record:
        if record.birthday:
            return f"Ім'я: {record.name.value} День народження: {record.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"Ім'я: {record.name.value} День народження: не вказаний"
    else:
        raise KeyError

@input_error
def birthdays(contacts):
    return contacts.get_upcoming_birthdays()

def main():
    contacts = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(contacts)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))                   
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
