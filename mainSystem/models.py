from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field is required")
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    kafedra = models.CharField(max_length=100, verbose_name='Kafedra')
    ish_soati = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        verbose_name='ish stavka', 
        default="2.0"
    )    
    ish_unvoni = models.CharField(max_length=50, verbose_name='ilmiy darajasi')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"
    class Meta:
        verbose_name = "Ustozlar"
        verbose_name_plural = "Ustozlar"


class MaxScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    score_for = GenericForeignKey('content_type', 'object_id')
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(0.0)]
    )

    def __str__(self):
        return f"Max Score: {self.max_score} for {self.user} on {self.content_type}"

    def clean(self):
        if self.max_score < 0:
            raise ValidationError("Max score cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    


class FaolInterfaolMetodlar(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 4.0
        decimal_places=1,
        validators=[MaxValueValidator(4.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
        MaxScore,
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='faol_interfaol_metodlar'
    )
    izoh = models.TextField(blank=True, null=True)  # Optional field

    class Meta:
        verbose_name = "Pedagogik mahorat"
        verbose_name_plural = "Pedagogik mahorat"
        permissions = [
            ('can_evaluate_FaolInterfaolMetodlar', 'Can evaluate FaolInterfaolMetodlar'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Pedagogik mahorat"

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range for this model (0.0 to 4.0)
            if self.score < 0 or self.score > 4.0:
                raise ValidationError("Baholash 0.0 va 4.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = FaolInterfaolMetodlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class MustaqilTalimTopshiriqlari(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 4.0
        decimal_places=1,
        validators=[MaxValueValidator(4.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
        MaxScore,
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='mustaqil_talim_topshiriqlari'
    )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Mustaqil ta'lim topshiriqlar"
        verbose_name_plural = "Mustaqil ta'lim topshiriqlar"
        permissions = [
            ('can_evaluate_MustaqilTalimTopshiriqlari', 'Can evaluate MustaqilTalimTopshiriqlari'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Mustaqil ta'lim topshiriqlar"

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range for this model (0.0 to 4.0)
            if self.score < 0 or self.score > 4.0:
                raise ValidationError("Baholash 0.0 va 4.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = MustaqilTalimTopshiriqlari.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class FanVideoKontent(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,
        decimal_places=1,
        validators=[MaxValueValidator(8.00), MinValueValidator(0.0)]
    )
    link = models.URLField(verbose_name="Maqolaga havola")
    izoh = models.TextField(blank=True, null=True)
    max_score_value = models.ForeignKey(
        MaxScore,
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='fan_video_kontents'
    )

    class Meta:
        verbose_name = "Video kontent"
        verbose_name_plural = "Video kontent"
        permissions = [
            ('can_evaluate_FanVideoKontent', 'Can evaluate FanVideoKontent'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Video kontent"

    def clean(self):
        if self.score is not None:  # self.score None emasligiga tekshirish
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 8.0:
                raise ValidationError("Baholash 0.0 va 8.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = FanVideoKontent.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class NashrEtilganDarsliklar(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    maqola = models.FileField(
        upload_to='nashr_etilgan_darsliklar_files/',
        verbose_name="Nashr etilgan darsliklar, qo'llanmalar va uslubiy ko'rsatmalar"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 6.0
        decimal_places=1,
        validators=[MaxValueValidator(6.0), MinValueValidator(0.0)]
    )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed
    max_score_value = models.ForeignKey(
        MaxScore,
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='nashr_etilgan_darsliklar'
    )

    class Meta:
        verbose_name = "Darsliklar (6 ball), o‘quv qo‘llanmalar (5 ball),  uslubiy qo‘llanma (4 ball)"
        verbose_name_plural = "Darsliklar (6 ball), o‘quv qo‘llanmalar (5 ball),  uslubiy qo‘llanma (4 ball)"
        permissions = [
            ('can_evaluate_NashrEtilganDarsliklar', 'Can evaluate NashrEtilganDarsliklar'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Darsliklar (6 ball), o‘quv qo‘llanmalar (5 ball),  uslubiy qo‘llanma (4 ball)"

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 6.0:
                raise ValidationError("Baholash 0.0 va 6.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = NashrEtilganDarsliklar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class OquvYiliFanlar(models.Model): #+
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=2,
        decimal_places=1,
        validators=[MaxValueValidator(2.00), MinValueValidator(0.0)]
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    izoh = models.TextField(blank=True, null=True)  # Optional field
    max_score_value = models.ForeignKey(
        MaxScore,
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='oquv_yili_fanlar'
    )

    class Meta:
        verbose_name = "Resurslarni HEMIS ga kiritilishi"
        verbose_name_plural = "Resurslarni HEMIS ga kiritilishi"
        permissions = [
            ('can_evaluate_OquvYiliFanlar', 'Can evaluate OquvYiliFanlar'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Resurslarni HEMIS ga kiritilishi"

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 2.0:
                raise ValidationError("Baholash 0.0 va 2.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = OquvYiliFanlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class OqitishSifati(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    talim_sifat_xulosasi = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Ta'lim sifatini nazorat qilish bo‘limi xulosasi bo‘yicha",
        max_digits=2,
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    talim_sifat = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Talabalardan o‘tkazilgan so‘rovnomalar natijalari bo‘yicha",
        max_digits=2,
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Umumiy ball",
        editable=False,
        max_digits=3,  # 6.0 kabi qiymatlar uchun yetarli raqamlar o'rnatildi
        decimal_places=1,
        validators=[MaxValueValidator(6.0), MinValueValidator(0.0)]
    )
    izoh = models.TextField(blank=True, null=True)
    max_score_value = models.ForeignKey(
        'MaxScore',
        on_delete=models.CASCADE,
        verbose_name="Max Score Value",
        related_name='oqitish_sifati'
    )

    class Meta:
        verbose_name = "O‘qitish sifati darajasi (ta'lim sifati– 3 ball, talabalar so‘rovnomalari – 3 ball) – maksimal 6 ball"
        verbose_name_plural = "O‘qitish sifati darajasi (ta'lim sifati– 3 ball, talabalar so‘rovnomalari – 3 ball) – maksimal 6 ball"
        permissions = [
            ('can_evaluate_OqitishSifati', 'Can evaluate OqitishSifati'),
        ]

    def clean(self):
        # Ensure talim_sifat and talim_sifat_xulosasi are valid before calculating score
        if self.talim_sifat is not None and self.talim_sifat_xulosasi is not None:
            total_score = self.talim_sifat + self.talim_sifat_xulosasi
            if total_score > 6.0:
                raise ValidationError("Umumiy ball 6.0 dan yuqori bo'lishi mumkin emas.")
            self.score = total_score  # Umumiy ballni avtomatik hisoblash

        # Validate that the score does not exceed the user's available max_score
        if self.score is not None and self.max_score_value:
            if self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Calculate score as the sum of talim_sifat and talim_sifat_xulosasi
        if self.talim_sifat is not None and self.talim_sifat_xulosasi is not None:
            self.score = self.talim_sifat + self.talim_sifat_xulosasi
        else:
            self.score = None  # Handle case where either value is None

        # Call the clean method for validation
        self.clean()

        # Adjust the max_score_value if the score changes
        if self.score is not None:
            # Retrieve the previous score if it exists
            if self.pk:
                previous_instance = OqitishSifati.objects.get(pk=self.pk)
                previous_score = previous_instance.score
            else:
                previous_score = None

            # If previous score exists, restore max_score_value before updating
            if previous_score is not None and self.max_score_value:
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            if self.max_score_value:
                self.max_score_value.max_score -= self.score

                # Ensure that max_score_value is not negative
                if self.max_score_value.max_score < 0:
                    raise ValidationError(
                        "Max score value cannot be negative. Adjust the score accordingly."
                    )

                # Save the updated MaxScore instance
                self.max_score_value.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - O'qitish sifati baholanishi"
    
########################################################
class ScopusWebOfScience(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")  # Foydalanuvchiga bog'langan
    maqola = models.FileField(
        upload_to='scopus_web_of_science_files/',
        verbose_name="Scopus va Web of Science xalqaro jurnallarida maqola chop etganligi",
        null=True,
        blank=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",null=True,blank=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=4,  # Adjusted to accommodate values like 15.0
        decimal_places=1,
        validators=[MaxValueValidator(15.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='scopus_web_science'
        )
    izoh = models.TextField(blank=True, null=True) 
    class Meta:
        verbose_name = "“Scopus” va “Web of Science”"
        verbose_name_plural = "“Scopus” va “Web of Science”"
        permissions = [
            ('can_evaluate_ScopusWebOfScience', 'Can evaluate ScopusWebOfScience'),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Scopus/Web of Science maqola"

    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
    
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 15.0:
                raise ValidationError("Baholash 0.0 va 15.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = ScopusWebOfScience.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)
    
class OAKJurnaliMaqola(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='oak_jurnal_maqolalar_files/',
        verbose_name="OAK tasarrufidagi jurnalda maqola chop etganligi",
        null=True,
        blank=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",null=True,blank=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 5.0
        decimal_places=1,
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='oak_jurnali_maqolalar'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "OAK jurnal"
        verbose_name_plural = "OAK jurnal"
        permissions = [
            ('can_evaluate_OAKJurnaliMaqola', 'Can evaluate OAKJurnaliMaqola'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -OAK jurnali"
        
    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 5.0:
                raise ValidationError("Baholash 0.0 va 5.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = OAKJurnaliMaqola.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class HIndex(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='h_indeks_files/',
        verbose_name="Scopus, Web of Science va Google Scholar h-indeksiga egaligi",
        null=True,
        blank=True
    )
    link = models.URLField(verbose_name="H-indeks hujjatiga havola",null=True,blank=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 5.0
        decimal_places=1,
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='h_indexsi'
        )
    izoh = models.TextField(blank=True, null=True) 
    class Meta:
        verbose_name = "h-indeks"
        verbose_name_plural = "h-indeks"
        permissions = [
            ('can_evaluate_HIndex', 'Can evaluate HIndex'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Scopus jurnali"

    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 5.0:
                raise ValidationError("Baholash 0.0 va 5.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = HIndex.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)


class KonferensiyaMaqola(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='konferensiya_maqolalari_files/',
        verbose_name="Xalqaro va Respublika konferensiyalaridagi ma'ruza",
        null=True,
        blank=True,
    )
    link = models.URLField(verbose_name="Ma'ruzaga havola",null=True,blank=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 2.0
        decimal_places=1,
        validators=[MaxValueValidator(2.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='konferensiya_maqola'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Konferensiya"
        verbose_name_plural = "Konferensiya"
        permissions = [
            ('can_evaluate_KonferensiyaMaqola', 'Can evaluate KonferensiyaMaqola'),
        ]
        
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Xalqaro konferensiya"
    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 2.0:
                raise ValidationError("Baholash 0.0 va 2.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = KonferensiyaMaqola.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)


class LoyihalarTayyorlash(models.Model): #+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='loyihalar_tayyorlash_files/',
        verbose_name="Loyiha tayyorlash"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 5.0
        decimal_places=1,
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='loyiha_tayyorlash'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Loyihalar tayyorlagani"
        verbose_name_plural = "Loyihalar tayyorlagani"
        permissions = [
            ('can_evaluate_LoyihalarTayyorlash', 'Can evaluate LoyihalarTayyorlash'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Loyiha tayyorlash"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 5.0:
                raise ValidationError("Baholash 0.0 va 5.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = LoyihalarTayyorlash.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class LoyihaMoliya(models.Model):#+
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='loyiha_moliya_files/',
        verbose_name="Ilmiy loyihalarni moliyalashtirish"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 6.0
        decimal_places=1,
        validators=[MaxValueValidator(6.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='loyiha_moliya'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Loyihani moliyalashtirish"
        verbose_name_plural = "Loyihani moliyalashtirish"
        permissions = [
            ('can_evaluate_LoyihaMoliya', 'Can evaluate LoyihaMoliya'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Ilmiy loyihalarni moliyalashtirish"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 6.0:
                raise ValidationError("Baholash 0.0 va 6.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = LoyihaMoliya.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class AKTDasturlar(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='akt_dasturlar_guvohnoma_files/',
        verbose_name="AKT dasturlari va elektron ma'lumotlar bazalari guvohnomalari"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='akt_dasturlar'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Mualliflik huquqi"
        verbose_name_plural = "Mualliflik huquqi"
        permissions = [
            ('can_evaluate_AKTDasturlar', 'Can evaluate AKTDasturlar'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - AKT dasturlar"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = AKTDasturlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class TalabaIlmiyFaoliyati(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='talaba_ilmiy_faoliyati_files/',
        verbose_name="Talabaning ilmiy faoliyati"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 5.0
        decimal_places=1,
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='talaba_ilmiy_faoliyati'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Talabalar yutuqlari"
        verbose_name_plural = "Talabalar yutuqlari"
        permissions = [
            ('can_evaluate_TalabaIlmiyFaoliyati', 'Can evaluate TalabaIlmiyFaoliyati'),
        ]
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - talaba ilmiy faoliyati"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 5.0:
                raise ValidationError("Baholash 0.0 va 5.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = TalabaIlmiyFaoliyati.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class TarbiyaTadbirlar(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='tarbiya_tadbirlar_files/',
        verbose_name="Talabalar bilan tarbiyaviy ish bo'yicha tadbir"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='Tarbiy_tadbiri'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "“Ma`naviy ustozlar kunlari”"
        verbose_name_plural = "“Ma`naviy ustozlar kunlari”"
        permissions = [
            ('can_evaluate_TarbiyaTadbirlar', 'Can evaluate TarbiyaTadbirlar'),
        ]
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -“Ma`naviy ustozlar kunlari”"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = TarbiyaTadbirlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class DarstanTashqariTadbirlar(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='darsdan_tashqari_files/',
        verbose_name="Darsdan tashqari madaniy va ma'rifiy tadbir"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 4.0
        decimal_places=1,
        validators=[MaxValueValidator(4.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='Darsdan_tashqari_tadbirlar'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Darsdan bo‘sh vaqti"
    class Meta:
        verbose_name = "Darsdan bo‘sh vaqti"
        verbose_name_plural = "Darsdan bo‘sh vaqti"
        permissions = [
            ('can_evaluate_DarstanTashqariTadbirlar', 'Can evaluate DarstanTashqariTadbirlar'),
        ]

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 4.0:
                raise ValidationError("Baholash 0.0 va 6.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = DarstanTashqariTadbirlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class TalabalarTurarJoyTadbirlar(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='talabalar_ttj_tadbirlar_files/',
        verbose_name="Talabalar turar joyidagi madaniy va ma'rifiy tadbir"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='talaba_turar_joy_tadbirlari'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "TTJ da  tadbirlar"
        verbose_name_plural = "TTJ da  tadbirlar"
        permissions = [
            ('can_evaluate_TalabalarTurarJoyTadbirlar', 'Can evaluate TalabalarTurarJoyTadbirlar'),
        ]
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - TTJ da  tadbirlar"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = TalabalarTurarJoyTadbirlar.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)
    
    
class OtaOnalarIshlash(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='ota_onalar_bilan_ishlash_field/',
        verbose_name="Talabalar ota-onalari bilan ishlash"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='ota_onalar_bilan_ishlash'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Ota-onalar hamkorligi"
        verbose_name_plural = "Ota-onalar hamkorligi"
        permissions = [
            ('can_evaluate_OtaOnalarIshlash', 'Can evaluate OtaOnalarIshlash'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Ota-onalar hamkorligi"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = OtaOnalarIshlash.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class AxborotMurobbiylikSoat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='axborot_murabbylik_soati'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Ma`rifat soatini"
        verbose_name_plural = "Ma`rifat soatini"
        permissions = [
            ('can_evaluate_AxborotMurobbiylikSoat', 'Can evaluate AxborotMurobbiylikSoat'),
        ]
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Ma`rifat soatini"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = AxborotMurobbiylikSoat.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

class MuhimTashabbuslarIshlari(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='muhim_tashabbus_field/',
        verbose_name="5 muhim tashabbus doirasidagi ishlari"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 3.0
        decimal_places=1,
        validators=[MaxValueValidator(3.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='muhim_tashabbus'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "5 ta muhim tashabbus"
        verbose_name_plural = "5 ta muhim tashabbus"     
        permissions = [
            ('can_evaluate_MuhimTashabbuslarIshlari', 'Can evaluate MuhimTashabbuslarIshlari'),
        ]  

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -5 ta muhim tashabbus"
    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 3.0:
                raise ValidationError("Baholash 0.0 va 3.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = MuhimTashabbuslarIshlari.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)
        
class BirZiyoliBirMahalla(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='birziyoli_birmahalla_field/',
        verbose_name="Bir ziyoli – bir mahallaga ma'naviy homiy ishi"
    )
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=3,  # Adjusted to accommodate values like 5.0
        decimal_places=1,
        validators=[MaxValueValidator(5.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
                'MaxScore',
                on_delete=models.CASCADE,
                verbose_name="Max Score Value",
                related_name='birziyoli_birmahalla_field'
            )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Mahalla va OAVda chiqishlar"
    class Meta:
        verbose_name = "Mahalla va OAVda chiqishlar"
        verbose_name_plural = "Mahalla va OAVda chiqishlar"
        permissions = [
            ('can_evaluate_BirZiyoliBirMahalla', 'Can evaluate BirZiyoliBirMahalla'),
        ]  

    def clean(self):
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 5.0:
                raise ValidationError("Baholash 0.0 va 5.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = BirZiyoliBirMahalla.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)
        
class DarslikYokiQollanma(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='darslik_yoki_qollanma_files/',
        verbose_name="Darslik yoki o‘quv qo‘llanma tayyorlash va nashr qilish",
        blank=True,
        null=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",null=True,blank=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=4,  # Adjusted to accommodate values up to 50.0
        decimal_places=1,
        validators=[MaxValueValidator(50.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='darslik_yoki_qollanma_file'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Darslik yoki o‘quv qo‘llanma"
    class Meta:
        verbose_name = "Darslik yoki o‘quv qo‘llanma"
        verbose_name_plural = "Darsliklar yoki o‘quv qo‘llanmalar"
        permissions = [
            ('can_evaluate_DarslikYokiQollanma', 'Can evaluate DarslikYokiQollanma'),
        ]  

    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 50.0:
                raise ValidationError("Baholash 0.0 va 50.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = DarslikYokiQollanma.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)
    

class DissertationHimoya(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='dissertatsiya_himoya_files/',
        verbose_name="PhD yoki DSc dissertatsiyani himoya qilish",
        blank=True,
        null=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",blank=True,null=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=5,  # Adjusted to accommodate values up to 100.0
        decimal_places=1,
        validators=[MaxValueValidator(100.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='Dissertatsiyalar_himoyalari'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Dissertatsiyani himoyasi"
        verbose_name_plural = "Dissertatsiyalar himoyasi"
        permissions = [
            ('can_evaluate_DissertationHimoya', 'Can evaluate DissertationHimoya'),
        ] 
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Dissertatsiyalar himoyasi"
    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 100.0:
                raise ValidationError("Baholash 0.0 va 100.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = DissertationHimoya.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)


class IlmiyRahbarlik(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='ilmiy_rahbarlik_files/',
        verbose_name="Ilmiy rahbarlik",
        blank=True,
        null=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",blank=True,null=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=5,  # Adjusted to accommodate values up to 100.0
        decimal_places=1,
        validators=[MaxValueValidator(100.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='ilmiy_rahbarlik'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    class Meta:
        verbose_name = "Ilmiy rahbarlik"
        verbose_name_plural = "Ilmiy rahbarliklar"
        permissions = [
            ('can_evaluate_IlmiyRahbarlik', 'Can evaluate IlmiyRahbarlik'),
        ] 
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -Ilmiy rahbarliklar"
    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 100.0:
                raise ValidationError("Baholash 0.0 va 100.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = IlmiyRahbarlik.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)


class HorijdaMalakaOshirish(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    maqola = models.FileField(
        upload_to='xorijda_malaka_oshirish_files/',
        verbose_name="Xorijda malaka oshirish yoki stajirovka",
        blank=True,
        null=True
    )
    link = models.URLField(verbose_name="Maqolaga havola",blank=True,null=True)
    score = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Baholash",
        max_digits=5,  # Adjusted to accommodate values up to 100.0
        decimal_places=1,
        validators=[MaxValueValidator(100.0), MinValueValidator(0.0)]
    )
    max_score_value = models.ForeignKey(
            'MaxScore',
            on_delete=models.CASCADE,
            verbose_name="Max Score Value",
            related_name='xorijda_malaka_oshirish'
        )
    izoh = models.TextField(blank=True, null=True)  # Made optional if needed

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Xorijda malaka oshirishlar"
    class Meta:
        verbose_name = "Xorijda malaka oshirish"
        verbose_name_plural = "Xorijda malaka oshirishlar"
        permissions = [
            ('can_evaluate_HorijdaMalakaOshirish', 'Can evaluate HorijdaMalakaOshirish'),
        ] 

    def clean(self):
        super().clean()
        if not self.maqola and not self.link:
            raise ValidationError("Kamida bitta (maqola fayli yoki maqola havolasi) to'ldirilishi shart.")
        if self.score is not None:
            if isinstance(self.score, str):
                self.score = Decimal(self.score)

            # Validate that the score is within the allowed range
            if self.score < 0 or self.score > 100.0:
                raise ValidationError("Baholash 0.0 va 100.0 oralig'ida bo'lishi kerak.")

            # Validate that the score does not exceed the user's available max_score
            if self.max_score_value and self.score > self.max_score_value.max_score:
                raise ValidationError(
                    f"Baho {self.score} maksimal bahodan ({self.max_score_value.max_score}) yuqori bo'lishi mumkin emas."
                )

    def save(self, *args, **kwargs):
        # Retrieve the previous score if it exists
        if self.pk:
            previous_instance = HorijdaMalakaOshirish.objects.get(pk=self.pk)
            previous_score = previous_instance.score
        else:
            previous_score = None

        # Call the clean method for validation
        self.clean()

        # If a score is set, and it differs from the previous one, adjust the max_score_value
        if self.score is not None:
            if previous_score is not None:
                # Restore the max_score_value first by adding back the previous score
                self.max_score_value.max_score += previous_score

            # Subtract the new score from max_score_value
            self.max_score_value.max_score -= self.score

            # Ensure that max_score_value is not negative
            if self.max_score_value.max_score < 0:
                raise ValidationError(
                    f"Max score value cannot be negative. Adjust the score accordingly."
                )

            # Save the updated MaxScore instance
            self.max_score_value.save()

        super().save(*args, **kwargs)

@receiver(post_save, sender=CustomUser)
def create_user_max_score(sender, instance, created, **kwargs):
    if created:
        user_content_type = ContentType.objects.get_for_model(CustomUser)
        fan_video_content_type = ContentType.objects.get_for_model(FanVideoKontent)
        nashr_darslik_content_type = ContentType.objects.get_for_model(NashrEtilganDarsliklar)
        mustaqil_talim_content_type = ContentType.objects.get_for_model(MustaqilTalimTopshiriqlari)
        faol_inter_faol_content_type = ContentType.objects.get_for_model(FaolInterfaolMetodlar)
        oak_jurnali_maqola_content_type = ContentType.objects.get_for_model(OAKJurnaliMaqola)
        scopus_web_content_type = ContentType.objects.get_for_model(ScopusWebOfScience)
        h_index_content_type = ContentType.objects.get_for_model(HIndex)
        konferensiya_maqola_content_type = ContentType.objects.get_for_model(KonferensiyaMaqola)
        loyihalar_tayyorlash_content_type = ContentType.objects.get_for_model(LoyihalarTayyorlash)
        loyihalar_moliya_content_type = ContentType.objects.get_for_model(LoyihaMoliya)
        akt_dasturlar_content_type = ContentType.objects.get_for_model(AKTDasturlar)
        talaba_ilmiy_faoliyati_content_type = ContentType.objects.get_for_model(TalabaIlmiyFaoliyati)
        tarbiya_tadbirlar_content_type = ContentType.objects.get_for_model(TarbiyaTadbirlar)
        darstan_tashqari_tadbirlar_content_type = ContentType.objects.get_for_model(DarstanTashqariTadbirlar)
        talabalar_ttj_tadbirlar_content_type = ContentType.objects.get_for_model(TalabalarTurarJoyTadbirlar)
        ota_onalar_ishlash_content_type = ContentType.objects.get_for_model(OtaOnalarIshlash)
        axborot_murobbiylik_soat_content_type = ContentType.objects.get_for_model(AxborotMurobbiylikSoat)
        muhim_tashabbuslar_content_type = ContentType.objects.get_for_model(MuhimTashabbuslarIshlari)
        bir_ziyoli_bir_mahalla_content_type = ContentType.objects.get_for_model(BirZiyoliBirMahalla)
        darslik_yoki_qollanma_content_type = ContentType.objects.get_for_model(DarslikYokiQollanma)
        dissertation_himoya_content_type = ContentType.objects.get_for_model(DissertationHimoya)
        ilmiy_rahbarlik_content_type = ContentType.objects.get_for_model(IlmiyRahbarlik)
        xorijda_malaka_oshirish_content_type = ContentType.objects.get_for_model(HorijdaMalakaOshirish)
        oquv_yili_fanlar_content_type = ContentType.objects.get_for_model(OquvYiliFanlar)
        oqitish_sifati_content_type = ContentType.objects.get_for_model(OqitishSifati)  # Qo'shildi
        MaxScore.objects.create(
            user=instance,
            content_type=oqitish_sifati_content_type,
            object_id=instance.id,
            max_score=Decimal('6.0')
        )

        MaxScore.objects.create(
            user=instance,
            content_type=oquv_yili_fanlar_content_type,
            object_id=instance.id,
            max_score=Decimal('2.0')
        )
        # Create MaxScore instances for each model for the newly created user
        MaxScore.objects.create(
            user=instance,
            content_type=fan_video_content_type,
            object_id=instance.id,
            max_score=Decimal('8.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=nashr_darslik_content_type,
            object_id=instance.id,
            max_score=Decimal('6.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=mustaqil_talim_content_type,
            object_id=instance.id,
            max_score=Decimal('4.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=faol_inter_faol_content_type,
            object_id=instance.id,
            max_score=Decimal('4.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=oak_jurnali_maqola_content_type,
            object_id=instance.id,
            max_score=Decimal('5.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=scopus_web_content_type,
            object_id=instance.id,
            max_score=Decimal('15.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=h_index_content_type,
            object_id=instance.id,
            max_score=Decimal('5.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=konferensiya_maqola_content_type,
            object_id=instance.id,
            max_score=Decimal('2.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=loyihalar_tayyorlash_content_type,
            object_id=instance.id,
            max_score=Decimal('5.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=loyihalar_moliya_content_type,
            object_id=instance.id,
            max_score=Decimal('6.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=akt_dasturlar_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=talaba_ilmiy_faoliyati_content_type,
            object_id=instance.id,
            max_score=Decimal('5.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=tarbiya_tadbirlar_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=darstan_tashqari_tadbirlar_content_type,
            object_id=instance.id,
            max_score=Decimal('4.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=talabalar_ttj_tadbirlar_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=ota_onalar_ishlash_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=axborot_murobbiylik_soat_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=muhim_tashabbuslar_content_type,
            object_id=instance.id,
            max_score=Decimal('3.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=bir_ziyoli_bir_mahalla_content_type,
            object_id=instance.id,
            max_score=Decimal('5.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=darslik_yoki_qollanma_content_type,
            object_id=instance.id,
            max_score=Decimal('50.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=dissertation_himoya_content_type,
            object_id=instance.id,
            max_score=Decimal('100.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=ilmiy_rahbarlik_content_type,
            object_id=instance.id,
            max_score=Decimal('100.0')
        )
        MaxScore.objects.create(
            user=instance,
            content_type=xorijda_malaka_oshirish_content_type,
            object_id=instance.id,
            max_score=Decimal('100.0')
        )


@receiver(post_save, sender=CustomUser)
def create_oquv_yili_fanlar(sender, instance, created, **kwargs):
    if created:
        try:
            # Start a transaction block
            with transaction.atomic():
                # Check if MaxScore objects exist or create them first
                oqitish_sifati_max_score, _ = MaxScore.objects.get_or_create(
                    user=instance,
                    content_type=ContentType.objects.get_for_model(OqitishSifati),
                    object_id=instance.id,
                    defaults={'max_score': Decimal('6.0')}
                )

                oquv_yili_fanlar_max_score, _ = MaxScore.objects.get_or_create(
                    user=instance,
                    content_type=ContentType.objects.get_for_model(OquvYiliFanlar),
                    object_id=instance.id,
                    defaults={'max_score': Decimal('2.0')}
                )

                # Create the related models with the appropriate max_score_value linked
                OquvYiliFanlar.objects.get_or_create(
                    user=instance,
                    max_score_value=oquv_yili_fanlar_max_score
                )
#
                OqitishSifati.objects.get_or_create(
                    user=instance,
                    max_score_value=oqitish_sifati_max_score
                )
#
                # Repeat similar for other models where needed
                MustaqilTalimTopshiriqlari.objects.get_or_create(
                    user=instance,
                    max_score_value=MaxScore.objects.get_or_create(
                        user=instance,
                        content_type=ContentType.objects.get_for_model(MustaqilTalimTopshiriqlari),
                        object_id=instance.id,
                        defaults={'max_score': Decimal('4.0')}
                    )[0]
                )

                FaolInterfaolMetodlar.objects.get_or_create(
                    user=instance,
                    max_score_value=MaxScore.objects.get_or_create(
                        user=instance,
                        content_type=ContentType.objects.get_for_model(FaolInterfaolMetodlar),
                        object_id=instance.id,
                        defaults={'max_score': Decimal('4.0')}
                    )[0]
                )
#
                AxborotMurobbiylikSoat.objects.get_or_create(
                    user=instance,
                    max_score_value=MaxScore.objects.get_or_create(
                        user=instance,
                        content_type=ContentType.objects.get_for_model(AxborotMurobbiylikSoat),
                        object_id=instance.id,
                        defaults={'max_score': Decimal('3.0')}
                    )[0]
                )
        except Exception as e:
            # Log the error or raise an exception if necessary
            print(f"Error occurred while creating associated objects: {e}")