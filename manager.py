import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import csv
from datetime import datetime, date
from tkcalendar import DateEntry
from database import get_all_items, add_item, update_item, delete_item, get_sales, get_all_managers, add_manager, update_manager, delete_manager
from config import CAFE_THEME

#Display the manager menu with tabs for item management and sales
def show_manager_menu():
    root = tk.Tk()
    root.title("Smart Cafe 360 - Manager Menu")
    root.geometry("1000x600")
    root.resizable(False, False)

    # Ensure images folder exists
    project_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(project_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # Load background image if available
    try:
        bg_image = Image.open(os.path.join(images_dir, "cafe_background.jpg")).resize((1000, 600))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo
    except FileNotFoundError:
        pass

    # Tabbed interface
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    style = ttk.Style()
    style.configure("TNotebook", background="#F0EDE4")
    style.configure("TFrame", background="#F0EDE4")
    style.configure("TButton", background=CAFE_THEME['primary_button_bg'], foreground=CAFE_THEME['primary_button_fg'])

    # Add Item Tab
    add_frame = ttk.Frame(notebook)
    notebook.add(add_frame, text="Add Item")

    tk.Label(add_frame, text="Add New Item", font=("Arial", 16, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    name_var = tk.StringVar()
    price_var = tk.StringVar()
    image_path_var = tk.StringVar()

    tk.Label(add_frame, text="Name:", font=("Arial", 12), bg="#F0EDE4").pack()
    tk.Entry(add_frame, font=("Arial", 12), width=30, textvariable=name_var).pack(pady=5)

    tk.Label(add_frame, text="Price (₹):", font=("Arial", 12), bg="#F0EDE4").pack()
    tk.Entry(add_frame, font=("Arial", 12), width=30, textvariable=price_var).pack(pady=5)

    tk.Label(add_frame, text="Image:", font=("Arial", 12), bg="#F0EDE4").pack()
    image_entry = tk.Entry(add_frame, textvariable=image_path_var, state="readonly", font=("Arial", 12), width=30)
    image_entry.pack(pady=5)

    preview_label = tk.Label(add_frame, text="No image selected", font=("Arial", 10), bg="#F0EDE4")
    preview_label.pack(pady=5)

    #Update the image preview when a new image is selected
    def update_image_preview():
        image_path = image_path_var.get()
        full_image_path = os.path.join(project_dir, image_path) if image_path else ""
        if image_path and os.path.exists(full_image_path):
            try:
                img = Image.open(full_image_path).resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                preview_label.config(image=photo, text="")
                preview_label.image = photo
            except Exception:
                preview_label.config(image="", text="Invalid image")
        else:
            preview_label.config(image="", text="No image selected")

    #Select and copy an image to the images folder
    def choose_image():
        file_path = filedialog.askopenfilename(
            initialdir=images_dir,
            filetypes=[("Images", "*.jpg *.png *.jpeg *.webp")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, filename)
            try:
                shutil.copy(file_path, dest_path)
                relative_path = os.path.join("images", filename).replace("\\", "/")
                image_path_var.set(relative_path)
                update_image_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy image: {str(e)}")

    tk.Button(add_frame, text="Choose Image", bg=CAFE_THEME['secondary_button_bg'], fg=CAFE_THEME['secondary_button_fg'], font=("Arial", 12, "bold"), command=choose_image).pack(pady=5)

    #Add a new item to the database
    def add_new_item():
        try:
            name = name_var.get().strip()
            price_input = price_var.get().strip()
            image_path = image_path_var.get().strip()
            missing_fields = []
            if not name:
                missing_fields.append("Name")
            if not price_input:
                missing_fields.append("Price")
            if not image_path:
                missing_fields.append("Image")
            if missing_fields:
                messagebox.showerror("Error", f"Missing required fields: {', '.join(missing_fields)}")
                return
            price = float(price_input)
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                return
            full_image_path = os.path.join(project_dir, image_path)
            if not os.path.exists(full_image_path):
                messagebox.showerror("Error", f"Image file does not exist: {image_path}")
                return
            add_item(name, price, image_path)
            messagebox.showinfo("Success", f"Item '{name}' added successfully!")
            name_var.set("")
            price_var.set("")
            image_path_var.set("")
            preview_label.config(image="", text="No image selected")
        except ValueError:
            messagebox.showerror("Error", "Invalid price")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add item: {str(e)}")

    tk.Button(add_frame, text="Add Item", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), command=add_new_item).pack(pady=10)

    # Edit/Delete Item Tab
    edit_frame = ttk.Frame(notebook)
    notebook.add(edit_frame, text="Edit/Delete Item")

    tk.Label(edit_frame, text="Manage Items", font=("Arial", 16, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    main_frame = tk.Frame(edit_frame, bg="#F0EDE4")
    main_frame.pack(fill="both", expand=True, padx=10)

    tree_frame = tk.Frame(main_frame, bg="#F0EDE4")
    tree_frame.pack(side="left", fill="both", expand=True, padx=5)
    item_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Price"), show="headings")
    item_tree.heading("ID", text="ID")
    item_tree.heading("Name", text="Name")
    item_tree.heading("Price", text="Price (₹)")
    item_tree.column("ID", width=50, anchor="center")
    item_tree.column("Name", width=200, anchor="w")
    item_tree.column("Price", width=100, anchor="center")
    item_tree.pack(fill="both", expand=True)

    edit_area = tk.Frame(main_frame, bg="#F0EDE4", relief="groove", borderwidth=2)
    edit_area.pack(side="right", fill="y", padx=5, pady=5, ipadx=10, ipady=10)

    tk.Label(edit_area, text="Edit Item", font=("Arial", 14, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=5)
    tk.Label(edit_area, text="Select an item from the table", font=("Arial", 10, "italic"), bg="#F0EDE4").pack()

    name_entry = tk.Entry(edit_area, font=("Arial", 12), width=30, state="disabled")
    tk.Label(edit_area, text="Name:", font=("Arial", 12), bg="#F0EDE4").pack()
    name_entry.pack(pady=5)

    price_entry = tk.Entry(edit_area, font=("Arial", 12), width=30, state="disabled")
    tk.Label(edit_area, text="Price (₹):", font=("Arial", 12), bg="#F0EDE4").pack()
    price_entry.pack(pady=5)

    image_path_var = tk.StringVar()
    tk.Label(edit_area, text="Image:", font=("Arial", 12), bg="#F0EDE4").pack()
    image_entry = tk.Entry(edit_area, textvariable=image_path_var, state="disabled", font=("Arial", 12), width=30)
    image_entry.pack(pady=5)

    #Select a new image for editing an item
    def choose_edit_image():
        file_path = filedialog.askopenfilename(
            initialdir=images_dir,
            filetypes=[("Images", "*.jpg *.png *.jpeg")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, filename)
            try:
                shutil.copy(file_path, dest_path)
                relative_path = os.path.join("images", filename).replace("\\", "/")
                image_path_var.set(relative_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy image: {str(e)}")

    tk.Button(edit_area, text="Choose Image", bg=CAFE_THEME['secondary_button_bg'], fg=CAFE_THEME['secondary_button_fg'], font=("Arial", 12, "bold"), state="disabled",
              command=choose_edit_image).pack(pady=5)

    selected_item_id = None

    #Populate the edit area with selected item details
    def populate_edit_area(event):
        nonlocal selected_item_id
        selected = item_tree.selection()
        if not selected:
            return
        item_id = item_tree.item(selected[0])["values"][0]
        item = next((i for i in get_all_items() if i[0] == item_id), None)
        if item:
            selected_item_id = item_id
            name_entry.config(state="normal")
            name_entry.delete(0, tk.END)
            name_entry.insert(0, item[1])
            price_entry.config(state="normal")
            price_entry.delete(0, tk.END)
            price_entry.insert(0, str(item[2]))
            image_path_var.set(item[4])
            image_entry.config(state="readonly")
            edit_area.winfo_children()[-1].config(state="normal")

    #Refresh the item list in the table
    def refresh_items():
        for item in item_tree.get_children():
            item_tree.delete(item)
        items = get_all_items()
        for item in items:
            item_id, name, price, _, image_path = item
            item_tree.insert("", "end", values=(item_id, name, f"₹{price:.2f}"))
        name_entry.config(state="disabled")
        price_entry.config(state="disabled")
        image_entry.config(state="disabled")
        image_path_var.set("")
        edit_area.winfo_children()[-1].config(state="disabled")

    item_tree.bind("<<TreeviewSelect>>", populate_edit_area)
    refresh_items()

    #Save changes to the selected item
    def save_changes():
        nonlocal selected_item_id
        if not selected_item_id:
            messagebox.showerror("Error", "No item selected")
            return
        try:
            name = name_entry.get().strip()
            price = float(price_entry.get())
            image_path = image_path_var.get()
            if not all([name, price, image_path]):
                messagebox.showerror("Error", "All fields are required")
                return
            full_image_path = os.path.join(project_dir, image_path)
            if not os.path.exists(full_image_path):
                messagebox.showerror("Error", f"Image file does not exist: {image_path}")
                return
            update_item(selected_item_id, name, price, image_path)
            messagebox.showinfo("Success", f"Item '{name}' updated successfully!")
            refresh_items()
        except ValueError:
            messagebox.showerror("Error", "Invalid price")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update item: {str(e)}")

    tk.Button(edit_area, text="Save Changes", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), command=save_changes).pack(pady=5)

    #Delete the selected item after confirmation
    def delete_item_action():
        nonlocal selected_item_id
        if not selected_item_id:
            messagebox.showerror("Error", "No item selected")
            return
        item_name = name_entry.get().strip()
        if messagebox.askyesno("Confirm Delete", f"Delete item '{item_name}'?"):
            delete_item(selected_item_id)
            messagebox.showinfo("Success", f"Item '{item_name}' deleted!")
            refresh_items()

    tk.Button(edit_area, text="Delete Item", bg=CAFE_THEME['accent_button_bg'], fg=CAFE_THEME['accent_button_fg'], font=("Arial", 12, "bold"), command=delete_item_action).pack(pady=5)

    # View Sales Tab
    sales_frame = ttk.Frame(notebook)
    notebook.add(sales_frame, text="View Sales")

    tk.Label(sales_frame, text="Sales Report", font=("Arial", 16, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    date_frame = tk.Frame(sales_frame, bg="#F0EDE4")
    date_frame.pack(pady=5)
    tk.Label(date_frame, text="Select Date:", font=("Arial", 12), bg="#F0EDE4").pack(side="left")
    date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    date_entry.pack(side="left", padx=5)
    date_entry.set_date(date.today())

    tree_frame = tk.Frame(sales_frame, bg="#F0EDE4")
    tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
    sales_tree = ttk.Treeview(tree_frame, columns=("ID", "Item", "Qty", "Total", "Date"), show="headings")
    sales_tree.heading("ID", text="Sale ID")
    sales_tree.heading("Item", text="Item")
    sales_tree.heading("Qty", text="Qty Sold")
    sales_tree.heading("Total", text="Total (₹)")
    sales_tree.heading("Date", text="Date")
    sales_tree.column("ID", width=80, anchor="center")
    sales_tree.column("Item", width=200, anchor="w")
    sales_tree.column("Qty", width=80, anchor="center")
    sales_tree.column("Total", width=100, anchor="center")
    sales_tree.column("Date", width=150, anchor="center")
    sales_tree.pack(fill="both", expand=True)

    selected_revenue_var = tk.StringVar()
    tk.Label(sales_frame, textvariable=selected_revenue_var, font=("Arial", 14, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    #Update the sales table and revenue for the selected date
    def update_sales_display():
        selected_date = date_entry.get_date().strftime('%Y-%m-%d')
        sales = get_sales()
        selected_sales = [sale for sale in sales if str(sale[4]).startswith(selected_date)]
        selected_revenue = sum(sale[3] for sale in selected_sales)
        selected_revenue_var.set(f"Revenue for {selected_date}: ₹{selected_revenue:.2f}")

        for item in sales_tree.get_children():
            sales_tree.delete(item)
        for sale in selected_sales:
            sale_id, item_id, qty_sold, total_price, sale_date = sale
            item = next((i for i in get_all_items() if i[0] == item_id), None)
            item_name = item[1] if item else "Unknown Item"
            sales_tree.insert("", "end", values=(sale_id, item_name, qty_sold, f"₹{total_price:.2f}", sale_date))

    #Save the selected date's revenue to daily_revenue.csv
    def update_daily_revenue_csv():
        selected_date = date_entry.get_date()
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        csv_filename = os.path.join(project_dir, "daily_revenue.csv")
        sales = get_sales()
        
        selected_sales = [sale for sale in sales if str(sale[4]).startswith(selected_date_str)]
        selected_revenue = sum(sale[3] for sale in selected_sales)

        csv_data = []
        write_header = not os.path.exists(csv_filename)
        try:
            if not write_header:
                with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    csv_data = list(reader)
                    if csv_data and csv_data[0] != ["Date", "Total Revenue"]:
                        csv_data.insert(0, ["Date", "Total Revenue"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
            return

        updated = False
        if not write_header:
            for i in range(1, len(csv_data)):
                if csv_data[i] and csv_data[i][0] == selected_date_str:
                    csv_data[i] = [selected_date_str, f"{selected_revenue:.2f}"]
                    updated = True
                    break

        if not updated:
            csv_data.append([selected_date_str, f"{selected_revenue:.2f}"])

        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)
            messagebox.showinfo("Success", f"Saved revenue for {selected_date_str} to daily_revenue.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")

        update_sales_display()

    date_entry.bind("<<DateEntrySelected>>", lambda event: update_sales_display())
    update_sales_display()

    tk.Button(sales_frame, text="Save Today's Revenue", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"),
              command=update_daily_revenue_csv).pack(pady=10)

    # Manage Credentials Tab
    cred_frame = ttk.Frame(notebook)
    notebook.add(cred_frame, text="Manage Credentials")

    tk.Label(cred_frame, text="Manage Manager Credentials", font=("Arial", 16, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    cred_main_frame = tk.Frame(cred_frame, bg="#F0EDE4")
    cred_main_frame.pack(fill="both", expand=True, padx=10)

    cred_tree_frame = tk.Frame(cred_main_frame, bg="#F0EDE4")
    cred_tree_frame.pack(side="left", fill="both", expand=True, padx=5)
    cred_tree = ttk.Treeview(cred_tree_frame, columns=("Username",), show="headings")
    cred_tree.heading("Username", text="Username")
    cred_tree.column("Username", width=200, anchor="w")
    cred_tree.pack(fill="both", expand=True)

    cred_edit_area = tk.Frame(cred_main_frame, bg="#F0EDE4", relief="groove", borderwidth=2)
    cred_edit_area.pack(side="right", fill="y", padx=5, pady=5, ipadx=10, ipady=10)

    tk.Label(cred_edit_area, text="Edit Credentials", font=("Arial", 14, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=5)
    tk.Label(cred_edit_area, text="Select a manager from the table", font=("Arial", 10, "italic"), bg="#F0EDE4").pack()

    cred_username_entry = tk.Entry(cred_edit_area, font=("Arial", 12), width=30, state="disabled")
    tk.Label(cred_edit_area, text="Username:", font=("Arial", 12), bg="#F0EDE4").pack()
    cred_username_entry.pack(pady=5)

    cred_password_entry = tk.Entry(cred_edit_area, font=("Arial", 12), width=30, state="disabled", show="*")
    tk.Label(cred_edit_area, text="Password:", font=("Arial", 12), bg="#F0EDE4").pack()
    cred_password_entry.pack(pady=5)

    selected_username = None

    #Populate the edit area with selected manager credentials
    def populate_cred_edit_area(event):
        nonlocal selected_username
        selected = cred_tree.selection()
        if not selected:
            return
        username = cred_tree.item(selected[0])["values"][0]
        managers = get_all_managers()
        manager = next((m for m in managers if m[0] == username), None)
        if manager:
            selected_username = username
            cred_username_entry.config(state="normal")
            cred_username_entry.delete(0, tk.END)
            cred_username_entry.insert(0, manager[0])
            cred_password_entry.config(state="normal")
            cred_password_entry.delete(0, tk.END)
            cred_password_entry.insert(0, manager[1])

    #Refresh the manager list in the table
    def refresh_managers():
        for item in cred_tree.get_children():
            cred_tree.delete(item)
        managers = get_all_managers()
        for manager in managers:
            cred_tree.insert("", "end", values=(manager[0],))
        cred_username_entry.config(state="disabled")
        cred_password_entry.config(state="disabled")
        cred_username_entry.delete(0, tk.END)
        cred_password_entry.delete(0, tk.END)

    cred_tree.bind("<<TreeviewSelect>>", populate_cred_edit_area)
    refresh_managers()

    #Open a window to add a new manager
    def add_new_manager():
        add_window = tk.Toplevel(root)
        add_window.title("Add New Manager")
        add_window.geometry("400x300")
        add_window.configure(bg="#F0EDE4")

        tk.Label(add_window, text="Add New Manager", font=("Arial", 16, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

        tk.Label(add_window, text="Username:", font=("Arial", 12), bg="#F0EDE4").pack()
        new_username_entry = tk.Entry(add_window, font=("Arial", 12), width=30)
        new_username_entry.pack(pady=5)

        tk.Label(add_window, text="Password:", font=("Arial", 12), bg="#F0EDE4").pack()
        new_password_entry = tk.Entry(add_window, font=("Arial", 12), width=30, show="*")
        new_password_entry.pack(pady=5)

        def save_new_manager():
            username = new_username_entry.get().strip()
            password = new_password_entry.get().strip()
            if not all([username, password]):
                messagebox.showerror("Error", "All fields are required")
                return
            try:
                add_manager(username, password)
                messagebox.showinfo("Success", f"Manager '{username}' added successfully!")
                add_window.destroy()
                refresh_managers()
            except Exception as e:
                if "Duplicate entry" in str(e) or "UNIQUE constraint" in str(e):
                    messagebox.showerror("Error", "Username already exists")
                else:
                    messagebox.showerror("Error", f"Failed to add manager: {str(e)}")

        tk.Button(add_window, text="Add Manager", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), command=save_new_manager).pack(pady=10)

    tk.Button(cred_edit_area, text="Add New Manager", bg=CAFE_THEME['secondary_button_bg'], fg=CAFE_THEME['secondary_button_fg'], font=("Arial", 12, "bold"), command=add_new_manager).pack(pady=5)

    #Save changes to the selected manager's credentials
    def save_manager_changes():
        nonlocal selected_username
        if not selected_username:
            messagebox.showerror("Error", "No manager selected")
            return
        username = cred_username_entry.get().strip()
        password = cred_password_entry.get().strip()
        if not all([username, password]):
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            update_manager(selected_username, username, password)
            messagebox.showinfo("Success", f"Manager '{username}' updated successfully!")
            refresh_managers()
        except Exception as e:
            if "Duplicate entry" in str(e) or "UNIQUE constraint" in str(e):
                messagebox.showerror("Error", "Username already exists")
            else:
                messagebox.showerror("Error", f"Failed to update manager: {str(e)}")

    tk.Button(cred_edit_area, text="Save Changes", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), command=save_manager_changes).pack(pady=5)

    #Delete the selected manager after confirmation
    def delete_manager_action():                 
        nonlocal selected_username
        if not selected_username:
            messagebox.showerror("Error", "No manager selected")
            return
        if selected_username == "admin":
            messagebox.showerror("Error", "Cannot delete the default admin account")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete manager '{selected_username}'?"):
            delete_manager(selected_username)
            messagebox.showinfo("Success", f"Manager '{selected_username}' deleted!")
            refresh_managers()

    tk.Button(cred_edit_area, text="Delete Manager", bg=CAFE_THEME['accent_button_bg'], fg=CAFE_THEME['accent_button_fg'], font=("Arial", 12, "bold"), command=delete_manager_action).pack(pady=5)
 
    #Clear edit area when switching to Edit/Delete tab
    def on_tab_change(event):                          
        selected_tab = notebook.index(notebook.select())
        if selected_tab == notebook.index(edit_frame):
            refresh_items()
            name_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            image_path_var.set("")
            name_entry.config(state="disabled")
            price_entry.config(state="disabled")
            image_entry.config(state="disabled")
            edit_area.winfo_children()[-1].config(state="disabled")
            nonlocal selected_item_id
            selected_item_id = None

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    #Return to the login screen  
    def exit_to_login():                      
        from main import login_screen
        root.destroy()
        login_screen()

    tk.Button(root, text="Exit", bg=CAFE_THEME['accent_button_bg'], fg=CAFE_THEME['accent_button_fg'], font=("Arial", 14, "bold"), command=exit_to_login).place(relx=0.75, rely=0.9, anchor="sw", width=150, height=40)

    root.mainloop()

if __name__ == "__main__":
    show_manager_menu()