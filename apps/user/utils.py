from .models import PhoneConfirmation

def send_confirmation_code(phone_number):
    code = PhoneConfirmation.generate_code()
    PhoneConfirmation.objects.update_or_create(phone_number=phone_number, defaults={"code": code})
    # 🧠 Здесь ты подключишь реальный SMS API (Beeline, PlayMobile, Eskiz, etc)
    print(f"📲 Код подтверждения для {phone_number}: {code}")  # пока просто в консоль
