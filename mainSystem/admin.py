from django.contrib.admin import AdminSite
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'kafedra', 'ish_soati', 'ish_unvoni', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'kafedra', 'ish_soati', 'ish_unvoni')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'kafedra', 'ish_soati', 'ish_unvoni', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register([OquvYiliFanlar,FaolInterfaolMetodlar,MustaqilTalimTopshiriqlari,FanVideoKontent,OqitishSifati,NashrEtilganDarsliklar])
admin.site.register([ScopusWebOfScience,OAKJurnaliMaqola,HIndex,KonferensiyaMaqola,LoyihalarTayyorlash,LoyihaMoliya,AKTDasturlar,TalabaIlmiyFaoliyati])
admin.site.register([TarbiyaTadbirlar,DarstanTashqariTadbirlar,TalabalarTurarJoyTadbirlar,OtaOnalarIshlash,AxborotMurobbiylikSoat,MuhimTashabbuslarIshlari,BirZiyoliBirMahalla])
admin.site.register([DarslikYokiQollanma,DissertationHimoya,IlmiyRahbarlik,HorijdaMalakaOshirish])
admin.site.register(MaxScore)