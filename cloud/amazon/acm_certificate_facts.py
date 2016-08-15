#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: acm_certificate_facts
short_description: Retrieve the facts of a Certificate from AWS Certificate Manager.
description:
  - Retrieve the attributes of a Certificate from AWS Certificate Manager.
version_added: "2.2"
author: "Allen Sanabria (@linuxdynasty)"
requirements: [boto3, botocore]
options:
  name:
    description:
      - The name of the certificate you are retrieving attributes for.
    required: false
  arn:
    description:
      - The amazon resource identifier of the certificate you are retrieving attributes for.
extends_documentation_fragment:
    - aws
    - ec2
requirements: ['boto3']
'''

EXAMPLES = '''
# Retrieve certificate by domain name
- acm_certificate_facts:
    domain_name: *.foobar.com
  register: acm_cert

# Retrieve certificate by arn (Amazon Resource Identifier)
- acm_certificate_facts:
    arn: "arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7" (http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html)
  register: acm_cert

# Retrieve all Amazon certificates.
- acm_certificate_facts:
  register: acm_certs
'''

RETURN = '''
status:
    description: The status of the certificate.
    returned: success
    type: str
    sample: "ISSUED"
domain_name:
    description: The fully qualified domain name (FQDN) for the certificate, such as www.example.com or example.com.
    returned: success
    type: str
    sample: "*.foobar.com"
certificate_arn:
    description: The Amazon Resource Identifier (http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html)
    returned: success
    type: str
    sample: "arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7"
signature_algorithm:
    description: The algorithm used to generate a signature. Currently the only supported value is SHA256WITHRSA
    returned: success
    type: str
    sample: SHA256WITHRSA
key_algorithm:
    description: The algorithm used to generate the key pair (the public and private key). Currently the only supported value is RSA_2048.
    returned: success
    type: str
    sample: "RSA-2048"
serial:
    description: The serial number of the certificate.
    returned: success
    type: str
    sample: "37:4d:97:96:e5:87:d7:2b:2b:cf:72:ad:1d:71:72:5f"
issuer:
    description: The X.500 distinguished name of the CA that issued and signed the certificate.
    returned: success
    type: str
    sample: "Amazon"
subject:
    description: The X.500 distinguished name of the entity associated with the public key contained in the certificate
    returned: success
    type: str
    sample: "CN=*.foobar.com"
subject_alternative_names:
    description: One or more domain names (subject alternative names) included in the certificate request. After the certificate is issued, this list includes the domain names bound to the public key contained in the certificate. The subject alternative names include the canonical domain name (CN) of the certificate and additional domain names that can be used to connect to the website.
    returned: success
    type: str
    sample: "*.foobar.com"
domain_validation_options:
    description: Contains information about the email address or addresses used for domain validation.
    returned: success
    type: list
    sample: [
        {
            "validation_domain": "foobar.com",
            "domain_name": "*.foobar.com",
            "validation_emails": [
                "webmaster@foobar.com",
                "dnsadmin@foobar.com",
                "admin@foobar.com",
                "administrator@foobar.com",
                "hostmaster@foobar.com",
                "postmaster@foobar.com"
            ]
        }
    ]
issued_at:
    description: The time at which the certificate was issued.
    returned: success
    type: str
    sample: "2017-06-15T12:00:00+00:00"
created_at:
    description: The time at which the certificate was requested.
    returned: success
    type: str
    sample: "2017-06-15T12:00:00+00:00"
not_after:
    description: The time after which the certificate is not valid.
    returned: success
    type: str
    sample: "2017-06-15T12:00:00+00:00"
not_before:
    description: The time before which the certificate is not valid.
    returned: success
    type: str
    sample: "2017-06-15T12:00:00+00:00"
in_use_by:
    description: A list of ARNs for the resources that are using the certificate. An ACM Certificate can be used by multiple AWS resources.
    returned: success
    type: str
    sample: ["arn:aws:elasticloadbalancing:us-west-2:123456789:loadbalancer/super-fast-web-app"]
'''
import datetime
from dateutil.tz import tzlocal

import ansible.module_utils.ec2 as ec2

try:
    import boto3
    import botocore.exceptions
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

ARN = 'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7'
DOMAIN_NAME = '*.api.foo.com'
LIST_CERTIFICATES = [
    {
        u'CertificateArn': ARN,
        u'DomainName': DOMAIN_NAME
    }
]
DESCRIBE_CERTIFICATE = {
    u'CertificateArn': u'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7',
    u'Status': u'ISSUED',
    u'SubjectAlternativeNames': [
        u'*.api.foo.com'
    ],
    u'DomainName': u'*.api.foo.com',
    u'NotBefore': datetime.datetime(2016, 6, 2, 17, 0, tzinfo=tzlocal()),
    u'NotAfter': datetime.datetime(2017, 7, 3, 5, 0, tzinfo=tzlocal()),
    u'KeyAlgorithm': u'RSA-2048',
    u'InUseBy': [],
    u'SignatureAlgorithm': u'SHA256WITHRSA',
    u'CreatedAt': datetime.datetime(2016, 6, 3, 7, 18, 18, tzinfo=tzlocal()),
    u'IssuedAt': datetime.datetime(2016, 6, 3, 10, 32, 39, tzinfo=tzlocal()),
    u'Serial': u'07:4b:97:96:e5:87:e4:2e:0d:ac:34:aa:3d:45:74:6f',
    u'Issuer': u'Amazon',
    u'DomainValidationOptions': [
        {
            u'ValidationEmails': [
                u'webmaster@foo.com', u'admin@foo.com', u'administrator@foo.com', u'hostmaster@foo.com', u'postmaster@foo.com'
            ],
            u'ValidationDomain': u'foo.com',
            u'DomainName': u'*.api.foo.com'
        }
    ],
    u'Subject': u'CN=*.api.foo.com'
}


BOTO_DESCRIBE_ERROR = {
    'Error': {
        'Code': 'ResourceNotFoundException',
        'Message': None
    }
}


@ec2.AWSRetry.backoff()
def describe_certificate(client, arn, check_mode=False):
    """ Wrapper function for describe_certificate
    Args:
        client (botocore.client.acm): The boto3 acm instance.
        arn (str): The Amazon Resource Identifier.

    Basic Usage:
        >>> client = boto3.client('acm', 'us-west-2')
        >>> arn = 'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7'
        >>> describe_certificate(client, arn)
        {
            u'CertificateArn': u'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7',
            u'Status': u'ISSUED',
            u'SubjectAlternativeNames': [
                u'*.api.foo.com'
            ],
            u'DomainName': u'*.api.foo.com',
            u'NotBefore': datetime.datetime(2016, 6, 2, 17, 0, tzinfo=tzlocal()),
            u'NotAfter': datetime.datetime(2017, 7, 3, 5, 0, tzinfo=tzlocal()),
            u'KeyAlgorithm': u'RSA-2048',
            u'InUseBy': [],
            u'SignatureAlgorithm': u'SHA256WITHRSA',
            u'CreatedAt': datetime.datetime(2016, 6, 3, 7, 18, 18, tzinfo=tzlocal()),
            u'IssuedAt': datetime.datetime(2016, 6, 3, 10, 32, 39, tzinfo=tzlocal()),
            u'Serial': u'07:4b:97:96:e5:87:e4:2e:0d:ac:34:aa:3d:45:74:6f',
            u'Issuer': u'Amazon',
            u'DomainValidationOptions': [
                {
                    u'ValidationEmails': [
                        u'webmaster@foo.com', u'admin@foo.com', u'administrator@foo.com', u'hostmaster@foo.com', u'postmaster@foo.com'
                    ],
                    u'ValidationDomain': u'foo.com',
                    u'DomainName': u'*.api.foo.com'
                }
            ],
            u'Subject': u'CN=*.api.foo.com'
        }

    Returns:
        Tuple (bool, str, dict)
    """
    success = True
    err_msg = ''
    results = dict()
    try:
        if not check_mode:
            results = client.describe_certificate(CertificateArn=arn)['Certificate']
        else:
            if arn == ARN:
                results = DESCRIBE_CERTIFICATE
            else:
                account_id =  arn.split(':')[4]
                BOTO_DESCRIBE_ERROR['Error']['Message'] = (
                    'Could not find certificate {0} in account {1}'
                    .format(arn, account_id)
                )
                raise(
                    botocore.exceptions.ClientError(BOTO_DESCRIBE_ERROR, 'DescribeCertificate')
                )

    except Exception as e:
        success = False
        err_msg = e.response['Error']['Message']

    return (success, err_msg, results)


@ec2.AWSRetry.backoff()
def list_certificates(client, check_mode=False):
    """ Wrapper function for list_certificate
    Args:
        client (botocore.client.acm): The boto3 acm instance.

    Basic Usage:
        >>> client = boto3.client('acm', 'us-west-2')
        >>> list_certificate(client)
        [
            {
                u'CertificateArn': u'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7',
                u'DomainName': u'*.api.foo.com'
            }
        ]

    Returns:
        Tuple (bool, str, list)
    """
    success = True
    err_msg = ''
    results = list()
    try:
        if not check_mode:
            results = client.list_certificates()['CertificateSummaryList']
        else:
            results = LIST_CERTIFICATES
    except Exception as e:
        success = False
        err_msg = str(e)

    return (success, err_msg, results)


def get_acm_arn(domain_name, certificates):
    """Retrieve the arn of a certificate from the domain name.
    Args:
        domain_name (str): The domain name of the certificate.
        certificates (list): List of certificates from the list_certificates call.

    Basic Usage:
        >>> import boto3
        >>> acm = boto3.client('acm')
        >>> domain_name = '*.foobar.com'
        >>> acm_certs = acm.list_certificates()['CertificateSummaryList']
        >>> get_acm_arn(domain_name, acm_certs)
        "arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7"

    Returns:
        String
    """
    arn = None
    for cert in certificates:
        if domain_name == cert['DomainName']:
            arn = cert['CertificateArn']
            break
    return arn


def convert_to_lower(data):
    """Convert all uppercase keys in dict with lowercase_
    Args:
        data (dict): Dictionary with keys that have upper cases in them
            Example.. FooBar == foo_bar
            if a val is of type datetime.datetime, it will be converted to
            the ISO 8601
    Basic Usage:
        >>> test = {'FooBar': []}
        >>> test = convert_to_lower(test)
        {
            'foo_bar': []
        }

    Returns:
        Dictionary
    """
    results = dict()
    if isinstance(data, dict):
        for key, val in data.items():
            key = re.sub(r'(([A-Z]{1,3}){1})', r'_\1', key).lower()
            if key[0] == '_':
                key = key[1:]
            if isinstance(val, datetime.datetime):
                results[key] = val.isoformat()
            elif isinstance(val, dict):
                results[key] = convert_to_lower(val)
            elif isinstance(val, list):
                converted = list()
                for item in val:
                    converted.append(convert_to_lower(item))
                results[key] = converted
            else:
                results[key] = val
    elif isinstance(data, basestring):
        return data
    return results


def get_acm_certs(client, domain_name=None, arn=None, check_mode=False):
    """Retrieve the attributes of a certificate if it exists or all certs.
    Args:
        client (botocore.client.acm): The boto3 acm instance.

    Kwargs:
        domain_name (str): The domain name of the certificate.
        arn (str): The Amazon resource identifier of the certificate.

    Basic Usage:
        >>> import boto3
        >>> client = boto3.client('acm')
        >>> results = get_acm_certs(acm)
        (
            True,
            '',
            {
                u'*.api.foo.com': {
                    u'status': u'ISSUED',
                    u'key_algorithm': u'RSA-2048',
                    u'domain_validation_options': [
                        {
                            u'validation_domain': u'foo.com',
                            u'domain_name': u'*.api.foo.com',
                            u'validation_emails': [
                                u'webmaster@foo.com', u'admin@foo.com', u'administrator@foo.com', u'hostmaster@foo.com', u'postmaster@foo.com'
                            ]
                        }
                    ],
                    u'not_after': '2017-07-03T05:00:00-07:00',
                    u'created_at': '2016-06-03T07:18:18-07:00',
                    u'domain_name': u'*.api.foo.com',
                    u'in_use_by': [],
                    u'signature_algorithm': u'SHA256WITHRSA',
                    u'issued_at': '2016-06-03T10:32:39-07:00',
                    u'certificate_arn': u'arn:aws:acm:us-west-2:123456789:certificate/25b4ad8a-1e24-4001-bcd0-e82fb3554cd7',
                    u'subject': u'CN=*.api.foo.com',
                    u'subject_alternative_names': [u'*.api.foo.com'],
                    u'not_before': '2016-06-02T17:00:00-07:00',
                    u'serial': u'07:4b:97:96:e5:87:e4:2e:0d:ac:34:aa:3d:45:74:6f',
                    u'issuer': u'Amazon'
                }
            }
        )

    Returns:
        Tuple (bool, str, dict)
    """
    results = dict()
    success = True
    err_msg = ''
    try:
        if arn:
            success, err_msg, acm_certs = (
                describe_certificate(client, arn, check_mode)
            )
        else:
            success, err_msg, acm_certs = list_certificates(client, check_mode)
            if domain_name and success:
                arn = get_acm_arn(domain_name, acm_certs)
                if not arn:
                    err_msg = (
                        'Certificate {0} does not exist'.format(domain_name)
                    )
                    success = False
                    return success, err_msg, results
                else:
                    success, err_msg, acm_certs = (
                        describe_certificate(client, arn, check_mode)
                    )

        if isinstance(acm_certs, dict):
            acm_certs = [acm_certs]

        for acm_cert in acm_certs:
            if not arn and not domain_name:
                success, err_msg, acm_cert = (
                    describe_certificate(
                        client, acm_cert['CertificateArn'], check_mode
                    )
                )
            if success:
                acm_cert = convert_to_lower(acm_cert)
                results[acm_cert['domain_name']] = acm_cert
            else:
                return success, err_msg, results

    except botocore.exceptions.ClientError as e:
        err_msg = str(e)
        success = False

    return success, err_msg, results


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        domain_name=dict(type='str'),
        arn=dict(type='str'),
    ))

    module = (
        AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
            mutually_exclusive=[
                ['domain_name', 'arn'],
            ],
        )
    )

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        acm = boto3_conn(module, conn_type='client', resource='acm', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Boto3 Client Error - " + str(e.msg))

    check_mode = module.check_mode
    domain_name = module.params.get('domain_name')
    arn = module.params.get('arn')
    success, err_msg, results = get_acm_certs(acm, domain_name, arn, check_mode)
    if success:
        module.exit_json(success=success, results=results)
    else:
        module.fail_json(msg=err_msg)


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
