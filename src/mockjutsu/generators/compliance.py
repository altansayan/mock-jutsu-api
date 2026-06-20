"""
mock-jutsu — Compliance / KYC / AML Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import uuid
from datetime import datetime

_PEP_STATUSES      = ['Not PEP', 'PEP', 'RCA', 'Former PEP', 'Unknown']
_AML_RISK_RATINGS  = ['Low', 'Medium', 'High', 'Critical']
_CDD_LEVELS        = ['Standard', 'Enhanced', 'Simplified']
_KYC_DOC_TYPES     = [
    'Passport', 'National ID', "Driver's License", 'Residence Permit',
    'Tax ID', 'Utility Bill', 'Bank Statement', 'Birth Certificate',
]
_ONBOARDING_METHODS = ['eKYC', 'Video KYC', 'In-Branch', 'Document Upload', 'Biometric', 'Agent']


class ComplianceGenerator:
    """Compliance, KYC, AML, and regulatory data generator."""

    def generate(self, data_type: str, locale: str = 'TR', **kwargs):
        dt = data_type.lower().strip()

        if dt == 'policy_number':
            date_part = datetime.now().strftime('%Y%m%d')
            seq = random.randint(10000, 99999)
            return f"POL-{date_part}-{seq}"

        if dt == 'claim_number':
            date_part = datetime.now().strftime('%Y%m%d')
            seq = random.randint(10000, 99999)
            return f"CLM-{date_part}-{seq}"

        if dt == 'pep_status':
            return random.choice(_PEP_STATUSES)

        if dt == 'aml_risk_rating':
            return random.choice(_AML_RISK_RATINGS)

        if dt == 'cdd_level':
            return random.choice(_CDD_LEVELS)

        if dt == 'sar_number':
            date_part = datetime.now().strftime('%Y%m%d')
            seq = random.randint(1000, 999999)
            return f"SAR-{date_part}-{seq:04d}"

        if dt == 'ubo_ownership_percentage':
            # Ownership thresholds: below 25%, 25%+, majority 51%+, full 100%
            tier = random.randrange(10)
            if tier <= 3:
                v = round(0.01 + random.random() * 24.98, 2)
            elif tier <= 7:
                v = round(25.0 + random.random() * 25.99, 2)
            elif tier <= 8:
                v = round(51.0 + random.random() * 48.99, 2)
            else:
                v = 100.00
            return f"{v:.2f}"

        if dt == 'kyc_document_type':
            return random.choice(_KYC_DOC_TYPES)

        if dt == 'consent_id':
            # 80% UUID v4, 20% CONSENT- prefixed
            if random.random() < 0.8:
                return str(uuid.uuid4())
            suffix = str(uuid.uuid4()).replace('-', '').upper()[:12]
            return f"CONSENT-{suffix}"

        if dt == 'tpp_id':
            prefix = random.choice(['PSP', 'TPP'])
            suffix = ''.join(
                random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ0123456789')
                for _ in range(10)
            )
            return f"{prefix}-{suffix}"

        if dt == 'onboarding_method':
            return random.choice(_ONBOARDING_METHODS)

        if dt == 'sanctions_hit':
            return random.random() < 0.05  # 5% hit rate (realistic)

        if dt == 'sar_number_masked':
            # BSA §5318(g)(2) + FinCEN 2010 SAR Advisory: full mask mandatory —
            # any disclosure of SAR existence constitutes tipping-off violation.
            return '****-****-****'

        if dt == 'policy_number_masked':
            # GLBA §501: policy number is NPI — last 5 (sequence) visible for support reference
            seq = random.randint(10000, 99999)
            return f"POL-****-{seq}"

        if dt == 'claim_number_masked':
            # GLBA §501: claim number is NPI — last 5 (sequence) visible for support reference
            seq = random.randint(10000, 99999)
            return f"CLM-****-{seq}"

        if dt == 'ubo_ownership_percentage_masked':
            # EU 4AMLD/5AMLD Art. 30: exact beneficial ownership % is confidential
            return '**%'

        if dt == 'consent_id_masked':
            # GDPR Art. 7 + ePrivacy: consent ID is internal reference — last 8 hex chars visible
            full = str(uuid.uuid4())  # xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            last8 = full.replace('-', '')[-8:]
            return f"****-****-****-****-{last8}"

        return f"ERROR: Unknown DataType '{dt}'"
