import tkinter as tk
from tkinter import messagebox
import random

def generate_key():
    return random.randint(0, 0xFFFFFFFFFFFFFFFF)

def seed_encrypt(plain_text, key):
    cipher_text = ""
    for char in plain_text:
        cipher_char = chr(ord(char) ^ (key & 0xFF))
        cipher_text += cipher_char
        key = (key >> 8) | ((key & 0xFF) << 56)
    return cipher_text

def seed_decrypt(cipher_text, key):
    return seed_encrypt(cipher_text, key)  # Симметричный процесс

def encrypt():
    text = input_text.get()
    if not text:
        messagebox.showwarning("Ошибка", "Введите текст для шифрования")
        return
    key = generate_key()
    key_entry.delete(0, tk.END)
    key_entry.insert(0, str(key))
    result = seed_encrypt(text, key)
    result_label.config(text="Результат шифровки:")
    result_text.delete(0, tk.END)
    result_text.insert(0, result)

def decrypt():
    text = result_text.get()
    key = key_entry.get()
    if not text or not key:
        messagebox.showwarning("Ошибка", "Введите зашифрованный текст и ключ")
        return
    try:
        key = int(key)
        decrypted = seed_decrypt(text, key)
        result_label.config(text="Результат расшифровки:")
        result_text.delete(0, tk.END)
        result_text.insert(0, decrypted)
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат ключа")

# Создание графического интерфейса
root = tk.Tk()
root.title("SEED Шифрование")

tk.Label(root, text="Текст для шифрования").pack()
input_text = tk.Entry(root, width=50)
input_text.pack()

tk.Label(root, text="Ключ").pack()
key_entry = tk.Entry(root, width=50)
key_entry.pack()

tk.Button(root, text="Шифровать", command=encrypt).pack()
tk.Button(root, text="Расшифровать", command=decrypt).pack()

result_label = tk.Label(root, text="Результат")
result_label.pack()

result_text = tk.Entry(root, width=50)
result_text.pack()

root.mainloop()
