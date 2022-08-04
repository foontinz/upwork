import csv
import tkinter as tk
import mysql.connector
from tkinter import filedialog
from tkinter import messagebox


def create_window(height, width, title):
    window = tk.Tk()
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.resizable(False, False)
    return window


class App:

    def __init__(self, db: 'DataBaseInterface'):
        self.db = db
        self.login_window = None
        self.main_window = None
        self.all_products_window = None

        self.login_input = None
        self.pass_input = None

        self.btn_start = None
        self.btn_stop = None
        self.btn_upload = None
        self.btn_show_all = None

        self.create_login_window()

    def start_all(self):
        query_start_all = """UPDATE products SET running = 1"""
        self.db.cursor.execute(query_start_all)
        self.db.connection.commit()
        self.refresh_all_products_window()

        if not self.db.is_any_state(0):
            self.btn_stop.config(state='normal')
            self.btn_start.config(state='disabled')

    def stop_all(self):
        query_stop_all = """UPDATE products SET running = 0"""
        self.db.cursor.execute(query_stop_all)
        self.db.connection.commit()
        self.refresh_all_products_window()

        if not self.db.is_any_state(1):
            self.btn_stop.config(state='disabled')
            self.btn_start.config(state='normal')

    def on_closing_window(self, id):
        if id == "login":
            self.login_window.destroy()
            self.login_window = None
        if id == "main":
            self.main_window.destroy()
            self.main_window = None
        if id == "all_products":
            self.all_products_window.destroy()
            self.all_products_window = None

    def create_login_window(self):
        if not self.main_window:
            self.login_window = create_window(360, 300, 'Login')
            self.login_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_login_window_widgets()
            self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("login"))

    def create_main_window(self):
        if not self.main_window:
            self.main_window = create_window(360, 300, 'eBay Tool')
            self.main_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_main_window_widgets()
            self.main_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("main"))

    def create_all_products_window(self):
        if not self.all_products_window:
            self.all_products_window = create_window(720, 1280, 'All Products')
            self.build_all_products_window_widgets()
            self.all_products_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("all_products"))

    def build_login_window_widgets(self):
        self.create_login_label()
        self.create_login_input()
        self.create_password_label()
        self.create_password_input()
        self.create_login_button()

    def build_main_window_widgets(self):
        self.create_upload_button()
        self.create_stop_button()
        self.create_start_button()
        self.create_all_products_button()

    def build_all_products_window_widgets(self):
        self.create_label_entries()
        row = 1
        for product in self.db.get_all_products():
            product = [product[0], product[1], product[8], product[5], product[4], product[10]]
            row += 1
            self.create_products_visible(product, row)
            self.create_product_delete_btn(product, row)
        self.create_refresh_all_products_window_btn()

    def refresh_main_window(self):
        if self.main_window:
            if self.main_window.winfo_exists():
                for widget in self.main_window.winfo_children():
                    widget.destroy()
                self.build_main_window_widgets()

    def refresh_all_products_window(self):
        if self.all_products_window:
            if self.all_products_window.winfo_exists():
                for widget in self.all_products_window.winfo_children():
                    widget.destroy()
                self.build_all_products_window_widgets()

    def create_refresh_all_products_window_btn(self):
        refresh_btn = tk.Button(self.all_products_window, text='Refresh', fg='grey',
                                command=self.refresh_all_products_window, font=('Arial', 13, 'bold'))
        refresh_btn.grid(row=1, column=7)

    def create_products_visible(self, product, row):
        column = 0
        self.create_product_entry(value=row - 1, row=row, column=column)
        for parameter in product:
            column += 1
            self.create_product_entry(value=parameter, row=row, column=column)

    def create_label_entries(self):
        parameters = ['ID', 'Status', 'Ebay_id', 'Expected_profit', 'Ebay_price', 'First_EC_price', 'User_id']
        for parameter in parameters:
            tk.Label(
                self.all_products_window,
                width=15,
                text=parameter,
                font=('Arial', 13, 'bold'),
                justify=tk.LEFT,
                bg='LightSteelBlue',
                fg='Black',
                relief=tk.RAISED).grid(column=parameters.index(parameter), row=1)

    def create_product_entry(self, value, row, column):
        entry_temp = tk.Entry(
            self.all_products_window,
            width=17,
            font=('Arial', 13, 'bold'),
            justify=tk.LEFT,
            fg='Black',
            relief=tk.RAISED)
        entry_temp.insert(0, value)
        entry_temp.grid(column=column, row=row)

    def del_product_build(self, product):
        if tk.messagebox.askyesno('Check', 'Delete?'):
            self.db.del_product(product)
            self.refresh_all_products_window()
            self.refresh_main_window()

    def create_product_delete_btn(self, product, row):
        delete_button = tk.Button(self.all_products_window, text='Delete', fg='grey',
                                  command=lambda: self.del_product_build(product), font=('Arial', 13, 'bold'))
        delete_button.grid(row=row, column=7)

    def create_product_off_btn(self, product):
        pass

    def create_product_on_btn(self, product):
        pass

    def create_upload_button(self):
        tk.Button(self.main_window, text='Upload', fg='grey',
                  command=self.upload_file, font=('Arial', 18, 'bold'), ).place(relx=0.1, rely=0.3, anchor='sw')

    def create_start_button(self):
        self.btn_start = tk.Button(self.main_window, text='Start all', fg='Green',
                                   command=self.start_all, font=('Arial', 18, 'bold'))
        self.btn_start.place(relx=0.1, rely=0.65, anchor='sw')

        if not self.db.is_any_state(0):
            self.btn_start.config(state='disabled')

    def create_stop_button(self):
        self.btn_stop = tk.Button(self.main_window, text='Stop all', fg='Red',
                                  command=self.stop_all, font=('Arial', 18, 'bold'))
        self.btn_stop.place(relx=0.1, rely=0.8, anchor='sw')
        if not self.db.is_any_state(1):
            self.btn_stop.config(state='disabled')

    def create_all_products_button(self):
        self.btn_show_all = tk.Button(self.main_window, text='Show all products', fg='grey',
                                      command=self.create_all_products_window, font=('Arial', 18, 'bold'), )
        self.btn_show_all.place(relx=0.1, rely=0.5, anchor='sw')

    def create_login_label(self):
        tk.Label(self.login_window,
                 text='Login', font=('Arial', 15,), justify=tk.LEFT).place(relx=0.5, rely=0.15, anchor='center')

    def create_login_input(self):
        self.login_input = tk.Entry(self.login_window, font=('Arial', 15,), justify=tk.LEFT)
        self.login_input.place(relx=0.5, rely=0.3, anchor='center')

    def create_password_label(self):
        tk.Label(self.login_window, height=1, width=12, text='Password', font=('Arial', 15,),
                 justify=tk.LEFT).place(relx=0.5, rely=0.45, anchor='center')

    def create_password_input(self):
        self.pass_input = tk.Entry(self.login_window, font=('Arial', 15,), justify=tk.LEFT)
        self.pass_input.place(relx=0.5, rely=0.6, anchor='center')

    def create_login_button(self):
        tk.Button(self.login_window, width=9, text='Log in', bg='#CACDCE', font=('Arial', 15, 'bold'),
                  command=self.successful_login).place(relx=0.5, rely=0.75, anchor='center')

    def successful_login(self):
        if self.db.check_login_password(login=self.login_input.get().strip(), password=self.pass_input.get().strip()):
            self.login_window.destroy()
            self.create_main_window()

    def upload_file(self):
        filepath = filedialog.askopenfilename()

        if not filepath:
            return

        if filepath[-3:] != "csv":
            messagebox.showwarning("Wrong format", 'You can use only CSV format')
            return

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            datareader = csv.reader(csvfile)
            datareader.__next__()
            try:
                for row in datareader:
                    if len(row) == 11:
                        print(row)

                        if not self.db.is_entry_added(ebay_id=row[0]):
                            self.db.add_entry(row=row)

                if self.all_products_window:
                    self.refresh_all_products_window()
                if self.main_window:
                    self.refresh_main_window()
            except Exception as ex:
                messagebox.showwarning("Error", f'Error: {ex}')
                print(ex)


class DataBaseInterface:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='suzzuya',
                port=3306,
                database='ebay'

            )
            print('connected')
            self.cursor = self.connection.cursor()

        except Exception as ex:
            print(ex)

    def check_login_password(self, login, password):
        query_login = f"""SELECT password FROM users WHERE login = '{login}'"""
        try:
            self.cursor.execute(query_login)
            res = self.cursor.fetchall()
            if res:
                if res[0][0] == password:
                    return True
                messagebox.showwarning("Error", 'Wrong password')
                return False
            messagebox.showwarning("Error", 'Not found login')
            return False
        except Exception as ex:
            print(ex)

    def is_any_state(self, state: int):
        query_running = f"""SELECT * FROM products WHERE running = {state}"""
        self.cursor.execute(query_running)
        return any(self.cursor.fetchall())

    def is_entry_added(self, ebay_id):
        query = f"""SELECT * FROM products WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)
        return any(self.cursor.fetchall())

    def add_entry(self, row):
        query_add_entry = f"""
        INSERT INTO products (
        running,
        ebay_id,
        ecommerce_url,
        stock_word,
        ecommerce_price,
        ebay_price,
        ebay_shipping_price,
        invoicing_charge_price,
        expected_profit,
        commission_factor,
        sku,
        user_id)
        VALUES (
        0,
        '{row[0]}',
        '{row[1]}',
        '{row[2]}',
        '{row[3]}',
        '{row[4]}',
        '{row[5]}',
        '{row[6]}',
        '{row[7]}',
        '{row[8]}',
        '{row[9]}',
        '{row[10]}')"""
        self.cursor.execute(query_add_entry)
        self.connection.commit()

    def get_all_products(self):
        query = """SELECT * FROM products"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def del_product(self, product):
        query = f"""DELETE FROM products WHERE ebay_id = '{product[1]}' """
        self.cursor.execute(query)
        self.connection.commit()


if __name__ == '__main__':
    dbase = DataBaseInterface()

    log_in = App(dbase)

    log_in.login_window.mainloop()
