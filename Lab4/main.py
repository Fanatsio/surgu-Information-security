import tkinter as tk
from tkinter import messagebox
import random

def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

def generate_keys():
    q = 23  # Простое число
    p = 47  # Простое число, p = kq + 1
    g = 2   # Генератор g < p
    x = random.randint(1, q - 1)  # Закрытый ключ
    y = mod_exp(g, x, p)  # Открытый ключ
    return p, q, g, x, y

def sign_message(message, p, q, g, x):
    k = random.randint(1, q - 1)
    r = mod_exp(g, k, p) % q
    s = ((hash(message) + x * r) * pow(k, -1, q)) % q
    return r, s

def verify_signature(message, r, s, p, q, g, y):
    w = pow(s, -1, q)
    u1 = (hash(message) * w) % q
    u2 = (r * w) % q
    v = ((mod_exp(g, u1, p) * mod_exp(y, u2, p)) % p) % q
    return v == r

def generate_and_display_keys():
    global p, q, g, x, y
    p, q, g, x, y = generate_keys()
    key_entry.config(state='normal')
    key_entry.delete(1.0, tk.END)
    key_entry.insert(tk.END, f"p={p}\nq={q}\ng={g}\nx={x}\ny={y}")
    key_entry.config(state='disabled')

def sign():
    message = input_text.get()
    if not message:
        messagebox.showwarning("Ошибка", "Введите текст для подписи")
        return
    r, s = sign_message(message, p, q, g, x)
    result_label.config(text="Подпись:")
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"r={r}\ns={s}")
    result_text.config(state='disabled')

def verify():
    message = input_text.get()
    signature = result_text.get(1.0, tk.END).strip()
    if not message or not signature:
        messagebox.showwarning("Ошибка", "Введите текст и подпись для проверки")
        return
    try:
        r, s = map(int, signature.replace("r=", "").replace("s=", "").split("\n"))
        valid = verify_signature(message, r, s, p, q, g, y)
        messagebox.showinfo("Результат", "Подпись верна" if valid else "Подпись неверна")
    except Exception:
        messagebox.showerror("Ошибка", "Неверный формат подписи")

root = tk.Tk()
root.title("DSA Подпись")
root.geometry("400x400")

tk.Label(root, text="Текст для подписи:").pack()
input_text = tk.Entry(root, width=50)
input_text.pack()

tk.Label(root, text="Ключи:").pack()
key_entry = tk.Text(root, width=50, height=5, state='disabled')
key_entry.pack()

tk.Button(root, text="Генерировать ключи", command=generate_and_display_keys).pack()
tk.Button(root, text="Подписать", command=sign).pack()
tk.Button(root, text="Проверить подпись", command=verify).pack()

result_label = tk.Label(root, text="Подпись")
result_label.pack()

result_text = tk.Text(root, width=50, height=3, state='disabled')
result_text.pack()

root.mainloop()
