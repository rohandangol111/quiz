
import tkinter as tk
from tkinter import *
import sqlite3
import time
# Connect an SQLite database and tables for questions
conn = sqlite3.connect('QUIZ.db')
cursor = conn.cursor()

# Create User table for user accounts
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()

# Initialize variables
question_number = 0
score = 0
exam_start_time = None
exam_duration = 300  # Set the exam duration in seconds (5 minutes)
timer_label = None
timer_id = None
current_user = None

# Function to load a question from the database
def load_question():
    global question_number, score
    if question_number >= len(questions):
        show_final_score()
        return

    question_data = questions[question_number]
    question_label.config(text=question_data[1])
    option1.config(text=question_data[2])
    option2.config(text=question_data[3])
    option3.config(text=question_data[4])
    option4.config(text=question_data[5])
    correct_option = question_data[6]
    question_number += 1

    def check_answer(selected_option):
        global score
        if selected_option == correct_option:
            score += 1
        load_question()

    option1.config(command=lambda: check_answer(1))
    option2.config(command=lambda: check_answer(2))
    option3.config(command=lambda: check_answer(3))
    option4.config(command=lambda: check_answer(4))

# Function to show the final score
def show_final_score():
    elapsed_time = time.time() - exam_start_time
    question_label.config(text="Quiz Completed! Your Score: {}/{}".format(score, question_number))
#to disable the options and buttons after completing
    option1.config(state=tk.DISABLED)
    option2.config(state=tk.DISABLED)
    option3.config(state=tk.DISABLED)
    option4.config(state=tk.DISABLED)
    next_button.config(state=tk.DISABLED)
    previous_button.config(state=tk.DISABLED)
    time_label.config(text="Time Elapsed: {:.0f} minute(s) {:.0f} seconds(s)".format(elapsed_time // 60, elapsed_time % 60))
    stop_timer()

# Function to handle user sign-in
def sign_in():
    global current_user, exam_start_time
    username = username_entry.get()
    password = password_entry.get()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user_data = cursor.fetchone()
    if user_data:
        current_user = username
        sign_in_frame.pack_forget()
        load_question_frame.pack()
        exam_start_time = time.time()
        load_question()
        start_timer(exam_duration)
    else:
        sign_in_error_label.config(text="Invalid username or password")

# Function to create a new account
def create_account():
    username = new_username_entry.get()
    password = new_password_entry.get()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        create_account_frame.pack_forget()
        sign_in_frame.pack()
        sign_in_error_label.config(text="Account created successfully. Please sign in.")
    except sqlite3.IntegrityError:
        create_account_error_label.config(text="Username already exists. Please choose another.")

# Function to start the timer
def start_timer(duration):
    global timer_label, timer_id
    if timer_label:
        timer_label.pack_forget()
    timer_label = tk.Label(load_question_frame, text=f"Time Left: {duration // 60} minute(s) {duration % 60} second(s)", font=("Arial", 12))
    timer_label.pack()
    timer_id = load_question_frame.after(1000, lambda: update_timer(duration))

# Function to update the timer
def update_timer(duration):
    global timer_id
    duration -= 1
    if duration < 0:
        show_final_score()
    else:
        timer_label.config(text=f"Time Left: {duration // 60} minute(s) {duration % 60} second(s)")
        timer_id = load_question_frame.after(1000, lambda: update_timer(duration))

# Function to stop the timer
def stop_timer():
    global timer_id
    if timer_id:
        load_question_frame.after_cancel(timer_id)

# Function to navigate to the previous question
def previous_question():
    global question_number, score
    if question_number > 1:
        question_number -= 2  # Go back two steps (to account for the current question and the next question)
        load_question()
    elif question_number == 1:
        question_number -= 1
        load_question()

# Create the main window
root = tk.Tk()
root.title("Multiple Choice Quiz")
root.geometry("1280x720")

# Create widgets for sign-in page
sign_in_frame = tk.Frame(root)
sign_in_label = tk.Label(sign_in_frame, text="Sign In", font=("Arial bold", 23),fg="#28a745")
username_label = tk.Label(sign_in_frame, text="Username:",font =('arial',14))
password_label = tk.Label(sign_in_frame, text="Password:",font =('arial',14))
username_entry = tk.Entry(sign_in_frame,fg="black", bg="white",font =('arial',11))
password_entry = tk.Entry(sign_in_frame, show="*",font =('arial',11))
sign_in_button = tk.Button(sign_in_frame, text="Sign In", command=sign_in,font =('arial',14),fg="#28a745")
create_account_button = tk.Button(sign_in_frame, text="Create Account",fg="white",bg="#28a745",font =('arial',13), command=lambda: create_account_frame.pack())
sign_in_error_label = tk.Label(sign_in_frame, text="", fg="red")

# Create widgets for create account page
create_account_frame = tk.Frame(root)

create_account_label = tk.Label(create_account_frame, text="Create Account",fg="#28a745", font=("Arial bold", 23))
new_username_label = tk.Label(create_account_frame, text="New Username:",font =('arial',14))
new_password_label = tk.Label(create_account_frame, text="New Password:",font =('arial',14))
new_username_entry = tk.Entry(create_account_frame,font =('arial',11))
new_password_entry = tk.Entry(create_account_frame, show="*",font =('arial',11))
create_button = tk.Button(create_account_frame, text="Create",bg="#28a745",fg="white",font =('arial',11), command=create_account)
create_account_error_label = tk.Label(create_account_frame, text="", fg="red")

# Create widgets for the quiz page
load_question_frame = tk.Frame(root)
question_label = tk.Label(load_question_frame, text="", font=("Arial bold", 14))
option1 = tk.Button(load_question_frame, text="", font=("Arial"))
option2 = tk.Button(load_question_frame, text="", font=("Arial"))
option3 = tk.Button(load_question_frame, text="", font=("Arial"))
option4 = tk.Button(load_question_frame, text="", font =('arial'))
next_button = tk.Button(load_question_frame, text="Next", font=("Arial"), command=load_question)
previous_button = tk.Button(load_question_frame, text="Previous", font=("Arial"), command=previous_question)
exit_button = tk.Button(load_question_frame, text="Exit", font=("Arial"),bg="Red", command=root.quit)
time_label = tk.Label(load_question_frame, text="", font=("Arial"))

questions = []
cursor.execute('SELECT * FROM questions')
for row in cursor.fetchall():
    questions.append(row)

# Place widgets on the sign-in page
sign_in_frame.pack(pady=50)
sign_in_label.pack(pady=10)
username_label.pack()
username_entry.pack()
password_label.pack()
password_entry.pack()
sign_in_button.pack(pady=10)
create_account_button.pack(pady=5)
sign_in_error_label.pack(pady=5)


# Place widgets on the create account page (initially hidden)
create_account_frame.pack()
create_account_label.pack(pady=10)
new_username_label.pack()
new_username_entry.pack()
new_password_label.pack()
new_password_entry.pack()
create_button.pack(pady=10)
create_account_error_label.pack(pady=5)
create_account_frame.pack_forget()

# Place widgets on the quiz page (initially hidden)
load_question_frame.pack()
question_label.pack(padx=30, pady=10)
option1.pack(padx=30, pady=10)

option2.pack(padx=30, pady=10)
option3.pack(padx=30, pady=10)
option4.pack(padx=30, pady=10)
previous_button.pack(side=tk.LEFT, padx=30, pady=10)
next_button.pack(side=tk.LEFT, padx=30, pady=10)
exit_button.pack(side=tk.LEFT, padx=30, pady=10)
time_label.pack()
load_question_frame.pack_forget()
#Start the application
root.mainloop()

# Close the database connection when the program exits
conn.close()
