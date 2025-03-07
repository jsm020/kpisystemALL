# helpers.py
from django.shortcuts import get_object_or_404

def check_and_delete_item(model, pk, user):
    """
    Element egasi va baholanganligini tekshiradi va kerakli javobni qaytaradi.

    :param model: Model sinfi (masalan, FanVideoKontent)
    :param pk: Elementning asosiy kaliti
    :param user: Hozirgi foydalanuvchi (request.user)
    :return: (status, message, item) tuple. Agar muvaffaqiyatli bo'lsa, item qaytariladi.
    """
    item = get_object_or_404(model, pk=pk)

    # Tekshiruv: Foydalanuvchi faqat o‘z ma‘lumotini o‘chirishi mumkin
    if item.user != user:
        print(item.user,user)
        return False, "Siz faqat o'zingizga tegishli ma'lumotni o'chira olasiz.", None

    # Tekshiruv: Baholangan elementni o‘chirib bo‘lmaydi
    if item.score:
        return False, "Bu elementni o'chirishga ruxsat yo'q. Chunki u baholangan.", None

    # Muvaffaqiyat
    item.delete()
    return True, "Element muvaffaqiyatli o'chirildi.", item
