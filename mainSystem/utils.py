from django.apps import apps
from django.db.models import Sum

GROUP_MODEL_MAP = {
    "O‘quv-metodik faoliyati (maksimal 30 ball)": [
        "mainSystem.OquvYiliFanlar", 
        "mainSystem.FaolInterfaolMetodlar", 
        "mainSystem.MustaqilTalimTopshiriqlari",
        "mainSystem.FanVideoKontent", 
        "mainSystem.OqitishSifati", 
        "mainSystem.NashrEtilganDarsliklar"
    ],
    "Manaviy-marifiy(maksimal 24 ball)": [
        "mainSystem.TarbiyaTadbirlar", 
        "mainSystem.DarstanTashqariTadbirlar", 
        "mainSystem.TalabalarTurarJoyTadbirlar",
        "mainSystem.OtaOnalarIshlash", 
        "mainSystem.AxborotMurobbiylikSoat", 
        "mainSystem.MuhimTashabbuslarIshlari",
        "mainSystem.BirZiyoliBirMahalla"
    ],
    "Ilmiy faoliyati (maksimal 46 ball)": [
        "mainSystem.ScopusWebOfScience", 
        "mainSystem.OAKJurnaliMaqola", 
        "mainSystem.HIndex", 
        "mainSystem.KonferensiyaMaqola",
        "mainSystem.LoyihalarTayyorlash", 
        "mainSystem.LoyihaMoliya", 
        "mainSystem.AKTDasturlar", 
        "mainSystem.TalabaIlmiyFaoliyati",
        "mainSystem.DarslikYokiQollanma", 
        "mainSystem.DissertationHimoya", 
        "mainSystem.IlmiyRahbarlik", 
        "mainSystem.HorijdaMalakaOshirish"
    ]
}

def get_user_models(user):
    """
    Foydalanuvchining guruhlari asosida modellarni qaytaradi.
    """
    user_models = []
    for group_name, model_paths in GROUP_MODEL_MAP.items():
        if user.groups.filter(name=group_name).exists():
            for model_path in model_paths:
                app_label, model_name = model_path.split('.')
                user_models.append(apps.get_model(app_label, model_name))
    return user_models

def calculate_progress(queryset, max_score):
    """
    Helper function to calculate total score and progress percentage.
    """
    total_score = queryset.aggregate(Sum('score'))['score__sum'] or 0
    progress_percent = (total_score / max_score) * 100 if max_score > 0 else 0
    return total_score, progress_percent
