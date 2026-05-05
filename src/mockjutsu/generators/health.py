"""
mock-jutsu — Health Generator (Blood Type, NHS, ICD-10, Height/Weight)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random

# Common ICD-10 codes (public WHO standard)
ICD10_POOL = [
    ("J18.9",  "Pneumonia, unspecified"),
    ("E11.9",  "Type 2 diabetes mellitus without complications"),
    ("I10",    "Essential hypertension"),
    ("E78.5",  "Hyperlipidemia, unspecified"),
    ("M54.5",  "Low back pain"),
    ("J06.9",  "Acute upper respiratory infection, unspecified"),
    ("F32.1",  "Major depressive disorder, moderate"),
    ("K21.0",  "GERD with oesophagitis"),
    ("N18.3",  "Chronic kidney disease, stage 3"),
    ("I21.0",  "Acute myocardial infarction, anterior wall"),
    ("C34.1",  "Malignant neoplasm, upper lobe bronchus"),
    ("Z00.00", "Encounter for general adult medical examination"),
    ("J45.909","Unspecified asthma, uncomplicated"),
    ("G43.909","Migraine, unspecified, not intractable"),
    ("F41.1",  "Generalized anxiety disorder"),
    ("K29.70", "Gastritis, unspecified, without bleeding"),
    ("M17.11", "Primary osteoarthritis, right knee"),
    ("E03.9",  "Hypothyroidism, unspecified"),
    ("I25.10", "Atherosclerotic heart disease, unspecified vessel"),
    ("J20.9",  "Acute bronchitis, unspecified"),
]


class HealthGenerator:
    """Healthcare mock data for 6 locales."""

    @staticmethod
    def generate_blood_type():
        return random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

    @staticmethod
    def generate_nhs_number():
        """UK NHS number — 10 digits with weighted checksum (weights 10→2, check = 1)."""
        while True:
            base = [random.randint(0, 9) for _ in range(9)]
            weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
            total = sum(d * w for d, w in zip(base, weights))
            remainder = total % 11
            if remainder == 1:
                continue
            check = 0 if remainder == 0 else 11 - remainder
            if check == 10:
                continue
            digits = "".join(map(str, base)) + str(check)
            return f"{digits[:3]} {digits[3:6]} {digits[6:]}"

    @staticmethod
    def generate_icd10(with_description=False):
        code, desc = random.choice(ICD10_POOL)
        if with_description:
            return {"code": code, "description": desc}
        return code

    @staticmethod
    def generate_height(locale="TR"):
        l = locale.upper()
        cm = random.randint(155, 195)
        if l == "US":
            total_inches = round(cm / 2.54)
            feet, inches = divmod(total_inches, 12)
            return f"{feet}'{inches}\""
        if l == "UK":
            total_inches = round(cm / 2.54)
            feet, inches = divmod(total_inches, 12)
            return f"{feet}'{inches}\" ({cm} cm)"
        return f"{cm} cm"

    @staticmethod
    def generate_weight(locale="TR"):
        l = locale.upper()
        kg = random.randint(50, 110)
        if l == "US":
            lbs = round(kg * 2.20462)
            return f"{lbs} lbs"
        if l == "UK":
            total_lbs = round(kg * 2.20462)
            stones, lbs = divmod(total_lbs, 14)
            return f"{stones}st {lbs}lb ({kg} kg)"
        return f"{kg} kg"

    def generate(self, data_type, locale="TR", **kwargs):
        dt = data_type.lower().replace("_", "")
        if dt == "bloodtype":
            return self.generate_blood_type()
        if dt == "nhsnumber":
            return self.generate_nhs_number()
        if dt == "icd10":
            with_desc = kwargs.get("description", False)
            return self.generate_icd10(with_description=with_desc)
        if dt == "height":
            return self.generate_height(locale)
        if dt == "weight":
            return self.generate_weight(locale)
        return None
