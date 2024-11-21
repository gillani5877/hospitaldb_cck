import hashlib
import sqlite3
import re
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
import calendar
import time

def set_terminal_size(columns=125, lines=30):
    """Sets the terminal size for Windows."""
    os.system(f'mode con: cols={columns} lines={lines}')

def create_db():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
            kit_no TEXT PRIMARY KEY,
            name TEXT,
            house TEXT,
            grade TEXT,
            reason TEXT,
            admit_date TEXT,
            discharge_date TEXT
        )
    ''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS excuses (
            kit_no TEXT PRIMARY KEY,
            name TEXT,
            grade TEXT,  
            house TEXT,  
            reason TEXT,  
            excuse TEXT,
            start_date TEXT,
            end_date TEXT,
            FOREIGN KEY(kit_no) REFERENCES patients(kit_no)
        )
    ''')
    
    # Create a table for expired excuses
    cursor.execute('''CREATE TABLE IF NOT EXISTS expired_excuses (
            kit_no TEXT PRIMARY KEY,
            name TEXT,
            grade TEXT,  
            house TEXT,  
            reason TEXT,  
            excuse TEXT,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    
    # Create a table for expired admitted patients
    cursor.execute('''CREATE TABLE IF NOT EXISTS expired_patients (
            kit_no TEXT PRIMARY KEY,
            name TEXT,
            house TEXT,
            grade TEXT,
            reason TEXT,
            admit_date TEXT,
            discharge_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine_record (
            kit_no TEXT PRIMARY KEY,
            name TEXT,
            house TEXT,
            medicine_name TEXT,
            date_added TEXT,
            FOREIGN KEY(kit_no) REFERENCES patients(kit_no)
        )
    ''') 
    conn.commit()
    conn.close()


def clear_screen():
    # Clear command for Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Clear command for Linux/Mac
    else:
        _ = os.system('clear')


# Function to validate user choices
def validate_choice(prompt, options):
    choice = input(prompt)
    while choice not in options:
        print("Invalid choice. Please try again.")
        choice = input(prompt)
    return choice

def validate_house(prompt):
    choice = input(prompt)
    options = ['mh','MH','ah',"AH",'ih','IH','kh','KH','rh','RH','jh','JH','jnr','JNR']
    while choice not in options:
        print("Invalid House Name, please write like mh or KH or jnr.")
        choice = input(prompt)
    return choice



def validate_date(date_text):
    try:
        date_obj = datetime.strptime(date_text, '%Y-%m-%d')
        return date_obj
    except ValueError:
        return None

def add_or_admit_patient():
    kit_no = input("Enter Patient's Kit No: ")
    name = input("Enter Patient's Name: ").upper()
    # house = validate_choice("Enter Patient's House: ",['mh','MH','ah',"AH",'ih','IH','kh','KH','rh','RH','jh','JH','jnr','JNR'])
    house = validate_house("Enter Patient's House: ")
    house = house.upper()
    grade = input("Enter Patient's Grade: ")

    reason = input("Enter Reason for Admitting: ").upper()
    discharge_date = None
    admit_date = None

    if reason:
        discharge_date_input = input("Enter Discharge Date (YYYY-MM-DD): ")
        discharge_date_obj = validate_date(discharge_date_input)

        while discharge_date_obj is None or discharge_date_obj <= datetime.now():
            if discharge_date_obj is None:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
            else:
                print("Discharge date must be in the future. Please enter a valid date.")
            discharge_date_input = input("Enter Discharge Date (YYYY-MM-DD): ")
            discharge_date_obj = validate_date(discharge_date_input)

        discharge_date = discharge_date_input
        admit_date = datetime.now().date().isoformat()

    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT OR REPLACE INTO patients (kit_no, name, house, grade, reason, admit_date, discharge_date)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (kit_no, name, house, grade, reason, admit_date, discharge_date))

    conn.commit()
    conn.close()
    print("Patient added/admitted successfully.")

def add_medicine():
    medicine_name = input("Enter Medicine/Item Name: ").strip().upper()
    kit_no = input("Enter Patient's Kit No: ").strip()
    name = input("Enter Patient's Name: ").strip().upper()
    house = validate_house("Enter Patient's House: ")
    house = house.strip().upper()
    date_added = datetime.now().strftime('%d-%m-%Y')


    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO medicine_record (kit_no, name, house, medicine_name, date_added)
        VALUES (?, ?, ?, ?, ?)
    ''', (kit_no, name, house, medicine_name, date_added))

    conn.commit()
    conn.close()
    print("Medicine record added successfully.")


def display_medicine_records():
    # Ask for the month to display
    month = input("Enter the month (1-12) for which you want to display medicine records: ").strip()

    # Validate the month input
    try:
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        print("Invalid month input. Please enter a number between 1 and 12.")
        return

    # Ask for the year to display
    year = input("Enter Year (e.g., 2024): ").strip()
    
    # Validate the year input
    try:
        year = int(year)
    except ValueError:
        print("Invalid year input. Please enter a valid year.")
        return

    # Convert month to two-character format (e.g., "01" for January)
    month_str = f"{month:02d}"
    month_name = calendar.month_name[month]  # Get the month name (e.g., January, February)

    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()

    # Query records for the specified month and year using the full date format "DD-MM-YYYY"
    cursor.execute('''
        SELECT medicine_name, name, kit_no, house, date_added
        FROM medicine_record
    ''')
    records = cursor.fetchall()

    # Filter records based on both month and year from the 'DD-MM-YYYY' format
    filtered_records = [
        record for record in records if record[4][3:5] == month_str and record[4][6:10] == str(year)
    ]  # Slice date_added to get both month and year

    if filtered_records:
        print(f"Medicine Records for {month_name} {year}:")
        for idx, record in enumerate(filtered_records, start=1):
            print(f"({idx}). (Medicine: {record[0]} | Patient's Name: {record[1]} | Kit No.: {record[2]} | House: {record[3]} | Date: {record[4]})\n")
    else:
        print(f"No medicine records found for {month_name} {year}.")

    conn.close()


def export_medicine_records_to_txt():
    # Ask for the month to export
    print("1-12. Enter Month to export Medicine Records (1-12) \n0. Go back")
    month = input("Enter Your Choice: ").strip()

    if month == '0':
        pass
    else:
        # Validate the month input
        try:
            month = int(month)
            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            print("Invalid month input. Please enter a number between 1 and 12.")
            return

        # Ask for the year to export
        year = input("Enter Year (e.g., 2024): ").strip()
        
        # Validate the year input
        try:
            year = int(year)
        except ValueError:
            print("Invalid year input. Please enter a valid year.")
            return

        # Convert month to two-character format (e.g., "01" for January)
        month_str = f"{month:02d}"
        month_name = calendar.month_name[month]  # Get the month name (e.g., January, February)
        
        # Connect to the database
        conn = sqlite3.connect('hospital_records.db')
        cursor = conn.cursor()
        
        # Query records for the specified month and year using full date format "DD-MM-YYYY"
        cursor.execute('''
            SELECT medicine_name, name, kit_no, house, date_added
            FROM medicine_record
        ''')
        records = cursor.fetchall()
        
        # Filter records based on both month and year from the 'DD-MM-YYYY' format
        filtered_records = [
            record for record in records if record[4][3:5] == month_str and record[4][6:10] == str(year)
        ]  # Slice date_added to get both month and year

        # If there are records, save them to a file
        if filtered_records:
            filename = f'prescription_records_{month_name}_{year}.txt'
            with open(filename, 'w') as file:
                for idx, record in enumerate(filtered_records, 1):  # Start serial number at 1
                    # Format and write each record
                    line = f"{idx}.\tMedicine: {record[0]} | Patient's Name: {record[1]} | Kit No: {record[2]} | House: {record[3]} | Date: {record[4]}\n"
                    file.write(line)
            print(f"Medicine records for {month_name} {year} have been successfully exported to '{filename}'.")
        else:
            print(f"No medicine records found for {month_name} {year}.")
        
        # Close the connection to the database
        conn.close()

# Function to add an excuse for a patient
def add_excuse():
    kit_no = input("Enter Patient's Kit No: ")
    name = input("Enter Patient's Name: ").upper()
    grade = input("Enter Patient's Grade: ")
    house = validate_house("Enter Patient's House: ")
    house = house.upper()
    reason = input("Enter Reason for Excuse: ").upper()
    excuse = input("Enter the excuse: ").upper()
    duration_days = int(input("Enter duration in days: "))
    
    start_date = datetime.now().date().isoformat()
    end_date = (datetime.now() + timedelta(days=duration_days)).date().isoformat()
    
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM excuses WHERE kit_no = ? AND excuse = ?', (kit_no, excuse))
    existing_excuse = cursor.fetchone()
    
    if existing_excuse:
        print("An excuse for this patient already exists.")
    else:
        cursor.execute('''INSERT INTO excuses (kit_no, name, grade, house, reason, excuse, start_date, end_date)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (kit_no, name, grade, house, reason, excuse, start_date, end_date))
        conn.commit()
        print("Excuse added successfully.")
    
    conn.close()

# Function to display excuses
def display_excuses():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM excuses')
    records = cursor.fetchall()
    
    print("Excuses Records:")
    for idx, record in enumerate(records, start=1):
        # print(f"({idx}). (Kit No: {record[1]}, Name: {record[2]}, Excuse: {record[6]}, Grade: {record[3]}, House: {record[4]}, Date: {record[7]} to {record[8]})")
        # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Excuse: {record[5]}, Reason: {record[4]}, Grade: {record[2]}, House: {record[3]}, Date: {record[6]} to {record[7]})")
        print(f"({idx}). \t{record[1]} ({record[0]}):\n\tExcuse: {record[5]}\n\tReason: {record[4]}\n\tGrade: {record[2]}\n\tHouse: {record[3]}\n\tDuration: {record[6]} to {record[7]}\n")
    conn.close()

# Function to search for patients
def search_patients():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    search_for = validate_choice("1. Currently Admitted Patients\n2. Past Admitted Patients\n0. Go Back\nEnter Your Choice: ", ['1', '2','0'])

    if search_for == '1':
        search_type = validate_choice("Search by (1) Kit No, (2) House, (3) Grade: ", ['1', '2', '3'])
        search_value = input("Enter search value: ").strip().upper()

        if search_type == '1':
            cursor.execute('SELECT * FROM patients WHERE kit_no = ?', (search_value,))
        elif search_type == '2':
            cursor.execute('SELECT * FROM patients WHERE house = ?', (search_value,))
        elif search_type == '3':
            cursor.execute('SELECT * FROM patients WHERE grade = ?', (search_value,))
        
    elif search_for == '2':
        search_type = validate_choice("Search by (1) Kit No, (2) House, (3) Grade: ", ['1', '2', '3'])
        search_value = input("Enter search value: ").strip().upper()

        if search_type == '1':
            cursor.execute('SELECT * FROM expired_patients WHERE kit_no = ?', (search_value,))
        elif search_type == '2':
            cursor.execute('SELECT * FROM expired_patients WHERE house = ?', (search_value,))
        elif search_type == '3':
            cursor.execute('SELECT * FROM expired_patients WHERE grade = ?', (search_value,))


    records = cursor.fetchall()

    if search_for == '1' or search_for == '2':
        if records:
            print("Search Results:")
            for idx, record in enumerate(records, start=1):
                # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Reason: {record[4]}, Grade: {record[3]}, House: {record[2]}, Date: {record[5]} to {record[6]})")
                print(f"({idx}). \t{record[1]}({record[0]}):\n\tReason: {record[4]}\n\tGrade: {record[3]}\n\tHouse: {record[2]}\n\tDuration: {record[5]} to {record[6]}")
        else:
            print("No matching records found.")

    elif search_for == '0':
        pass

    conn.close()

def display_admitted_patients():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE admit_date IS NOT NULL')
    records = cursor.fetchall()
    
    print("Admitted Patients:")
    for idx, record in enumerate(records, start=1):
        # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Reason: {record[4]}, Grade: {record[3]}, House: {record[2]}, Date: {record[5]} to {record[6]})")
        print(f"({idx}). \t{record[1]}({record[0]}):\n\tReason: {record[4]}\n\tGrade: {record[3]}\n\tHouse: {record[2]}\n\tDuration: {record[5]} to {record[6]}\n")
    
    conn.close()

def search_excuses():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()

    search_type = validate_choice("1. Current Excuses\n2. Expired Excuses\n0. Go Back\nEnter Your Choice: ", ['1', '2', '0'])

    if search_type == '1':
        search_value = validate_choice("Search by (1) Kit No, (2) House, (3) Grade: ", ['1', '2', '3'])
        search_input = input("Enter search value: ").upper().upper()

        if search_value == '1':
            cursor.execute('SELECT * FROM excuses WHERE kit_no = ?', (search_input,))
        elif search_value == '2':
            cursor.execute('SELECT * FROM excuses WHERE house = ?', (search_input,))
        elif search_value == '3':
            cursor.execute('SELECT * FROM excuses WHERE grade = ?', (search_input,))
    elif search_type == '2':
        search_value = validate_choice("Search by (1) Kit No, (2) House, (3) Grade: ", ['1', '2', '3'])
        search_input = input("Enter search value: ").upper().upper()

        if search_value == '1':
            cursor.execute('SELECT * FROM expired_excuses WHERE kit_no = ?', (search_input,))
        elif search_value == '2':
            cursor.execute('SELECT * FROM expired_excuses WHERE house = ?', (search_input,))
        elif search_value == '3':
            cursor.execute('SELECT * FROM expired_excuses WHERE grade = ?', (search_input,))

    records = cursor.fetchall()

    if search_type == '0':
        pass
    
    if search_type == '1' or search_type == '2':
        if records:
            print("Search Results:")
            for idx, record in enumerate(records, start=1):
                # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Excuse: {record[5]}, Reason: {record[4]}, Grade: {record[2]}, House: {record[3]}, Date: {record[6]} to {record[7]})")
                print(f"({idx}). \t{record[1]} ({record[0]}):\n\tExcuse: {record[5]}\n\tReason: {record[4]}\n\tGrade: {record[2]}\n\tHouse: {record[3]}\n\tDuration: {record[6]} to {record[7]}")
        else:
            print("No matching records found.")

    conn.close()

# Function to check and move old records to different tables
def clean_old_records():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.now().date().isoformat()
    
    # Fetch expired excuses
    cursor.execute('SELECT kit_no, name, grade, house, reason, excuse, start_date, end_date FROM excuses WHERE end_date < ?', (today,))
    expired_excuses = cursor.fetchall()

    # Move expired excuses to the expired_excuses table
    if expired_excuses:
        cursor.executemany('''INSERT INTO expired_excuses (kit_no, name, grade, house, reason, excuse, start_date, end_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', expired_excuses)
        cursor.execute('DELETE FROM excuses WHERE end_date < ?', (today,))
        print("Expired Excuses Records moved to the Expired Excuses List.")

    elif not expired_excuses:
        print("No Expired Excuses Found!")
    
    # Fetch expired admitted patients
    cursor.execute('SELECT * FROM patients WHERE discharge_date < ?', (today,))
    expired_patients = cursor.fetchall()
    
    # Move expired patients to the expired_patients table
    if expired_patients:
        cursor.executemany('''INSERT INTO expired_patients (kit_no, name, house, grade, reason, admit_date, discharge_date)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', expired_patients)
        cursor.execute('DELETE FROM patients WHERE discharge_date < ?', (today,))
        print("Old Patient Records moved to Past Admit Patients List.")
    elif not expired_patients:
        print("No Old Patient Records Found!")
    
    conn.commit()
    conn.close()

# Function to display expired excuses
def display_expired_excuses():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM expired_excuses')
    records = cursor.fetchall()
    
    print("Expired Excuses Records:")
    for idx, record in enumerate(records, start=1):
        # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Excuse: {record[5]}, Reason: {record[4]}, Grade: {record[2]}, House: {record[3]}, Date: {record[6]} to {record[7]})")
        print(f"({idx}). \t{record[1]} ({record[0]}):\n\tExcuse: {record[5]}\n\tReason: {record[4]}\n\tGrade: {record[2]}\n\tHouse: {record[3]}\n\tDuration: {record[6]} to {record[7]}\n")
    
    conn.close()

# Function to display expired patients
def display_expired_patients():
    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM expired_patients')
    records = cursor.fetchall()
    
    print("Expired Admitted Patients Records:")
    for idx, record in enumerate(records, start=1):
        # print(f"({idx}). (Kit No: {record[0]}, Name: {record[1]}, Reason: {record[4]}, Grade: {record[3]}, House: {record[2]}, Date: {record[5]} to {record[6]})")
        print(f"({idx}). \t{record[1]}({record[0]}):\n\tReason: {record[4]}\n\tGrade: {record[3]}\n\tHouse: {record[2]}\n\tDuration: {record[5]} to {record[6]}\n")
    conn.close()

def delete_entry():
    print("1. Delete Admitted Patients")
    print("2. Delete Excuses")
    print("0. Exit")
    # delete_type = validate_choice("Delete (1) Admitted Patients or (2) Excuses? ", ['1', '2'])
    delete_type = validate_choice("Enter Your Choice: ", ['1', '2', '0'])

    conn = sqlite3.connect('hospital_records.db')
    cursor = conn.cursor()

    if delete_type == '1':
        record_type = validate_choice("Delete (1) Current Record or (2) Past Record? ", ['1', '2'])
        kit_no = input("Enter Patient's Kit No: ").strip()  # Strip any extra spaces

        if record_type == '1':
            cursor.execute('SELECT * FROM patients WHERE kit_no = ?', (kit_no,))
        elif record_type == '2':
            cursor.execute('SELECT * FROM expired_patients WHERE kit_no = ?', (kit_no,))
        else:
            print("Invalid option.")
            conn.close()
            return
        
        record = cursor.fetchone()
        
        if record:
            confirmation = validate_choice(f"Are you sure you want to delete record for {record[1]},({record[2]}) (Y/N)? ",['y','Y','n','N']).strip().upper()
            if confirmation == 'Y' or confirmation == 'y':
                if record_type == '1':
                    cursor.execute('DELETE FROM patients WHERE kit_no = ?', (kit_no,))
                else:
                    cursor.execute('DELETE FROM expired_patients WHERE kit_no = ?', (kit_no,))
                conn.commit()
                print("Record deleted successfully.")
            elif confirmation == 'N' or confirmation == 'n':
                print("Deletion canceled.")
        else:
            print(f"No matching record found for Kit No: {kit_no}.")

    elif delete_type == '2':
        record_type = validate_choice("Delete (1) Current Excuse or (2) Expired Excuse? ", ['1', '2'])
        kit_no = input("Enter Patient's Kit No: ").strip()  # Strip any extra spaces

        if record_type == '1':
            cursor.execute('SELECT * FROM excuses WHERE kit_no = ?', (kit_no,))
        elif record_type == '2':
            cursor.execute('SELECT * FROM expired_excuses WHERE kit_no = ?', (kit_no,))
        else:
            print("Invalid option.")
            conn.close()
            return
        
        record = cursor.fetchone()

        if record:
            confirmation = validate_choice(f"Are you sure you want to delete excuse for {record[2]},({record[4]}) (Y/N)? ",['y','Y','n','N']).strip().upper()
            if confirmation == 'Y' or confirmation == 'y':
                if record_type == '1':
                    cursor.execute('DELETE FROM excuses WHERE kit_no = ?', (kit_no,))
                else:
                    cursor.execute('DELETE FROM expired_excuses WHERE kit_no = ?', (kit_no,))
                conn.commit()
                print("Excuse deleted successfully.")
            elif confirmation == 'N' or confirmation == 'n':
                print("Deletion canceled.")
        else:
            print(f"No matching record found for Kit No: {kit_no}.")
    
    elif delete_type == '0':
        pass

    else:
        print("Invalid option.")

    conn.close()
# Constants
KEY_FILE = 'secret.key'
DB_FILE = 'users.db'

# Key management
def generate_and_store_key():
    """Generates and saves a key (only for first-time use)."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Loads the encryption key from a file."""
    if not os.path.exists(KEY_FILE):
        generate_and_store_key()  # Generate key if not found
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

# Load the key and create cipher
KEY = load_key()
cipher = Fernet(KEY)

# Database connection setup
def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

# Initialize database
def initialize_db():
    """Initializes the users table if it doesn't exist."""
    print(r"""  _____            _     _              ___                 _       
 |  __ \          (_)   | |            / / |               (_)      
 | |__) |___  __ _ _ ___| |_ ___ _ __ / /| |     ___   __ _ _ _ __  
 |  _  // _ \/ _` | / __| __/ _ \ '__/ / | |    / _ \ / _` | | '_ \ 
 | | \ \  __/ (_| | \__ \ ||  __/ | / /  | |___| (_) | (_| | | | | |
 |_|  \_\___|\__, |_|___/\__\___|_|/_/   |______\___/ \__, |_|_| |_|
              __/ |                                    __/ |        
             |___/                                    |___/      
          Developed by Abdul Subhan(5877)""")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hashed_password TEXT
        )
        """)
        conn.commit()

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_data(data):
    """Encrypts data using Fernet symmetric encryption."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data):
    """Decrypts data using Fernet symmetric encryption."""
    return cipher.decrypt(data.encode()).decode()

def password_strength_check(password):
    """Checks if the password meets the required complexity criteria."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, "Password is strong."

def register_user(username, password):
    """Registers a new user with a hashed and encrypted password."""
    strong, message = password_strength_check(password)
    if not strong:
        print(f"Password Error: {message}")
        return
    
    hashed_password = hash_password(password)
    encrypted_password = encrypt_data(hashed_password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (username, encrypted_password))
            conn.commit()
        print("User registered successfully.")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")

def login_user(username, password):
    """Logs in a user by checking provided credentials against stored data."""
    hashed_password = hash_password(password)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
    
    if row:
        stored_encrypted_password = row[0]
        try:
            stored_hashed_password = decrypt_data(stored_encrypted_password)
            if hashed_password == stored_hashed_password:
                print("Login successful!")
                user_dashboard(username)  # Call another function upon successful login
                return True
        except Exception as e:
            print("Error during decryption:", e)
    
    print("Invalid username or password.")
    return False
    

def user_dashboard(username):
    clear_screen()
    set_terminal_size()
    create_db()
    
    print(r"""  _    _                 _ _        _   _____                        _       _____        _        _                    
 | |  | |               (_) |      | | |  __ \                      | |     |  __ \      | |      | |                   
 | |__| | ___  ___ _ __  _| |_ __ _| | | |__) |___  ___ ___  _ __ __| |___  | |  | | __ _| |_ __ _| |__   __ _ ___  ___ 
 |  __  |/ _ \/ __| '_ \| | __/ _` | | |  _  // _ \/ __/ _ \| '__/ _` / __| | |  | |/ _` | __/ _` | '_ \ / _` / __|/ _ \
 | |  | | (_) \__ \ |_) | | || (_| | | | | \ \  __/ (_| (_) | | | (_| \__ \ | |__| | (_| | || (_| | |_) | (_| \__ \  __/
 |_|  |_|\___/|___/ .__/|_|\__\__,_|_| |_|  \_\___|\___\___/|_|  \__,_|___/ |_____/ \__,_|\__\__,_|_.__/ \__,_|___/\___|
                  | |                                                                                                   
                  |_|                                                                                                   """)
    
    while True:
        # print("\nHospital Management System")
        print("1. Add Record")
        print("2. Delete Records")
        print("3. Search Records")
        print("4. Display Records")
        print("5. Export Medicine Records")
        print("6. Sweep Old Records")
        print("0. Exit")

        choice = validate_choice("Enter your choice: ", ['1', '2', '3', '4', '5', '6', '0'])

        if choice == '1':
            print("1. Admit Patient")
            print("2. Add Excuse")
            print("3. Add Medicine Record")
            print("0. Go Back")

            choice_2 = validate_choice("Enter Your Choice: ",['1','2','3','0'])

            if choice_2 == '1':
                add_or_admit_patient()
            elif choice_2 == '2':
                add_excuse()
            elif choice_2 == '3':
                add_medicine()
            elif choice_2 == '0':
                continue


        elif choice == '2':
            delete_entry()


        elif choice == '3':
            print("1. Search Admitted Patients")
            print("2. Search Excuses")
            print("0. Go Back")

            choice_2 = validate_choice("Enter Your Choice: ",['1','2','0'])

            if choice_2 == '1':
                search_patients()
            elif choice_2 == '2':
                search_excuses()
            elif choice_2 == '0':
                continue


        elif choice == '4':
            print("1. Display All Admitted Patients")
            print("2. Display All Expired Admitted Patients")
            print("3. Display All Excuses")
            print("4. Display All Expired Excuses")
            print("5. Display Medicine Records")
            print("0. Go Back")

            choice_2 = validate_choice("Enter Your Choice: ",['1','2','3','4','5','0'])

            if choice_2 == '1':
                display_admitted_patients()
            elif choice_2 == '2':
                display_expired_patients()
            elif choice_2 == '3':
                display_excuses()
            elif choice_2 == '4':
                display_expired_excuses()
            elif choice_2 == '5':
                display_medicine_records()
            elif choice_2 == '0':
                continue


        elif choice == '5':
            export_medicine_records_to_txt()


        elif choice == '6':
            clean_old_records()

        elif choice == '0':
            print("Exiting.......")
            time.sleep(1)
            break



def main():
    initialize_db()  # Initialize the database on program start
    login_attempts = 3
    while True:
        choice = input("1.Login \n2.Register \n0.Exit\nEnter Your Choice: ").strip().lower()
        if choice == "2":
            print(r"""  _____            _     _              _    _               
 |  __ \          (_)   | |            | |  | |              
 | |__) |___  __ _ _ ___| |_ ___ _ __  | |  | |___  ___ _ __ 
 |  _  // _ \/ _` | / __| __/ _ \ '__| | |  | / __|/ _ \ '__|
 | | \ \  __/ (_| | \__ \ ||  __/ |    | |__| \__ \  __/ |   
 |_|  \_\___|\__, |_|___/\__\___|_|     \____/|___/\___|_|   
              __/ |                                          
             |___/                                           """)
            print("\n")
            string1="cck12345"
            username = input("Enter a username: ").strip()
            password = input("Enter a password: ").strip()
            string = input("Enter PassPhrase: ").strip()
            if string1 == string:
                register_user(username, password)
            elif string1 != string:
                print("Wrong Passphrase")
        elif choice == "1":
            print(r"""  _    _                 _                 _       
 | |  | |               | |               (_)      
 | |  | |___  ___ _ __  | |     ___   __ _ _ _ __  
 | |  | / __|/ _ \ '__| | |    / _ \ / _` | | '_ \ 
 | |__| \__ \  __/ |    | |___| (_) | (_| | | | | |
  \____/|___/\___|_|    |______\___/ \__, |_|_| |_|
                                      __/ |        
                                     |___/           """)
            print("\n")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            if login_user(username, password):
                break
            login_attempts -= 1
            if login_attempts <= 0:
                print("Too many failed attempts. Please try again later.")
                break
        elif choice == "0":
            print("Exiting the program.")
            time.sleep(1)
            break
        else:
            print("Invalid option. Please choose 1,2 or 0.")

if __name__=="__main__":
    main()
