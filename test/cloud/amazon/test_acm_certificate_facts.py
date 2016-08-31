#!/usr/bin/python

import boto3
import unittest

import acm_certificate_facts as acf


CHECK_MODE = True

class AnsibleACMFunctions(unittest.TestCase):

    def test_convert_to_lower(self):
        example = acf.DESCRIBE_CERTIFICATE
        converted_example = acf.convert_to_lower(example)
        keys = converted_example.keys()
        keys.sort()
        keys_to_match = [
            u'certificate_arn', u'created_at', u'domain_name',
            u'domain_validation_options', u'in_use_by', u'issued_at',
            u'issuer', u'key_algorithm', u'not_after', u'not_before',
            u'serial', u'signature_algorithm', u'status', u'subject',
            u'subject_alternative_names'
        ]
        for i in range(len(keys)):
            if keys[i] == keys_to_match[i]:
                self.assertEqual(keys[i], keys_to_match[i])

    def test_describe_certificate_pass(self):
        client = boto3.client('acm', region_name='us-west-2')
        arn = 'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7'
        success, err_msg, results = acf.describe_certificate(client, arn, CHECK_MODE)
        self.assertTrue(success)
        self.assertEqual(err_msg, '')
        self.assertEqual(results, acf.DESCRIBE_CERTIFICATE)


    def test_describe_certificate_fail(self):
        client = boto3.client('acm', region_name='us-west-2')
        arn = 'arn:aws:acm:us-west-2:123456789:certificate/donotexist'
        success, err_msg, results = acf.describe_certificate(client, arn, CHECK_MODE)
        msg_to_match = 'Could not find certificate {0} in account {1}'.format(arn, '123456789')
        self.assertFalse(success)
        self.assertEqual(err_msg, msg_to_match)
        self.assertEqual(results, dict())


    def test_list_certificates(self):
        client = boto3.client('acm', region_name='us-west-2')
        success, err_msg, results = acf.list_certificates(client, CHECK_MODE)
        self.assertTrue(success)
        self.assertEqual(err_msg, '')
        self.assertEqual(results, acf.LIST_CERTIFICATES)


    def test_get_acm_arn_pass(self):
        client = boto3.client('acm', region_name='us-west-2')
        _, _, certs = acf.list_certificates(client, CHECK_MODE)
        matched_arn = 'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7'
        arn = acf.get_acm_arn('*.api.foo.com', certs)
        self.assertEqual(arn, matched_arn)


    def test_get_acm_arn_fail(self):
        client = boto3.client('acm', region_name='us-west-2')
        _, _, certs = acf.list_certificates(client, CHECK_MODE)
        arn = acf.get_acm_arn('*.api.bar.com', certs)
        self.assertEqual(arn, None)


    def test_get_acm_certs_by_domain_name_pass(self):
        client = boto3.client('acm', region_name='us-west-2')
        domain_name = '*.api.foo.com'
        success, err_msg, results = (
            acf.get_acm_certs(client, domain_name=domain_name, check_mode=CHECK_MODE)
        )
        matched_results = acf.convert_to_lower(acf.DESCRIBE_CERTIFICATE)
        self.maxDiff = None
        self.assertTrue(success)
        self.assertEqual(err_msg, '')
        self.assertDictEqual(results[domain_name], matched_results)


    def test_get_acm_certs_by_domain_name_fail(self):
        client = boto3.client('acm', region_name='us-west-2')
        domain_name = '*.api.bar.com'
        success, err_msg, results = (
            acf.get_acm_certs(client, domain_name=domain_name, check_mode=CHECK_MODE)
        )
        self.assertFalse(success)
        self.assertEqual(err_msg, 'Certificate {0} does not exist'.format(domain_name))
        self.assertDictEqual(results, {})


    def test_get_acm_certs_by_arn_pass(self):
        client = boto3.client('acm', region_name='us-west-2')
        arn = 'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7'
        domain_name = '*.api.foo.com'
        success, err_msg, results = (
            acf.get_acm_certs(client, arn=arn, check_mode=CHECK_MODE)
        )
        matched_results = acf.convert_to_lower(acf.DESCRIBE_CERTIFICATE)
        self.maxDiff = None
        self.assertTrue(success)
        self.assertEqual(err_msg, '')
        self.assertDictEqual(results[domain_name], matched_results)


    def test_get_acm_certs_by_arn_fail(self):
        client = boto3.client('acm', region_name='us-west-2')
        domain_name = '*.api.bar.com'
        arn = 'arn:aws:acm:us-west-2:123456789:certificate/donotexist'
        success, err_msg, results = (
            acf.get_acm_certs(client, arn=arn, check_mode=CHECK_MODE)
        )
        self.assertFalse(success)
        self.assertDictEqual(results, {})

def main():
    unittest.main()

if __name__ == '__main__':
    main()
