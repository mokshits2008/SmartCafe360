import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import get_all_items, add_sale
from datetime import datetime
from config import CAFE_THEME

# Global cart to store selected items
cart = []  # Format: [{'id': 1, 'name': 'Coffee', 'price': 50, 'quantity': 2}, ...]

#Display the customer menu with items from the database
def show_customer_menu():
    root = tk.Tk()
    root.title("Smart Cafe 360 - Customer Menu")
    root.geometry("1000x600")
    root.resizable(False, False)

    # Load background image if available
    try:
        bg_image = Image.open("images/cafe_background.jpg").resize((800, 600))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo  
    except FileNotFoundError:
        pass  

    # Main frame for the menu
    main_frame = tk.Frame(root, bg="#F0EDE4")
    main_frame.pack(fill="both", expand=True)
    
    # Scrollable canvas for item grid
    canvas = tk.Canvas(main_frame, bg="#F0EDE4", height=500)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Enable mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux scroll down
    
    canvas.pack(side="top", fill="x", padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    # Fetch and display items from database
    items = get_all_items()
    for index, item in enumerate(items):
        item_id, name, price, _, image_path = item
        item_frame = tk.Frame(scrollable_frame, bg="#F0EDE4", relief="raised", borderwidth=0.5)
        item_frame.grid(row=index // 4, column=index % 4, padx=15, pady=15, sticky="nsew")

        # Load item image
        try:
            img = Image.open(image_path).resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(item_frame, image=photo, bg="#F0EDE4")
            img_label.image = photo  
            img_label.pack(pady=5)
        except FileNotFoundError:
            tk.Label(item_frame, text="No Image", bg="#F0EDE4", font=("Arial", 10)).pack(pady=5)

        # Display item name and price
        tk.Label(item_frame, text=name, font=("Arial", 12, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack()
        tk.Label(item_frame, text=f"₹{price}", font=("Arial", 10), bg="#F0EDE4").pack()

        # Quantity selector
        qty_var = tk.IntVar(value=1)
        qty_spin = ttk.Spinbox(item_frame, from_=1, to=999, width=5, textvariable=qty_var, font=("Arial", 10))
        qty_spin.pack(pady=5)

        # Add to cart button with duplicate fix
        def add_to_cart(i_id=item_id, i_name=name, i_price=price, spin=qty_var):
            qty = int(spin.get())
            # Check if item already exists in cart
            existing_item = next((item for item in cart if item['id'] == i_id), None)
            if existing_item:
                # Update quantity instead of adding duplicate
                existing_item['quantity'] += qty
                messagebox.showinfo("Success", f"Updated {i_name} quantity to {existing_item['quantity']}")
            else:
                # Add new item to cart
                cart.append({"id": i_id, "name": i_name, "price": i_price, "quantity": qty})
                messagebox.showinfo("Success", f"Added {qty} {i_name} to cart")

        tk.Button(item_frame, text="Add to Cart", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 10, "bold"), command=add_to_cart).pack(pady=5)

    # View cart button
    tk.Button(root, text="View Cart", bg=CAFE_THEME['secondary_button_bg'], fg=CAFE_THEME['secondary_button_fg'], font=("Arial", 14, "bold"), command=lambda: show_cart(root)).place(relx=0.9, rely=0.95, anchor="se", width=150, height=40)

    # Exit button to return to login
    def exit_to_login():
        from main import login_screen
        root.destroy()
        login_screen()

    tk.Button(root, text="Exit", bg=CAFE_THEME['accent_button_bg'], fg=CAFE_THEME['accent_button_fg'], font=("Arial", 14, "bold"), command=exit_to_login).place(relx=0.1, rely=0.95, anchor="sw", width=150, height=40)

    root.mainloop()

#Display the cart with selected items and checkout option
def show_cart(parent_root):
    if not cart:
        messagebox.showinfo("Cart", "Cart is empty!")
        return
    cart_window = tk.Toplevel(parent_root)
    cart_window.title("Your Cart - Smart Cafe 360")
    cart_window.geometry("700x500")
    cart_window.configure(bg="#F0EDE4")

    tk.Label(cart_window, text="Your Cart", font=("Arial", 18, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    # Scrollable frame for cart items
    canvas = tk.Canvas(cart_window, bg="#F0EDE4")
    scrollbar = ttk.Scrollbar(cart_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Calculate and update total
    total_var = tk.StringVar()
    def update_total():
        total = sum(int(item['quantity']) * item['price'] for item in cart)
        total_var.set(f"Total: ₹{total:.2f}")

    update_total()

    # Display cart items
    for index, item in enumerate(cart):
        frame = tk.Frame(scrollable_frame, bg="#F0EDE4", relief="groove", borderwidth=2)
        frame.pack(fill="x", pady=5, padx=10)

        tk.Label(frame, text=item['name'], font=("Arial", 12, "bold"), bg="#F0EDE4").pack(side="left", padx=5)

        qty_var = tk.IntVar(value=int(item['quantity']))
        qty_spin = ttk.Spinbox(frame, from_=1, to=999, width=5, textvariable=qty_var, font=("Arial", 10),
                              command=lambda i=index, v=qty_var: (cart[i].update({'quantity': v.get()}), update_total()))
        qty_spin.pack(side="left", padx=5)

        tk.Label(frame, text=f"₹{item['price']}", font=("Arial", 10), bg="#F0EDE4").pack(side="left", padx=5)

        def remove_item(i=index):
            del cart[i]
            cart_window.destroy()
            show_cart(parent_root)

        tk.Button(frame, text="Remove", bg=CAFE_THEME['accent_button_bg'], fg=CAFE_THEME['accent_button_fg'], font=("Arial", 10, "bold"), command=remove_item).pack(side="right", padx=5)

    tk.Label(cart_window, textvariable=total_var, font=("Arial", 14, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    # Buttons for adding more items or checking out
    button_frame = tk.Frame(cart_window, bg="#F0EDE4")
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Add More Items", bg=CAFE_THEME['secondary_button_bg'], fg=CAFE_THEME['secondary_button_fg'], font=("Arial", 12, "bold"), command=cart_window.destroy).pack(side="left", padx=10)
    tk.Button(button_frame, text="Checkout", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), 
              command=lambda: checkout(cart_window, total_var)).pack(side="left", padx=10)

#Process the checkout and generate a bill
def checkout(cart_window, total_var):
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return
    try:
        total = float(total_var.get().split('₹')[1])
        for item in cart:
            item_id = item["id"]
            quantity = int(item["quantity"])
            add_sale(item_id, quantity, item["price"] * quantity)
        show_bill(total)
        cart.clear()
        cart_window.destroy()
    except ValueError:
        messagebox.showerror("Error", "Checkout failed: Invalid total")
    except Exception as e:
        messagebox.showerror("Error", f"Checkout failed: {str(e)}")

#Display the final bill with purchased items
def show_bill(total):
    bill_window = tk.Toplevel()
    bill_window.title("Smart Cafe 360 - Bill")
    bill_window.geometry("500x600")
    bill_window.configure(bg="#F0EDE4")

    tk.Label(bill_window, text="Smart Cafe 360", font=("Arial", 20, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)
    tk.Label(bill_window, text="123 Brew Street, Coffee City", font=("Arial", 10, "italic"), bg="#F0EDE4").pack()
    tk.Label(bill_window, text=f"Date: {datetime.now().strftime('%Y-%m-%d')}", font=("Arial", 12), bg="#F0EDE4").pack()
    tk.Label(bill_window, text=f"Time: {datetime.now().strftime('%H:%M:%S')}", font=("Arial", 12), bg="#F0EDE4").pack()
    invoice_num = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tk.Label(bill_window, text=f"Invoice Number: {invoice_num}", font=("Arial", 12), bg="#F0EDE4").pack(pady=5)

    tk.Label(bill_window, text="─" * 60, font=("Arial", 12), bg="#F0EDE4", fg="#4A4A4A").pack()

    # Table for bill items
    tree_frame = tk.Frame(bill_window, bg="#F0EDE4")
    tree_frame.pack(pady=10, padx=20, fill="x")
    tree = ttk.Treeview(tree_frame, columns=("Item", "Qty", "Price", "Total"), show="headings", height=len(cart))
    tree.heading("Item", text="Item")
    tree.heading("Qty", text="Qty")
    tree.heading("Price", text="Price")
    tree.heading("Total", text="Total")
    tree.column("Item", width=200, anchor="w")
    tree.column("Qty", width=50, anchor="center")
    tree.column("Price", width=80, anchor="center")
    tree.column("Total", width=80, anchor="center")
    tree.pack()

    for item in cart:
        tree.insert("", "end", values=(item['name'], item['quantity'], f"₹{item['price']:.2f}", f"₹{item['price'] * int(item['quantity']):.2f}"))

    tk.Label(bill_window, text="─" * 60, font=("Arial", 12), bg="#F0EDE4", fg="#4A4A4A").pack()

    tk.Label(bill_window, text=f"Grand Total: ₹{total:.2f}", font=("Arial", 14, "bold"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    tk.Label(bill_window, text="Thank you for your purchase!", font=("Arial", 12, "italic"), bg="#F0EDE4", fg="#4A4A4A").pack(pady=10)

    tk.Button(bill_window, text="Close", bg=CAFE_THEME['primary_button_bg'], fg=CAFE_THEME['primary_button_fg'], font=("Arial", 12, "bold"), command=bill_window.destroy).pack(pady=10)

if __name__ == "__main__":
    show_customer_menu()