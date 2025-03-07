from django import forms
from .models import *
from django.core.exceptions import ValidationError

class FanVideoKontentForm(forms.ModelForm):
    class Meta:
        model = FanVideoKontent
        fields = ['link', 'score', 'izoh']  # 'max_score_value' ni shakldan olib tashlaymiz, avtomatik tanlaymiz
        widgets = {
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholash'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FanVideoKontentForm, self).__init__(*args, **kwargs)

        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydonini olib tashlaymiz
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(FanVideoKontent)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(FanVideoKontent)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class NashrEtilganDarsliklarForm(forms.ModelForm):
    class Meta:
        model = NashrEtilganDarsliklar
        fields = ['maqola', 'score', 'izoh']  # 'max_score_value' ni shakldan olib tashlaymiz, avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholash'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(NashrEtilganDarsliklarForm, self).__init__(*args, **kwargs)

        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydonini olib tashlaymiz
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(NashrEtilganDarsliklar)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(NashrEtilganDarsliklar)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

###########################################################################
class ScopusWebOfScienceForm(forms.ModelForm):
    class Meta:
        model = ScopusWebOfScience
        fields = ['maqola', 'link', 'izoh', 'score']  # 'max_score_value' ni shakldan olib tashlaymiz, avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(ScopusWebOfScienceForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(ScopusWebOfScience)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(ScopusWebOfScience)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)


class OAKJurnaliMaqolaForm(forms.ModelForm):
    class Meta:
        model = OAKJurnaliMaqola
        fields = ['maqola', 'link', 'izoh', 'score']  # 'max_score_value' ni shakldan olib tashlaymiz, avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(OAKJurnaliMaqolaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(OAKJurnaliMaqola)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(OAKJurnaliMaqola)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class HIndexForm(forms.ModelForm):
    class Meta:
        model = HIndex
        fields = ['maqola', 'link', 'izoh', 'score']  # 'max_score_value' ni avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(HIndexForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(HIndex)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(HIndex)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class KonferensiyaMaqolaForm(forms.ModelForm):
    class Meta:
        model = KonferensiyaMaqola
        fields = ['maqola', 'link', 'izoh', 'score']  # 'max_score_value' ni avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(KonferensiyaMaqolaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(KonferensiyaMaqola)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(KonferensiyaMaqola)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class LoyihalarTayyorlashForm(forms.ModelForm):
    class Meta:
        model = LoyihalarTayyorlash
        fields = ['maqola', 'izoh', 'score']  # 'max_score_value' ni avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(LoyihalarTayyorlashForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(LoyihalarTayyorlash)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(LoyihalarTayyorlash)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class LoyihaMoliyaForm(forms.ModelForm):
    class Meta:
        model = LoyihaMoliya
        fields = ['maqola', 'izoh', 'score']  # 'max_score_value' ni avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(LoyihaMoliyaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(LoyihaMoliya)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(LoyihaMoliya)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class AKTDasturlarForm(forms.ModelForm):
    class Meta:
        model = AKTDasturlar
        fields = ['maqola', 'izoh', 'score']  # 'max_score_value' ni avtomatik tanlaymiz
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(AKTDasturlarForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')

        # Avtomatik tarzda 'max_score_value' ni foydalanuvchi va model asosida tanlash
        if user:
            content_type = ContentType.objects.get_for_model(AKTDasturlar)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value

    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(AKTDasturlar)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)


class TalabaIlmiyFaoliyatiForm(forms.ModelForm):
    class Meta:
        model = TalabaIlmiyFaoliyati
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(TalabaIlmiyFaoliyatiForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(TalabaIlmiyFaoliyati)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(TalabaIlmiyFaoliyati)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)


class TarbiyaTadbirlarForm(forms.ModelForm):
    class Meta:
        model = TarbiyaTadbirlar
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(TarbiyaTadbirlarForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(TarbiyaTadbirlar)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(TarbiyaTadbirlar)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class DarstanTashqariTadbirlarForm(forms.ModelForm):
    class Meta:
        model = DarstanTashqariTadbirlar
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(DarstanTashqariTadbirlarForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(DarstanTashqariTadbirlar)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(DarstanTashqariTadbirlar)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class TalabalarTurarJoyTadbirlarForm(forms.ModelForm):
    class Meta:
        model = TalabalarTurarJoyTadbirlar
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(TalabalarTurarJoyTadbirlarForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(TalabalarTurarJoyTadbirlar)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(TalabalarTurarJoyTadbirlar)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class OtaOnalarIshlashForm(forms.ModelForm):
    class Meta:
        model = OtaOnalarIshlash
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(OtaOnalarIshlashForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(OtaOnalarIshlash)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(OtaOnalarIshlash)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class AxborotMurobbiylikSoatForm(forms.ModelForm):
    class Meta:
        model = AxborotMurobbiylikSoat
        fields = ['izoh', 'score']
        widgets = {
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(AxborotMurobbiylikSoatForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(AxborotMurobbiylikSoat)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(AxborotMurobbiylikSoat)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class MuhimTashabbuslarIshlariForm(forms.ModelForm):
    class Meta:
        model = MuhimTashabbuslarIshlari
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(MuhimTashabbuslarIshlariForm, self).__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(MuhimTashabbuslarIshlari)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(MuhimTashabbuslarIshlari)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class BirZiyoliBirMahallaForm(forms.ModelForm):
    class Meta:
        model = BirZiyoliBirMahalla
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(BirZiyoliBirMahallaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(BirZiyoliBirMahalla)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(BirZiyoliBirMahalla)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
########################
class DarslikYokiQollanmaForm(forms.ModelForm):
    class Meta:
        model = DarslikYokiQollanma
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(DarslikYokiQollanmaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(DarslikYokiQollanma)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(DarslikYokiQollanma)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)

class DissertationHimoyaForm(forms.ModelForm):
    class Meta:
        model = DissertationHimoya
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(DissertationHimoyaForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(DissertationHimoya)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(DissertationHimoya)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class IlmiyRahbarlikForm(forms.ModelForm):
    class Meta:
        model = IlmiyRahbarlik
        fields = ['maqola','izoh', 'score','link']
        widgets = {
            'link': forms.URLInput(attrs={'class': 'form-control', 'id': 'linkInput1', 'placeholder': 'Linkni kiriting'}),
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(IlmiyRahbarlikForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(IlmiyRahbarlik)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(IlmiyRahbarlik)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)
class HorijdaMalakaOshirishForm(forms.ModelForm):
    class Meta:
        model = HorijdaMalakaOshirish
        fields = ['maqola','izoh', 'score']
        widgets = {
            'maqola': forms.FileInput(attrs={'class': 'form-control', 'id': 'maqolaInput1', 'placeholder': 'Maqolani yuklang'}),
            'izoh': forms.Textarea(attrs={'class': 'form-control', 'id': 'commentInput1', 'rows': 3, 'placeholder': 'Izoh kiriting'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'scoreInput1', 'placeholder': 'Baholashni kiriting'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Foydalanuvchini olish
        super(HorijdaMalakaOshirishForm, self).__init__(*args, **kwargs)
        
        # Agar foydalanuvchi superuser bo'lmasa, 'score' maydoni olib tashlanadi
        if user and not user.is_superuser:
            self.fields.pop('score')
        if user:
            content_type = ContentType.objects.get_for_model(HorijdaMalakaOshirish)
            max_score_value = MaxScore.objects.filter(user=user, content_type=content_type).first()
            if max_score_value:
                # Maydon qiymatini avtomatik tarzda to'ldirish
                self.instance.max_score_value = max_score_value
    def save(self, *args, **kwargs):
        # Agar shakl orqali kiritilmagan bo'lsa, avtomatik 'max_score_value' ni aniqlash
        if not self.instance.max_score_value:
            content_type = ContentType.objects.get_for_model(HorijdaMalakaOshirish)
            max_score_value = MaxScore.objects.filter(user=self.instance.user, content_type=content_type).first()
            if max_score_value:
                self.instance.max_score_value = max_score_value
            else:
                raise ValidationError("MaxScore obyektini topib bo'lmadi.")
        
        return super().save(*args, **kwargs)