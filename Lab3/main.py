import random
import tkinter as tk
from tkinter import messagebox

KEY_SIZE = 16  # Размер ключа в байтах (16 байт = 128 бит)
BLOCK_SIZE = 16  # Размер блока данных в байтах (16 байт = 128 бит)
NUM_ROUNDS = 16  # Количество раундов шифрования (стандарт для SEED)

# Таблица замены (S-Box) для преобразования байтов
S_BOX = [
    0xa9, 0x67, 0xb3, 0xe8, 0x04, 0xfd, 0xa3, 0x76, 0x2c, 0xf2, 0xb0, 0x6b, 0xd1, 0x45, 0x8f, 0xc9,
    0x53, 0x6a, 0xb4, 0x69, 0xe4, 0x7c, 0x86, 0x8d, 0xe7, 0xf3, 0x1e, 0xad, 0x8a, 0x8f, 0x32, 0x8c,
    0x43, 0x0c, 0x92, 0x93, 0x68, 0x1d, 0x3f, 0x13, 0x06, 0x2a, 0xa2, 0xc7, 0xc4, 0x2f, 0xfd, 0x91,
    0xb0, 0x51, 0x2c, 0x19, 0x37, 0x87, 0xf4, 0xa8, 0xd0, 0x93, 0x25, 0xa0, 0x30, 0x1a, 0xa1, 0x1c,
    0x52, 0xbc, 0x8b, 0x41, 0x26, 0xf7, 0x5e, 0x56, 0xf8, 0x35, 0xa7, 0x07, 0x0a, 0xa4, 0x81, 0x51,
    0xc6, 0x9b, 0xd7, 0x3b, 0xbf, 0x84, 0x6c, 0x8e, 0xf0, 0x9a, 0xe3, 0x97, 0x52, 0x14, 0xed, 0x0d,
    0x4c, 0x49, 0x3a, 0x61, 0xc5, 0x9d, 0xc2, 0xac, 0xa5, 0x27, 0x09, 0xc1, 0x89, 0x4e, 0x3d, 0xcd,
    0x08, 0xe2, 0x5a, 0x5f, 0xf9, 0xbe, 0xa6, 0x9c, 0x17, 0x6e, 0x42, 0xd8, 0x11, 0x33, 0xa9, 0xde,
    0xc8, 0x10, 0xfb, 0xff, 0xb2, 0x2d, 0xea, 0x48, 0x1f, 0xd4, 0xc3, 0x6d, 0x71, 0xe0, 0xe1, 0x63,
    0x96, 0x62, 0x7e, 0xd5, 0x21, 0x22, 0xe9, 0xce, 0x8d, 0x6f, 0x60, 0x47, 0xc0, 0xb6, 0xf1, 0x72,
    0xcc, 0x79, 0x83, 0xdb, 0x9e, 0xee, 0x4f, 0xab, 0xa8, 0x7b, 0xb8, 0x9f, 0x0b, 0xd3, 0x28, 0xaf,
    0x75, 0xb7, 0x3e, 0xf5, 0x20, 0x5b, 0x31, 0x50, 0x2b, 0x85, 0xdc, 0x94, 0x7f, 0xf6, 0x77, 0x83,
    0xd6, 0x1b, 0x4b, 0x40, 0xba, 0x3c, 0x98, 0xc9, 0x4a, 0x66, 0xfd, 0x5d, 0x2e, 0x6a, 0x78, 0x15,
    0xda, 0x16, 0x5c, 0xbb, 0x4d, 0xb9, 0x55, 0x70, 0x29, 0x39, 0x46, 0x38, 0x74, 0xb5, 0x58, 0xcf,
    0x82, 0x99, 0x36, 0x00, 0x59, 0xd2, 0x44, 0x57, 0xcb, 0x90, 0x2f, 0x1e, 0x95, 0xbd, 0x23, 0x9b,
    0xe6, 0x88, 0xfa, 0xf3, 0x24, 0x3f, 0xd9, 0xca, 0xdf, 0xaa, 0xe5, 0x5f, 0x12, 0xfe, 0xa2, 0x18
]

def generate_key():
    """Генерирует случайный ключ из 16 случайных байтов (каждый от 0 до 255)"""
    key = bytes(random.randint(0, 255) for _ in range(KEY_SIZE))
    entry_key.delete(0, tk.END)
    entry_key.insert(0, key.hex().upper())

def sbox_transform(value):
    """Преобразование байта через таблицу S-Box.
    Берём значение по индексу value % (размер S_BOX), чтобы избежать выхода за пределы"""
    return S_BOX[value % len(S_BOX)]

def feistel_function(data, key):
    """Функция Фейстеля — основа шифрования SEED."""
    # Делим блок данных (16 байт) на две половины: левая (left) и правая (right), по 8 байт
    left, right = data[:BLOCK_SIZE // 2], data[BLOCK_SIZE // 2:]
    # Преобразуем правую часть: каждый байт XOR’им с байтом ключа и пропускаем через S-Box
    result = bytes(sbox_transform(b ^ k) for b, k in zip(right, key))
    # Новая правая часть становится старой правой, новая левая — XOR старой левой и результата
    return right, bytes(l ^ r for l, r in zip(left, result))

def key_schedule(key):
    """Генерирует 16 ключей для каждого раунда шифрования."""
    # Преобразуем ключ в байты
    key_bytes = bytes.fromhex(key)
    # Создаём список из 16 ключей путём циклического сдвига байтов исходного ключа
    # Например, для i=1: берём байты с 1 до конца + с начала до 1
    return [key_bytes[i:] + key_bytes[:i] for i in range(NUM_ROUNDS)]

def seed_encrypt_block(block, key):
    """Шифрует один блок данных (16 байт) с использованием SEED."""
    # Делим блок на две половины: левая и правая, по 8 байт
    left, right = block[:BLOCK_SIZE // 2], block[BLOCK_SIZE // 2:]
    # Проходим 16 раундов шифрования
    for round_key in key_schedule(key):
        # Применяем функцию Фейстеля, обновляя left и right
        left, right = feistel_function(left + right, round_key)
    # После всех раундов объединяем половины в зашифрованный блок
    return left + right

def seed_decrypt_block(block, key):
    """Расшифровывает один блок данных (16 байт) с использованием SEED."""
    # Делим блок на две половины: левая и правая, по 8 байт
    left, right = block[:BLOCK_SIZE // 2], block[BLOCK_SIZE // 2:]
    # Проходим 16 раундов в обратном порядке (реверс ключей)
    for round_key in reversed(key_schedule(key)):
        # Применяем функцию Фейстеля, но меняем местами right и left для обратного процесса
        right, left = feistel_function(right + left, round_key)
    # После всех раундов объединяем половины в расшифрованный блок
    return left + right

def pad(text):
    """Добавляет дополнение к тексту, чтобы длина стала кратна 16 байтам."""
    # Вычисляем, сколько байтов нужно добавить
    padding_len = BLOCK_SIZE - len(text) % BLOCK_SIZE
    # Добавляем байты, каждый равен длине дополнения (например, для 5 байтов — 5 пятёрок)
    return text + bytes([padding_len] * padding_len)

def unpad(text):
    """Удаляет дополнение из текста."""
    # Последний байт текста указывает длину дополнения; убираем столько байтов с конца
    return text[:-text[-1]]

def process_text(encrypting=True):
    key = entry_key.get().strip()
    
    try:
        if encrypting:
            text = entry_text.get("1.0", tk.END).strip().encode()
            # Добавляем дополнение, делим на блоки по 16 байт и шифруем каждый
            encrypted_blocks = [
                seed_encrypt_block(pad(text)[i:i + BLOCK_SIZE], key)
                for i in range(0, len(pad(text)), BLOCK_SIZE)
            ]
            # Объединяем зашифрованные блоки и преобразуем в HEX-строку
            result_text = b"".join(encrypted_blocks).hex()
        else:
            text = bytes.fromhex(entry_result.get("1.0", tk.END).strip())
            # Делим на блоки по 16 байт и расшифровываем каждый
            decrypted_blocks = [
                seed_decrypt_block(text[i:i + BLOCK_SIZE], key)
                for i in range(0, len(text), BLOCK_SIZE)
            ]
            # Объединяем блоки, убираем дополнение и декодируем в строку
            result_text = unpad(b"".join(decrypted_blocks)).decode()
    except Exception:
        messagebox.showerror("Ошибка", "Неверный ввод для расшифровки!")
        return

    entry_result.delete("1.0", tk.END)
    entry_result.insert("1.0", result_text)

def create_label(parent, text, row, column):
    tk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=10, pady=5)

def create_text_widget(parent, height, width, row, columnspan):
    widget = tk.Text(parent, height=height, width=width)
    widget.grid(row=row, column=0, columnspan=columnspan, padx=10)
    return widget

def create_button(parent, text, command, row, column, columnspan=1):
    tk.Button(parent, text=text, command=command).grid(row=row, column=column, columnspan=columnspan, padx=10, pady=5)

root = tk.Tk()
root.title("Шифр SEED")
root.resizable(False, False)

create_label(root, "Введите текст:", 0, 0)
entry_text = create_text_widget(root, 4, 50, 1, 2)

create_label(root, "Сгенерированный ключ:", 2, 0)

entry_key = tk.Entry(root, width=35)
entry_key.grid(row=2, column=1, padx=10)

create_button(root, "Сгенерировать ключ", generate_key, 2, 2)
create_button(root, "Зашифровать", lambda: process_text(True), 3, 0)
create_button(root, "Расшифровать", lambda: process_text(False), 3, 1)

create_label(root, "Результат:", 4, 0)
entry_result = create_text_widget(root, 4, 50, 5, 2)

generate_key()

root.update_idletasks()
root.geometry(f"{root.winfo_reqwidth() + 20}x{root.winfo_reqheight() + 20}")

root.mainloop()
