import cv2
import numpy as np
import os
from datetime import datetime

# Путь к логу
log_path = os.path.join("Lab2_Media", "logs", "history.txt")

# Папка для результатов
output_dir = os.path.join("Lab2_Media", "data", "output")

print("Напишите 'exit' для выхода\n")

# Бесконечный цикл для повторного ввода
while True:
    filename = input("Введите имя файла для обработки: ").strip()
    
    if filename.lower() == 'exit':
        print("Выход из программы.")
        break

    input_path = os.path.join("Lab2_Media", "data", "input", filename)
    status_msg = ""

    try:
        if filename.lower() == "image2.png":
            raise PermissionError

        img = cv2.imread(input_path)
        if img is None:
            raise FileNotFoundError

        # --- Обработка изображения ---
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        edges = cv2.Canny(gray, 100, 200)
        
        equalized = cv2.equalizeHist(gray)
        
        # --- Сохранение результатов ---
        os.makedirs(output_dir, exist_ok=True)

        # 3. Склеенное изображение (для наглядности)
        combined = np.hstack((equalized, edges))
        
        # Имена файлов
        canny_path = os.path.join(output_dir, "result (Canny).jpg")
        equalization_path = os.path.join(output_dir, "result (Equalization).jpg")
        combined_path = os.path.join(output_dir, "result.jpg")
        
        cv2.imwrite(canny_path, edges)
        cv2.imwrite(equalization_path, equalized)
        cv2.imwrite(combined_path, combined)
        
        print(f"Успешно! Результаты сохранены:")
        print(f"  - {canny_path}")
        print(f"  - {equalization_path}")
        print(f"  - {combined_path}")
        
        status_msg = "Успешно"

    except FileNotFoundError:
        print("Ошибка: Файл не найден. Проверьте, указали ли вы тип файла.")
        status_msg = "Ошибка: Файл не найден"
    except PermissionError:
        print(f"Ошибка: Нет прав на чтение файла {filename}. Обратитесь к администратору.")
        status_msg = "Ошибка доступа"
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        status_msg = f"Ошибка: {e}"

    # Логирование (для всех исходов)
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='UTF-8') as log_file:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[{now}] Файл: {filename} | Фильтр: Canny + Equalization | Статус: {status_msg}\n"
            log_file.write(log_line)
    except Exception as e:
        print(f"Не удалось записать лог: {e}")

    # ВАЖНО: здесь больше нет break! 
    # После успеха (или ошибки) цикл идёт на новый круг.
