import tkinter as tk
from tkinter import messagebox

RUSSIAN_ALPHABET_SIZE = 32
ASCII_PRINTABLE_SIZE = 95
RUSSIAN_UPPER_START = ord('А')
RUSSIAN_LOWER_START = ord('а')
ASCII_PRINTABLE_START = 32
ASCII_PRINTABLE_END = 126

def shift_char(char, shift):
    if 'А' <= char <= 'Я':
        start = RUSSIAN_UPPER_START
        return chr(start + (ord(char) - start + shift) % RUSSIAN_ALPHABET_SIZE)
    elif 'а' <= char <= 'я':
        start = RUSSIAN_LOWER_START
        return chr(start + (ord(char) - start + shift) % RUSSIAN_ALPHABET_SIZE)
    elif ASCII_PRINTABLE_START <= ord(char) <= ASCII_PRINTABLE_END:
        new_char_code = ASCII_PRINTABLE_START + (ord(char) - ASCII_PRINTABLE_START + shift) % ASCII_PRINTABLE_SIZE
        return chr(new_char_code)
    return char

def caesar_cipher(text, shift):
    return ''.join(shift_char(char, shift) for char in text)

def process_text(encrypting=True):
    try:
        text = entry_text.get("1.0", tk.END).strip()
        shift = int(entry_shift.get())
        if not text:
            messagebox.showwarning("Предупреждение", "Поле текста не должно быть пустым!")
            return
        if not encrypting:
            text = entry_result.get("1.0", tk.END).strip()
            shift = -shift
        entry_result.delete("1.0", tk.END)
        entry_result.insert("1.0", caesar_cipher(text, shift))
    except ValueError:
        messagebox.showerror("Ошибка", "Сдвиг должен быть целым числом!")

root = tk.Tk()
root.title("Шифр Цезаря")
root.geometry("400x300")
root.resizable(False, False)

label_text = tk.Label(root, text="Введите текст:")
label_text.pack()
entry_text = tk.Text(root, height=5, width=50)
entry_text.pack()

label_shift = tk.Label(root, text="Введите сдвиг:")
label_shift.pack()
entry_shift = tk.Entry(root)
entry_shift.pack()

frame_buttons = tk.Frame(root)
frame_buttons.pack()

button_encrypt = tk.Button(frame_buttons, text="Зашифровать", command=lambda: process_text(True))
button_encrypt.pack(side=tk.LEFT, padx=5)

button_decrypt = tk.Button(frame_buttons, text="Расшифровать", command=lambda: process_text(False))
button_decrypt.pack(side=tk.RIGHT, padx=5)

label_result = tk.Label(root, text="Результат:")
label_result.pack()
entry_result = tk.Text(root, height=5, width=50)
entry_result.pack()

root.mainloop()