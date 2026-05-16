"""
mock-jutsu — Health Generator
Standards:
  HL7 v2.5 §2.9 / §3.3.1 (ADT^A01 message structure)
  HL7 FHIR R4 v4.0.1 §8.1 (Patient resource)
  NEMA DICOM PS3.5 §9.1 + ISO/IEC 9834-8 (UUID-based UID root 2.25)
  NHS Number Standard (NHS Digital, weighted Mod-11 checksum)
  CMS NPI Algorithm (Luhn with 80840 prefix)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Entropy:
  hl7_message : unique per call (MSG + 8 hex control ID = 2^32 space)
  fhir_patient: UUID v4 ID → ~5.3×10^36
  dicom_uid   : 128-bit random decimal → ~3.4×10^38
"""

import json
import random
import secrets
import uuid as _uuid
from datetime import datetime, timezone

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

# ──────────────────────────────────────────────────────────────────────────────
# HL7 v2.5 ADT^A01 — static lookup tables
# HL7 International standard; all field values are synthetic.
# ──────────────────────────────────────────────────────────────────────────────
_HL7_APPS: list[str] = ["EMR_SYS", "LIS", "RADIOLOGY", "PHARMACY", "BILLING"]
_HL7_FACILITIES: list[str] = ["CITYHOSP", "METRO_MEDICAL", "ST_JOHNS", "CENTRAL_CLINIC"]
_HL7_UNITS: list[str] = ["2EAST", "3WEST", "ICU", "ED", "ONCOLOGY", "SURGERY"]
_HL7_LAST_NAMES: list[str] = [
    "SMITH", "JONES", "WILLIAMS", "BROWN", "TAYLOR",
    "ANDERSON", "THOMAS", "JACKSON", "WHITE", "HARRIS",
]
_HL7_FIRST_NAMES: list[str] = [
    "JAMES", "MARY", "ROBERT", "LINDA", "MICHAEL",
    "PATRICIA", "WILLIAM", "BARBARA", "DAVID", "SUSAN",
]
_HL7_PHYSICIANS: list[str] = [
    "001^SMITH^JAMES^A^^MD", "002^JOHNSON^MARY^B^^DO",
    "003^WILLIAMS^ROBERT^C^^MD", "004^BROWN^LINDA^D^^NP",
    "005^DAVIS^MICHAEL^E^^MD", "006^MILLER^SUSAN^F^^DO",
]

# ──────────────────────────────────────────────────────────────────────────────
# FHIR R4 Patient — static lookup tables
# HL7 FHIR R4 v4.0.1 §8.1; synthetic names, real country codes.
# ──────────────────────────────────────────────────────────────────────────────
_FHIR_FAMILIES: dict[str, list[str]] = {
    "TR": ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Aydın", "Arslan"],
    "US": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"],
    "UK": ["Smith", "Jones", "Taylor", "Brown", "Davies", "Evans", "Wilson"],
    "DE": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer"],
    "FR": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard"],
    "RU": ["Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Новиков"],
}
_FHIR_GIVENS_M: dict[str, list[str]] = {
    "TR": ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "Hasan"],
    "US": ["James", "John", "Robert", "Michael", "William", "David"],
    "UK": ["Oliver", "George", "Harry", "Jack", "Charlie", "Thomas"],
    "DE": ["Lukas", "Jonas", "Leon", "Finn", "Elias", "Noah"],
    "FR": ["Lucas", "Hugo", "Gabriel", "Arthur", "Louis", "Raphaël"],
    "RU": ["Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей"],
}
_FHIR_GIVENS_F: dict[str, list[str]] = {
    "TR": ["Fatma", "Ayşe", "Emine", "Hatice", "Zeynep", "Elif"],
    "US": ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Susan"],
    "UK": ["Olivia", "Amelia", "Isla", "Ava", "Mia", "Isabella"],
    "DE": ["Emma", "Mia", "Hannah", "Lena", "Lea", "Anna"],
    "FR": ["Emma", "Jade", "Louise", "Alice", "Chloé", "Inès"],
    "RU": ["Анастасия", "Мария", "Анна", "Виктория", "Екатерина", "Наталья"],
}
_FHIR_CITIES: dict[str, list[str]] = {
    "TR": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"],
    "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "UK": ["London", "Birmingham", "Manchester", "Leeds", "Glasgow"],
    "DE": ["Berlin", "Hamburg", "München", "Köln", "Frankfurt"],
    "FR": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
    "RU": ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"],
}
# ISO 3166-1 alpha-2
_FHIR_COUNTRY_CODE: dict[str, str] = {
    "TR": "TR", "US": "US", "UK": "GB", "DE": "DE", "FR": "FR", "RU": "RU",
}
# E.164 country calling codes per locale
_E164_CC: dict[str, str] = {
    "TR": "90", "US": "1", "UK": "44", "DE": "49", "FR": "33", "RU": "7",
}

# ──────────────────────────────────────────────────────────────────────────────
# DICOM UID — root 2.25 (ISO/IEC 9834-8 UUID-derived UID org root)
# NEMA DICOM PS3.5 §9.1: digits and dots only, max 64 chars, no leading zeros.
# ──────────────────────────────────────────────────────────────────────────────
_DICOM_ROOT = "2.25"


class HealthGenerator:
    """Healthcare mock data for 6 locales."""

    @staticmethod
    def generate_blood_type():
        return random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])

    @staticmethod
    def generate_nhs_number():
        """UK NHS number — 10 digits with weighted checksum (weights 10→2, check = 1)."""
        while True:
            base    = [random.randrange(10) for _ in range(9)]
            weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
            total   = sum(d * w for d, w in zip(base, weights))
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
        l  = locale.upper()
        cm = random.randrange(41) + 155  # 155–195
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
        l  = locale.upper()
        kg = random.randrange(61) + 50  # 50–110
        if l == "US":
            lbs = round(kg * 2.20462)
            return f"{lbs} lbs"
        if l == "UK":
            total_lbs = round(kg * 2.20462)
            stones, lbs = divmod(total_lbs, 14)
            return f"{stones}st {lbs}lb ({kg} kg)"
        return f"{kg} kg"

    @staticmethod
    def generate_npi():
        """US National Provider Identifier — 10 digits, Luhn check with '80840' prefix.

        CMS algorithm: prepend '80840' to the 9-digit base, apply Luhn to all 14 digits.
        check = (10 - (sum_of_first_13 % 10)) % 10
        """
        while True:
            base = [random.randrange(10) for _ in range(9)]
            padded = [8, 0, 8, 4, 0] + base
            total = 0
            for i, d in enumerate(reversed(padded)):
                n = d * 2 if i % 2 == 0 else d
                if n > 9:
                    n -= 9
                total += n
            check = (10 - total % 10) % 10
            digits = base + [check]
            return "".join(map(str, digits))

    @staticmethod
    def generate_bmi():
        """Body Mass Index — float 18.5–35.0, one decimal place."""
        raw = 18.5 + random.randrange(166) / 10  # 18.5–35.0 (0.1 steps)
        return round(raw, 1)

    @staticmethod
    def generate_hl7_message() -> str:
        """
        HL7 v2.5 ADT^A01 (Patient Admission) message.
        HL7 International standard v2.5 §3.3.1.
        Segments: MSH | EVN | PID | PV1, CR-terminated (\\r).
        No check digit — transport reliability delegated to TCP/IP per HL7 spec.
        """
        ts    = datetime.now().strftime("%Y%m%d%H%M%S")
        # Date of birth: random year 1940–2000, random month 01–12, day 01–28
        dob   = (f"{random.randint(1940, 2000)}"
                 f"{random.randint(1, 12):02d}"
                 f"{random.randint(1, 28):02d}")

        sending_app  = random.choice(_HL7_APPS)
        sending_fac  = random.choice(_HL7_FACILITIES)
        recv_app     = random.choice(_HL7_APPS)
        recv_fac     = random.choice(_HL7_FACILITIES)
        ctrl_id      = "MSG" + secrets.token_hex(4).upper()  # MSG + 8 hex chars = 11 chars total
        last         = random.choice(_HL7_LAST_NAMES)
        first        = random.choice(_HL7_FIRST_NAMES)
        gender       = random.choice(["M", "F"])
        mrn          = f"MRN{random.randint(100000, 999999)}"
        unit         = random.choice(_HL7_UNITS)
        room         = random.randint(100, 499)
        bed          = random.choice(["A", "B", "C"])
        physician    = random.choice(_HL7_PHYSICIANS)

        SEP = "|"
        msh = SEP.join([
            "MSH", r"^~\&", sending_app, sending_fac, recv_app, recv_fac,
            ts, "", "ADT^A01^ADT_A01", ctrl_id, "P", "2.5",
        ])
        evn = SEP.join(["EVN", "A01", ts])
        pid = SEP.join([
            "PID", "1", "", f"{mrn}^^^{sending_fac}^MR", "",
            f"{last}^{first}^", "", dob, gender,
            "", "", "", "", "S",
        ])
        pv1 = SEP.join([
            "PV1", "1", "I", f"{unit}^{room}^{bed}", "E",
            "", "", physician, "", "", "MED", "", "", "A",
        ])
        return "\r".join([msh, evn, pid, pv1]) + "\r"

    @staticmethod
    def generate_fhir_patient(locale: str = "TR") -> str:
        """
        FHIR R4 Patient resource (JSON string).
        HL7 FHIR v4.0.1 §8.1 — resourceType Patient.
        Locale-aware: names, city, and ISO 3166-1 country code.
        """
        loc       = locale.upper() if locale.upper() in _FHIR_FAMILIES else "US"
        gender    = random.choice(["male", "female", "other", "unknown"])
        families  = _FHIR_FAMILIES.get(loc, _FHIR_FAMILIES["US"])
        givens_m  = _FHIR_GIVENS_M.get(loc, _FHIR_GIVENS_M["US"])
        givens_f  = _FHIR_GIVENS_F.get(loc, _FHIR_GIVENS_F["US"])
        givens    = givens_f if gender == "female" else givens_m
        family    = random.choice(families)
        given     = random.choice(givens)
        cities    = _FHIR_CITIES.get(loc, _FHIR_CITIES["US"])
        country   = _FHIR_COUNTRY_CODE.get(loc, loc)
        city      = random.choice(cities)
        birth_yr  = random.randint(1940, 2005)
        birth_mo  = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_dt  = f"{birth_yr}-{birth_mo:02d}-{birth_day:02d}"
        now_iso   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        patient_id = str(_uuid.uuid4())

        resource = {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": now_iso,
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                ],
            },
            "active": True,
            "identifier": [
                {
                    "use": "official",
                    "system": "urn:oid:2.16.840.1.113883.4.1",
                    "value": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": family,
                    "given": [given],
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": f"+{_E164_CC.get(loc, '90')}-{random.randint(100,999)}-{random.randint(1000000,9999999)}",
                    "use": "home",
                }
            ],
            "gender": gender,
            "birthDate": birth_dt,
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "city": city,
                    "country": country,
                }
            ],
        }
        return json.dumps(resource, ensure_ascii=False)

    @staticmethod
    def generate_dicom_uid() -> str:
        """
        DICOM UID — root 2.25 (ISO/IEC 9834-8, UUID-based org root).
        NEMA DICOM PS3.5 §9.1: only digits and dots, max 64 chars,
        no component starts with 0 (unless the component is '0' itself).
        Suffix = 128-bit random integer represented as decimal (≤ 39 digits).
        """
        # 16 random bytes = 128-bit integer; strip leading zeros from decimal repr.
        decimal_suffix = str(int.from_bytes(secrets.token_bytes(16), "big"))
        return f"{_DICOM_ROOT}.{decimal_suffix}"

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
        if dt == "npi":
            return self.generate_npi()
        if dt == "bmi":
            return self.generate_bmi()
        if dt == "hl7message":
            return self.generate_hl7_message()
        if dt == "fhirpatient":
            return self.generate_fhir_patient(locale)
        if dt == "dicomuid":
            return self.generate_dicom_uid()
        return None
