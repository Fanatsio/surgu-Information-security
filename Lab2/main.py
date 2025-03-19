import tkinter as tk
from tkinter import messagebox
import os

def xor_encrypt_decrypt(text: bytes, key: bytes) -> bytes:
    return bytes(t ^ key[i % len(key)] for i, t in enumerate(text))

def generate_key():
    text = entry_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Ошибка", "Введите текст для генерации ключа!")
        return
    key = os.urandom(len(text)).hex()
    entry_key_encrypt.delete(0, tk.END)
    entry_key_encrypt.insert(0, key)

def process_text(encrypting: bool):
    source_widget = entry_text if encrypting else entry_result
    text = source_widget.get("1.0", tk.END).strip()
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

def create_label(parent, text, row, column, **kwargs):
    tk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=10, pady=5, **kwargs)

def create_button(parent, text, command, row, column, **kwargs):
    return tk.Button(parent, text=text, command=command).grid(row=row, column=column, padx=10, pady=5, **kwargs)

# Настройки основного окна
root = tk.Tk()
root.title("XOR Шифрование")
root.geometry("700x600")
root.resizable(False, False)

# Ввод текста
create_label(root, "Введите текст:", 0, 0)
entry_text = tk.Text(root, height=5, width=60)
entry_text.grid(row=1, column=0, columnspan=2, padx=10)

# Ключ
create_label(root, "Ключ (шифрование):", 2, 0)
entry_key_encrypt = tk.Entry(root, width=50)
entry_key_encrypt.grid(row=3, column=0, padx=10)
create_button(root, "Сгенерировать", generate_key, 3, 1)

# Кнопки обработки
create_button(root, "Зашифровать", lambda: process_text(True), 6, 0)
create_button(root, "Расшифровать", lambda: process_text(False), 6, 1)

# Вывод результата
create_label(root, "Результат:", 7, 0)
entry_result = tk.Text(root, height=5, width=60)
entry_result.grid(row=8, column=0, columnspan=2, padx=10)

root.mainloop()
