import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email2FAService:
    @staticmethod
    def generate_numeric_code(length: int = 6) -> str:
        """Генерує випадковий 6-значний код (наприклад, '583921')"""
        # Використовуємо secrets для безпечної генерації криптографічних чисел
        return "".join(secrets.choice("0123456789") for _ in range(length))

    @staticmethod
    def send_code_to_email(user_email: str, code: str):
        """Відправляє згенерований код на пошту користувача"""
        
        # НАЛАШТУВАННЯ ПОШТОВОГО СЕРВЕРУ (на прикладі Gmail)
        # Для тестів краще використовувати тимчасові пошти або SMTP-заглушки (Mailtrap)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your_project_email@gmail.com"      # Пошта вашого проєкту
        sender_password = "your_app_password"               # Спеціальний пароль додатка від Google
        
        # Створення листа
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = user_email
        message["Subject"] = "Ваш код підтвердження входу (ProgectLibrary)"
        
        # Текст листа
        body = f"Привіт! Ваш одноразовий код для входу в систему: {code}\nКод дійсний протягом 5 хвилин."
        message.attach(MIMEText(body, "plain", "utf-8"))
        
        try:
            # Підключаємося до поштового серверу
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls() # Шифрування
            server.login(sender_email, sender_password)
            
            # Відправляємо
            server.sendmail(sender_email, user_email, message.as_string())
            server.quit()
            print(f"Код {code} успішно відправлено на {user_email}")
            return True
        except Exception as e:
            print(f"Помилка відправки пошти: {e}")
            return False