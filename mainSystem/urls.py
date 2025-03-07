from django.urls import path
from .views import *
from . import views  # Make sure to import your views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin/',kafedralar_jadvali, name='admin'),
    path('user/<str:username>/',view_name, name='view_name'),
    path('user/<str:username>/oquv-yili-fanlar/', update_OquvYiliFanlar_score, name='update_OquvYiliFanlar_score'),
    path('user/<str:username>/faol-interfaol-metodlar/', update_FaolInterfaolMetodlar_score, name='update_FaolInterfaolMetodlar_score'),
    path('user/<str:username>/mustaqil-talim-topshiriqlari/', update_MustaqilTalimTopshiriqlari_score, name='update_MustaqilTalimTopshiriqlari_score'),
    path('user/<str:username>/fan-video-kontent/', update_FanVideoKontent_score, name='update_FanVideoKontent_score'),
    path('user/<str:username>/oqitish-sifati/', update_OqitishSifati_score, name='update_OqitishSifati_score'),
    path('user/<str:username>/nashr-etilgan-darsliklar/', update_NashrEtilganDarsliklar, name='update_NashrEtilganDarsliklar'),
    path('user/<str:username>/scopus-web-of-science/', update_ScopusWebOfScience, name='update_ScopusWebOfScience'),
    path('user/<str:username>/oak-jurnali-maqola/', update_OAKJurnaliMaqola, name='update_OAKJurnaliMaqola'),
    path('user/<str:username>/h-index/', update_HIndex, name='update_HIndex'),
    path('user/<str:username>/konferensiya-maqola/', update_KonferensiyaMaqola, name='update_KonferensiyaMaqola'),
    path('user/<str:username>/loyihalar-tayyorlash/', update_LoyihalarTayyorlash, name='update_LoyihalarTayyorlash'),
    path('user/<str:username>/loyiha-moliya/', update_LoyihaMoliya, name='update_LoyihaMoliya'),
    path('user/<str:username>/akt-dasturlar/', update_AKTDasturlar, name='update_AKTDasturlar'),
    path('user/<str:username>/talaba-ilmiy-faoliyati/', update_TalabaIlmiyFaoliyati, name='update_TalabaIlmiyFaoliyati'),
    path('user/<str:username>/tarbiya-tadbirlar/', update_TarbiyaTadbirlar, name='update_TarbiyaTadbirlar'),
    path('user/<str:username>/darstan-tashqari-tadbirlar/', update_DarstanTashqariTadbirlar, name='update_DarstanTashqariTadbirlar'),
    path('user/<str:username>/talabalar-turar-joy-tadbirlar/', update_TalabalarTurarJoyTadbirlar, name='update_TalabalarTurarJoyTadbirlar'),
    path('user/<str:username>/ota-onalar-ishlash/', update_OtaOnalarIshlash, name='update_OtaOnalarIshlash'),
    path('user/<str:username>/axborot-murobbiylik-soat/', update_AxborotMurobbiylikSoat, name='update_AxborotMurobbiylikSoat'),
    path('user/<str:username>/muhim-tashabbuslar-ishlari/', update_MuhimTashabbuslarIshlari, name='update_MuhimTashabbuslarIshlari'),
    path('user/<str:username>/bir-ziyoli-bir-mahalla/', update_BirZiyoliBirMahalla, name='update_BirZiyoliBirMahalla'),
    path('user/<str:username>/darslik-yoki-qollanma/', update_DarslikYokiQollanma, name='update_DarslikYokiQollanma'),
    path('user/<str:username>/dissertation-himoya/', update_DissertationHimoya, name='update_DissertationHimoya'),
    path('user/<str:username>/ilmiy-rahbarlik/', update_IlmiyRahbarlik, name='update_IlmiyRahbarlik'),
    path('user/<str:username>/xorijda-malaka-oshirish/', update_HorijdaMalakaOshirish, name='update_HorijdaMalakaOshirish'),
    path('add-oquv-yili-fanlar/<str:username>/', add_oquv_yili_fanlar, name='add_oquv_yili_fanlar'),
    path('add-faol_interfaol_metodlar/<str:username>/', add_faol_interfaol_metodlar, name='add_faol_interfaol_metodlar'),
    path('add-oqitish-sifati/<str:username>/', add_oqitish_sifati, name='add_oqitish_sifati'),
    path('add-mustaqil-talim-topshiriqlari/<str:username>/', add_mustaqil_talim_topshiriqlari, name='add_mustaqil_talim_topshiriqlari'),
    path('add-axborot-murabiylik-soati/<str:username>/', add_axborot_murobbiylik_soat, name='add_axborot_murobbiylik_soat'),
    path('', all_data_view, name='home'),
    path('export/', views.export_view, name='export_url_name'),
    path('export_all/', views.export_view_all, name='export_url_all'),
    path('export_ilmiy/', views.export_view_ilmiy_bulim, name='export_url_ilmiy'),
    path('export_manaviy/', views.export_view_manaviy_bulim, name='export_url_manaviy'),
    path('export_uquv/', views.export_view_uquv_bulim, name='export_url_uquv'),
    path('delete/<str:model_name>/<int:pk>/', views.delete_item, name='delete_item'),
]
