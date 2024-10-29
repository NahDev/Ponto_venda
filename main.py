import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Configuração inicial do banco de dados
def setup_database():
    conn = sqlite3.connect("pos.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
                      (id INTEGER PRIMARY KEY, product_id INTEGER, quantity INTEGER, 
                       sale_date TEXT, FOREIGN KEY (product_id) REFERENCES products(id))''')
    conn.commit()
    conn.close()

setup_database()

# Função para adicionar produto
def add_product():
    name = entry_name.get()
    price = float(entry_price.get())
    stock = int(entry_stock.get())
    
    conn = sqlite3.connect("pos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()
    
    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_stock.delete(0, tk.END)
    messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

# Função para realizar uma venda
def make_sale():
    product_id = int(entry_product_id.get())
    quantity = int(entry_quantity.get())
    
    conn = sqlite3.connect("pos.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT stock, price FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    
    if product and product[0] >= quantity:
        # Atualiza o estoque e registra a venda
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, product_id))
        cursor.execute("INSERT INTO sales (product_id, quantity, sale_date) VALUES (?, ?, ?)", 
                       (product_id, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        messagebox.showinfo("Sucesso", "Venda realizada com sucesso!")
    else:
        messagebox.showerror("Erro", "Estoque insuficiente ou produto não encontrado.")
    
    conn.close()

# Função para mostrar relatório de vendas
def show_sales_report():
    conn = sqlite3.connect("pos.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT products.name, sales.quantity, products.price, 
                      (sales.quantity * products.price) as total, sales.sale_date 
                      FROM sales JOIN products ON sales.product_id = products.id''')
    sales = cursor.fetchall()
    conn.close()

    report_window = tk.Toplevel(root)
    report_window.title("Relatório de Vendas")

    text = tk.Text(report_window, width=60, height=20)
    text.pack()
    text.insert(tk.END, "Produto\tQuantidade\tPreço\tTotal\tData\n")
    for sale in sales:
        text.insert(tk.END, f"{sale[0]}\t{sale[1]}\t{sale[2]:.2f}\t{sale[3]:.2f}\t{sale[4]}\n")

# Configuração da interface principal
root = tk.Tk()
root.title("Sistema de Ponto de Venda (POS)")

# Seção de Cadastro de Produto
frame_product = tk.LabelFrame(root, text="Cadastro de Produto")
frame_product.pack(fill="both", expand="yes", padx=20, pady=10)

tk.Label(frame_product, text="Nome do Produto:").grid(row=0, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame_product)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_product, text="Preço:").grid(row=1, column=0, padx=5, pady=5)
entry_price = tk.Entry(frame_product)
entry_price.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_product, text="Estoque:").grid(row=2, column=0, padx=5, pady=5)
entry_stock = tk.Entry(frame_product)
entry_stock.grid(row=2, column=1, padx=5, pady=5)

btn_add_product = tk.Button(frame_product, text="Adicionar Produto", command=add_product)
btn_add_product.grid(row=3, columnspan=2, pady=10)

# Seção de Registro de Venda
frame_sale = tk.LabelFrame(root, text="Registrar Venda")
frame_sale.pack(fill="both", expand="yes", padx=20, pady=10)

tk.Label(frame_sale, text="ID do Produto:").grid(row=0, column=0, padx=5, pady=5)
entry_product_id = tk.Entry(frame_sale)
entry_product_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_sale, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5)
entry_quantity = tk.Entry(frame_sale)
entry_quantity.grid(row=1, column=1, padx=5, pady=5)

btn_make_sale = tk.Button(frame_sale, text="Realizar Venda", command=make_sale)
btn_make_sale.grid(row=2, columnspan=2, pady=10)

# Botão para Relatório de Vendas
btn_report = tk.Button(root, text="Relatório de Vendas", command=show_sales_report)
btn_report.pack(pady=10)

root.mainloop()
