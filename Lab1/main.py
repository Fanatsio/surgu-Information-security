import tkinter as tk
from tkinter import messagebox

RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUSSIAN_ALPHABET_SIZE = len(RUSSIAN_ALPHABET)
ASCII_PRINTABLE_SIZE = 95
ASCII_PRINTABLE_START = 32
ASCII_PRINTABLE_END = 126

RUS_UPPER = {c: i for i, c in enumerate(RUSSIAN_ALPHABET)}
RUS_LOWER = {c.lower(): i for i, c in enumerate(RUSSIAN_ALPHABET)}

def shift_char(char, shift):
    if char in RUS_UPPER:
        new_index = (RUS_UPPER[char] + shift) % RUSSIAN_ALPHABET_SIZE
        return RUSSIAN_ALPHABET[new_index]
    elif char in RUS_LOWER:
        new_index = (RUS_LOWER[char] + shift) % RUSSIAN_ALPHABET_SIZE
        return RUSSIAN_ALPHABET[new_index].lower()
    elif ASCII_PRINTABLE_START <= ord(char) <= ASCII_PRINTABLE_END:
        return chr(ASCII_PRINTABLE_START + (ord(char) - ASCII_PRINTABLE_START + shift) % ASCII_PRINTABLE_SIZE)
    return char

def caesar_cipher(text, shift):
    return ''.join(shift_char(char, shift) for char in text)

def process_text(encrypting=True):
    text = entry_text.get("1.0", tk.END).strip()
    shift_input = entry_shift.get().strip()

    if not text:
        messagebox.showwarning("Предупреждение", "Поле текста не должно быть пустым!")
        return
    if not shift_input.isdigit() and not (shift_input.startswith('-') and shift_input[1:].isdigit()):
        messagebox.showerror("Ошибка", "Сдвиг должен быть целым числом!")
        return

    shift = int(shift_input)
    if not encrypting:
        text = entry_result.get("1.0", tk.END).strip()
        shift = -shift

    result_text = caesar_cipher(text, shift)
    entry_result.delete("1.0", tk.END)
    entry_result.insert("1.0", result_text)

root = tk.Tk()
root.title("Шифр Цезаря")
root.geometry("400x300")
root.resizable(False, False)

tk.Label(root, text="Введите текст:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entry_text = tk.Text(root, height=4, width=50)
entry_text.grid(row=1, column=0, columnspan=2, padx=10)

tk.Label(root, text="Введите сдвиг:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_shift = tk.Entry(root)
entry_shift.grid(row=2, column=1, padx=10)

tk.Button(root, text="Зашифровать", command=lambda: process_text(True)).grid(row=3, column=0, padx=10, pady=5)
tk.Button(root, text="Расшифровать", command=lambda: process_text(False)).grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Результат:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_result = tk.Text(root, height=4, width=50)
entry_result.grid(row=5, column=0, columnspan=2, padx=10)

root.mainloop()
