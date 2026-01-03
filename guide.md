# создаём виртуальное окружение
python3 -m venv .venv

# активируем окружение
source .venv/bin/activate

# создаём файл requirements.txt и устанавливаем зависимости
pip install -r requirements.txt

# создаем main.py в корневой папке

# запускаем сервер
uvicorn main:app --reload --port 5000


