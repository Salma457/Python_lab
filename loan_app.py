import psycopg2
from decimal import Decimal

class LoanApp:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="loan_db",
            user="salmahuissein457",
            password="salmahu457@12345",
            host="127.0.0.1"
        )
        self.user = None

    def register(self):
        cur = self.conn.cursor()
        username = input("Choose a username: ")
        password = input("Choose a password: ")

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.conn.commit()
            print("Registration successful.")
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print("Username already exists.")
        finally:
            cur.close()

    def login(self):
        cur = self.conn.cursor()
        username = input("Enter username: ")
        password = input("Enter password: ")

        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            self.user = user
            print(f"\nWelcome back, {username}!\n")
            return True
        else:
            print("Invalid credentials.")
            return False
    def main_menu(self):
        while True:
            print("\n--- Loan Application System ---")
            print("1. Login")
            print("2. Register")
            print("3. Exit")

            choice = input("Select an option: ")

            if choice == "1":
                if self.login():
                    self.user_menu()
            elif choice == "2":
                self.register()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
    def user_menu(self):
        while True:
            print("\n--- User Menu ---")
            print("1. Apply for a loan")
            print("2. Make a payment")
            print("3. Check balance")
            print("4. View payment history")
            print("5. Logout")

            choice = input("Select an option: ")

            if choice == "1":
                self.apply_loan()
            elif choice == "2":
                self.make_payment()
            elif choice == "3":
                self.check_balance()
            elif choice == "4":
                self.view_payments()
            elif choice == "5":
                self.user = None
                break
            else:
                print("Invalid choice.")
    def apply_loan(self):
        cur = self.conn.cursor()
        try:
            amount = float(input("Enter loan amount: "))
            user_id = self.user[0]
            cur.execute("INSERT INTO loans (user_id, amount, balance) VALUES (%s, %s, %s)",
                        (user_id, amount, amount))
            self.conn.commit()
            print("Loan application submitted successfully.")
        except Exception as e:
            self.conn.rollback()
            print("Error applying for loan:", e)
        finally:
            cur.close()

    def make_payment(self):
        cur = self.conn.cursor()
        try:
            user_id = self.user[0]
            cur.execute("SELECT id, balance FROM loans WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
            loan = cur.fetchone()

            if not loan:
                print("No active loans found.")
                return

            loan_id, balance = loan
            print(f"Your current loan balance: {balance}")
            payment_amount = Decimal(input("Enter payment amount: "))

            if payment_amount > balance:
                print("Payment exceeds loan balance.")
                return

            cur.execute("INSERT INTO payments (loan_id, amount) VALUES (%s, %s)", (loan_id, payment_amount))
            new_balance = balance - payment_amount
            cur.execute("UPDATE loans SET balance = %s WHERE id = %s", (new_balance, loan_id))

            self.conn.commit()
            print("Payment successful.")
        except Exception as e:
            self.conn.rollback()
            print("Error making payment:", e)
        finally:
            cur.close()

    def check_balance(self):
        cur = self.conn.cursor()
        try:
            user_id = self.user[0]
            cur.execute("SELECT balance FROM loans WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
            result = cur.fetchone()
            if result:
                print(f"Your current loan balance is: {result[0]}")
            else:
                print("No loan found.")
        except Exception as e:
            print("Error checking balance:", e)
        finally:
            cur.close()
    def view_payments(self):
        cur = self.conn.cursor()
        try:
            user_id = self.user[0]
            cur.execute("""
                SELECT p.amount, p.paid_at 
                FROM payments p 
                JOIN loans l ON p.loan_id = l.id 
                WHERE l.user_id = %s 
                ORDER BY p.paid_at DESC
            """, (user_id,))
            payments = cur.fetchall()
            if payments:
                print("\n--- Payment History ---")
                for amount, paid_at in payments:
                    print(f"{paid_at.strftime('%Y-%m-%d %H:%M:%S')}: ${amount}")
            else:
                print("No payments found.")
        except Exception as e:
            print("Error viewing payment history:", e)
        finally:
            cur.close()
if __name__ == "__main__":
    app = LoanApp()
    app.main_menu()












