"""
mock-jutsu — Core Orchestrator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import unicodedata

from .generators.identity      import IdentityGenerator
from .generators.financial     import FinancialGenerator
from .generators.communication import CommunicationGenerator
from .generators.meta          import MetaGenerator
from .generators.banking       import BankingGenerator
from .generators.corporate     import CorporateGenerator
from .generators.health        import HealthGenerator
from .generators.commerce      import CommerceGenerator
from .generators.iot           import IoTGenerator
from .generators.barcode       import BarcodeGenerator
from .generators.telecom       import TelecomGenerator
from .generators.financial_markets import FinancialMarketsGenerator
from .generators.crypto            import CryptoGenerator
from .generators.ecommerce         import EcommerceGenerator
from .generators.location          import LocationGenerator
from .generators.social            import SocialGenerator
from .generators.hardware          import HardwareGenerator
from .generators.security          import SecurityGenerator
from .generators.aviation          import AviationGenerator
from .generators.reverse_regex     import ReverseRegexGenerator
from .generators.fido2             import Fido2Generator
from .generators.wallet            import WalletGenerator
from .generators.ai_vector         import AiVectorGenerator
from .generators.oidc              import OidcGenerator
from .generators.bank_statement    import BankStatementGenerator
from .generators.edi               import EdiGenerator
from .generators.event_sourcing    import EventSourcingGenerator
from .generators.telemetry         import TelemetryGenerator
from .generators.crypto_fuzz       import CryptoFuzzGenerator
from .generators.mrz               import MrzGenerator
from .generators.ohlcv             import OhlcvGenerator
from .generators.nmea              import NmeaGenerator
from .generators.prometheus        import PrometheusGenerator
from .generators.gamedev           import GameDevGenerator
from .generators.ubl               import UblGenerator
from .generators.automotive        import AutomotiveGenerator
from .generators.tle               import TleGenerator
from .generators.communication     import EMAIL_DOMAINS

_IDENTITY_TYPES = {
    'tckn', 'ykn', 'taxid', 'vkn', 'nationalid', 'ssn', 'nin',
    'inn', 'inn_individual', 'snils',
    'sgk', 'mersis',
    'ein',
    'utr', 'crn', 'paye',
    'ust_id', 'ustid', 'hrb', 'rvn',
    'siren', 'siret', 'tva',
    'ogrn', 'kpp',
    'employer_id', 'insurance_id',
    'firstname', 'lastname', 'fullname', 'patronymic',
    'passport', 'license', 'age', 'gender', 'birthdate',
    'tckn_masked', 'ssn_masked', 'nationality',
    'vat_number',
}

_FINANCIAL_TYPES = {
    'cardnum', 'cardnetwork', 'cardtype', 'cardstatus', 'cvv3', 'cvv4',
    'issuer', 'expiry', 'expirymonth', 'expiryyear', 'pin', 'balance',
    'iban', 'cardcategory', 'credit_score', 'sepa_qr', 'emv_qr_p2p',
    'emv_qr_atm', 'emv_qr_pos', '3ds_cavv', '3ds_eci',
}

_COMM_TYPES = {
    'phone', 'phone_country', 'phone_area', 'phone_local',
    'address_city', 'address_street', 'address_full',
    'postalcode', 'plate', 'email',
}

_META_TYPES = {
    'uuid', 'requestid', 'correlationid', 'sessionid', 'idempotencykey',
    'deviceid', 'ipv4', 'ipv6', 'browser_name', 'browser_version',
    'browser_engine', 'useragent', 'timestamp', 'timestamp_iso',
    'clientversion', 'bearertoken', 'signature', 'apppassword',
    'jwt', 'hash', 'mac_address', 'domain', 'url', 'color',
    'api_key', 'totp_code', 'webhook_signature', 'transaction_id',
    'public_ip', 'private_ip',
}

_REVERSE_REGEX_TYPES = {'regex_string'}

_BANKING_TYPES = {
    'swift', 'bic', 'sort_code', 'routing_number', 'bik_code',
    'transaction', 'bank_name', 'sepa_ref', 'creditor_ref',
}

_CORPORATE_TYPES = {
    'company_name', 'job_title', 'occupation', 'jobtitle',
}

_HEALTH_TYPES = {
    'blood_type', 'bloodtype', 'nhs_number', 'nhsnumber',
    'icd10', 'height', 'weight', 'npi', 'bmi',
    'hl7_message', 'fhir_patient', 'dicom_uid',
}

_COMMERCE_TYPES = {
    'currency', 'tax_rate', 'taxrate', 'invoice_number', 'invoicenumber',
    'vin', 'vehicle',
}

_IOT_TYPES = {
    'rfid_uid', 'epc', 'rfid_tag',
    'nfc_uid', 'nfc_atqa', 'nfc_sak', 'ndef_uri', 'ndef_text', 'apdu', 'nfc_tag',
    'ir_nec', 'ir_rc5', 'ir_pronto', 'ir_raw',
    'mqtt_payload', 'lora_packet',
}

_BARCODE_TYPES = {
    'ean13', 'ean8', 'upca', 'isbn13', 'isbn10', 'gs1_128',
}

_TELECOM_TYPES = {
    'imei', 'imei2', 'iccid', 'imsi', 'msisdn',
}

_SECURITIES_TYPES = {
    'isin', 'cusip', 'sedol', 'lei', 'fix_message', 'psd2_consent',
}

_CRYPTO_TYPES = {
    'btc_address', 'eth_address', 'crypto_address', 'tx_hash', 'block_hash',
    'mnemonic',
}

_ECOMMERCE_TYPES = {
    'product_name', 'sku', 'order_id', 'tracking_number', 'category', 'rating',
    'dhl_tracking',
}

_LOCATION_TYPES = {
    'latitude', 'longitude', 'timezone', 'country_code', 'coordinates',
}

_SOCIAL_TYPES = {
    'username', 'hashtag', 'bio', 'handle', 'follower_count',
}

_HARDWARE_TYPES = {
    'track2_data', 'chip_data', 'pin_block',
}

_CYBERSEC_TYPES = {
    'cef_log', 'x509_cert', 'pcap_hex',
}

_AVIATION_TYPES = {
    'iata_ticket', 'imo_number', 'pnr_code',
}

_FIDO2_TYPES = {
    'webauthn_credential', 'fido2_assertion',
}

_WALLET_TYPES = {
    'eth_wallet', 'btc_wallet', 'sol_wallet',
}

_AI_VECTOR_TYPES = {
    'ai_embedding', 'ai_vector', 'ai_sparse_vector',
}

_OIDC_TYPES = {
    'oidc_token_set', 'jwks', 'oidc_token',
}

_BANK_STATEMENT_TYPES = {
    'mt940', 'camt053',
}

_EDI_TYPES = {
    'edi_850', 'edifact_orders',
}

_EVENT_SOURCING_TYPES = {
    'event_stream', 'cdc_event',
}

_TELEMETRY_TYPES = {
    'fdr_record', 'drone_telemetry',
}

_CRYPTO_FUZZ_TYPES = {
    'jwt_attack', 'asn1_fuzz',
}

_MRZ_TYPES = {
    'mrz_td3', 'mrz_td1',
}

_OHLCV_TYPES = {
    'ohlcv_candles', 'market_tick',
}

_NMEA_TYPES = {
    'nmea_gpgga', 'nmea_gprmc',
}

_PROMETHEUS_TYPES = {
    'prometheus_metrics', 'openmetrics_snapshot',
}

_GAMEDEV_TYPES = {
    'quaternion', 'navmesh_path',
}

_UBL_TYPES = {
    'ubl_invoice', 'xmldsig',
}

_AUTOMOTIVE_TYPES = {
    'can_frame', 'obd2_response',
}

_TLE_TYPES = {
    'tle_satellite',
}


class MockJutsuCore:
    """Master orchestrator — 6 locales, 182 data types."""

    def __init__(self, locale='TR'):
        self.locale     = str(locale).upper()
        self.identity   = IdentityGenerator()
        self.financial  = FinancialGenerator()
        self.comm       = CommunicationGenerator()
        self.meta       = MetaGenerator()
        self.banking    = BankingGenerator()
        self.corporate  = CorporateGenerator()
        self.health     = HealthGenerator()
        self.commerce   = CommerceGenerator()
        self.iot        = IoTGenerator()
        self.barcode    = BarcodeGenerator()
        self.telecom    = TelecomGenerator()
        self.securities = FinancialMarketsGenerator()
        self.crypto     = CryptoGenerator()
        self.ecommerce  = EcommerceGenerator()
        self.location   = LocationGenerator()
        self.social     = SocialGenerator()
        self.hardware   = HardwareGenerator()
        self.cybersec   = SecurityGenerator()
        self.aviation       = AviationGenerator()
        self.reverse_regex  = ReverseRegexGenerator()
        self.fido2          = Fido2Generator()
        self.wallet         = WalletGenerator()
        self.ai_vector      = AiVectorGenerator()
        self.oidc           = OidcGenerator()
        self.bank_statement = BankStatementGenerator()
        self.edi            = EdiGenerator()
        self.event_sourcing = EventSourcingGenerator()
        self.telemetry      = TelemetryGenerator()
        self.crypto_fuzz    = CryptoFuzzGenerator()
        self.mrz            = MrzGenerator()
        self.ohlcv          = OhlcvGenerator()
        self.nmea           = NmeaGenerator()
        self.prometheus     = PrometheusGenerator()
        self.gamedev        = GameDevGenerator()
        self.ubl            = UblGenerator()
        self.automotive     = AutomotiveGenerator()
        self.tle            = TleGenerator()

    # ── Single value ────────────────────────────────────────────────────────────

    def generate(self, data_type, **kwargs):
        if not data_type:
            return "ERROR: Missing DataType"
        dt     = str(data_type).lower().strip()
        locale = str(kwargs.pop('locale', self.locale)).upper()
        prefix = str(kwargs.pop('prefix', ''))

        result = ""
        if dt == 'apppassword':
            result = self.meta.generate(dt, **kwargs)
        elif dt == 'cardowner':
            result = str(self.identity.generate('fullname', locale=locale, **kwargs)).upper()
        elif dt in _IDENTITY_TYPES:
            result = self.identity.generate(dt, locale=locale, **kwargs)
        elif dt in _FINANCIAL_TYPES:
            result = self.financial.generate(dt, locale=locale, **kwargs)
        elif dt in _COMM_TYPES:
            result = self.comm.generate(dt, locale=locale, **kwargs)
        elif dt in _META_TYPES:
            result = self.meta.generate(dt, locale=locale, **kwargs)
        elif dt in _BANKING_TYPES:
            result = self.banking.generate(dt, locale=locale, **kwargs)
        elif dt in _CORPORATE_TYPES:
            result = self.corporate.generate(dt, locale=locale, **kwargs)
        elif dt in _HEALTH_TYPES:
            result = self.health.generate(dt, locale=locale, **kwargs)
        elif dt in _COMMERCE_TYPES:
            result = self.commerce.generate(dt, locale=locale, **kwargs)
        elif dt in _IOT_TYPES:
            result = self.iot.generate(dt, locale=locale, **kwargs)
        elif dt in _BARCODE_TYPES:
            result = self.barcode.generate(dt, locale=locale, **kwargs)
        elif dt in _TELECOM_TYPES:
            result = self.telecom.generate(dt, locale=locale, **kwargs)
        elif dt in _SECURITIES_TYPES:
            result = self.securities.generate(dt, locale=locale, **kwargs)
        elif dt in _CRYPTO_TYPES:
            result = self.crypto.generate(dt, **kwargs)
        elif dt in _ECOMMERCE_TYPES:
            result = self.ecommerce.generate(dt, **kwargs)
        elif dt in _LOCATION_TYPES:
            result = self.location.generate(dt, locale=locale, **kwargs)
        elif dt in _SOCIAL_TYPES:
            result = self.social.generate(dt, **kwargs)
        elif dt in _HARDWARE_TYPES:
            result = self.hardware.generate(dt, **kwargs)
        elif dt in _CYBERSEC_TYPES:
            result = self.cybersec.generate(dt, **kwargs)
        elif dt in _AVIATION_TYPES:
            result = self.aviation.generate(dt, **kwargs)
        elif dt in _REVERSE_REGEX_TYPES:
            result = self.reverse_regex.generate(dt, **kwargs)
        elif dt in _FIDO2_TYPES:
            result = self.fido2.generate(dt, **kwargs)
        elif dt in _WALLET_TYPES:
            result = self.wallet.generate(dt, **kwargs)
        elif dt in _AI_VECTOR_TYPES:
            result = self.ai_vector.generate(dt, **kwargs)
        elif dt in _OIDC_TYPES:
            result = self.oidc.generate(dt, **kwargs)
        elif dt in _BANK_STATEMENT_TYPES:
            result = self.bank_statement.generate(dt, locale=locale, **kwargs)
        elif dt in _EDI_TYPES:
            result = self.edi.generate(dt, **kwargs)
        elif dt in _EVENT_SOURCING_TYPES:
            result = self.event_sourcing.generate(dt, **kwargs)
        elif dt in _TELEMETRY_TYPES:
            result = self.telemetry.generate(dt, **kwargs)
        elif dt in _CRYPTO_FUZZ_TYPES:
            result = self.crypto_fuzz.generate(dt, **kwargs)
        elif dt in _MRZ_TYPES:
            result = self.mrz.generate(dt, **kwargs)
        elif dt in _OHLCV_TYPES:
            result = self.ohlcv.generate(dt, **kwargs)
        elif dt in _NMEA_TYPES:
            result = self.nmea.generate(dt, **kwargs)
        elif dt in _PROMETHEUS_TYPES:
            result = self.prometheus.generate(dt, **kwargs)
        elif dt in _GAMEDEV_TYPES:
            result = self.gamedev.generate(dt, **kwargs)
        elif dt in _UBL_TYPES:
            result = self.ubl.generate(dt, **kwargs)
        elif dt in _AUTOMOTIVE_TYPES:
            result = self.automotive.generate(dt, **kwargs)
        elif dt in _TLE_TYPES:
            result = self.tle.generate(dt, **kwargs)
        else:
            return f"ERROR: Unknown DataType '{dt}'"

        if prefix and not str(result).startswith("ERROR"):
            return f"{prefix}{result}"
        return result

    # ── Bulk ────────────────────────────────────────────────────────────────────

    def bulk(self, data_type, count=10, **kwargs):
        """Generate a list of values for the same data type."""
        return [self.generate(data_type, **kwargs) for _ in range(count)]

    # ── Template ────────────────────────────────────────────────────────────────

    def template(self, schema, count=10, locale='TR'):
        """Generate structured records from a schema.

        schema accepts:
          - dict:        {field_name: data_type}  — custom field names
          - list/tuple:  [data_type, ...]          — field name equals type name
        """
        loc = str(locale).upper()
        if isinstance(schema, (list, tuple)):
            schema = {t: t for t in schema}
        return [
            {key: self.generate(dt, locale=loc) for key, dt in schema.items()}
            for _ in range(count)
        ]

    # ── Profile ─────────────────────────────────────────────────────────────────

    def profile(self, locale='TR'):
        """Generate a complete, consistent person profile for a given locale."""
        l      = str(locale).upper()
        gender = random.choice(['male', 'female'])
        fn     = self.identity.generate('firstname', locale=l, gender=gender)
        ln     = self.identity.generate('lastname',  locale=l, gender=gender)

        # Build locale-aware email from name
        fn_norm = self._normalize_name(fn)
        ln_norm = self._normalize_name(ln)
        sep     = random.choice(['', '.', '_'])
        num     = str(random.randint(1, 999)) if random.random() > 0.5 else ''
        domain  = random.choice(EMAIL_DOMAINS.get(l, EMAIL_DOMAINS["TR"]))
        email   = f"{fn_norm}{sep}{ln_norm}{num}@{domain}"

        fullname = (
            f"{fn} {self.identity.generate('patronymic', locale=l, gender=gender)} {ln}"
            if l == 'RU' else f"{fn} {ln}"
        )

        return {
            "id":         str(self.meta.generate('uuid')),
            "firstname":  fn,
            "lastname":   ln,
            "fullname":   fullname,
            "gender":     gender[0].upper(),
            "birthdate":  self.identity.generate('birthdate'),
            "nationalid": self.identity.generate('nationalid', locale=l),
            "phone":      self.comm.generate('phone', locale=l),
            "email":      email,
            "address":    self.comm.generate('address_full', locale=l),
            "iban":       self.financial.generate('iban', locale=l),
        }

    # ── Company ─────────────────────────────────────────────────────────────────

    def company(self, locale='TR'):
        """Generate a complete company profile for a given locale."""
        l = str(locale).upper()
        return {
            "id":          str(self.meta.generate('uuid')),
            "name":        self.corporate.generate('company_name', locale=l),
            "employer_id": self.identity.generate('employer_id',  locale=l),
            "tax_id":      self.identity.generate('taxid',         locale=l),
            "iban":        self.financial.generate('iban',         locale=l),
            "bic":         self.banking.generate('swift',          locale=l),
            "phone":       self.comm.generate('phone',             locale=l),
            "address":     self.comm.generate('address_full',      locale=l),
        }

    # ── Export ──────────────────────────────────────────────────────────────────

    def export(self, schema: dict, count=10, format='json', locale='TR', table='records'):
        """Export generated records as JSON, CSV, or SQL INSERT statements."""
        import json
        records = self.template(schema, count=count, locale=locale)

        if format == 'json':
            return json.dumps(records, ensure_ascii=False, indent=2)

        if format == 'csv':
            if not records:
                return ''
            headers = list(records[0].keys())
            lines   = [','.join(headers)]
            for row in records:
                cells = []
                for v in row.values():
                    s = str(v)
                    cells.append(f'"{s}"' if (',' in s or '"' in s) else s)
                lines.append(','.join(cells))
            return '\n'.join(lines)

        if format == 'sql':
            if not records:
                return ''
            headers  = list(records[0].keys())
            col_list = ', '.join(headers)
            rows     = []
            for row in records:
                vals = []
                for v in row.values():
                    if isinstance(v, (int, float)):
                        vals.append(str(v))
                    else:
                        vals.append("'" + str(v).replace("'", "''") + "'")
                rows.append(f"  ({', '.join(vals)})")
            return f"INSERT INTO {table} ({col_list}) VALUES\n" + ',\n'.join(rows) + ';'

        return json.dumps(records, ensure_ascii=False, indent=2)

    # ── Internal ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize_name(s):
        """Lowercase + remove diacritics + remove non-ASCII for email use."""
        normalized = unicodedata.normalize('NFD', s.lower())
        ascii_only = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return ''.join(c if c.isalnum() else '' for c in ascii_only)


jutsu = MockJutsuCore()
