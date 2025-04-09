import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from tkinter import simpledialog, messagebox
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
import cv2
from PIL import Image, ImageTk
import numpy as np
import sys
import sqlite3
from tkinter import ttk



# Import necessary modules from your project
from face_detection import detect_faces
from embeddings import extract_embedding
from vector_store import add_embedding_to_faiss, search_faiss
from database import (
    insert_child_metadata,
    get_child_by_embedding_id,
    update_case_status,
    initialize_database
)
from storage import store_encrypted_image, retrieve_encrypted_image
from config import IMAGE_STORAGE_PATH
from notification import notify_guardian_async

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

import tkinter as tk
from tkinter import messagebox
import sqlite3

import tkinter as tk
from tkinter import messagebox
import sqlite3

class SignupFrame(tk.Frame):
    def __init__(self, master, switch_to_login):
        super().__init__(master, bg="#2c3e50")
        self.master = master
        self.switch_to_login = switch_to_login

        # Set master window background to dark
        self.master.configure(bg="#2c3e50")

        # Fill the entire window
        self.pack(fill="both", expand=True)

        # Wrapper for centering content
        content = tk.Frame(self, bg="#2c3e50")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(content,
                 text="Create New Account",
                 font=("Helvetica", 18, "bold"),
                 bg="#2c3e50",
                 fg="white").grid(row=0, column=0, columnspan=2, pady=(10, 30))

        # Username
        tk.Label(content, text="Username:", font=("Helvetica", 12), bg="#2c3e50", fg="white")\
            .grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(content, font=("Helvetica", 12), width=25, bg="white", fg="black")
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password
        tk.Label(content, text="Password:", font=("Helvetica", 12), bg="#2c3e50", fg="white")\
            .grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(content, font=("Helvetica", 12), show="*", width=25, bg="white", fg="black")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Role
        tk.Label(content, text="Role (Developer / Authority):", font=("Helvetica", 12), bg="#2c3e50", fg="white")\
            .grid(row=3, column=0, sticky="e", padx=10, pady=10)
        self.role_entry = tk.Entry(content, font=("Helvetica", 12), width=25, bg="white", fg="black")
        self.role_entry.grid(row=3, column=1, padx=10, pady=10)

        # Style for buttons
        style = ttk.Style()
        style.configure("Signup.TButton",
                        font=("Arial", 12, "bold"),
                        foreground="white",
                        background="#007BFF",
                        padding=10)
        style.map("Signup.TButton",
                  background=[("active", "#0056b3")],
                  foreground=[("active", "white")])

        # Sign Up button
        self.signup_button = ttk.Button(content, text="Sign Up", style="Signup.TButton", command=self.create_account)
        self.signup_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Back to login button
        self.back_button = ttk.Button(content, text="Back to Login", style="Signup.TButton", command=self.switch_to_login)
        self.back_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Message label
        self.message_label = tk.Label(content, text="", font=("Helvetica", 10), fg="red", bg="#2c3e50")
        self.message_label.grid(row=6, column=0, columnspan=2, pady=5)


    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_entry.get().strip().capitalize()

        if not username or not password or role not in ["Developer", "Authority"]:
            self.message_label.config(text="Please fill all fields correctly.", fg="red")
            return

        conn = sqlite3.connect("child_safety.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, password, role))
            conn.commit()
            self.message_label.config(text="Account created successfully!", fg="green")
        except sqlite3.IntegrityError:
            self.message_label.config(text="Username already exists.", fg="red")
        finally:
            conn.close()


class LoginFrame(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master, bg="#2c3e50")  # Dark background
        self.master = master
        self.on_login_success = on_login_success

        self.configure(width=900, height=700)
        self.place(relx=0.5, rely=0.5, anchor="center")

        # Center wrapper
        content = tk.Frame(self, bg="#2c3e50")
        content.pack(expand=True)

        # Title
        tk.Label(content,
                 text="Child Safety Recognition System Login",
                 font=("Helvetica", 18, "bold"),
                 bg="#2c3e50",
                 fg="white").grid(row=0, column=0, columnspan=2, pady=(10, 30))

        # Username Label
        tk.Label(content, text="Username:", font=("Helvetica", 12), bg="#2c3e50", fg="white")\
            .grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(content, font=("Helvetica", 12), width=25, bg="white", fg="black")
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password Label
        tk.Label(content, text="Password:", font=("Helvetica", 12), bg="#2c3e50", fg="white")\
            .grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(content, font=("Helvetica", 12), show="*", width=25, bg="white", fg="black")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        style = ttk.Style()
        style.configure("Login.TButton",
                        font=("Arial", 12, "bold"),
                        foreground="white",
                        background="#007BFF",
                        padding=10)
        style.map("Login.TButton",
                  background=[("active", "#0056b3")],
                  foreground=[("active", "white")])

        self.login_button = ttk.Button(
            content,
            text="Login",
            style="Login.TButton",
            command=self.check_credentials
        )

        self.login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Sign Up button (same size, same style)
        self.signup_button = ttk.Button(
            content,
            text="Sign Up",
            style="Login.TButton",
            command=self.switch_to_signup
        )
        self.signup_button.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        # Message Label
        self.message_label = tk.Label(content, text="", font=("Helvetica", 10), fg="red", bg="#2c3e50")
        self.message_label.grid(row=5, column=0, columnspan=2)

    def check_credentials(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        conn = sqlite3.connect("child_safety.db")
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
        conn.close()

        if result:
            role = result[0]
            self.on_login_success(role=role)
        else:
            self.message_label.config(text="Invalid credentials!")

    def switch_to_signup(self):
        self.pack_forget()
        self.master.signup_frame = SignupFrame(self.master, switch_to_login=self.switch_to_login_from_signup)
        self.master.signup_frame.pack(fill="both", expand=True)

    def switch_to_login_from_signup(self):
        self.master.signup_frame.destroy()
        self.master.login_frame = LoginFrame(self.master, self.on_login_success)





class ChildSafetyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x700")
        self.title("Child Safety Recognition System")
        # self.configure(bg="#f0f0f0")
        self.resizable(False, False)  # Optional: Fix window size

        self.initialize_user_db()

        self.role = None  # Will be set after login

        # Set up basic window (can be hidden until login)
        # self.withdraw()  # Hide main window until login succeeds

        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.pack(expand=True, fill="both")      


    def initialize_user_db(self):
        conn = sqlite3.connect("child_safety.db")
        c = conn.cursor()

        # Create users table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Developer', 'Authority'))
            )
        ''')

        # Add default users only if table is empty
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Developer"))
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("authority", "auth123", "Authority"))

        conn.commit()
        conn.close()

    def on_login_success(self, role):
        self.login_frame.destroy()
        self.deiconify()
        self.role = role
        self.initialize_app_ui()

    def initialize_app_ui(self):
        # Initialize database
        initialize_database()

        # Check for scheduled cleanup
        self.check_for_scheduled_cleanup()
        
        # Configure main window
        self.title("Child Safety Recognition System")
        self.geometry("900x700")
        self.configure(bg="#f0f0f0")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.register_tab = ttk.Frame(self.notebook)
        self.identify_tab = ttk.Frame(self.notebook)
        self.case_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.register_tab, text="Register Lost Child")
        self.notebook.add(self.identify_tab, text="Identify Found Child")
        self.notebook.add(self.case_tab, text="Manage Cases")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))
        
        # Setup tabs
        self.setup_register_tab()
        self.setup_identify_tab()
        self.setup_case_tab()
        
        # Video capture variables
        self.cap = None
        self.is_webcam_running = False
        self.webcam_thread = None
        self.current_frame = None
    
        # # Initialize database
        # initialize_database()

        # # Check for scheduled cleanup
        # self.check_for_scheduled_cleanup()
        
        # # Configure main window
        # self.title("Child Safety Recognition System")
        # self.geometry("900x700")
        # # self.configure(bg="#2c3e50") 

        # self.configure(bg="#f0f0f0")
        # # self.resizable(False, False)
        

        # # # Use modern theme
        # # self.style = ttk.Style()
        # # self.style.theme_use("clam")
        # # self.style.configure("TButton", font=("Segoe UI", 12), padding=6)
        # # self.style.configure("TLabel", font=("Segoe UI", 12))
        # # self.style.configure("TEntry", font=("Segoe UI", 12))

        # # # Optionally customize button colors
        # # self.style.configure("TButton",
        # #                     background="#007acc",
        # #                     foreground="white")
        # # self.style.map("TButton",
        # #             background=[("active", "#005f99")],
        # #             foreground=[("active", "white")])

        # # # Create notebook for tabs
        # # self.notebook = ttk.Notebook(self)
        # # self.notebook.pack(expand=True, fill="both", padx=20, pady=20)
        # # # self.notebook.pack(expand=True, fill="both")  


        # # # Create tabs with consistent background

        # # # self.style.configure('TNotebook', background='#2c3e50', borderwidth=0)
        # # # self.style.configure('TNotebook.Tab', background='#34495e', foreground='white', padding=10)
        # # # self.style.map("TNotebook.Tab",
        # # #             background=[("selected", "#1abc9c")],
        # # #             foreground=[("selected", "white")])

        
        # # self.register_tab = ttk.Frame(self.notebook, padding=20)
        # # self.identify_tab = ttk.Frame(self.notebook, padding=20)
        # # self.case_tab = ttk.Frame(self.notebook, padding=20)
        
        # # # for tab in (self.register_tab, self.identify_tab, self.case_tab):
        # # #     tab.configure(style="TFrame")  # Apply uniform styling

        # # self.notebook.add(self.register_tab, text="📝 Register Lost Child")
        # # self.notebook.add(self.identify_tab, text="🔍 Identify Found Child")
        # # self.notebook.add(self.case_tab, text="📁 Manage Cases")

        # # # Setup each tab
        # # self.setup_register_tab()
        # # self.setup_identify_tab()
        # # self.setup_case_tab()

        # # self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        # # self.style.configure("TLabel", font=("Segoe UI", 11))
        # # self.style.configure("TEntry", font=("Segoe UI", 11))

        # # # Video capture variables
        # # self.cap = None
        # # self.is_webcam_running = False
        # # self.webcam_thread = None
        # # self.current_frame = None

        # # Create notebook for tabs
        # self.notebook = ttk.Notebook(self)
        # self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # # Create tabs
        # self.register_tab = ttk.Frame(self.notebook)
        # self.identify_tab = ttk.Frame(self.notebook)
        # self.case_tab = ttk.Frame(self.notebook)
        
        # self.notebook.add(self.register_tab, text="Register Lost Child")
        # self.notebook.add(self.identify_tab, text="Identify Found Child")
        # self.notebook.add(self.case_tab, text="Manage Cases")
        
        # # Configure style
        # self.style = ttk.Style()
        # self.style.configure("TButton", font=("Arial", 12))
        # self.style.configure("TLabel", font=("Arial", 12))
        # self.style.configure("TEntry", font=("Arial", 12))
        
        # # Setup tabs
        # self.setup_register_tab()
        # self.setup_identify_tab()
        # self.setup_case_tab()
        
        # # Video capture variables
        # self.cap = None
        # self.is_webcam_running = False
        # self.webcam_thread = None
        # self.current_frame = None


    def check_for_scheduled_cleanup(self):  
        """Check if monthly cleanup should run"""
        from database import schedule_monthly_cleanup
        
        # Run in a thread to avoid blocking the UI
        threading.Thread(target=schedule_monthly_cleanup).start()
        
    def get_all_guardian_contacts(self, child_name):
        """Get all guardian contacts registered for a child with the same name"""
        try:
            # Create a database connection
            from database import create_connection
            conn = create_connection()
            if not conn:
                return []
                
            cursor = conn.cursor(dictionary=True)
            
            # Query to find all guardian contacts for a child with the same name
            query = "SELECT guardian_contact FROM Children_Metadata WHERE name = %s AND case_status = 'Open'"
            cursor.execute(query, (child_name,))
            
            # Get all results
            results = cursor.fetchall()
            
            # Extract guardian contacts
            guardian_contacts = [result['guardian_contact'] for result in results]
            
            # Remove duplicates while preserving order
            unique_contacts = []
            for contact in guardian_contacts:
                if contact not in unique_contacts:
                    unique_contacts.append(contact)
            
            conn.close()
            return unique_contacts
            
        except Exception as e:
            print(f"Error getting guardian contacts: {e}")
            return []

    def cleanup_temp_files(self):
        """Remove all temporary files when closing the application"""
        temp_dirs = ["temp_captures", "temp_decrypts"]
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
    
    def manual_cleanup(self):
        """Run manual cleanup of old closed cases"""
        from database import cleanup_closed_cases

        if self.role != "Developer":
            messagebox.showwarning("Access Denied", "Only developers can perform cleanup.")
            return
        
        # Ask for confirmation with a custom dialog
        confirm_dialog = tk.Toplevel(self)
        confirm_dialog.title("Confirm Cleanup")
        confirm_dialog.geometry("400x200")
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.update_idletasks()
        width = confirm_dialog.winfo_width()
        height = confirm_dialog.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add content to the dialog
        ttk.Label(
            confirm_dialog, 
            text="This will permanently delete all closed cases\nthat are older than 30 days.",
            font=("Arial", 12)
        ).pack(pady=(20, 10))
        
        # Add days input
        days_frame = ttk.Frame(confirm_dialog)
        days_frame.pack(pady=(0, 10))
        
        ttk.Label(days_frame, text="Delete cases older than:").grid(row=0, column=0, padx=5)
        days_var = tk.StringVar(value="30")
        days_entry = ttk.Entry(days_frame, textvariable=days_var, width=5)
        days_entry.grid(row=0, column=1)
        ttk.Label(days_frame, text="days").grid(row=0, column=2, padx=5)
        
        # Add buttons
        button_frame = ttk.Frame(confirm_dialog)
        button_frame.pack(pady=10)
        
        def on_confirm():
            try:
                days = int(days_var.get())
                if days < 1:
                    messagebox.showerror("Error", "Days must be at least 1")
                    return
                    
                confirm_dialog.destroy()
                deleted_count = cleanup_closed_cases(older_than_days=days)
                messagebox.showinfo("Cleanup Complete", f"{deleted_count} old closed cases were permanently deleted")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of days")
        
        ttk.Button(
            button_frame, 
            text="Confirm", 
            command=on_confirm
        ).grid(row=0, column=0, padx=10)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=confirm_dialog.destroy
        ).grid(row=0, column=1, padx=10)

    # Add this function to your gui.py file

    def get_all_guardian_contacts(self, child_name):
        """Get all guardian contacts registered for a child with the same name"""
        try:
            # Create a database connection
            from database import create_connection
            conn = create_connection()
            if not conn:
                return []
                
            cursor = conn.cursor(dictionary=True)
            
            # Query to find all guardian contacts for a child with the same name
            query = "SELECT guardian_contact FROM Children_Metadata WHERE name = %s AND case_status = 'Open'"
            cursor.execute(query, (child_name,))
            
            # Get all results
            results = cursor.fetchall()
            
            # Extract guardian contacts
            guardian_contacts = [result['guardian_contact'] for result in results]
            
            # Remove duplicates while preserving order
            unique_contacts = []
            for contact in guardian_contacts:
                if contact not in unique_contacts:
                    unique_contacts.append(contact)
            
            conn.close()
            return unique_contacts
            
        except Exception as e:
            print(f"Error getting guardian contacts: {e}")
            return []

    def notify_identified_guardian(self):
        """Notify all guardians of the currently identified child"""
        # First check if we have identification results
        self.results_text.config(state="normal")
        results_content = self.results_text.get("1.0", tk.END)
        self.results_text.config(state="disabled")
        
        if "No matches found" in results_content or not results_content.strip():
            messagebox.showinfo("Info", "No cases are currently identified")
            return
        
        # Parse the results to find details we need
        import re
        
        # Extract the first child's details
        name_match = re.search(r"Name: ([^\n]+)", results_content)
        
        if not name_match:
            messagebox.showinfo("Info", "Could not find child details in results")
            return
        
        child_name = name_match.group(1).strip()
        
        # Get all guardian contacts for this child
        guardian_contacts = self.get_all_guardian_contacts(child_name)  # Use self here
        
        if not guardian_contacts:
            messagebox.showinfo("Info", "No guardian contacts found for this child")
            return
        
        # Show confirmation dialog with details of all contacts
        contacts_display = "\n".join(guardian_contacts)
        confirm = messagebox.askyesno(
            "Confirm Multiple Notifications",
            f"Send notification to ALL guardians of {child_name}?\n\nContacts ({len(guardian_contacts)}):\n{contacts_display}"
        )
        
        if confirm:
            # Start a loading indicator
            self.show_loading_notification()
            
            # Define callback for when all notifications complete
            def on_notification_complete(results):
                self.hide_loading_notification()
                
                # Count successes and failures
                successes = sum(1 for result, _ in results.values() if result)
                failures = len(results) - successes
                
                if successes > 0:
                    if failures == 0:
                        messagebox.showinfo(
                            "Success", 
                            f"All {successes} guardian notifications sent successfully.\n\n"
                            f"Child: {child_name}"
                        )
                    else:
                        messagebox.showinfo(
                            "Partial Success", 
                            f"{successes} notifications sent successfully.\n"
                            f"{failures} notifications failed.\n\n"
                            f"Child: {child_name}"
                        )
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to send notifications to any of the {len(guardian_contacts)} guardians.\n"
                        f"Please try calling the guardians directly."
                    )
            
            # Get the location of the authorities (could be made configurable)
            location = "local authorities"
            
            # Send notification to all guardians asynchronously
            from notification import notify_multiple_guardians_async
            notify_multiple_guardians_async(
                guardian_contacts, 
                child_name, 
                location, 
                "The child has been identified by our Child Safety System.", 
                on_notification_complete
            )

    def notify_case_guardian(self):
        """Notify all guardians of the currently displayed case"""
        try:
            # Get details from the case details text widget
            case_details = self.case_details_text.get("1.0", tk.END)
            
            # Parse the details to find what we need
            import re
            
            name_match = re.search(r"Name: ([^\n]+)", case_details)
            
            if not name_match:
                messagebox.showinfo("Info", "Could not find child details")
                return
            
            child_name = name_match.group(1).strip()
            
            # Get all guardian contacts for this child
            guardian_contacts = self.get_all_guardian_contacts(child_name)  # Use self here
            
            if not guardian_contacts:
                messagebox.showinfo("Info", "No guardian contacts found for this child")
                return
            
            # Show confirmation dialog with details of all contacts
            contacts_display = "\n".join(guardian_contacts)
            confirm = messagebox.askyesno(
                "Confirm Multiple Notifications",
                f"Send notification to ALL guardians of {child_name}?\n\nContacts ({len(guardian_contacts)}):\n{contacts_display}"
            )
            
            if not confirm:
                return
            
            # Start a loading indicator
            self.show_loading_notification()
            
            # Define callback for when all notifications complete
            def on_notification_complete(results):
                self.hide_loading_notification()
                
                # Count successes and failures
                successes = sum(1 for result, _ in results.values() if result)
                failures = len(results) - successes
                
                if successes > 0:
                    if failures == 0:
                        messagebox.showinfo(
                            "Success", 
                            f"All {successes} guardian notifications sent successfully.\n\n"
                            f"Child: {child_name}"
                        )
                    else:
                        messagebox.showinfo(
                            "Partial Success", 
                            f"{successes} notifications sent successfully.\n"
                            f"{failures} notifications failed.\n\n"
                            f"Child: {child_name}"
                        )
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to send notifications to any of the {len(guardian_contacts)} guardians.\n"
                        f"Please try calling the guardians directly."
                    )
            
            # Get the location of the authorities (could be made configurable)
            location = "local authorities"
            
            # Send notification to all guardians asynchronously
            from notification import notify_multiple_guardians_async
            notify_multiple_guardians_async(
                guardian_contacts, 
                child_name, 
                location, 
                "The child has been identified by our Child Safety System.", 
                on_notification_complete
            )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error notifying guardians: {e}")

    def show_loading_notification(self):
        """Show a loading window for notification in progress"""
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Sending Notification")
        self.loading_window.geometry("300x100")
        self.loading_window.resizable(False, False)
        self.loading_window.transient(self)
        self.loading_window.grab_set()
        
        # Center the loading window
        self.loading_window.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add loading message and animation
        message_label = ttk.Label(
            self.loading_window, 
            text="Sending notification to guardian...",
            font=("Arial", 12)
        )
        message_label.pack(pady=(20, 10))
        
        progress = ttk.Progressbar(
            self.loading_window,
            mode="indeterminate",
            length=200
        )
        progress.pack(pady=(0, 20))
        progress.start(10)

    def hide_loading_notification(self):
        """Hide the loading window"""
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.destroy()

    def setup_register_tab(self):
        """Setup the registration tab for lost children"""
        # Frame for image preview
        preview_frame = ttk.LabelFrame(self.register_tab, text="Child Image")
        preview_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.register_image_label = ttk.Label(preview_frame, text="No image selected")
        self.register_image_label.pack(padx=10, pady=10, expand=True, fill="both")
        
        # Frame for form fields
        form_frame = ttk.LabelFrame(self.register_tab, text="Child Information")
        form_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.age_entry = ttk.Entry(form_frame, width=30)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(form_frame, textvariable=self.gender_var, width=28, state="readonly")
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Guardian Contact:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.guardian_entry = ttk.Entry(form_frame, width=30)
        self.guardian_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Distinguishing Features:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.features_text = tk.Text(form_frame, width=30, height=4)
        self.features_text.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Last Known Location:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.location_entry = ttk.Entry(form_frame, width=30)
        self.location_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.register_tab)
        buttons_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Buttons
        upload_btn = ttk.Button(buttons_frame, text="Upload Image", command=self.upload_register_image)
        upload_btn.pack(side="left", padx=5, pady=5)
        
        webcam_btn = ttk.Button(buttons_frame, text="Use Webcam", command=lambda: self.toggle_webcam("register"))
        webcam_btn.pack(side="left", padx=5, pady=5)
        
        capture_btn = ttk.Button(buttons_frame, text="Capture", command=lambda: self.capture_image("register"))
        capture_btn.pack(side="left", padx=5, pady=5)
        
        register_btn = ttk.Button(buttons_frame, text="Register Child", command=self.register_child)
        register_btn.pack(side="right", padx=5, pady=5)
        
        # Status label
        self.register_status = ttk.Label(self.register_tab, text="")
        self.register_status.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Configure grid weights
        self.register_tab.grid_columnconfigure(0, weight=1)
        self.register_tab.grid_columnconfigure(1, weight=1)
        
        # Image path variable
        self.register_image_path = None
    
    def get_all_guardian_contacts(self, child_name):
        """Get all guardian contacts registered for a child with the same name"""
        try:
            # Create a database connection
            from database import create_connection
            conn = create_connection()
            if not conn:
                return []
                
            cursor = conn.cursor(dictionary=True)
            
            # Query to find all guardian contacts for a child with the same name
            query = "SELECT guardian_contact FROM Children_Metadata WHERE name = %s AND case_status = 'Open'"
            cursor.execute(query, (child_name,))
            
            # Get all results
            results = cursor.fetchall()
            
            # Extract guardian contacts
            guardian_contacts = [result['guardian_contact'] for result in results]
            
            # Remove duplicates while preserving order
            unique_contacts = []
            for contact in guardian_contacts:
                if contact not in unique_contacts:
                    unique_contacts.append(contact)
            
            conn.close()
            return unique_contacts
            
        except Exception as e:
            print(f"Error getting guardian contacts: {e}")
            return []

    def notify_identified_guardian(self):
        """Notify all guardians of the currently identified child"""
        # First check if we have identification results
        self.results_text.config(state="normal")
        results_content = self.results_text.get("1.0", tk.END)
        self.results_text.config(state="disabled")
        
        if "No matches found" in results_content or not results_content.strip():
            messagebox.showinfo("Info", "No cases are currently identified")
            return
        
        # Parse the results to find details we need
        import re
        
        # Extract the first child's details
        name_match = re.search(r"Name: ([^\n]+)", results_content)
        
        if not name_match:
            messagebox.showinfo("Info", "Could not find child details in results")
            return
        
        child_name = name_match.group(1).strip()
        
        # Get all guardian contacts for this child
        guardian_contacts = self.get_all_guardian_contacts(child_name)
        
        if not guardian_contacts:
            messagebox.showinfo("Info", "No guardian contacts found for this child")
            return
        
        # Show confirmation dialog with details of all contacts
        contacts_display = "\n".join(guardian_contacts)
        confirm = messagebox.askyesno(
            "Confirm Multiple Notifications",
            f"Send notification to ALL guardians of {child_name}?\n\nContacts ({len(guardian_contacts)}):\n{contacts_display}"
        )
        
        if confirm:
            # Start a loading indicator
            self.show_loading_notification()
            
            # Define callback for when all notifications complete
            def on_notification_complete(results):
                self.hide_loading_notification()
                
                # Count successes and failures
                successes = sum(1 for result, _ in results.values() if result)
                failures = len(results) - successes
                
                if successes > 0:
                    if failures == 0:
                        messagebox.showinfo(
                            "Success", 
                            f"All {successes} guardian notifications sent successfully.\n\n"
                            f"Child: {child_name}"
                        )
                    else:
                        messagebox.showinfo(
                            "Partial Success", 
                            f"{successes} notifications sent successfully.\n"
                            f"{failures} notifications failed.\n\n"
                            f"Child: {child_name}"
                        )
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to send notifications to any of the {len(guardian_contacts)} guardians.\n"
                        f"Please try calling the guardians directly."
                    )
            
            # Get the location of the authorities (could be made configurable)
            location = "local authorities"
            
            # Send notification to all guardians asynchronously
            from notification import notify_multiple_guardians_async
            notify_multiple_guardians_async(
                guardian_contacts, 
                child_name, 
                location, 
                "The child has been identified by our Child Safety System.", 
                on_notification_complete
            )

    def notify_case_guardian(self):
        """Notify all guardians of the currently displayed case"""
        try:
            # Get details from the case details text widget
            case_details = self.case_details_text.get("1.0", tk.END)
            
            # Parse the details to find what we need
            import re
            
            name_match = re.search(r"Name: ([^\n]+)", case_details)
            
            if not name_match:
                messagebox.showinfo("Info", "Could not find child details")
                return
            
            child_name = name_match.group(1).strip()
            
            # Get all guardian contacts for this child
            guardian_contacts = self.get_all_guardian_contacts(child_name)
            
            if not guardian_contacts:
                messagebox.showinfo("Info", "No guardian contacts found for this child")
                return
            
            # Show confirmation dialog with details of all contacts
            contacts_display = "\n".join(guardian_contacts)
            confirm = messagebox.askyesno(
                "Confirm Multiple Notifications",
                f"Send notification to ALL guardians of {child_name}?\n\nContacts ({len(guardian_contacts)}):\n{contacts_display}"
            )
            
            if not confirm:
                return
            
            # Start a loading indicator
            self.show_loading_notification()
            
            # Define callback for when all notifications complete
            def on_notification_complete(results):
                self.hide_loading_notification()
                
                # Count successes and failures
                successes = sum(1 for result, _ in results.values() if result)
                failures = len(results) - successes
                
                if successes > 0:
                    if failures == 0:
                        messagebox.showinfo(
                            "Success", 
                            f"All {successes} guardian notifications sent successfully.\n\n"
                            f"Child: {child_name}"
                        )
                    else:
                        messagebox.showinfo(
                            "Partial Success", 
                            f"{successes} notifications sent successfully.\n"
                            f"{failures} notifications failed.\n\n"
                            f"Child: {child_name}"
                        )
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to send notifications to any of the {len(guardian_contacts)} guardians.\n"
                        f"Please try calling the guardians directly."
                    )
            
            # Get the location of the authorities (could be made configurable)
            location = "local authorities"
            
            # Send notification to all guardians asynchronously
            from notification import notify_multiple_guardians_async
            notify_multiple_guardians_async(
                guardian_contacts, 
                child_name, 
                location, 
                "The child has been identified by our Child Safety System.", 
                on_notification_complete
            )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error notifying guardians: {e}")

    def show_loading_notification(self):
        """Show a loading window for notification in progress"""
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Sending Notification")
        self.loading_window.geometry("300x100")
        self.loading_window.resizable(False, False)
        self.loading_window.transient(self)
        self.loading_window.grab_set()
        
        # Center the loading window
        self.loading_window.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add loading message and animation
        message_label = ttk.Label(
            self.loading_window, 
            text="Sending notification to guardian...",
            font=("Arial", 12)
        )
        message_label.pack(pady=(20, 10))
        
        progress = ttk.Progressbar(
            self.loading_window,
            mode="indeterminate",
            length=200
        )
        progress.pack(pady=(0, 20))
        progress.start(10)

    def hide_loading_notification(self):
        """Hide the loading window"""
        if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
            self.loading_window.destroy()

    def setup_identify_tab(self):
        """Setup the identification tab for found children"""
        # Create a canvas with scrollbar for the entire identify tab
        identify_canvas = tk.Canvas(self.identify_tab)
        identify_scrollbar = ttk.Scrollbar(self.identify_tab, orient="vertical", command=identify_canvas.yview)
        
        # Create a frame inside the canvas that will contain all the elements
        scrollable_frame = ttk.Frame(identify_canvas)
        
        # Bind the frame's configure event to update the canvas's scroll region
        scrollable_frame.bind(
            "<Configure>",
            lambda e: identify_canvas.configure(scrollregion=identify_canvas.bbox("all"))
        )
        
        # Create the window in the canvas that contains the scrollable frame
        identify_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        identify_canvas.configure(yscrollcommand=identify_scrollbar.set)
        
        # Pack the canvas and scrollbar
        identify_canvas.pack(side="left", fill="both", expand=True)
        identify_scrollbar.pack(side="right", fill="y")
        
        # Frame for image/video preview
        preview_frame = ttk.LabelFrame(scrollable_frame, text="Image/Video Preview")
        preview_frame.pack(padx=10, pady=10, expand=True, fill="both")
        
        self.identify_image_label = ttk.Label(preview_frame, text="No image/video selected")
        self.identify_image_label.pack(padx=10, pady=10, expand=True, fill="both")
        
        # Input selection frame
        input_frame = ttk.LabelFrame(self.identify_tab, text="Input Selection")
        input_frame.pack(padx=10, pady=10, fill="x")
        
        # Buttons for different input methods
        upload_img_btn = ttk.Button(input_frame, text="Upload Image", command=self.upload_identify_image)
        upload_img_btn.pack(side="left", padx=5, pady=5)
        
        upload_video_btn = ttk.Button(input_frame, text="Upload Video", command=self.upload_identify_video)
        upload_video_btn.pack(side="left", padx=5, pady=5)
        
        webcam_btn = ttk.Button(input_frame, text="Use Webcam", command=lambda: self.toggle_webcam("identify"))
        webcam_btn.pack(side="left", padx=5, pady=5)
        
        # Identify button
        identify_frame = ttk.Frame(self.identify_tab)
        identify_frame.pack(padx=10, pady=10, fill="x")
        
        identify_btn = ttk.Button(identify_frame, text="Identify Child", command=self.identify_child)
        identify_btn.pack(side="right", padx=5, pady=5)
        
        capture_btn = ttk.Button(identify_frame, text="Capture", command=lambda: self.capture_image("identify"))
        capture_btn.pack(side="right", padx=5, pady=5)

        notify_guardian_btn = ttk.Button(identify_frame, text="Notify Guardian", command=self.notify_identified_guardian)
        notify_guardian_btn.pack(side="right", padx=5, pady=5)

        close_case_btn = ttk.Button(identify_frame, text="Close Case", command=self.close_identified_case)
        close_case_btn.pack(side="right", padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.identify_tab, text="Identification Results")
        results_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.results_text = tk.Text(results_frame, height=10, width=80, state="disabled")
        self.results_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Create a new frame with a labeled border for displaying matched images
        self.match_preview_frame = ttk.LabelFrame(self.identify_tab, text="Match Preview")
        # Position it below the results text area
        self.match_preview_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a canvas with scrollbar for the match images
        match_canvas = tk.Canvas(self.match_preview_frame)
        match_scrollbar_h = ttk.Scrollbar(self.match_preview_frame, orient="horizontal", command=match_canvas.xview)
        match_scrollbar_v = ttk.Scrollbar(self.match_preview_frame, orient="vertical", command=match_canvas.yview)

        # Create a frame inside the canvas that will contain all the match images
        self.match_images_container = ttk.Frame(match_canvas)

        # Bind the frame's configure event to update the canvas's scroll region
        self.match_images_container.bind(
            "<Configure>",
            lambda e: match_canvas.configure(scrollregion=match_canvas.bbox("all"))
        )

        # Create the window in the canvas that contains the match images container
        match_canvas.create_window((0, 0), window=self.match_images_container, anchor="nw")
        match_canvas.configure(
            xscrollcommand=match_scrollbar_h.set,
            yscrollcommand=match_scrollbar_v.set
        )

        # Pack the canvas and scrollbars
        match_canvas.pack(side="top", fill="both", expand=True)
        match_scrollbar_h.pack(side="bottom", fill="x")
        match_scrollbar_v.pack(side="right", fill="y")        

        # Variables
        self.identify_input_path = None
        self.is_video = False
    
    def setup_case_tab(self):
        """Setup the case management tab"""
        # Search frame
        search_frame = ttk.Frame(self.case_tab)
        search_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(search_frame, text="Embedding ID:").pack(side="left", padx=5, pady=5)
        self.embedding_id_entry = ttk.Entry(search_frame, width=20)
        self.embedding_id_entry.pack(side="left", padx=5, pady=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_case)
        search_btn.pack(side="left", padx=5, pady=5)
        
        refresh_btn = ttk.Button(search_frame, text="Refresh Open Cases", command=self.refresh_cases)
        refresh_btn.pack(side="right", padx=5, pady=5)
        
        # Case details frame
        details_frame = ttk.LabelFrame(self.case_tab, text="Case Details")
        details_frame.pack(padx=10, pady=10, fill="both", expand=True)

        details_columns_frame = ttk.Frame(details_frame)
        details_columns_frame.pack(padx=5, pady=5, fill="both", expand=True)

        details_text_frame = ttk.Frame(details_columns_frame)
        details_text_frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)

        self.case_details_text = tk.Text(details_text_frame, height=5, width=50)
        self.case_details_text.pack(padx=5, pady=5, fill="both", expand=True)

        details_image_frame = ttk.Frame(details_columns_frame)
        details_image_frame.pack(side="right", padx=5, pady=5, fill="both", expand=True)

        self.case_details_image = ttk.Label(details_image_frame, text="No image available")
        self.case_details_image.pack(padx=5, pady=5, fill="both", expand=True)

        # Create admin frame at the bottom — only visible to Developers
        if self.role == "Developer":
            admin_frame = ttk.LabelFrame(self.case_tab, text="Administration")
            admin_frame.pack(padx=10, pady=(5, 10), fill="x")

            cleanup_btn = ttk.Button(
                admin_frame, 
                text="Clean Up Old Closed Cases", 
                command=self.manual_cleanup
            )
            cleanup_btn.pack(side="right", padx=10, pady=10)

            help_text = "Cases marked as 'Closed' will be automatically deleted at the start of each month"
            ttk.Label(admin_frame, text=help_text, font=("Arial", 9, "italic")).pack(side="left", padx=10, pady=10)

        # Add Close Case and Notify Guardian button — Developer only (can change as needed)
        details_button_frame = ttk.Frame(details_frame)
        details_button_frame.pack(padx=5, pady=5, fill="x")

        if self.role == "Developer":
            self.close_details_btn = ttk.Button(
                details_button_frame, 
                text="Close This Case", 
                command=self.close_searched_case,
                state="disabled"
            )
            self.close_details_btn.pack(side="right", padx=5, pady=5)

        self.notify_guardian_details_btn = ttk.Button(
            details_button_frame, 
            text="Notify Guardian", 
            command=self.notify_case_guardian,
            state="disabled"
        )
        self.notify_guardian_details_btn.pack(side="right", padx=5, pady=5)

        # Filter by name
        search_filter_frame = ttk.Frame(self.case_tab)
        search_filter_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(search_filter_frame, text="Search by name:").pack(side="left", padx=5, pady=5)
        self.case_search_entry = ttk.Entry(search_filter_frame, width=30)
        self.case_search_entry.pack(side="left", padx=5, pady=5)
        self.case_search_entry.bind("<Return>", lambda event: self.filter_cases())

        search_filter_btn = ttk.Button(search_filter_frame, text="Search", command=self.filter_cases)
        search_filter_btn.pack(side="left", padx=5, pady=5)

        clear_filter_btn = ttk.Button(search_filter_frame, text="Clear Filter", command=self.refresh_cases)
        clear_filter_btn.pack(side="left", padx=5, pady=5)

        # Treeview
        cases_frame = ttk.LabelFrame(self.case_tab, text="Open Cases")
        cases_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("ID", "Name", "Age", "Gender", "Guardian Contact", "Last Known Location")
        self.cases_tree = ttk.Treeview(cases_frame, columns=columns, show="headings")
        
        for col in columns:
            self.cases_tree.heading(col, text=col)
            self.cases_tree.column(col, width=100)

        self.cases_tree.pack(padx=5, pady=5, fill="both", expand=True)
        self.cases_tree.bind("<Double-1>", self.on_case_selected)


    def close_searched_case(self):
        """Close the case that was found through search"""
        # Restrict access for non-developers
        if self.role != "Developer":
            messagebox.showwarning("Access Denied", "Only developers can close cases.")
            return
        try:
            embedding_id = self.embedding_id_entry.get().strip()
            
            if not embedding_id:
                messagebox.showinfo("Info", "No case is currently displayed")
                return
            
            # Confirm before closing
            confirm = messagebox.askyesno(
                "Confirm",
                "Are you sure you want to close this case? This action cannot be undone."
            )
            
            if confirm:
                # Get case details to check if it exists and is open
                child_details = get_child_by_embedding_id(int(embedding_id))
                
                if not child_details:
                    messagebox.showerror("Error", "Case not found")
                    return
                
                if child_details['case_status'] == "Closed":
                    messagebox.showinfo("Info", "This case is already closed")
                    return
                
                # Close the case
                if update_case_status(embedding_id, "Closed"):
                    messagebox.showinfo("Success", "Case closed successfully")
                    # Update the case details to show the new status
                    self.search_case()
                    # Refresh the open cases list
                    self.refresh_cases()
                    # Disable the close button
                    self.close_details_btn.config(state="disabled")
                    self.notify_guardian_details_btn.config(state="disabled")
                else:
                    messagebox.showerror("Error", "Failed to close case")
        
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric Embedding ID")
        except Exception as e:
            messagebox.showerror("Error", f"Error closing case: {e}")

    def close_identified_case(self):
        """Close all identified cases in the identify tab"""
        # Restrict access for non-developers
        if self.role != "Developer":
            messagebox.showwarning("Access Denied", "Only developers can close cases.")
            return
        try:
            # Get text from results_text to find embedding IDs
            self.results_text.config(state="normal")
            results_content = self.results_text.get("1.0", tk.END)
            self.results_text.config(state="disabled")
            
            # Check if any results are displayed
            if "No matches found" in results_content or not results_content.strip():
                messagebox.showinfo("Info", "No cases are currently identified")
                return
            
            # Parse the results to find embedding IDs
            import re
            embedding_ids = re.findall(r"Embedding ID: (\d+)", results_content)
            
            if not embedding_ids:
                messagebox.showinfo("Info", "No embedding IDs found in results")
                return
            
            # Check if all cases are already closed
            all_closed = True
            for eid in embedding_ids:
                child = get_child_by_embedding_id(int(eid))
                if child and child['case_status'] == "Open":
                    all_closed = False
                    break
            
            if all_closed:
                messagebox.showinfo("Info", "All identified cases are already closed")
                return
            
            # Confirm before closing
            confirm = messagebox.askyesno(
                "Confirm",
                f"Are you sure you want to close all {len(embedding_ids)} identified cases? This action cannot be undone."
            )
            
            if confirm:
                # Close all the cases
                success_count = 0
                for eid in embedding_ids:
                    child = get_child_by_embedding_id(int(eid))
                    if child and child['case_status'] == "Open":
                        if update_case_status(eid, "Closed"):
                            success_count += 1
                
                if success_count > 0:
                    messagebox.showinfo("Success", f"Successfully closed {success_count} case(s)")
                    # Update the identification results to reflect the change
                    self.identify_child()  # Re-run identification to refresh results
                    # Refresh the open cases list
                    self.refresh_cases()
                else:
                    messagebox.showinfo("Info", "No cases were closed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error closing cases: {e}")
    
    def upload_register_image(self):
        """Upload image for registration"""
        file_path = filedialog.askopenfilename(
            title="Select Child Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            self.register_image_path = file_path
            self.display_image(file_path, self.register_image_label)
            self.register_status.config(text=f"Image loaded: {os.path.basename(file_path)}")
    
    def upload_identify_image(self):
        """Upload image for identification"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            self.identify_input_path = file_path
            self.is_video = False
            self.display_image(file_path, self.identify_image_label)
            self.update_results_text("Image loaded. Click 'Identify Child' to process.")
    
    def upload_identify_video(self):
        """Upload video for identification"""
        file_path = filedialog.askopenfilename(
            title="Select Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        
        if file_path:
            self.identify_input_path = file_path
            self.is_video = True
            
            # Display first frame of video
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_np_image(frame_rgb, self.identify_image_label)
                self.update_results_text(f"Video loaded: {os.path.basename(file_path)}\nClick 'Identify Child' to process.")
            else:
                self.update_results_text("Error: Could not read video file.")
            cap.release()
    
    def toggle_webcam(self, target="register"):
        """Toggle webcam feed for either register or identify tabs"""
        if self.is_webcam_running:
            # Stop webcam
            self.is_webcam_running = False
            if self.webcam_thread and self.webcam_thread.is_alive():
                self.webcam_thread.join(timeout=1.0)
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            # Reset labels
            if target == "register":
                self.register_image_label.config(text="No image selected", image="")
            else:
                self.identify_image_label.config(text="No image selected", image="")
        else:
            # Start webcam
            self.is_webcam_running = True
            self.webcam_thread = threading.Thread(target=self.update_webcam, args=(target,))
            self.webcam_thread.daemon = True
            self.webcam_thread.start()
    
    def update_webcam(self, target):
        """Update webcam feed"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            self.is_webcam_running = False
            return
        
        while self.is_webcam_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame_rgb.copy()
            
            if target == "register":
                self.display_np_image(frame_rgb, self.register_image_label)
            else:
                self.display_np_image(frame_rgb, self.identify_image_label)
            
            time.sleep(0.03)  # ~30 FPS
        
        if self.cap.isOpened():
            self.cap.release()
    
    def capture_image(self, target):
        """Capture current frame from webcam"""
        if not self.is_webcam_running or self.current_frame is None:
            messagebox.showinfo("Info", "Webcam is not active")
            return
        
        # Save captured frame
        timestamp = int(time.time())
        temp_dir = "temp_captures"
        os.makedirs(temp_dir, exist_ok=True)
        capture_path = os.path.join(temp_dir, f"capture_{timestamp}.jpg")
        
        cv2.imwrite(capture_path, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))
        
        if target == "register":
            self.register_image_path = capture_path
            self.register_status.config(text=f"Image captured: {os.path.basename(capture_path)}")
        else:
            self.identify_input_path = capture_path
            self.is_video = False
            self.update_results_text("Image captured. Click 'Identify Child' to process.")    

    def display_image(self, file_path, label_widget):
        """Display image in the specified label widget"""
        try:
            image = Image.open(file_path)
            image = self.resize_image(image, 300)
            photo = ImageTk.PhotoImage(image)
            label_widget.config(image=photo)
            label_widget.image = photo  # Keep a reference
        except Exception as e:
            label_widget.config(text=f"Error loading image: {e}")
    
    def display_np_image(self, np_image, label_widget):
        """Display numpy image array in the specified label widget"""
        try:
            image = Image.fromarray(np_image)
            image = self.resize_image(image, 300)
            photo = ImageTk.PhotoImage(image)
            label_widget.config(image=photo)
            label_widget.image = photo  # Keep a reference
        except Exception as e:
            label_widget.config(text=f"Error displaying image: {e}")
    
    def resize_image(self, image, max_size):
        """Resize image while maintaining aspect ratio"""
        width, height = image.size
        
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        
        return image.resize((new_width, new_height), Image.LANCZOS)
    
    def register_child(self):
        """Register lost child with details from the form"""
        # Validate image
        if not self.register_image_path:
            messagebox.showerror("Error", "Please select or capture an image")
            return
        
        # Validate form fields
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_var.get()
        guardian_contact = self.guardian_entry.get().strip()
        distinguishing_features = self.features_text.get("1.0", tk.END).strip()
        last_known_location = self.location_entry.get().strip()
        
        # Basic validation
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        
        try:
            age = int(age_str)
            if age <= 0 or age >= 18:
                messagebox.showerror("Error", "Age must be between 1 and 17")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
            return
        
        if not gender:
            messagebox.showerror("Error", "Gender is required")
            return
        
        if not guardian_contact:
            messagebox.showerror("Error", "Guardian contact is required")
            return
        
        # Process registration in a separate thread to keep UI responsive
        threading.Thread(target=self._process_registration, args=(
            self.register_image_path,
            name,
            age,
            gender,
            guardian_contact,
            distinguishing_features,
            last_known_location
        )).start()
        
        self.register_status.config(text="Processing registration...")
    
    def _process_registration(self, image_path, name, age, gender, guardian_contact, 
                            distinguishing_features, last_known_location):
        """Process registration in a separate thread"""
        try:
            # Detect faces
            faces = detect_faces(image_path)
            
            if not faces:
                self.update_status("Error: No face detected in the image")
                return
            
            # Use the first detected face
            face = faces[0]
            
            # Extract embedding
            embedding = extract_embedding(face)
            
            if embedding is None:
                self.update_status("Error: Failed to extract facial embedding")
                return
            
            # Generate unique embedding ID
            embedding_id = hash(name + str(age) + str(np.mean(embedding))) % 1000000
            
            # Add embedding to vector store
            if not add_embedding_to_faiss(embedding, embedding_id):
                self.update_status("Error: Failed to add embedding to database")
                return
            
            # Store encrypted image
            encrypted_image_path = store_encrypted_image(image_path, embedding_id)
            
            # Insert metadata
            metadata_id = insert_child_metadata(
                name, age, gender, guardian_contact, 
                embedding_id, encrypted_image_path,
                distinguishing_features, last_known_location
            )
            
            if metadata_id:
                self.update_status(f"Child registered successfully. Embedding ID: {embedding_id}")
                self.clear_register_form()
                self.refresh_cases()  # Refresh case list
            else:
                self.update_status("Error: Failed to insert child metadata")
        
        except Exception as e:
            self.update_status(f"Registration error: {e}")
    
    def update_status(self, message):
        """Update status label in register tab safely from any thread"""
        if self.register_status.winfo_exists():
            self.after(0, lambda: self.register_status.config(text=message))
    
    def update_results_text(self, message):
        """Update results text in identify tab safely from any thread"""
        def _update():
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", message)
            self.results_text.config(state="disabled")
        
        if self.results_text.winfo_exists():
            self.after(0, _update)
    
    def identify_child(self):
        """Process identification of a child"""
        if not self.identify_input_path:
            messagebox.showerror("Error", "Please select an image, video, or capture from webcam")
            return
        
        # Process identification in a separate thread
        self.update_results_text("Processing identification...")
        threading.Thread(target=self._process_identification).start()
    
    def _process_identification(self):
        """Process identification in a separate thread"""
        try:
            # Detect faces
            faces = detect_faces(
                self.identify_input_path, 
                is_video=self.is_video, 
                is_webcam=False
            )
            
            if not faces:
                self.update_results_text("No faces detected in the input")
                return
            
            # Unique matches tracking
            unique_matches = set()
            
            # Process each detected face
            self.update_results_text(f"Processing {len(faces)} detected faces...")
            
            for i, face in enumerate(faces, 1):
                # Extract embedding
                embedding = extract_embedding(face)
                
                if embedding is None:
                    continue
                
                # Search for matches
                matches = search_faiss(embedding, top_k=5, similarity_threshold=0.50)
                
                if matches[0] != -1:
                    # Add matches to the unique set
                    unique_matches.update(matches)
            
            if unique_matches:
                # Convert to list and sort for consistent output
                sorted_matches = sorted(list(unique_matches))
                
                results = "Potential matches found:\n\n"
                
                # Track already printed child IDs
                printed_child_ids = set()
                
                for embedding_id in sorted_matches:
                    # Convert numpy.int64 to regular integer
                    embedding_id = int(embedding_id)
                    
                    # Retrieve child details
                    child_details = get_child_by_embedding_id(embedding_id)
                    
                    if child_details and child_details['child_id'] not in printed_child_ids:
                        results += f"Child ID: {child_details['child_id']}\n"
                        results += f"Embedding ID: {embedding_id}\n"
                        results += f"Name: {child_details['name']}\n"
                        results += f"Age: {child_details['age']}\n"
                        results += f"Gender: {child_details['gender']}\n"
                        results += f"Guardian Contact: {child_details['guardian_contact']}\n"
                        results += f"Case Status: {child_details['case_status']}\n"
                        
                        if child_details['distinguishing_features']:
                            results += f"Distinguishing Features: {child_details['distinguishing_features']}\n"
                        
                        if child_details['last_known_location']:
                            results += f"Last Known Location: {child_details['last_known_location']}\n"
                        
                        results += "\n" + "-"*50 + "\n\n"
                        
                        # Add to printed child IDs to prevent duplicates
                        printed_child_ids.add(child_details['child_id'])                        
                
                self.update_results_text(results)

                # Clear existing match images
                for widget in self.match_images_container.winfo_children():
                    widget.destroy()

                if printed_child_ids:  # If we found and printed any matches
                    # Display all match images
                    for i, embedding_id in enumerate(sorted_matches):
                        # Get child details
                        child_details = get_child_by_embedding_id(int(embedding_id))
                        if not child_details:
                            continue
                            
                        # Create a frame for this match
                        match_frame = ttk.Frame(self.match_images_container)
                        match_frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
                        
                        # Create label for child name
                        name_label = ttk.Label(match_frame, text=f"{child_details['name']} (ID: {embedding_id})")
                        name_label.pack(pady=(0, 5))
                        
                        # Create label for image
                        image_label = ttk.Label(match_frame, text="Loading image...")
                        image_label.pack(pady=5)
                        
                        # Retrieve and display image
                        self.retrieve_and_display_image(int(embedding_id), image_label)
                else:
                    # No matches were found, so display a message
                    no_match_label = ttk.Label(self.match_images_container, text="No matches found")
                    no_match_label.pack(padx=10, pady=10)

            else:
                self.update_results_text("No matches found.")
        
        except Exception as e:
            self.update_results_text(f"Error during identification: {e}")
    
    def search_case(self):
        """Search for a specific case by embedding ID"""
        try:
            embedding_id = int(self.embedding_id_entry.get().strip())
            
            child_details = get_child_by_embedding_id(embedding_id)
            
            if child_details:
                details = f"Child ID: {child_details['child_id']}\n"
                details += f"Name: {child_details['name']}\n"
                details += f"Age: {child_details['age']}\n"
                details += f"Gender: {child_details['gender']}\n"
                details += f"Guardian Contact: {child_details['guardian_contact']}\n"
                details += f"Case Status: {child_details['case_status']}\n"
                
                if child_details['distinguishing_features']:
                    details += f"Distinguishing Features: {child_details['distinguishing_features']}\n"
                
                if child_details['last_known_location']:
                    details += f"Last Known Location: {child_details['last_known_location']}\n"
                
                self.case_details_text.delete("1.0", tk.END)
                self.case_details_text.insert("1.0", details)
                
                # Display the child's image
                self.retrieve_and_display_image(embedding_id, self.case_details_image)
                
                # Enable buttons only if the case is open
                if child_details['case_status'] == "Open":
                    self.close_details_btn.config(state="normal")
                    self.notify_guardian_details_btn.config(state="normal")
                else:
                    self.close_details_btn.config(state="disabled")
                    self.notify_guardian_details_btn.config(state="disabled")
            else:
                self.case_details_text.delete("1.0", tk.END)
                self.case_details_text.insert("1.0", f"No child found with Embedding ID: {embedding_id}")
                self.case_details_image.config(text="No image available", image="")
                self.close_details_btn.config(state="disabled")
                self.notify_guardian_details_btn.config(state="disabled")
        
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric Embedding ID")
            self.close_details_btn.config(state="disabled")
            self.notify_guardian_details_btn.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Error searching case: {e}")
            self.close_details_btn.config(state="disabled")
            self.notify_guardian_details_btn.config(state="disabled")
    
    def refresh_cases(self):
        """Refresh the list of open cases"""
        try:
            # Clear search entry
            if hasattr(self, 'case_search_entry'):
                self.case_search_entry.delete(0, tk.END)
            
            # Clear existing cases
            for item in self.cases_tree.get_children():
                self.cases_tree.delete(item)
            
            # Import the search_open_cases function
            from database import search_open_cases
            
            # Get open cases
            open_cases = search_open_cases()
            
            # Populate tree
            for case in open_cases:
                self.cases_tree.insert(
                    "", "end",
                    values=(
                        case['child_id'],
                        case['name'],
                        case['age'],
                        case['gender'],
                        case['guardian_contact'],
                        case['last_known_location'] or "N/A"
                    ),
                    tags=(str(case['embedding_id']),)  # Store embedding_id as a tag
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing cases: {e}")

    def filter_cases(self):
        """Filter cases by name (case-insensitive)"""
        search_term = self.case_search_entry.get().strip().lower()
        
        if not search_term:
            # If search term is empty, just refresh all cases
            self.refresh_cases()
            return
        
        try:
            # Clear existing cases in the treeview
            for item in self.cases_tree.get_children():
                self.cases_tree.delete(item)
            
            # Import the search_open_cases function
            from database import search_open_cases
            
            # Get all open cases first
            open_cases = search_open_cases()
            
            # Filter cases by name (case-insensitive)
            filtered_cases = [case for case in open_cases if search_term in case['name'].lower()]
            
            # Populate tree with filtered cases
            for case in filtered_cases:
                self.cases_tree.insert(
                    "", "end",
                    values=(
                        case['child_id'],
                        case['name'],
                        case['age'],
                        case['gender'],
                        case['guardian_contact'],
                        case['last_known_location'] or "N/A"
                    ),
                    tags=(str(case['embedding_id']),)  # Store embedding_id as a tag
                )
            
            # Show feedback on results
            if not filtered_cases:
                messagebox.showinfo("Search Results", "No matching cases found")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering cases: {e}")
    
    def on_case_selected(self, event):
        """Handle case selection event"""
        selected_item = self.cases_tree.selection()[0]
        child_id = self.cases_tree.item(selected_item, "values")[0]
        embedding_id = self.cases_tree.item(selected_item, "tags")[0]
        
        # Display case details
        self.embedding_id_entry.delete(0, tk.END)
        self.embedding_id_entry.insert(0, embedding_id)
        self.search_case()
    
    def close_selected_case(self):
        """Close the selected case"""
        selected_items = self.cases_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("Info", "Please select a case to close")
            return
        
        selected_item = selected_items[0]
        embedding_id = self.cases_tree.item(selected_item, "tags")[0]
        
        # Confirm before closing
        confirm = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to close this case? This action cannot be undone."
        )
        
        if confirm:
            # Close the case
            from database import update_case_status
            
            if update_case_status(embedding_id, "Closed"):
                messagebox.showinfo("Success", "Case closed successfully")
                self.refresh_cases()
            else:
                messagebox.showerror("Error", "Failed to close case")
    
    def clear_register_form(self):
        """Clear registration form fields"""
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.gender_var.set("")
        self.guardian_entry.delete(0, tk.END)
        self.features_text.delete("1.0", tk.END)
        self.location_entry.delete(0, tk.END)
        self.register_image_label.config(image="", text="No image selected")
        self.register_image_path = None

    def retrieve_and_display_image(self, embedding_id, target_label):
        """Retrieve and display an encrypted image"""
        try:
            # Generate encrypted image path
            encrypted_path = os.path.join(IMAGE_STORAGE_PATH, f"{embedding_id}.enc")
            
            if not os.path.exists(encrypted_path):
                target_label.config(text="Image not found", image="")
                return False
            
            # Create temp directory for decryption
            temp_dir = "temp_decrypts"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate temp file for decrypted image
            temp_path = os.path.join(temp_dir, f"temp_{embedding_id}.jpg")
            
            # Decrypt the image
            from storage import retrieve_encrypted_image
            retrieve_encrypted_image(encrypted_path, temp_path)
            
            # Display the image
            image = Image.open(temp_path)
            image = self.resize_image(image, 200)  # Smaller size for multiple images
            photo = ImageTk.PhotoImage(image)
            target_label.config(image=photo)
            target_label.image = photo  # Keep a reference
            return True
        
        except Exception as e:
            target_label.config(text=f"Error loading image: {e}")
            return False

    def destroy(self):
        """Override destroy to clean up temporary files before exit"""
        # Stop webcam if running
        if self.is_webcam_running:
            self.is_webcam_running = False
            if self.webcam_thread and self.webcam_thread.is_alive():
                self.webcam_thread.join(timeout=1.0)
            if self.cap and self.cap.isOpened():
                self.cap.release()
        
        # Cleanup temporary files
        self.cleanup_temp_files()
        
        # Call the original destroy method
        super().destroy()    

if __name__ == "__main__":
    app = ChildSafetyApp()
    app.mainloop()
