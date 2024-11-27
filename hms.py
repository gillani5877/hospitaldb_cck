import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.messagebox as tkmb
import hashlib
import os
import sqlite3
from re import search
from datetime import datetime, timedelta
import calendar
from tkinter import messagebox as stkmb
import sys 
from pathlib import Path
import os



def create_folder(folder_path):
    """
    Checks if the folder exists and creates it if not.
    :param folder_path: The path of the folder to check/create.
    """
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Create the folder (including intermediate directories if needed)
            # print(f"Folder created: {folder_path}")
        else:
            # print(f"Folder already exists: {folder_path}")
            pass
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage



def get_documents_folder():
    """
    Returns the path to the user's Documents folder.
    Handles cross-platform cases.
    """
    # Windows, macOS, and Linux support
    documents_folder = Path.home() / "Documents"
    
    # Verify the folder exists
    if documents_folder.exists() and documents_folder.is_dir():
        return str(documents_folder)
    else:
        tkmb.showerror(title = "Error", message = "The Documents folder could not be found on this system.")

try:
    user_documents = get_documents_folder()
except FileNotFoundError as e:
    tkmb.showerror(title = "Error", message = f"{e}")


folder_path = f"{user_documents}\\HMS Database"
create_folder(folder_path)

# Get Path of exe
def get_exe_location():
    # Check if the script is running as an executable or from the source script
    if getattr(sys, 'frozen', False):
        # If running from a bundled .exe
        exe_location = os.path.dirname(sys.executable)
    else:
        # If running from the source Python script
        exe_location = os.path.dirname(os.path.abspath(sys.argv[0]))

    return exe_location

exe_path = get_exe_location()


# Database setup
def initialize_db():
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        hashed_password TEXT,
        salt TEXT
    )
    """)
    conn.commit()
    conn.close()

def create_db():
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
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

# Hashing function
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    password_salt = salt + password.encode()
    return hashlib.sha256(password_salt).hexdigest(), salt

# def clear_entry(frame):
#     for widget in frame.winfo_children():
#         # Reset CTkEntry widgets
#         if isinstance(widget, ctk.CTkEntry):
#             widget.delete(0, "end")  # Clear the entry widget
#         # Reset CTkComboBox widgets (dropdowns)
#         elif isinstance(widget, ctk.CTkComboBox):
#             widget.set("")  # Set the dropdown to an empty state
#         # Add checks for other widgets if needed

def clear_entry(frame):
    for widget in frame.winfo_children():
        # Reset CTkEntry widgets
        if isinstance(widget, ctk.CTkEntry):
            if widget.get() != "":  # Only clear user input, don't interfere with placeholder
                widget.delete(0, "end")  # Clear the entry widget
        # Reset CTkComboBox widgets (dropdowns)
        elif isinstance(widget, ctk.CTkComboBox):
            widget.set("")  # Set the dropdown to an empty state
        # Add checks for other widgets if needed





# Register user function
def register_user(username, password):
    if username_exists(username):
        tkmb.showerror(title="Username Exists", message="This username is already taken. Please choose another one.")
        return
    hashed_password, salt = hash_password(password)
    try:
        conn = sqlite3.connect(f"{user_documents}\\HMS Database\\users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)",
                       (username, hashed_password, salt.hex()))
        conn.commit()
        tkmb.showinfo(title="Registration Successful", message="User registered successfully!")
        clear_entry(register_frame)
    except sqlite3.IntegrityError:
        tkmb.showerror(title="Registration Error", message="This username is already taken.")
    finally:
        conn.close()

# Check if a username already exists in the database
def username_exists(username):
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Login function
def login():
    username = user_entry.get()
    password = user_pass.get()
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_password, stored_salt = result
        salt = bytes.fromhex(stored_salt)
        hashed_password, _ = hash_password(password, salt)
        if hashed_password == stored_password:
            tkmb.showinfo(title="Login Successful", message="You have logged in successfully!")
            clear_entry(login_frame)
            show_frame(main_frame)
            app.geometry("500x600")
        else:
            tkmb.showerror(title="Login Failed", message="Invalid Username or Password")
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username or Password")

def show_registration_window():
    login_frame.pack_forget()
    register_frame.pack(pady=20, padx=40, fill='both', expand=True)
    app.geometry("500x600")

def show_login_screen():
    register_frame.pack_forget()
    login_frame.pack(pady=20, padx=40, fill='both', expand=True)
    app.geometry("400x550")

def show_frame(frame):
    for f in [add_frame, search_frame, delete_frame, export_frame, main_frame, login_frame, register_frame, admit_frame, excuse_frame, medicine_frame]:
        f.pack_forget()
    frame.pack(pady=20, padx=40, fill='both', expand=True)

def logout():
    show_frame(login_frame)
    app.geometry("400x550")

def register_new_user():
    username = reg_user_entry.get()
    password = reg_pass_entry.get()
    confirm_password = confirm_pass_entry.get()
    passphrase = reg_passphrase_entry.get()
    if username == "" or password == "" or confirm_password == "" or passphrase == "":
        tkmb.showinfo(title="Insufficient Info", message="Please fill out all fields!")
    elif password == confirm_password:
        if passphrase == "cck12345":
            register_user(username, password)
            show_login_screen()
        else:
            tkmb.showinfo(title="Invalid Security Phrase", message="Security passphrase is incorrect!")
    else:
        tkmb.showinfo(title="Password Mismatch", message="Passwords don't Match!")

# Initialize database
initialize_db()
create_db()


# GUI setup
ctk.set_appearance_mode("system")
current_mode = ctk.get_appearance_mode()
app = ctk.CTk()
app.geometry("400x550")
app.title("Hospital Records Database")


# Input Medicine Record into DB
def inputmeddata():
    medicine_name = medicine_name_entry.get()
    kit_no = medicine_kitno_entry.get()
    name = medicine_patient_name_entry.get()
    house = medicine_house_dropdown.get()
    if house == "Iqbal House":
        house = "IH"
    elif house == "Khushal House":
        house = "KH"
    elif house == "Jinnah House":
        house = "JH"
    elif house == "Ayub House":
        house = "AH"
    elif house == "Munawar House":
        house = "MH"
    elif house == "Rustam House":
        house = "RH"
    elif house == "Junior House":
        house = "JNR"
    house = house.strip().upper()
    date_added = datetime.now().strftime('%d-%m-%Y')

    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicine_record (kit_no, name, house, medicine_name, date_added)
        VALUES (?, ?, ?, ?, ?)
    ''', (kit_no, name, house, medicine_name, date_added))
    conn.commit()
    conn.close()
    tkmb.showinfo(title="Succesful", message="Medicine Records Added Succesfully.")

# Admit Data Input
def inputadmitdata():
    kit_no = admit_kit_no_entry.get()
    name = admit_name_entry.get().upper()
    house = admit_house_dropdown.get()
    if house == "Iqbal House":
        house = "IH"
    elif house == "Khushal House":
        house = "KH"
    elif house == "Jinnah House":
        house = "JH"
    elif house == "Ayub House":
        house = "AH"
    elif house == "Munawar House":
        house = "MH"
    elif house == "Rustam House":
        house = "RH"
    elif house == "Junior House":
        house = "JNR"
    grade = admit_grade_dropdown.get()
    reason = admit_reason_entry.get().upper()
    admit_date = datetime.now().date().isoformat()
    discharge_date = admit_discharge_date_entry.get()
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO patients (kit_no, name, house, grade, reason, admit_date, discharge_date)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (kit_no, name, house, grade, reason, admit_date, discharge_date))

    conn.commit()
    conn.close()
    tkmb.showinfo(title="Succesful", message="Admit Patient Record Added Succesfully.")

# Excuse Data Input
def inputexcusedata():
    kit_no = excuse_kit_no_entry.get()
    name = excuse_name_entry.get().upper()
    grade = excuse_grade_dropdown.get()
    house = excuse_house_dropdown.get()
    if house == "Iqbal House":
        house = "IH"
    elif house == "Khushal House":
        house = "KH"
    elif house == "Jinnah House":
        house = "JH"
    elif house == "Ayub House":
        house = "AH"
    elif house == "Munawar House":
        house = "MH"
    elif house == "Rustam House":
        house = "RH"
    elif house == "Junior House":
        house = "JNR"
    reason = excuse_reason_entry.get().upper()
    excuse = excuse_excuse_entry.get().upper()
    duration_days = int(excuse_duration_days_entry.get())
    start_date = datetime.now().date().isoformat()
    end_date = (datetime.now() + timedelta(days=duration_days)).date().isoformat()
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM excuses WHERE kit_no = ? AND excuse = ?', (kit_no, excuse))
    existing_excuse = cursor.fetchone()
    
    if existing_excuse:
        tkmb.showinfo(title = "Excuse Already Exists", message = "An excuse for this patient already exists.")
    else:
        cursor.execute('''INSERT INTO excuses (kit_no, name, grade, house, reason, excuse, start_date, end_date)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (kit_no, name, grade, house, reason, excuse, start_date, end_date))
        conn.commit()
        tkmb.showinfo(title = "Succesful", message = "Excuse record added successfully")
        clear_entry(excuse_frame)
    
    conn.close()


# Functions for sweeping records
def sweep_old_records():
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
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
        a= "Expired Excuses Records moved to the Expired Excuses List."

    elif not expired_excuses:
        a= "No Expired Excuses Found!"
    
    # Fetch expired admitted patients
    cursor.execute('SELECT * FROM patients WHERE discharge_date < ?', (today,))
    expired_patients = cursor.fetchall()
    
    # Move expired patients to the expired_patients table
    if expired_patients:
        cursor.executemany('''INSERT INTO expired_patients (kit_no, name, house, grade, reason, admit_date, discharge_date)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', expired_patients)
        cursor.execute('DELETE FROM patients WHERE discharge_date < ?', (today,))
        b= "Old Patient Records moved to Past Admit Patients List."
    elif not expired_patients:
        b= "No Old Patient Records Found!"
    
    tkmb.showinfo(title = "Done", message = f"{a}\n{b}")
    
    conn.commit()
    conn.close()

# Export Medicine Records to txt file
def export_records():
    month = month_entry.get().strip()

    if month == '0':
        pass
    else:
        # Validate the month input
        try:
            month = int(month)
            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            tkmb.showinfo(title = "Invalid Input", message = "Please enter a month between 1 and 12.")
            return

        # Ask for the year to export
        year = year_entry.get().strip()
        
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
        conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
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
            filename = f"{user_documents}\\HMS Database\\prescription_records_{month_name}_{year}.txt"
            with open(filename, 'w') as file:
                for idx, record in enumerate(filtered_records, 1):  # Start serial number at 1
                    # Format and write each record
                    line = f"{idx}.\tMedicine: {record[0]} | Patient's Name: {record[1]} | Kit No: {record[2]} | House: {record[3]} | Date: {record[4]}\n"
                    file.write(line)
            tkmb.showinfo(title = "Succesful", message = f"Medicine records for {month_name} {year} have been successfully exported to '{filename}'.")
            clear_entry(export_frame)
        else:
            tkmb.showerror(title = "Records Not Found", message = f"No medicine records found for {month_name} {year}.")
        
        # Close the connection to the database
        conn.close()

# Delete Records from DB
def delete_entry():

    delete_type = record_type_dropdown.get()
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
    cursor = conn.cursor()
    # Admitted Patients
    # Past Admitted Patients
    # Excuses
    # Expired Excuses
    if delete_type == 'Admitted Patients':
        kit_no = delete_kitno_entry.get()

        cursor.execute('SELECT * FROM patients WHERE kit_no = ?', (kit_no,))
        record = cursor.fetchone()
        
        if record:
            confirmation = stkmb.askyesno(title = "Confirm", message = f"Are you sure you want to delete record for {record[1]},({record[2]})?")
            if confirmation == True:
                cursor.execute('DELETE FROM patients WHERE kit_no = ?', (kit_no,))
                conn.commit()
                tkmb.showinfo(title = "Done", message = f"Record for {record[1]},({record[2]}) deleted successfully.")
                clear_entry(delete_frame)
            elif confirmation == False:
                tkmb.showinfo(title = "Cancelled", message = "Deletion Cancelled.")
        else:
            tkmb.showerror(title = "Not Found", message = f"No matching record found for Kit No: {kit_no}.")

    elif delete_type == 'Past Admitted Patients':
        record_type = record_type_dropdown.get()
        kit_no = delete_kitno_entry.get()

        cursor.execute('SELECT * FROM expired_patients WHERE kit_no = ?', (kit_no,))
        record = cursor.fetchone()

        if record:
            confirmation = stkmb.askyesno(title = "Confirm", message = f"Are you sure you want to delete record for {record[1]},({record[2]})?")
            if confirmation == True:
                cursor.execute('DELETE FROM expired_patients WHERE kit_no = ?', (kit_no,))
                conn.commit()
                tkmb.showinfo(title = "Succesful", message = f"Past Admitted Patient Record for {record[1]}({record[2]} deleted successfully.")
                clear_entry(delete_frame)
            elif confirmation == False:
                tkmb.showinfo(title = "Cancelled", message = f"Deletion Cancelled")
        else:
            tkmb.showerror(title = "Not Found", message = f"No matching record found for Kit No: {kit_no}.")


    # Delete Excuses
    elif delete_type == 'Excuses':
        record_type = record_type_dropdown.get()
        kit_no = delete_kitno_entry.get()

        cursor.execute('SELECT * FROM excuses WHERE kit_no = ?', (kit_no,))
        record = cursor.fetchone()
        
        if record:
            confirmation = stkmb.askyesno(title = "Confirm", message = f"Are you sure you want to delete record for {record[2]},({record[4]})?")
            if confirmation == True:
                cursor.execute('DELETE FROM excuses WHERE kit_no = ?', (kit_no,))
                conn.commit()
                tkmb.showinfo(title = "Done", message = f"Record for {record[2]},({record[4]}) deleted successfully.")
                clear_entry(delete_frame)
            elif confirmation == False:
                tkmb.showinfo(title = "Cancelled", message = "Deletion Cancelled.")
        else:
            tkmb.showerror(title = "Not Found", message = f"No matching record found for Kit No: {kit_no}.")

    # Delete Expired Excuse
    elif delete_type == 'Expired Excuses':
        record_type = record_type_dropdown.get()
        kit_no = delete_kitno_entry.get()

        cursor.execute('SELECT * FROM expired_excuses WHERE kit_no = ?', (kit_no,))
        record = cursor.fetchone()

        if record:
            confirmation = stkmb.askyesno(title = "Confirm", message = f"Are you sure you want to delete record for {record[2]},({record[4]})?")
            if confirmation == True:
                cursor.execute('DELETE FROM expired_excuses WHERE kit_no = ?', (kit_no,))
                conn.commit()
                tkmb.showinfo(title = "Succesful", message = f"Past Admitted Patient Record for {record[2]}({record[4]} deleted successfully.")
                clear_entry(delete_frame)
            elif confirmation == False:
                tkmb.showinfo(title = "Cancelled", message = f"Deletion Cancelled")
        else:
            tkmb.showerror(title = "Not Found", message = f"No matching record found for Kit No: {kit_no}.")
    


    else:
        tkmb.showerror(title = "Invalid option.", message = "Please select a valid option")
    conn.close()

# Search Function
def search_record():
    conn = sqlite3.connect(f"{user_documents}\\HMS Database\\hospital_records.db")
    cursor = conn.cursor()
    # Admitted Patients
    # Past Admitted Patients
    # Excuses
    # Expired Excuses

    search_for = search_for_dropdown.get()

    if search_for == 'Admitted Patients':
        search_type = search_type_dropdown.get()
        search_value = search_value_entry.get().upper()

        if search_type == 'Kit No':
            cursor.execute('SELECT * FROM patients WHERE kit_no = ?', (search_value,))
        elif search_type == 'House':
            cursor.execute('SELECT * FROM patients WHERE house = ?', (search_value,))
        elif search_type == 'Grade':
            cursor.execute('SELECT * FROM patients WHERE grade = ?', (search_value,))
        records = cursor.fetchall()

    elif search_for == 'Past Admitted Patients':
        search_type = search_type_dropdown.get()
        search_value = search_value_entry.get().upper()

        if search_type == 'Kit No':
            cursor.execute('SELECT * FROM expired_patients WHERE kit_no = ?', (search_value,))
        elif search_type == 'House':
            cursor.execute('SELECT * FROM expired_patients WHERE house = ?', (search_value,))
        elif search_type == 'Grade':
            cursor.execute('SELECT * FROM expired_patients WHERE grade = ?', (search_value,))
        records = cursor.fetchall()


    elif search_for == 'Current Excuses':
        search_type = search_type_dropdown.get()
        search_value = search_value_entry.get().upper()

        if search_type == 'Kit No':
            cursor.execute('SELECT * FROM excuses WHERE kit_no = ?', (search_value,))
        elif search_type == 'House':
            cursor.execute('SELECT * FROM excuses WHERE house = ?', (search_value,))
        elif search_type == 'Grade':
            cursor.execute('SELECT * FROM excuses WHERE grade = ?', (search_value,))
        records = cursor.fetchall()


    elif search_type == 'Expired Excuses':
        search_type = search_type_dropdown.get()
        search_value = search_value_entry.get().upper()

        if search_type == 'Kit No':
            cursor.execute('SELECT * FROM expired_excuses WHERE kit_no = ?', (search_value,))
        elif search_type == 'House':
            cursor.execute('SELECT * FROM expired_excuses WHERE house = ?', (search_value,))
        elif search_type == 'Grade':
            cursor.execute('SELECT * FROM expired_excuses WHERE grade = ?', (search_value,))
        records = cursor.fetchall()


    # Create a new CTkToplevel window for the search results
    results_window = ctk.CTkToplevel()
    results_window.title("Search Results")
    results_window.geometry("400x600")
    results_window.lift()
    results_window.attributes("-topmost", 1)
    results_window.focus_force()
    results_window.grab_set()
    
    # Create a scrollable frame inside the window
    scrollable_frame = ctk.CTkScrollableFrame(results_window, width=580, height=380)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    if search_for in ["Admitted Patients", "Past Admitted Patients"]:
        if records:
            for idx, record in enumerate(records, start=1):
                # Add a label for each record inside the scrollable frame
                label = ctk.CTkLabel(scrollable_frame, text=(
                    f"({idx}). \t{record[1]} ({record[0]}):\n"
                    f"\tReason: {record[4]}\n"
                    f"\tGrade: {record[3]}\n"
                    f"\tHouse: {record[2]}\n"
                    f"\tDuration: {record[5]} to {record[6]}"
                ), justify="left", anchor="w", wraplength=560)
                label.pack(anchor="w", padx=10, pady=5)
            clear_entry(search_frame)

        else:
            error_label = ctk.CTkLabel(scrollable_frame, text="No matching records found.", text_color="red")
            error_label.pack(pady=10)
    
    elif search_for in ["Current Excuses", "Expired Excuses"]:
        if records:
            for idx, record in enumerate(records, start=1):
                # Add a label for each record inside the scrollable frame
                label = ctk.CTkLabel(scrollable_frame, text=(
                    f"({idx}). \t{record[1]} ({record[0]}):\n"
                    f"\tExcuse: {record[5]}\n"
                    f"\tReason: {record[4]}\n"
                    f"\tGrade: {record[2]}\n"
                    f"\tHouse: {record[3]}\n"
                    f"\tDuration: {record[6]} to {record[7]}"
                ), justify="left", anchor="w", wraplength=560)
                label.pack(anchor="w", padx=10, pady=5)
            clear_entry(search_frame)
            
        else:
            # Display a red error message if no records are found
            error_label = ctk.CTkLabel(scrollable_frame, text="No matching records found.", text_color="red")
            error_label.pack(pady=10)

    else:
        tkmb.showerror(title = "Not Found", message = "No matching records found.")

    conn.close()


# Common top header for frames
def create_top_header(parent_frame):
    top_frame = ctk.CTkFrame(parent_frame)
    top_frame.pack(pady=5, padx=5, fill="x")
    top_canvas = tk.Canvas(top_frame, width=120, height=120, bd=0, highlightthickness=0,
                           bg="#cfcfcf" if current_mode == "Light" else "#333333")
    top_canvas.pack(pady=5)
    
    img = Image.open(f"{exe_path}\\assets\\cck.png").resize((120, 120))
    img_photo = ImageTk.PhotoImage(img)
    
    # Keep a reference to the image to prevent garbage collection
    top_canvas.image = img_photo  # Fixed reference
    top_canvas.create_image(0, 0, anchor="nw", image=img_photo)
    
    label = ctk.CTkLabel(top_frame, text="Hospital Records Database", font=("Gisha", 20))
    label.pack()


# Login Frame
login_frame = ctk.CTkFrame(master=app)
if current_mode == "Light":
    canvas = tk.Canvas(login_frame, width=120, height=120, bd=0, highlightthickness=0, bg="#dbdbdb")
    canvas.pack(pady=20)
else:
    canvas = tk.Canvas(login_frame, width=120, height=120, bd=0, highlightthickness=0, bg="#2b2b2b")
    canvas.pack(pady=20)

image = Image.open(f"{exe_path}\\assets\\cck.png").resize((120, 120)).convert("RGBA")
photo = ImageTk.PhotoImage(image)
canvas.image = photo  # type: ignore # Keep reference to prevent garbage collection
canvas.create_image(0, 0, anchor="nw", image=photo)
label = ctk.CTkLabel(master=login_frame, text='Enter Login Details')
label.pack(pady=12, padx=10)
user_entry = ctk.CTkEntry(master=login_frame, placeholder_text="Username")
user_entry.pack(pady=12, padx=10)
user_pass = ctk.CTkEntry(master=login_frame, placeholder_text="Password", show="*")
user_pass.pack(pady=12, padx=10)
button = ctk.CTkButton(master=login_frame, text='Login', command=login)
button.pack(pady=12, padx=10)
register_button = ctk.CTkButton(master=login_frame, text='Register New User', command=show_registration_window)
register_button.pack(pady=12, padx=10)
exit_button = ctk.CTkButton(master=login_frame, text="Exit", command=app.quit)
exit_button.pack(pady=10, padx=10)
credit_label = ctk.CTkLabel(master=login_frame, text='Developed by Gillani5877', text_color="#5DADE2")
credit_label.pack(side="left", pady=12, padx=10)

# Registration Frame
register_frame = ctk.CTkFrame(master=app)
reg_canvas = tk.Canvas(register_frame, width=100, height=100, bd=0, highlightthickness=0,
                       bg="#dbdbdb" if current_mode == "Light" else "#2b2b2b")
reg_canvas.pack(pady=20)
reg_image = Image.open(f"{exe_path}\\assets\\user.png").resize((100, 100)).convert("RGBA")
reg_photo = ImageTk.PhotoImage(reg_image)
reg_canvas.image = reg_photo  # Keep reference to prevent garbage collection
reg_canvas.create_image(0, 0, anchor="nw", image=reg_photo)
reg_label = ctk.CTkLabel(register_frame, text="Enter Registration Details:", font=("Arial", 16))
reg_label.pack(pady=12, padx=10)
reg_user_entry = ctk.CTkEntry(register_frame, placeholder_text="Enter username")
reg_user_entry.pack(pady=12, padx=10)
reg_pass_entry = ctk.CTkEntry(register_frame, placeholder_text="Enter password", show="*")
reg_pass_entry.pack(pady=12, padx=10)
confirm_pass_entry = ctk.CTkEntry(register_frame, placeholder_text="Confirm password", show="*")
confirm_pass_entry.pack(pady=12, padx=10)
reg_passphrase_entry = ctk.CTkEntry(register_frame, placeholder_text="Enter passphrase", show="*")
reg_passphrase_entry.pack(pady=12, padx=10)
reg_button = ctk.CTkButton(register_frame, text="Register", command=register_new_user)
reg_button.pack(pady=12, padx=10)
back_button = ctk.CTkButton(register_frame, text="Back to Login", command=show_login_screen)
back_button.pack(pady=12, padx=10)
exit_button = ctk.CTkButton(register_frame, text="Exit", command=app.quit)
exit_button.pack(pady=10, padx=10)

# Main Frame
main_frame = ctk.CTkFrame(master=app)
top_frame = ctk.CTkFrame(main_frame)
top_frame.pack(pady=5, padx=5, fill="x")
if current_mode == "Light":
    top_canvas = tk.Canvas(top_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img = Image.open(f"{exe_path}\\assets\\main.png").resize((400, 100))
else:
    top_canvas = tk.Canvas(top_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img = Image.open(f"{exe_path}\\assets\\main.png").resize((400, 100))
img_photo = ImageTk.PhotoImage(img)
top_canvas.image = img_photo  # Keep reference to prevent garbage collection
top_canvas.create_image(0, 0, anchor="nw", image=img_photo)
top_canvas.pack(pady=5)

# label = ctk.CTkLabel(top_frame, text="Hospital Records Management", font=("Roboto Slab", 20))
# label.pack()

# Buttons for main functionalities
add_button = ctk.CTkButton(main_frame, text="Add New Record", command=lambda: show_frame(add_frame))
add_button.pack(pady=10)
search_button = ctk.CTkButton(main_frame, text="Search Record", command=lambda: show_frame(search_frame))
search_button.pack(pady=10)
delete_button = ctk.CTkButton(main_frame, text="Delete Record", command=lambda: show_frame(delete_frame))
delete_button.pack(pady=10)
export_button = ctk.CTkButton(main_frame, text="Export Medicine \nRecords", command=lambda: show_frame(export_frame))
export_button.pack(pady=10)
sweep_button = ctk.CTkButton(main_frame, text="Sweep Old Records", command=sweep_old_records)
sweep_button.pack(pady=10)
logout_button = ctk.CTkButton(main_frame, text="Logout", command=lambda: logout())
logout_button.pack(pady=10)
exit_button = ctk.CTkButton(main_frame, text="Exit", command=app.quit)
exit_button.pack(pady=10, padx=10)

# Add Record Frame
add_frame = ctk.CTkFrame(master=app)
# add_label = ctk.CTkLabel(add_frame, text="Add New Record", font=("Arial", 16))
# add_label.pack(pady=10)
img_photo_ref_add = None
if current_mode == "Light":
    add_canvas = tk.Canvas(add_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img4 = Image.open(f"{exe_path}\\assets\\add.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_add = ImageTk.PhotoImage(img4)  # Keep a reference to prevent garbage collection
    add_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_add)
elif current_mode == "Dark":
    add_canvas = tk.Canvas(add_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img4 = Image.open(f"{exe_path}\\assets\\add.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_add = ImageTk.PhotoImage(img4)  # Keep a reference to prevent garbage collection
    add_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_add)
add_canvas.pack(side="top", padx=10, pady=5)
add_admit_button = ctk.CTkButton(add_frame, text="Add Admit Patient", command=lambda: (show_frame(admit_frame), app.geometry("800x600")))
add_admit_button.pack(pady=10, padx=10)
add_excuse_button = ctk.CTkButton(add_frame, text="Add Excuse Record", command=lambda: (show_frame(excuse_frame), app.geometry("800x600")))
add_excuse_button.pack(pady=10, padx=10)
add_medicine_button = ctk.CTkButton(add_frame, text="Add Medicine Record", command=lambda: show_frame(medicine_frame))
add_medicine_button.pack(pady=10, padx=10)
go_back_button = ctk.CTkButton(add_frame, text="Go Back", command=lambda: show_frame(main_frame))
go_back_button.pack(pady=10, padx=10)

# Search Record Frame
search_frame = ctk.CTkFrame(master=app)
img_photo_ref_search = None
if current_mode == "Light":
    search_canvas = tk.Canvas(search_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img2 = Image.open(f"{exe_path}\\assets\\search.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_search = ImageTk.PhotoImage(img2)  # Keep a reference to prevent garbage collection
    search_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_search)
elif current_mode == "Dark":
    search_canvas = tk.Canvas(search_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img2 = Image.open(f"{exe_path}\\assets\\search.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_search = ImageTk.PhotoImage(img2)  # Keep a reference to prevent garbage collection
    search_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_search)
search_canvas.pack(side="top", padx=10, pady=5)
search_for_label = ctk.CTkLabel(search_frame, text="Search for:", font=("Arial", 14))
search_for_label.pack(pady=12, padx=10)
search_for_dropdown = ctk.CTkComboBox(
    master=search_frame,
    values=["Admitted Patients", "Past Admitted Patients", "Current Excuses", "Expired Excuses"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
search_for_dropdown.pack(pady=10, padx=10)
search_by_label = ctk.CTkLabel(search_frame, text="Search by:", font=("Arial", 14))
search_by_label.pack(pady=12, padx=10)
search_type_dropdown = ctk.CTkComboBox(
    master=search_frame,
    values=["Kit No", "House", "Grade"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
search_type_dropdown.pack(pady=10, padx=10)
search_by_label = ctk.CTkLabel(search_frame, text="Enter Search Value:", font=("Arial", 14))
search_by_label.pack(pady=12, padx=10)
search_value_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter Search Value")
search_value_entry.pack(pady=5)
search_search_button = ctk.CTkButton(search_frame, text="Search", command=lambda: search_record())
search_search_button.pack(pady=10, padx=10)
search_go_back_button = ctk.CTkButton(search_frame, text="Go Back", command=lambda: (show_frame(main_frame), clear_entry(search_frame)))
search_go_back_button.pack(pady=10, padx=10)
search_frame.pack()

# Delete Record Frame
delete_frame = ctk.CTkFrame(master=app)
if current_mode == "Light":
    delete_canvas = tk.Canvas(delete_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img3 = Image.open(f"{exe_path}\\assets\\delete.png").resize((400, 100))
    img_photo = ImageTk.PhotoImage(img3)  # Keep a reference to prevent garbage collection
    delete_canvas.create_image(-0, 0, anchor="nw", image=img_photo)
elif current_mode == "Dark":
    delete_canvas = tk.Canvas(delete_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img3 = Image.open(f"{exe_path}\\assets\\delete.png").resize((400, 100))
    img_photo = ImageTk.PhotoImage(img3)  # Keep a reference to prevent garbage collection
    delete_canvas.create_image(-0, 0, anchor="nw", image=img_photo)
delete_canvas.pack(side="top", padx=10, pady=5)

delete_type_label = ctk.CTkLabel(delete_frame, text="Select Delete Type:", font=("Arial", 16))
delete_type_label.pack(pady=10)
record_type_dropdown = ctk.CTkComboBox(
    master=delete_frame,
    values=["Admitted Patients", "Past Admitted Patients", "Excuses", "Expired Excuses"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
record_type_dropdown.pack(pady=10, padx=10)
delete_label = ctk.CTkLabel(delete_frame, text="Enter Kit No:", font=("Arial", 16))
delete_label.pack(pady=10)
delete_kitno_entry = ctk.CTkEntry(delete_frame, placeholder_text="Kit Number")
delete_kitno_entry.pack(pady=5)
delete_button_exec = ctk.CTkButton(delete_frame, text="Delete", command=lambda: delete_entry())
delete_button_exec.pack(pady=10)
delete_back_button = ctk.CTkButton(delete_frame, text="Back", command=lambda: (show_frame(main_frame), clear_entry(delete_frame)))
delete_back_button.pack(pady=5)



# Export Records Frame
export_frame = ctk.CTkFrame(master=app)
img_photo_ref_export = None
if current_mode == "Light":
    export_canvas = tk.Canvas(export_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img3 = Image.open(f"{exe_path}\\assets\\export.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_export = ImageTk.PhotoImage(img3)  # Keep a reference to prevent garbage collection
    export_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_export)
elif current_mode == "Dark":
    export_canvas = tk.Canvas(export_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img3 = Image.open(f"{exe_path}\\assets\\export.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_export = ImageTk.PhotoImage(img3)  # Keep a reference to prevent garbage collection
    export_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_export)
export_canvas.pack(side="top", padx=10, pady=5)
export_label = ctk.CTkLabel(export_frame, text="Enter Month No:", font=("Arial", 15))
export_label.pack(pady=10)
month_entry = ctk.CTkEntry(export_frame, placeholder_text="Enter Month")
month_entry.pack(pady=10, padx=10)
export_label = ctk.CTkLabel(export_frame, text="Enter Year:", font=("Arial", 15))
export_label.pack(pady=10)
year_entry = ctk.CTkEntry(export_frame, placeholder_text="Enter Year")
year_entry.pack(pady=10, padx=10)
export_button_exec = ctk.CTkButton(export_frame, text="Export", command=lambda: export_records())
export_button_exec.pack(pady=10)
export_back_button = ctk.CTkButton(export_frame, text="Back", command=lambda: show_frame(main_frame))
export_back_button.pack(pady=5)

# Admit Patients Frame
admit_frame = ctk.CTkFrame(master=app)
img_photo_ref_admit = None
if current_mode == "Light":
    admit_canvas = tk.Canvas(admit_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img5 = Image.open(f"{exe_path}\\assets\\admit.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_admit = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    admit_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_admit)
elif current_mode == "Dark":
    admit_canvas = tk.Canvas(admit_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img5 = Image.open(f"{exe_path}\\assets\\admit.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_admit = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    admit_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_admit)
# Configure columns to have equal weight for uniform widths
admit_frame.columnconfigure((0, 1), weight=1, uniform="col")  # Columns 0 and 1 are of equal width

# Canvas remains centered at the top
admit_canvas.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="n")  # Spans both columns

# Column 0 entries
admit_kit_no_label = ctk.CTkLabel(admit_frame, text="Enter Kit No:", font=("Arial", 14))
admit_kit_no_label.grid(row=2, column=0, pady=6, padx=10, sticky="w")
admit_kit_no_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="Kit Number", width=200)  # Fixed width
admit_kit_no_entry.grid(row=3, column=0, pady=6, padx=10, sticky="ew")

admit_name_label = ctk.CTkLabel(admit_frame, text="Enter Patient's Name:", font=("Arial", 14))
admit_name_label.grid(row=4, column=0, pady=6, padx=10, sticky="w")
admit_name_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="Patient's Name", width=200)
admit_name_entry.grid(row=5, column=0, pady=6, padx=10, sticky="ew")

admit_grade_label = ctk.CTkLabel(admit_frame, text="Select Grade:", font=("Arial", 14))
admit_grade_label.grid(row=2, column=1, pady=6, padx=10, sticky="w")
# admit_grade_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="Grade (e.g 9)", width=200)
# admit_grade_entry.grid(row=7, column=0, pady=6, padx=10, sticky="ew")
admit_grade_dropdown = ctk.CTkComboBox(
    master=admit_frame,
    values=["8", "9", "10", "11", "12"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
admit_grade_dropdown.grid(row=3, column=1, pady=6, padx=10, sticky="ew")

# Column 1 entries
admit_house_label = ctk.CTkLabel(admit_frame, text="Select House:", font=("Arial", 14))
admit_house_label.grid(row=4, column=1, pady=6, padx=10, sticky="w")
admit_house_dropdown = ctk.CTkComboBox(
    master=admit_frame,
    values=["Iqbal House", "Ayub House", "Khushal House", "Jinnah House", "Munawar House", "Rustam House", "Junior House"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
admit_house_dropdown.grid(row=5, column=1, pady=6, padx=10, sticky="ew")

# Second group on the right side (column 1)
admit_reason_label = ctk.CTkLabel(admit_frame, text="Enter Reason for admit:", font=("Arial", 14))
admit_reason_label.grid(row=6, column=0, sticky="w", pady=6, padx=10)
admit_reason_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="Reason (e.g Foot Injury)")
admit_reason_entry.grid(row=7, column=0, pady=6, padx=10, sticky="ew")

# admit_admit_label = ctk.CTkLabel(admit_frame, text="Enter admit(s):", font=("Arial", 14))
# admit_admit_label.grid(row=4, column=1, sticky="w", pady=6, padx=10)
# admit_admit_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="admit (e.g Shoes)")
# admit_admit_entry.grid(row=5, column=1, pady=6, padx=10, sticky="ew")

admit_discharge_date_label = ctk.CTkLabel(admit_frame, text="Enter Discharge Date (YYYY-MM-DD):", font=("Arial", 14))
admit_discharge_date_label.grid(row=8, column=0, sticky="w", pady=6, padx=10)
admit_discharge_date_entry = ctk.CTkEntry(master=admit_frame, placeholder_text="YYYY-MM-DD")
admit_discharge_date_entry.grid(row=9, column=0, pady=6, padx=10, sticky="ew")

admit_addrecord_button = ctk.CTkButton(admit_frame, text="Add Record", command=lambda: inputadmitdata())
admit_addrecord_button.grid(row=8, column=1, pady=10, padx=10, sticky="ew")

admit_go_back_button = ctk.CTkButton(admit_frame, text="Go Back", command=lambda: (show_frame(add_frame), clear_entry(export_frame), app.geometry("500x600")))
admit_go_back_button.grid(row=9, column=1, pady=10, padx=10, sticky="ew")

# Add Excuse Frame
excuse_frame = ctk.CTkFrame(master=app)
img_photo_ref_excuse = None
if current_mode == "Light":
    excuse_canvas = tk.Canvas(excuse_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img5 = Image.open(f"{exe_path}\\assets\\excuse.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_excuse = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    excuse_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_excuse)
elif current_mode == "Dark":
    excuse_canvas = tk.Canvas(excuse_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img5 = Image.open(f"{exe_path}\\assets\\excuse.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_excuse = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    excuse_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_excuse)
# Configure columns to have equal weight for uniform widths
excuse_frame.columnconfigure((0, 1), weight=1, uniform="col")  # Columns 0 and 1 are of equal width

# Canvas remains centered at the top
excuse_canvas.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="n")  # Spans both columns

# Column 0 entries
excuse_kit_no_label = ctk.CTkLabel(excuse_frame, text="Enter Kit No:", font=("Arial", 14))
excuse_kit_no_label.grid(row=2, column=0, pady=6, padx=10, sticky="w")
excuse_kit_no_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Kit Number", width=200)  # Fixed width
excuse_kit_no_entry.grid(row=3, column=0, pady=6, padx=10, sticky="ew")

excuse_name_label = ctk.CTkLabel(excuse_frame, text="Enter Patient's Name:", font=("Arial", 14))
excuse_name_label.grid(row=4, column=0, pady=6, padx=10, sticky="w")
excuse_name_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Patient's Name", width=200)
excuse_name_entry.grid(row=5, column=0, pady=6, padx=10, sticky="ew")

excuse_grade_label = ctk.CTkLabel(excuse_frame, text="Select Grade:", font=("Arial", 14))
excuse_grade_label.grid(row=4, column=1, pady=6, padx=10, sticky="w")
# excuse_grade_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Grade (e.g 9)", width=200)
# excuse_grade_entry.grid(row=7, column=0, pady=6, padx=10, sticky="ew")
excuse_grade_dropdown = ctk.CTkComboBox(
    master=excuse_frame,
    values=["8", "9", "10", "11", "12"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
excuse_grade_dropdown.grid(row=5, column=1, pady=6, padx=10, sticky="ew")

# Column 1 entries
excuse_house_label = ctk.CTkLabel(excuse_frame, text="Select House:", font=("Arial", 14))
excuse_house_label.grid(row=6, column=1, pady=6, padx=10, sticky="w")
excuse_house_dropdown = ctk.CTkComboBox(
    master=excuse_frame,
    values=["Iqbal House", "Ayub House", "Khushal House", "Jinnah House", "Munawar House", "Rustam House", "Junior House"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
excuse_house_dropdown.grid(row=7, column=1, pady=6, padx=10, sticky="ew")



# Second group on the right side (column 1)
excuse_reason_label = ctk.CTkLabel(excuse_frame, text="Enter Reason for Excuse:", font=("Arial", 14))
excuse_reason_label.grid(row=6, column=0, sticky="w", pady=6, padx=10)
excuse_reason_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Reason (e.g Foot Injury)")
excuse_reason_entry.grid(row=7, column=0, pady=6, padx=10, sticky="ew")

excuse_excuse_label = ctk.CTkLabel(excuse_frame, text="Enter Excuse(s):", font=("Arial", 14))
excuse_excuse_label.grid(row=8, column=0, sticky="w", pady=6, padx=10)
excuse_excuse_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Excuse (e.g Shoes)")
excuse_excuse_entry.grid(row=9, column=0, pady=6, padx=10, sticky="ew")

excuse_duration_days_label = ctk.CTkLabel(excuse_frame, text="Enter Duration (in days):", font=("Arial", 14))
excuse_duration_days_label.grid(row=2, column=1, sticky="w", pady=6, padx=10)
excuse_duration_days_entry = ctk.CTkEntry(master=excuse_frame, placeholder_text="Duration (in days)")
excuse_duration_days_entry.grid(row=3, column=1, pady=6, padx=10, sticky="ew")

excuse_addrecord_button = ctk.CTkButton(excuse_frame, text="Add Record", command=lambda: inputexcusedata())
excuse_addrecord_button.grid(row=8, column=1, pady=10, padx=10, sticky="ew")

excuse_go_back_button = ctk.CTkButton(excuse_frame, text="Go Back", command=lambda: (show_frame(add_frame), clear_entry(export_frame), app.geometry("500x600")))
excuse_go_back_button.grid(row=9, column=1, pady=10, padx=10, sticky="ew")



# Add Medicine Frame
medicine_frame = ctk.CTkFrame(master=app)
img_photo_ref_medicine = None
if current_mode == "Light":
    medicine_canvas = tk.Canvas(medicine_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#cfcfcf")
    img5 = Image.open(f"{exe_path}\\assets\\medicine.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_medicine = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    medicine_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_medicine)
elif current_mode == "Dark":
    medicine_canvas = tk.Canvas(medicine_frame, width=400, height=100, bd=0, highlightthickness=0, bg="#333333")
    img5 = Image.open(f"{exe_path}\\assets\\medicine.png").resize((400, 100))  # Resize to fit canvas
    img_photo_ref_medicine = ImageTk.PhotoImage(img5)  # Keep a reference to prevent garbage collection
    medicine_canvas.create_image(0, 0, anchor="nw", image=img_photo_ref_medicine)
medicine_canvas.pack(side="top", padx=10, pady=5)

medicine_name_label = ctk.CTkLabel(medicine_frame, text="Enter Medicine Name(s):", font=("Arial", 14))
medicine_name_label.pack(pady=6)
medicine_name_entry = ctk.CTkEntry(master=medicine_frame, placeholder_text="Medicine Name(s)")
medicine_name_entry.pack(pady=6, padx=10)

medicine_kitno_label = ctk.CTkLabel(medicine_frame, text="Enter Kit No:", font=("Arial", 14))
medicine_kitno_label.pack(pady=6)
medicine_kitno_entry = ctk.CTkEntry(master=medicine_frame, placeholder_text="Patient Name")
medicine_kitno_entry.pack(pady=6, padx=10)

medicine_patient_name_label = ctk.CTkLabel(medicine_frame, text="Enter Patient Name:", font=("Arial", 14))
medicine_patient_name_label.pack(pady=6)
medicine_patient_name_entry = ctk.CTkEntry(master=medicine_frame, placeholder_text="Patient Name")
medicine_patient_name_entry.pack(pady=6, padx=10)

medicine_house_label = ctk.CTkLabel(medicine_frame, text="Enter House:", font=("Arial", 14))
medicine_house_label.pack(pady=6)
medicine_house_dropdown = ctk.CTkComboBox(
    master=medicine_frame,
    values=["Iqbal House", "Ayub House", "Khushal House", "Jinnah House", "Munawar House", "Rustam House", "Junior House"],
    width=200,
    corner_radius=10,
    font=("Arial", 12),
    fg_color="gray",
    button_color="black",
    button_hover_color="#007BFF",
    dropdown_text_color="white",
    dropdown_fg_color="#333333",
    dropdown_hover_color="#555555"
)
medicine_house_dropdown.pack(pady=10, padx=10)

medicine_addrecord_button = ctk.CTkButton(medicine_frame, text="Add Record", command=lambda: inputmeddata())
medicine_addrecord_button.pack(pady=10, padx=10)

medicine_go_back_button = ctk.CTkButton(medicine_frame, text="Go Back", command=lambda: (show_frame(add_frame), clear_entry(export_frame)))
medicine_go_back_button.pack(pady=10, padx=10)

# Show login frame by default
show_frame(login_frame)

app.mainloop()

