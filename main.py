import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from database import init_db, check_manager_login
from customer import show_customer_menu
from manager import show_manager_menu

# Initialize the database
init_db()

#Clear placeholder text when the entry is focused
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="black")

#Restore placeholder text if the entry is empty
def restore_placeholder(event, entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="grey")

#Display the login screen for managers and customers
def login_screen():
    root = tk.Tk()
    root.title("Smart Cafe 360 - Login")
    root.geometry("400x500")
    root.resizable(False, False)

    try:
        bg_image = Image.open("images/cafe_background.jpg").resize((400, 500))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    except FileNotFoundError:
        pass

    username_entry = tk.Entry(root, width=30, bg="#D3C9B6", font=("Arial", 14))
    username_entry.place(relx=0.5, rely=0.4, anchor="center", width=300, height=40)
    username_entry.insert(0, "Enter Username")
    username_entry.config(fg="grey")
    username_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, username_entry, "Enter Username"))
    username_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, username_entry, "Enter Username"))

    password_entry = tk.Entry(root, width=30, show="*", bg="#D3C9B6", font=("Arial", 14))
    password_entry.place(relx=0.5, rely=0.5, anchor="center", width=300, height=40)
    password_entry.insert(0, "Enter Password")
    password_entry.config(fg="grey")
    password_entry.bind("<FocusIn>", lambda e: clear_placeholder(e, password_entry, "Enter Password"))
    password_entry.bind("<FocusOut>", lambda e: restore_placeholder(e, password_entry, "Enter Password"))

    #Handle manager login attempt
    def manager_login():
        username = username_entry.get()
        password = password_entry.get()
        if username in ["Enter Username", "Enter Password"] or password in ["Enter Username", "Enter Password"]:
            messagebox.showerror("Error", "Please enter valid credentials")
        elif check_manager_login(username, password):
            root.destroy()
            show_manager_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    login_btn = tk.Button(root, text="Login", width=20, bg="#D3C9B6", font=("Arial", 14), command=manager_login)
    login_btn.place(relx=0.5, rely=0.65, anchor="center", width=200, height=40)

    #Redirect to customer menu
    def customer_continue():
        root.destroy()
        show_customer_menu()

    customer_btn = tk.Button(root, text="Continue as Customer", width=25, bg="#F0EDE4", font=("Arial", 14), command=customer_continue)
    customer_btn.place(relx=0.5, rely=0.75, anchor="center", width=250, height=40)

    root.mainloop()

if __name__ == "__main__":
    login_screen()