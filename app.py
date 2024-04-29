import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import mysql.connector
current_balance = 0
def connect_to_mysql():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="c2c"
    )
    return connection

#Function for the text entries (Stores info for the mysql insert)

def create_account(): #Holds all the text entry boxes
    window = tk.Toplevel(root)
    window.title("Create Account")

    tk.Label(window, text="First Name:").grid(row=0, column=0)
    entry_first_name = tk.Entry(window)
    entry_first_name.grid(row=0, column=1)

    tk.Label(window, text="Last Name:").grid(row=1, column=0)
    entry_last_name = tk.Entry(window)
    entry_last_name.grid(row=1, column=1)

    tk.Label(window, text="Email:").grid(row=2, column=0)
    entry_email = tk.Entry(window)
    entry_email.grid(row=2, column=1)

    tk.Label(window, text="Birthday (YYYY-MM-DD):").grid(row=3, column=0)
    entry_birthday = tk.Entry(window)
    entry_birthday.grid(row=3, column=1)

    tk.Label(window, text="PIN:").grid(row=4, column=0)
    entry_pin = tk.Entry(window, show="*")
    entry_pin.grid(row=4, column=1)

    tk.Label(window, text="Starting Balance:").grid(row=5, column=0)
    entry_starting_balance = tk.Entry(window)
    entry_starting_balance.grid(row=5, column=1)

    #Submit button, (uses the text entry values)
    #Lambda allows us to send multiple data through the callback function
    submit_button = tk.Button(window, text="Submit", command=lambda: submit_account(entry_first_name, entry_last_name, entry_email, entry_birthday, entry_pin, entry_starting_balance))
    submit_button.grid(row=6, columnspan=2, pady=10)

def submit_account(entry_first_name, entry_last_name, entry_email, entry_birthday, entry_pin, entry_starting_balance):
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    email = entry_email.get()
    birthday = entry_birthday.get()
    pin = entry_pin.get()
    starting_balance = entry_starting_balance.get()

#Error message if a box is empty
    if not all([first_name, last_name, email, birthday, pin, starting_balance]):
        messagebox.showerror("Error", "All fields are required!")
        return

    connection = connect_to_mysql() #Inserts values into server
    if connection:
        try:
            cursor = connection.cursor()
            sql_query = "INSERT INTO accounts (first_name, last_name, email, birthday, pin, balance) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_query, (first_name, last_name, email, birthday, pin, starting_balance))
            connection.commit()
            messagebox.showinfo("Account created successfully!")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("Email:", email)
        print("Birthday:", birthday)
        print("PIN:", pin)
        print("Starting balance:", starting_balance)


def open_account():
    def account_login():  # Screen for the login
        email = entry_email.get()
        pin = entry_pin.get()

        connection = connect_to_mysql()
        if connection:
            try:
                cursor = connection.cursor()
                #Checks if there is an account that matches what user inputs
                sql_query = "SELECT * FROM accounts WHERE email = %s AND pin = %s"
                cursor.execute(sql_query, (email, pin))
                account = cursor.fetchone()

                if account:
                    display_account(account)
                    return email
                else: #if there isn't or if email invalid, error box shows up
                    messagebox.showerror("Invalid email or PIN!")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return email

    def display_account(account):  #All account details
        window = tk.Toplevel(root)
        window.title("Account Details")
        window.geometry("400x200")

        tk.Label(window, text="First Name:").grid(row=0, column=0)
        tk.Label(window, text=account[0]).grid(row=0, column=1)  
        tk.Label(window, text="Last Name:").grid(row=1, column=0)
        tk.Label(window, text=account[1]).grid(row=1, column=1)
        tk.Label(window, text="Email:").grid(row=2, column=0)
        tk.Label(window, text=account[2]).grid(row=2, column=1)
        tk.Label(window, text="Balance:").grid(row=3, column=0)
        tk.Label(window, text=account[5]).grid(row=3, column=1)

        withdraw_button = tk.Button(window, text="Withdraw", command=withdraw)  
        withdraw_button.grid(row=4, column=0)

        deposit_button = tk.Button(window, text="Deposit", command=deposit) 
        deposit_button.grid(row=4, column=1)

        delete_button = tk.Button(window, text="Delete", command=delete_account) #button for delete
        delete_button.grid(row=4, column=2) 

        return account 

    def withdraw():
        email = entry_email.get()
        connection = connect_to_mysql()

        withdraw_amount = simpledialog.askfloat("Withdraw", "Enter the amount to withdraw:")

        if connection:
            try:
                cursor = connection.cursor()
                
                # Retrieve the current balance of the user's account
                cursor.execute("SELECT balance FROM accounts WHERE email = %s", (email,))
                current_balance = cursor.fetchone()[0]
                
                # Check if the withdrawal amount is less than or equal to the current balance
                if int(withdraw_amount) <= int(current_balance):
                    # Update the balance by subtracting the withdrawal amount
                    new_balance = int(current_balance) - int(withdraw_amount)
                    
                    # Update the balance in the database
                    cursor.execute("UPDATE accounts SET balance = %s WHERE email = %s", (new_balance, email))
                    connection.commit()
                    
                    # Show a success message
                    messagebox.showinfo("Success", f"Withdrawal of ${withdraw_amount} successful!\nNew balance: ${new_balance}")
                else:
                    messagebox.showerror("Error", "Insufficient balance for withdrawal!")
                
            except mysql.connector.Error as err:
                print("Error:", err)
                messagebox.showerror("Failed to withdraw money!")
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return email



    def deposit():
        email = entry_email.get()
        connection = connect_to_mysql()

        deposit_amount = simpledialog.askfloat("Deposit", "Enter the amount to deposit:")

        if connection:
            try:
                cursor = connection.cursor()
            
            # Retrieve the current balance of the user's account
                cursor.execute("SELECT balance FROM accounts WHERE email = %s", (email,))
                current_balance = cursor.fetchone()[0]
            
            # Update the balance by adding the deposit amount
                new_balance = int(current_balance) + int(deposit_amount)
            
            # Update the balance in the database
                cursor.execute("UPDATE accounts SET balance = %s WHERE email = %s", (new_balance, email))
                connection.commit()
            
            # Show a success message
                messagebox.showinfo("Success", f"Deposit of ${deposit_amount} successful!\nNew balance: ${new_balance}")
            
            except mysql.connector.Error as err:
                print("Error:", err)
                messagebox.showerror("Failed to deposit money!")
        
            finally:
               if connection.is_connected():
                    cursor.close()
                    connection.close()
        return email

    def delete_account():
        email = entry_email.get()
        connection = connect_to_mysql()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM accounts WHERE email = %s ", (email,))
                connection.commit()
                messagebox.showinfo("Success", "Account deleted successfully!")
            finally:
                if connection.is_connected():
                 cursor.close()
                 connection.close()

    window = tk.Toplevel(root)
    window.title("Open Account")
    window.geometry("400x200")

    tk.Label(window, text="Email:").grid(row=0, column=0)
    entry_email = tk.Entry(window)
    entry_email.grid(row=0, column=1)

    tk.Label(window, text="PIN:").grid(row=1, column=0)
    entry_pin = tk.Entry(window, show="*")
    entry_pin.grid(row=1, column=1)

    login_button = tk.Button(window, text="Login", command=account_login)
    login_button.grid(row=2, columnspan=2, pady=10)

root = tk.Tk()  # First window
root.title("My Bank")
root.geometry("200x200")

#Initial Create account button
create_account_button = tk.Button(root, text="Create Account", command=create_account)
create_account_button.pack()

#Initial open account button
open_account_button = tk.Button(root, text="Open Account", command=open_account)
open_account_button.pack()

root.mainloop() #Main loop of the tkinter
