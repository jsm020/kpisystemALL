import pandas as pd
from django.core.management.base import BaseCommand
from mainSystem.models import CustomUser  # O'zingizning app nomingizni yozing

class Command(BaseCommand):
    help = 'Excel fayldagi ma\'lumotlarni CustomUser modeliga yuklash'

    def handle(self, *args, **kwargs):
        # Excel fayl yo'lini kiriting
        excel_file = './baza.xlsx'

        # Excelni o'qish
        try:
            data = pd.read_excel(excel_file)
        except Exception as e:
            self.stderr.write(f"Xatolik: {str(e)}")
            return

        # Har bir qatorni CustomUser modeliga qo‘shish
        for index, row in data.iterrows():
            try:
                user = CustomUser.objects.create_user(
                    username=row['username'],
                    password=row['password'],  # Excel fayldan parolni olish
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    kafedra=row['kafedra'],
                    ish_soati=row['ish_soati'],
                    ish_unvoni=row['ish_unvoni'],
                    is_active=row['is_active'],
                    is_staff=row['is_staff'],
                )

                self.stdout.write(f"Foydalanuvchi qo'shildi: {user.username}")
            except Exception as e:
                self.stderr.write(f"Xatolik ({row['username']}): {str(e)}")
