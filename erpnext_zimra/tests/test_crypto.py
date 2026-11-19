import unittest
from datetime import datetime, date
from erpnext_zimra.services.crypto import (
    minor_units, percent_text, receipt_signature_input, fiscal_day_counters_input,
    fiscal_day_signature_input, sha256_b64, create_csr
)
from cryptography import x509
from cryptography.hazmat.primitives import serialization

class TestZimraCrypto(unittest.TestCase):
    def test_minor_units(self):
        self.assertEqual(minor_units("500"), "50000")
        self.assertEqual(minor_units("12.34"), "1234")
        self.assertEqual(minor_units("-1.25"), "-125")

    def test_percent_formatting(self):
        self.assertEqual(percent_text("14.50"), "14.5")
        self.assertEqual(percent_text(None), "")

    def test_receipt_signature_input(self):
        receipt = {"receiptType":"FiscalInvoice","receiptCurrency":"USD","receiptGlobalNo":85,
                   "receiptDate":datetime(2019,9,19,9,23,7),"receiptTotal":"51.50",
                   "receiptTaxes":[
                    {"taxID":2,"taxCode":"B","taxPercent":0,"taxAmount":"0","salesAmountWithTax":"10"},
                    {"taxID":1,"taxCode":"A","taxPercent":None,"taxAmount":"0","salesAmountWithTax":"7"}]}
        expected = "322FISCALINVOICEUSD852019-09-19T09:23:075150A0700B001000"
        self.assertEqual(receipt_signature_input(322, receipt), expected)
        self.assertTrue(receipt_signature_input(322, receipt, "PREV").endswith("PREV"))

    def test_fiscal_day_counters_skip_zero_and_sort(self):
        counters = [
            {"fiscalCounterType":"SaleByTax","fiscalCounterCurrency":"ZWL","fiscalCounterTaxPercent":15,"fiscalCounterValue":"12"},
            {"fiscalCounterType":"SaleByTax","fiscalCounterCurrency":"ZWL","fiscalCounterTaxPercent":0,"fiscalCounterValue":"0"}]
        self.assertEqual(fiscal_day_counters_input(counters), "SALEBYTAXZWL151200")

    def test_fiscal_day_signature_prefix(self):
        self.assertEqual(fiscal_day_signature_input(321,84,date(2019,9,23),[]), "321842019-09-23")

    def test_csr_subject_and_curve(self):
        private_pem, csr_pem = create_csr("SERIAL123",7)
        csr = x509.load_pem_x509_csr(csr_pem.encode())
        self.assertEqual(csr.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value,
                         "ZIMRA-SERIAL123-0000000007")
        key = serialization.load_pem_private_key(private_pem.encode(), password=None)
        self.assertEqual(key.curve.name,"secp256r1")

    def test_hash_is_base64_sha256(self):
        import base64, hashlib
        self.assertEqual(sha256_b64("abc"),base64.b64encode(hashlib.sha256(b"abc").digest()).decode())

if __name__ == "__main__":
    unittest.main()
