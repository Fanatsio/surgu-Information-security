import tkinter as tk
from tkinter import messagebox
import os

def xor_encrypt_decrypt(text, key):
    return bytes([t ^ key[i % len(key)] for i, t in enumerate(text)])

def generate_key():
    text = entry_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Ошибка", "Введите текст для генерации ключа!")
        return

    key = os.urandom(len(text)).hex()
    entry_key_encrypt.delete(0, tk.END)
    entry_key_encrypt.insert(0, key)

def process_text(encrypting=True):
    text = entry_text.get("1.0", tk.END).strip() if encrypting else entry_result.get("1.0", tk.END).strip()
    key = entry_key_encrypt.get().strip()

    if not text or not key:
        messagebox.showwarning("Ошибка", "Введите текст и ключ!")
        return

    try:
        text_bytes = text.encode() if encrypting else bytes.fromhex(text)
        key_bytes = bytes.fromhex(key)

        result_bytes = xor_encrypt_decrypt(text_bytes, key_bytes)
        result = result_bytes.hex() if encrypting else result_bytes.decode(errors='ignore')

        entry_result.delete("1.0", tk.END)
        entry_result.insert("1.0", result)
    except ValueError:
        messagebox.showerror("Ошибка", "Ключ или входные данные содержат недопустимые символы!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка обработки текста: {e}")

root = tk.Tk()
root.title("XOR Шифрование")
root.geometry("500x400")
root.resizable(False, False)

tk.Label(root, text="Введите текст:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entry_text = tk.Text(root, height=5, width=60)
entry_text.grid(row=1, column=0, columnspan=2, padx=10)

tk.Label(root, text="Ключ (шифрование):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_key_encrypt = tk.Entry(root, width=50)
entry_key_encrypt.grid(row=3, column=0, padx=10)
tk.Button(root, text="Сгенерировать", command=generate_key).grid(row=3, column=1, padx=5)

tk.Button(root, text="Зашифровать", command=lambda: process_text(True)).grid(row=6, column=0, padx=10, pady=5)
tk.Button(root, text="Расшифровать", command=lambda: process_text(False)).grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="Результат:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
entry_result = tk.Text(root, height=5, width=60)
entry_result.grid(row=8, column=0, columnspan=2, padx=10)

root.mainloop()
