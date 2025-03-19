import platform
import math

def left_rotate(value, shift):
    """Левый циклический сдвиг 32-битного числа."""
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

def md5(message):
    S = [
        [7, 12, 17, 22],
        [5, 9, 14, 20],
        [4, 11, 16, 23],
        [6, 10, 15, 21]
    ]
    T = [int(2**32 * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]
    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    
    # Дополнение сообщения
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'
    message += b'\x00' * ((56 - (original_byte_len + 1) % 64) % 64)
    message += original_bit_len.to_bytes(8, byteorder='little')

    # Обработка блоков
    for chunk_start in range(0, len(message), 64):
        chunk = message[chunk_start:chunk_start + 64]
        X = [int.from_bytes(chunk[j:j + 4], byteorder='little') for j in range(0, 64, 4)]

        a, b, c, d = A, B, C, D

        for i in range(64):
            if i < 16:
                F = (b & c) | ((~b) & d)
                g = i
            elif i < 32:
                F = (d & b) | ((~d) & c)
                g = (5 * i + 1) % 16
            elif i < 48:
                F = b ^ c ^ d
                g = (3 * i + 5) % 16
            else:
                F = c ^ (b | (~d))
                g = (7 * i) % 16

            F = (F + a + X[g] + T[i]) & 0xFFFFFFFF
            shift = S[i // 16][i % 4]  # Используем двумерный массив
            a, d, c, b = d, c, b, (b + left_rotate(F, shift)) & 0xFFFFFFFF

        A = (A + a) & 0xFFFFFFFF
        B = (B + b) & 0xFFFFFFFF
        C = (C + c) & 0xFFFFFFFF
        D = (D + d) & 0xFFFFFFFF

    return (A.to_bytes(4, byteorder='little') +
            B.to_bytes(4, byteorder='little') +
            C.to_bytes(4, byteorder='little') +
            D.to_bytes(4, byteorder='little')).hex()

def get_hardware_info():
    system_info = platform.system() + platform.node()
    return system_info

def check_license():
    current_hardware_info = get_hardware_info()
    current_hash = md5(current_hardware_info.encode('utf-8'))

    try:
        with open('license.txt', 'r') as file:
            saved_hash = file.read().strip()
    except FileNotFoundError:
        with open('license.txt', 'w') as file:
            file.write(current_hash)
        print("Программа успешно установлена на этом компьютере.")
        return

    if current_hash == saved_hash:
        print("Программа запущена легально.")
    else:
        print("Обнаружено нелегальное использование программы!")

check_license()
