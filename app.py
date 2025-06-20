import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid 
from datetime import datetime
import threading
import time
import os

from supabase import create_client, Client 

SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY") 

supabase: Client = None
if SUPABASE_URL == "YOUR_SUPABASE_URL_HERE" or SUPABASE_KEY == "YOUR_SUPABASE_ANON_KEY_HERE":
    print("WARNING: Supabase not configured. Running in local mode.")
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized.")
    except Exception as e:
        print(f"ERROR: Could not initialize Supabase client: {e}")
        messagebox.showerror("Supabase Error", f"Could not connect to Supabase: {e}\n"
                                               "Please ensure SUPABASE_URL and SUPABASE_ANON_KEY are correct.")
        supabase = None

class P2PCryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exchange Tool v1.0.0")
        self.root.geometry("1250x700")
        self.root.option_add('*tearOff', False) 

        self.supabase = supabase 
        self.user_id = None 
        self.connected_wallet_address = ""
        self.connected_paypal_email = ""

        self.create_widgets()
        self._check_current_session() 
        self.listen_for_offers()

    def create_widgets(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)

        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=0) 
        left_frame.grid_rowconfigure(1, weight=0) 
        left_frame.grid_rowconfigure(2, weight=0) 
        left_frame.grid_rowconfigure(3, weight=1) 
        left_frame.grid_columnconfigure(0, weight=1)

        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        self.auth_frame = ttk.LabelFrame(left_frame, text="Authentication", padding="10")
        self.auth_frame.grid(row=0, column=0, sticky="ew", pady=10)
        self.auth_frame.columnconfigure(1, weight=1)
        self._create_auth_widgets()

        user_info_frame = ttk.LabelFrame(left_frame, text="Info & Connection", padding="10")
        user_info_frame.grid(row=1, column=0, sticky="ew", pady=10) 
        user_info_frame.columnconfigure(1, weight=1)

        ttk.Label(user_info_frame, text=f"Your User ID:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.user_id_label = ttk.Label(user_info_frame, text="Not logged in", wraplength=250)
        self.user_id_label.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(user_info_frame, text="Wallet Address:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.wallet_entry = ttk.Entry(user_info_frame)
        self.wallet_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.wallet_entry.insert(0, "mock_btc_wallet_abc123") 

        connect_wallet_btn = ttk.Button(user_info_frame, text="Connect Wallet", command=self.connect_wallet)
        connect_wallet_btn.grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Label(user_info_frame, text="PayPal Email:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.paypal_entry = ttk.Entry(user_info_frame)
        self.paypal_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.paypal_entry.insert(0, "mock_paypal@example.com") 

        connect_paypal_btn = ttk.Button(user_info_frame, text="Connect PayPal", command=self.connect_paypal)
        connect_paypal_btn.grid(row=4, column=0, columnspan=2, pady=5)

        send_receive_frame = ttk.LabelFrame(left_frame, text="Send/Receive BTC", padding="10")
        send_receive_frame.grid(row=2, column=0, sticky="nsew", pady=10) 
        send_receive_frame.columnconfigure(1, weight=1)

        ttk.Label(send_receive_frame, text="Recipient Address/PayPal:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.recipient_entry = ttk.Entry(send_receive_frame)
        self.recipient_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(send_receive_frame, text="Amount (BTC):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.amount_btc_entry = ttk.Entry(send_receive_frame)
        self.amount_btc_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        send_btc_btn = ttk.Button(send_receive_frame, text="Send BTC (Simulated)", command=self.send_btc)
        send_btc_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.status_log_frame = ttk.LabelFrame(left_frame, text="Activity Log", padding="10")
        self.status_log_frame.grid(row=3, column=0, sticky="nsew", pady=10) 
        self.status_log_frame.grid_rowconfigure(0, weight=1)
        self.status_log_frame.grid_columnconfigure(0, weight=1)

        self.status_text = tk.Text(self.status_log_frame, height=8, state='disabled', wrap='word')
        self.status_text.grid(row=0, column=0, sticky="nsew")
        status_scrollbar = ttk.Scrollbar(self.status_log_frame, command=self.status_text.yview)
        status_scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text['yscrollcommand'] = status_scrollbar.set
        
        self.log_message("Welcome to P2P Crypto Exchange! Please login or sign up.")
        if not self.supabase:
            self.log_message("Supabase not connected. Offers will not persist or listen in realtime.")

        offers_table_frame = ttk.LabelFrame(right_frame, text="Online Offers", padding="10")
        offers_table_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        offers_table_frame.grid_rowconfigure(0, weight=1)
        offers_table_frame.grid_columnconfigure(0, weight=1)

        self.offers_tree = ttk.Treeview(offers_table_frame, columns=("User ID", "Type", "BTC Amount", "Fiat Amount", "Fiat Currency", "Status"), show="headings")
        self.offers_tree.grid(row=0, column=0, sticky="nsew")

        self.offers_tree.heading("User ID", text="User ID")
        self.offers_tree.heading("Type", text="Type")
        self.offers_tree.heading("BTC Amount", text="BTC Amount")
        self.offers_tree.heading("Fiat Amount", text="Fiat Amount")
        self.offers_tree.heading("Fiat Currency", text="Fiat Currency")
        self.offers_tree.heading("Status", text="Status")

        self.offers_tree.column("User ID", width=120, anchor="w")
        self.offers_tree.column("Type", width=70, anchor="center")
        self.offers_tree.column("BTC Amount", width=100, anchor="e")
        self.offers_tree.column("Fiat Amount", width=100, anchor="e")
        self.offers_tree.column("Fiat Currency", width=90, anchor="center")
        self.offers_tree.column("Status", width=80, anchor="center")

        offers_scrollbar = ttk.Scrollbar(offers_table_frame, command=self.offers_tree.yview)
        offers_scrollbar.grid(row=0, column=1, sticky="ns")
        self.offers_tree['yscrollcommand'] = offers_scrollbar.set

        self.post_offer_frame = ttk.LabelFrame(right_frame, text="Your Offer", padding="10")
        self.post_offer_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.post_offer_frame.columnconfigure(1, weight=1)
        self.post_offer_frame.columnconfigure(3, weight=1)

        ttk.Label(self.post_offer_frame, text="BTC Amount:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.post_btc_amount_entry = ttk.Entry(self.post_offer_frame)
        self.post_btc_amount_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.post_offer_frame, text="Fiat Amount:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.post_fiat_amount_entry = ttk.Entry(self.post_offer_frame)
        self.post_fiat_amount_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        ttk.Label(self.post_offer_frame, text="Fiat Currency:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.post_fiat_currency_combo = ttk.Combobox(self.post_offer_frame, values=["USD", "EUR", "GBP", "JPY", "CAD", "AUD"])
        self.post_fiat_currency_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.post_fiat_currency_combo.set("USD") 

        self.post_buy_btn = ttk.Button(self.post_offer_frame, text="Post BUY Offer", command=lambda: self.post_offer("buy"))
        self.post_buy_btn.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="ew")

        self.post_sell_btn = ttk.Button(self.post_offer_frame, text="Post SELL Offer", command=lambda: self.post_offer("sell"))
        self.post_sell_btn.grid(row=2, column=2, columnspan=2, pady=5, padx=5, sticky="ew")

        self._update_ui_on_auth_status()

    def _create_auth_widgets(self):
        """Creates the authentication UI elements within self.auth_frame."""
        ttk.Label(self.auth_frame, text="Email:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.email_entry = ttk.Entry(self.auth_frame)
        self.email_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.auth_frame, text="Password:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.password_entry = ttk.Entry(self.auth_frame, show="*") 
        self.password_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        auth_btn_frame = ttk.Frame(self.auth_frame)
        auth_btn_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        auth_btn_frame.columnconfigure(0, weight=1)
        auth_btn_frame.columnconfigure(1, weight=1)
        auth_btn_frame.columnconfigure(2, weight=1)

        self.signup_btn = ttk.Button(auth_btn_frame, text="Sign Up", command=self.sign_up)
        self.signup_btn.grid(row=0, column=0, padx=2, sticky="ew")

        self.login_btn = ttk.Button(auth_btn_frame, text="Login", command=self.sign_in)
        self.login_btn.grid(row=0, column=1, padx=2, sticky="ew")

        self.logout_btn = ttk.Button(auth_btn_frame, text="Logout", command=self.sign_out)
        self.logout_btn.grid(row=0, column=2, padx=2, sticky="ew")


    def _update_ui_on_auth_status(self):
        """Enables/disables UI elements based on authentication status."""
        is_logged_in = self.user_id is not None
        
        self.email_entry.config(state='normal' if not is_logged_in else 'disabled')
        self.password_entry.config(state='normal' if not is_logged_in else 'disabled')
        self.signup_btn.config(state='normal' if not is_logged_in else 'disabled')
        self.login_btn.config(state='normal' if not is_logged_in else 'disabled')
        self.logout_btn.config(state='normal' if is_logged_in else 'disabled')

        offer_widgets = [
            self.post_btc_amount_entry, self.post_fiat_amount_entry,
            self.post_fiat_currency_combo, self.post_buy_btn, self.post_sell_btn
        ]
        for widget in offer_widgets:
            widget.config(state='normal' if is_logged_in else 'disabled')

        if is_logged_in:
            self.user_id_label.config(text=self.user_id)
            self.log_message(f"Logged in with UID: {self.user_id[:8]}...")
        else:
            self.user_id_label.config(text="Not logged in")
            self.log_message("Please log in or sign up to post offers.")

    def _check_current_session(self):
        """Checks for an existing Supabase session on application startup."""
        if not self.supabase:
            return

        def _check_thread():
            try:
                session_response = self.supabase.auth.get_session()
                user = getattr(session_response, 'user', None)
                session = getattr(session_response, 'session', None)
                
                self.root.after(0, self._handle_auth_response, user, session, None) 
            except Exception as e:
                self.root.after(0, self._handle_auth_response, None, None, f"Failed to check session: {e}")
        
        threading.Thread(target=_check_thread, daemon=True).start()

    def _handle_auth_response(self, user, session, error):
        """
        Handles the response from Supabase authentication calls (sign_up, sign_in, sign_out).
        'error' can be an AuthApiError object or a string message from a caught Exception.
        """
        display_error_message = None

        if isinstance(error, str):
            display_error_message = error
        elif error:
            display_error_message = str(error)
        
        if display_error_message:
            self.user_id = None
            self.log_message(f"Authentication Error: {display_error_message}")
            messagebox.showerror("Auth Error", display_error_message)
        elif user and session:
            self.user_id = user.id
            self.log_message(f"Authentication successful for user: {user.email}")
        else:
            self.user_id = None
            self.log_message("No active Supabase session or logged out.")
        
        self._update_ui_on_auth_status()

    def sign_up(self):
        """Handles user registration with Supabase."""
        if not self.supabase:
            messagebox.showwarning("Supabase Not Connected", "Supabase client is not initialized.")
            return

        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password for sign up.")
            return

        def _signup_thread():
            try:
                response = self.supabase.auth.sign_up({"email": email, "password": password})
                
                user_data = getattr(response, 'user', None)
                session_data = getattr(response, 'session', None)
                auth_error = getattr(response, 'error', None)
                
                self.root.after(0, self._handle_auth_response, user_data, session_data, auth_error)
            except Exception as e:
                self.root.after(0, self._handle_auth_response, None, None, f"Sign up request failed: {e}")

        self.log_message(f"Attempting to sign up {email}...")
        threading.Thread(target=_signup_thread, daemon=True).start()


    def sign_in(self):
        """Handles user login with Supabase."""
        if not self.supabase:
            messagebox.showwarning("Supabase Not Connected", "Supabase client is not initialized.")
            return

        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password for login.")
            return

        def _signin_thread():
            try:
                response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
                
                user_data = getattr(response, 'user', None)
                session_data = getattr(response, 'session', None)
                auth_error = getattr(response, 'error', None)
                
                self.root.after(0, self._handle_auth_response, user_data, session_data, auth_error)
            except Exception as e:
                self.root.after(0, self._handle_auth_response, None, None, f"Sign in request failed: {e}")

        self.log_message(f"Attempting to log in as {email}...")
        threading.Thread(target=_signin_thread, daemon=True).start()


    def sign_out(self):
        """Handles user logout from Supabase."""
        if not self.supabase:
            messagebox.showwarning("Supabase Not Connected", "Supabase client is not initialized.")
            return

        def _signout_thread():
            try:
                error = self.supabase.auth.sign_out() 
                if error:
                    self.root.after(0, self._handle_auth_response, None, None, error)
                else:
                    self.root.after(0, self._handle_auth_response, None, None, None)
                    self.log_message("Logged out successfully.")
            except Exception as e:
                self.root.after(0, self._handle_auth_response, None, None, f"Sign out request failed: {e}")

        self.log_message("Attempting to log out...")
        threading.Thread(target=_signout_thread, daemon=True).start()


    def log_message(self, message):
        """Appends a message to the activity log."""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def connect_wallet(self):
        self.connected_wallet_address = self.wallet_entry.get().strip()
        if self.connected_wallet_address:
            self.log_message(f"Wallet connected: {self.connected_wallet_address}")
            messagebox.showinfo("Connection", f"Wallet '{self.connected_wallet_address}' connected (simulated).")
        else:
            messagebox.showwarning("Input Error", "Please enter a wallet address.")

    def connect_paypal(self):
        self.connected_paypal_email = self.paypal_entry.get().strip()
        if self.connected_paypal_email:
            self.log_message(f"PayPal connected: {self.connected_paypal_email}")
            messagebox.showinfo("Connection", f"PayPal '{self.connected_paypal_email}' connected (simulated).")
        else:
            messagebox.showwarning("Input Error", "Please enter a PayPal email.")

    def send_btc(self):
        recipient = self.recipient_entry.get().strip()
        amount_str = self.amount_btc_entry.get().strip()

        if not recipient or not amount_str:
            messagebox.showwarning("Input Error", "Please enter recipient and amount.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid positive BTC amount.")
            return

        self.log_message(f"Simulating sending {amount} BTC to {recipient}...")
        messagebox.showinfo("Transaction Simulated", f"Successfully simulated sending {amount} BTC to {recipient}.")

    def post_offer(self, offer_type):
        if not self.supabase:
            messagebox.showwarning("Supabase Not Connected", "Cannot post offer: Supabase client is not initialized.")
            self.log_message("Failed to post offer: Supabase not connected.")
            return
          
        if not self.user_id:
            messagebox.showwarning("Login Required", "Please log in to your Supabase account to post an offer.")
            self.log_message("Offer not posted: User not logged in to Supabase.")
            return

        btc_amount_str = self.post_btc_amount_entry.get().strip()
        fiat_amount_str = self.post_fiat_amount_entry.get().strip()
        fiat_currency = self.post_fiat_currency_combo.get().strip()

        if not btc_amount_str or not fiat_amount_str or not fiat_currency:
            messagebox.showwarning("Input Error", "Please fill all offer fields.")
            return

        try:
            btc_amount = float(btc_amount_str)
            fiat_amount = float(fiat_amount_str)
            if btc_amount <= 0 or fiat_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter valid positive amounts for BTC and Fiat.")
            return
        
        offer_data = {
            "userId": self.user_id,
            "offerType": offer_type, 
            "cryptoType": "BTC", 
            "cryptoAmount": btc_amount,
            "fiatCurrency": fiat_currency,
            "fiatAmount": fiat_amount,
            "status": "active",
        }

        try:
            response = self.supabase.table('p2p_offers').insert(offer_data).execute()
            if response.data:
                self.log_message(f"Posted {offer_type.upper()} offer: {btc_amount} BTC for {fiat_amount} {fiat_currency} (by {self.user_id[:8]}...)")
                self.post_btc_amount_entry.delete(0, tk.END)
                self.post_fiat_amount_entry.delete(0, tk.END)
                self.post_fiat_currency_combo.set("USD")
            else:
                raise Exception(f"Supabase insert failed: No data in response (Status: {response.status_code})")

        except Exception as e:
            self.log_message(f"Error posting offer: {e}")
            messagebox.showerror("Supabase Error", f"Could not post offer: {e}")

    def listen_for_offers(self):
        if not self.supabase:
            self.log_message("Supabase not available to listen for offers.")
            return
          
        try:
            response = self.supabase.table('p2p_offers').select('*').order('created_at.desc').execute()
            if response.data:
                self.update_offers_table(response.data)
                self.log_message("Initial offers fetched from Supabase.")
            else:
                self.log_message("No initial offers found on Supabase.")
        except Exception as e:
            self.log_message(f"Error fetching initial offers from Supabase: {e}")
            messagebox.showerror("Supabase Error", f"Could not fetch initial offers: {e}")

        def _realtime_listener_thread():
            def handle_realtime_event(payload):
                self.log_message(f"Realtime event received: {payload.get('event_type')} on table '{payload.get('table')}'")
                try:
                    response = self.supabase.table('p2p_offers').select('*').order('created_at.desc').execute()
                    if response.data:
                        self.root.after(0, self.update_offers_table, response.data)
                except Exception as e:
                    self.log_message(f"Error updating offers from realtime event: {e}")
            
            try:
                print("Attempting to subscribe to Supabase Realtime...")
                self.supabase.channel('p2p_offers_channel').on(
                    'postgres_changes',
                    {'event': '*', 'schema': 'public', 'table': 'p2p_offers'},
                    handle_realtime_event
                ).subscribe()
                print("Subscribed to Supabase Realtime.")
                while True:
                    time.sleep(1) 

            except Exception as e:
                self.log_message(f"Error setting up Supabase Realtime listener: {e}")
                print(f"Supabase Realtime setup failed: {e}")


        listener_thread = threading.Thread(target=_realtime_listener_thread, daemon=True)
        listener_thread.start()
        self.log_message("Supabase Realtime listener started.")

    def update_offers_table(self, offers_data):
        """Updates the Treeview table with current offers data."""
        for i in self.offers_tree.get_children():
            self.offers_tree.delete(i)

        for offer in offers_data:
            display_user_id = offer.get("userId", "N/A")
            if len(display_user_id) == 36 and '-' in display_user_id: 
                display_user_id = display_user_id[:8] + "..." + display_user_id[-4:] 

            crypto_amount_val = float(offer.get('cryptoAmount', 0.0))
            fiat_amount_val = float(offer.get('fiatAmount', 0.0))

            self.offers_tree.insert("", "end", values=(
                display_user_id,
                offer.get("offerType", "N/A").capitalize(),
                f"{crypto_amount_val:.4f}",
                f"{fiat_amount_val:.2f}",
                offer.get("fiatCurrency", "N/A"),
                offer.get("status", "N/A").capitalize()
            ))

def main():
    root = tk.Tk()
    app = P2PCryptoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
