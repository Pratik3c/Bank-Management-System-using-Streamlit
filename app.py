import streamlit as st
import json
import random
import string
from pathlib import Path

# --- Bank Class (modified for Streamlit) ---
class Bank:
    database = 'data.json'

    def __init__(self):
        # Initialize session state for bank_data if not already present
        if 'bank_data' not in st.session_state:
            self._load_data_into_session()

    def _load_data_into_session(self):
        """Loads data from data.json into Streamlit's session state."""
        try:
            if Path(self.database).exists():
                with open(self.database, 'r') as fs:
                    # Handle empty file or malformed JSON
                    content = fs.read()
                    if content:
                        st.session_state.bank_data = json.loads(content)
                    else:
                        st.session_state.bank_data = []
            else:
                st.session_state.bank_data = []
                self.__update_file() # Create the file if it doesn't exist
        except json.JSONDecodeError:
            st.session_state.bank_data = [] # Handle malformed JSON
            self.__update_file()
        except Exception as err:
            st.error(f"An exception occurred during data loading: {err}")
            st.session_state.bank_data = []

    def __update_file(self):
        """Writes the current st.session_state.bank_data to the data.json file."""
        with open(self.database, 'w') as fs:
            json.dump(st.session_state.bank_data, fs, indent=4)

    @classmethod
    def __accountgenerate(cls):
        """Generates a random alphanumeric account number."""
        alpha = random.choices(string.ascii_letters, k=3)
        num = random.choices(string.digits, k=3)
        spchar = random.choices("!@#$%^&*", k=1)
        id_chars = alpha + num + spchar
        random.shuffle(id_chars)
        return "".join(id_chars)

    def _find_user(self, accnumber, pin):
        """Helper to find user data in session state."""
        for user in st.session_state.bank_data:
            if user['accountNo.'] == accnumber and user['pin'] == pin:
                return user
        return None

    def Createaccount(self, name, age, email, pin):
        """Creates a new bank account."""
        if age < 18 or len(str(pin)) != 4:
            return {"success": False, "message": "Sorry, you cannot create your account. Age must be 18+ and PIN must be 4 digits."}
        
        account_no = Bank.__accountgenerate()
        info = {
            "name": name,
            "age": age,
            "email": email,
            "pin": pin,
            "accountNo.": account_no,
            "balance": 0
        }
        st.session_state.bank_data.append(info) # Modify session state directly
        self.__update_file() # Save changes to file
        return {"success": True, "message": "Account has been created successfully!", "account_info": info}

    def depositmoney(self, accnumber, pin, amount):
        """Deposits money into an account."""
        user = self._find_user(accnumber, pin)
        if not user:
            return {"success": False, "message": "Sorry, no data found for the provided account number and PIN."}
        
        if not (0 < amount <= 10000):
            return {"success": False, "message": "Sorry, the amount must be between 1 and 10000."}
        
        user['balance'] += amount
        self.__update_file()
        return {"success": True, "message": "Amount deposited successfully!", "new_balance": user['balance']}

    def withdrawmoney(self, accnumber, pin, amount):
        """Withdraws money from an account."""
        user = self._find_user(accnumber, pin)
        if not user:
            return {"success": False, "message": "Sorry, no data found for the provided account number and PIN."}
        
        if user['balance'] < amount:
            return {"success": False, "message": "Sorry, you don't have enough money in your account."}
        
        user['balance'] -= amount
        self.__update_file()
        return {"success": True, "message": "Amount withdrawn successfully!", "new_balance": user['balance']}

    def showdetails(self, accnumber, pin):
        """Shows details of an account."""
        user = self._find_user(accnumber, pin)
        if not user:
            return {"success": False, "message": "Sorry, no data found for the provided account number and PIN."}
        
        return {"success": True, "message": "Your account information:", "account_info": user}

    def updatedetails(self, accnumber, pin, new_name=None, new_email=None, new_pin=None):
        """Updates details of an account."""
        user = self._find_user(accnumber, pin)
        if not user:
            return {"success": False, "message": "No such user found."}
        
        if new_name:
            user['name'] = new_name
        if new_email:
            user['email'] = new_email
        if new_pin is not None and new_pin != "": # Check for empty string from text_input
            try:
                new_pin_int = int(new_pin)
                if len(str(new_pin_int)) != 4:
                    return {"success": False, "message": "New PIN must be 4 digits."}
                user['pin'] = new_pin_int
            except ValueError:
                return {"success": False, "message": "New PIN must be a valid number."}
        
        self.__update_file()
        return {"success": True, "message": "Details updated successfully!", "updated_info": user}

    def Delete(self, accnumber, pin):
        """Deletes an account."""
        # Find the index of the user data to remove
        found_index = -1
        for idx, account in enumerate(st.session_state.bank_data):
            if account['accountNo.'] == accnumber and account['pin'] == pin:
                found_index = idx
                break
        
        if found_index != -1:
            st.session_state.bank_data.pop(found_index)
            self.__update_file()
            return {"success": True, "message": "Account deleted successfully!"}
        else:
            return {"success": False, "message": "Sorry, no such data exist."}

# --- Streamlit App ---
st.set_page_config(page_title="Simple Bank App", layout="centered")

st.title("🏦 Simple Bank Application")
st.markdown("Manage your accounts with ease.")

# Initialize Bank instance. This will load data into st.session_state.bank_data
bank = Bank()

# Sidebar for navigation
st.sidebar.header("Navigation")
options = ["Home", "Create Account", "Deposit Money", "Withdraw Money", "Show Details", "Update Details", "Delete Account"]
choice = st.sidebar.radio("Go to", options)

if choice == "Home":
    st.header("Welcome!")
    st.info("Select an option from the sidebar to get started.")
    st.subheader("Current Accounts (for demonstration purposes):")
    if st.session_state.bank_data:
        # Display a simplified view of accounts for overview
        display_data = [{"name": acc['name'], "accountNo.": acc['accountNo.'], "balance": acc['balance']} for acc in st.session_state.bank_data]
        st.dataframe(display_data, use_container_width=True)
    else:
        st.info("No accounts created yet.")

elif choice == "Create Account":
    st.header("Create New Account")
    with st.form("create_account_form"):
        name = st.text_input("Your Name", key="create_name")
        age = st.number_input("Your Age", min_value=0, max_value=120, value=18, key="create_age")
        email = st.text_input("Your Email", key="create_email")
        pin = st.text_input("4-Digit PIN", type="password", max_chars=4, key="create_pin")
        submitted = st.form_submit_button("Create Account")

        if submitted:
            try:
                pin_int = int(pin)
                result = bank.Createaccount(name, age, email, pin_int)
                if result["success"]:
                    st.success(result["message"])
                    st.json(result["account_info"])
                    st.info("Please note down your Account Number!")
                else:
                    st.error(result["message"])
            except ValueError:
                st.error("PIN must be a valid 4-digit number.")

elif choice == "Deposit Money":
    st.header("Deposit Money")
    with st.form("deposit_form"):
        acc_number = st.text_input("Account Number", key="deposit_acc_num")
        pin = st.text_input("PIN", type="password", max_chars=4, key="deposit_pin")
        amount = st.number_input("Amount to Deposit", min_value=1, max_value=10000, value=100, key="deposit_amount")
        submitted = st.form_submit_button("Deposit")

        if submitted:
            try:
                pin_int = int(pin)
                result = bank.depositmoney(acc_number, pin_int, amount)
                if result["success"]:
                    st.success(result["message"])
                    st.write(f"New Balance: ${result['new_balance']:.2f}")
                else:
                    st.error(result["message"])
            except ValueError:
                st.error("PIN must be a valid 4-digit number.")

elif choice == "Withdraw Money":
    st.header("Withdraw Money")
    with st.form("withdraw_form"):
        acc_number = st.text_input("Account Number", key="withdraw_acc_num")
        pin = st.text_input("PIN", type="password", max_chars=4, key="withdraw_pin")
        amount = st.number_input("Amount to Withdraw", min_value=1, value=100, key="withdraw_amount")
        submitted = st.form_submit_button("Withdraw")

        if submitted:
            try:
                pin_int = int(pin)
                result = bank.withdrawmoney(acc_number, pin_int, amount)
                if result["success"]:
                    st.success(result["message"])
                    st.write(f"New Balance: ${result['new_balance']:.2f}")
                else:
                    st.error(result["message"])
            except ValueError:
                st.error("PIN must be a valid 4-digit number.")

elif choice == "Show Details":
    st.header("Show Account Details")
    with st.form("show_details_form"):
        acc_number = st.text_input("Account Number", key="show_acc_num")
        pin = st.text_input("PIN", type="password", max_chars=4, key="show_pin")
        submitted = st.form_submit_button("Show Details")

        if submitted:
            try:
                pin_int = int(pin)
                result = bank.showdetails(acc_number, pin_int)
                if result["success"]:
                    st.success(result["message"])
                    st.json(result["account_info"])
                else:
                    st.error(result["message"])
            except ValueError:
                st.error("PIN must be a valid 4-digit number.")

elif choice == "Update Details":
    st.header("Update Account Details")
    st.info("You cannot change age, account number, or balance directly.")
    with st.form("update_details_form"):
        acc_number = st.text_input("Account Number", key="update_acc_num")
        pin = st.text_input("Current PIN", type="password", max_chars=4, key="update_current_pin")
        st.markdown("---")
        st.subheader("New Details (leave empty for no change)")
        new_name = st.text_input("New Name (optional)", key="update_new_name")
        new_email = st.text_input("New Email (optional)", key="update_new_email")
        new_pin = st.text_input("New 4-Digit PIN (optional)", type="password", max_chars=4, key="update_new_pin")
        submitted = st.form_submit_button("Update Details")

        if submitted:
            try:
                current_pin_int = int(pin)
                # Pass None if fields are empty, so the bank class knows not to update them
                result = bank.updatedetails(
                    acc_number,
                    current_pin_int,
                    new_name if new_name else None,
                    new_email if new_email else None,
                    int(new_pin) if new_pin else None # Convert to int only if not empty
                )
                if result["success"]:
                    st.success(result["message"])
                    st.json(result["updated_info"])
                else:
                    st.error(result["message"])
            except ValueError:
                st.error("PINs must be valid 4-digit numbers.")

elif choice == "Delete Account":
    st.header("Delete Account")
    with st.form("delete_account_form"):
        acc_number = st.text_input("Account Number", key="delete_acc_num")
        pin = st.text_input("PIN", type="password", max_chars=4, key="delete_pin")
        confirm_delete = st.checkbox("I understand this action is irreversible and want to delete my account.", key="delete_confirm")
        submitted = st.form_submit_button("Delete Account")

        if submitted:
            if confirm_delete:
                try:
                    pin_int = int(pin)
                    result = bank.Delete(acc_number, pin_int)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                except ValueError:
                    st.error("PIN must be a valid 4-digit number.")
            else:
                st.warning("Please confirm deletion by checking the box.")
