"""
mock-jutsu — Corporate Generator (Company Names, Job Titles)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random

COMPANY_WORDS = {
    "TR": {
        "adj":    ["Anadolu", "Ege", "Boğaz", "İstanbul", "Mavi", "Altın", "Yıldız", "Güneş", "Deniz", "Türk"],
        "noun":   ["Teknoloji", "Yazılım", "Finans", "Enerji", "Lojistik", "Sanayi", "Ticaret", "Danışmanlık", "İnşaat", "Holding"],
        "suffix": ["A.Ş.", "Ltd. Şti.", "Holding A.Ş.", "Grup A.Ş.", "A.Ş."],
    },
    "US": {
        "adj":    ["National", "Pacific", "Liberty", "American", "First", "Premier", "Global", "United", "Pioneer", "Apex"],
        "noun":   ["Technologies", "Solutions", "Financial", "Energy", "Logistics", "Industries", "Commerce", "Consulting", "Holdings", "Systems"],
        "suffix": ["LLC", "Inc.", "Corp.", "& Associates LLC", "Group Inc."],
    },
    "UK": {
        "adj":    ["Royal", "British", "Crown", "Imperial", "Northern", "Southern", "Central", "Allied", "United", "National"],
        "noun":   ["Technologies", "Solutions", "Finance", "Energy", "Logistics", "Industries", "Commerce", "Consulting", "Holdings", "Systems"],
        "suffix": ["Ltd.", "PLC", "& Co. Ltd.", "LLP", "Group Ltd."],
    },
    "DE": {
        "adj":    ["Deutsche", "Berliner", "Hamburger", "Bayrische", "Rheinische", "Nord", "Süd", "West", "Ost", "Zentral"],
        "noun":   ["Technologien", "Lösungen", "Finanzen", "Energie", "Logistik", "Industrien", "Handel", "Beratung", "Systeme", "Holding"],
        "suffix": ["GmbH", "AG", "KG", "GmbH & Co. KG"],
    },
    "FR": {
        "adj":    ["Française", "Parisienne", "Nationale", "Générale", "Centrale", "Atlantique", "Méditerranée", "Loire", "Normandie", "Alsace"],
        "noun":   ["Technologies", "Solutions", "Finance", "Énergie", "Logistique", "Industries", "Commerce", "Conseil", "Systèmes", "Groupe"],
        "suffix": ["SARL", "SA", "SAS", "SASU"],
    },
    "RU": {
        "adj":    ["Российский", "Московский", "Сибирский", "Уральский", "Северный", "Южный", "Восточный", "Западный", "Центральный", "Национальный"],
        "noun":   ["Технологии", "Решения", "Финанс", "Энергия", "Логистика", "Индустрия", "Торговля", "Консалтинг", "Системы", "Холдинг"],
        "suffix": ["ООО", "АО", "ПАО"],
    },
}

JOB_TITLES = {
    "TR": [
        "Yazılım Mühendisi", "Kıdemli Yazılım Mühendisi", "Ürün Müdürü", "Proje Yöneticisi",
        "Veri Bilimcisi", "DevOps Mühendisi", "Mali Müşavir", "Satış Müdürü",
        "İnsan Kaynakları Uzmanı", "Finans Analisti", "Operasyon Müdürü", "Pazarlama Uzmanı",
        "Sistem Analisti", "QA Mühendisi", "İş Geliştirme Müdürü",
    ],
    "US": [
        "Software Engineer", "Senior Software Engineer", "Product Manager", "Project Manager",
        "Data Scientist", "DevOps Engineer", "Financial Advisor", "Sales Manager",
        "HR Business Partner", "Financial Analyst", "Operations Manager", "Marketing Specialist",
        "Systems Analyst", "QA Engineer", "Business Development Manager",
    ],
    "UK": [
        "Software Engineer", "Senior Developer", "Product Manager", "Programme Manager",
        "Data Analyst", "Infrastructure Engineer", "Financial Consultant", "Account Manager",
        "HR Advisor", "Finance Manager", "Operations Director", "Marketing Manager",
        "Business Analyst", "Test Engineer", "Commercial Director",
    ],
    "DE": [
        "Softwareentwickler", "Senior Entwickler", "Produktmanager", "Projektleiter",
        "Datenwissenschaftler", "DevOps Ingenieur", "Finanzberater", "Vertriebsleiter",
        "Personalreferent", "Controller", "Betriebsleiter", "Marketingspezialist",
        "Systemanalytiker", "QA Ingenieur", "Geschäftsentwickler",
    ],
    "FR": [
        "Ingénieur Logiciel", "Ingénieur Senior", "Chef de Produit", "Chef de Projet",
        "Data Scientist", "Ingénieur DevOps", "Conseiller Financier", "Directeur Commercial",
        "Responsable RH", "Analyste Financier", "Directeur Opérations", "Responsable Marketing",
        "Analyste Systèmes", "Ingénieur QA", "Développeur Business",
    ],
    "RU": [
        "Разработчик ПО", "Старший разработчик", "Менеджер продукта", "Руководитель проекта",
        "Аналитик данных", "DevOps инженер", "Финансовый консультант", "Руководитель отдела продаж",
        "HR бизнес-партнёр", "Финансовый аналитик", "Операционный директор", "Маркетолог",
        "Системный аналитик", "Инженер QA", "Директор по развитию бизнеса",
    ],
}


class CorporateGenerator:
    """Company names and job titles for 6 locales."""

    @staticmethod
    def generate_company_name(locale="TR"):
        l = locale.upper()
        pool = COMPANY_WORDS.get(l, COMPANY_WORDS["TR"])
        adj    = random.choice(pool["adj"])
        noun   = random.choice(pool["noun"])
        suffix = random.choice(pool["suffix"])
        if l == "RU":
            return f"{suffix} «{adj} {noun}»"
        return f"{adj} {noun} {suffix}"

    @staticmethod
    def generate_job_title(locale="TR"):
        l = locale.upper()
        return random.choice(JOB_TITLES.get(l, JOB_TITLES["TR"]))

    def generate(self, data_type, locale="TR", **kwargs):
        dt = data_type.lower().replace(" ", "_")
        if dt == "company_name":
            return self.generate_company_name(locale)
        if dt in ("job_title", "occupation", "jobtitle"):
            return self.generate_job_title(locale)
        return None
