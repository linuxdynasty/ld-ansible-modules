#!/usr/bin/python

import boto3
import unittest

import ec2_vpc_nat_gateway as ng

aws_region = 'us-west-2'


class AnsibleEc2VpcNatGatewayFunctions(unittest.TestCase):

    def test_convert_to_lower(self):
        example = ng.DRY_RUN_GATEWAY_UNCONVERTED
        converted_example = ng.convert_to_lower(example[0])
        keys = converted_example.keys()
        keys.sort()
        for i in range(len(keys)):
            if i == 0:
                self.assertEqual(keys[i], 'create_time')
            if i == 1:
                self.assertEqual(keys[i], 'nat_gateway_addresses')
                gw_addresses_keys = converted_example[keys[i]][0].keys()
                gw_addresses_keys.sort()
                for j in range(len(gw_addresses_keys)):
                    if j == 0:
                        self.assertEqual(gw_addresses_keys[j], 'allocation_id')
                    if j == 1:
                        self.assertEqual(gw_addresses_keys[j], 'network_interface_id')
                    if j == 2:
                        self.assertEqual(gw_addresses_keys[j], 'private_ip')
                    if j == 3:
                        self.assertEqual(gw_addresses_keys[j], 'public_ip')
            if i == 2:
                self.assertEqual(keys[i], 'nat_gateway_id')
            if i == 3:
                self.assertEqual(keys[i], 'state')
            if i == 4:
                self.assertEqual(keys[i], 'subnet_id')
            if i == 5:
                self.assertEqual(keys[i], 'vpc_id')

    def test_get_nat_gateways(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, err_msg, stream = (
            ng.get_nat_gateways(client, 'subnet-123456789', check_mode=True)
        )
        should_return = ng.DRY_RUN_GATEWAYS
        self.assertTrue(success)
        self.assertEqual(stream, should_return)

    def test_get_nat_gateways_no_gateways_found(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, err_msg, stream = (
            ng.get_nat_gateways(client, 'subnet-1234567', check_mode=True)
        )
        self.assertTrue(success)
        self.assertEqual(stream, [])

    def test_wait_for_status(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, err_msg, gws = (
            ng.wait_for_status(
                client, 5, 'nat-123456789', 'available', check_mode=True
            )
        )
        should_return = ng.DRY_RUN_GATEWAYS[0]
        self.assertTrue(success)
        self.assertEqual(gws, should_return)

    def test_wait_for_status_to_timeout(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, err_msg, gws = (
            ng.wait_for_status(
                client, 2, 'nat-12345678', 'available', check_mode=True
            )
        )
        self.assertFalse(success)
        self.assertEqual(gws, {})

    def test_gateway_in_subnet_exists_with_allocation_id(self):
        client = boto3.client('ec2', region_name=aws_region)
        gws, err_msg = (
            ng.gateway_in_subnet_exists(
                client, 'subnet-123456789', 'eipalloc-1234567', check_mode=True
            )
        )
        should_return = ng.DRY_RUN_GATEWAYS
        self.assertEqual(gws, should_return)

    def test_gateway_in_subnet_exists_with_allocation_id_does_not_exist(self):
        client = boto3.client('ec2', region_name=aws_region)
        gws, err_msg = (
            ng.gateway_in_subnet_exists(
                client, 'subnet-123456789', 'eipalloc-123', check_mode=True
            )
        )
        should_return = list()
        self.assertEqual(gws, should_return)

    def test_gateway_in_subnet_exists_without_allocation_id(self):
        client = boto3.client('ec2', region_name=aws_region)
        gws, err_msg = (
            ng.gateway_in_subnet_exists(
                client, 'subnet-123456789',  check_mode=True
            )
        )
        should_return = ng.DRY_RUN_GATEWAYS
        self.assertEqual(gws, should_return)

    def test_get_eip_allocation_id_by_address(self):
        client = boto3.client('ec2', region_name=aws_region)
        allocation_id, _ = (
            ng.get_eip_allocation_id_by_address(
                client, '55.55.55.55',  check_mode=True
            )
        )
        should_return = 'eipalloc-1234567'
        self.assertEqual(allocation_id, should_return)

    def test_get_eip_allocation_id_by_address_does_not_exist(self):
        client = boto3.client('ec2', region_name=aws_region)
        allocation_id, err_msg = (
            ng.get_eip_allocation_id_by_address(
                client, '52.52.52.52',  check_mode=True
            )
        )
        self.assertEqual(err_msg, 'EIP 52.52.52.52 does not exist')
        self.assertIsNone(allocation_id)

    def test_allocate_eip_address(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, err_msg, eip_id = (
            ng.allocate_eip_address(
                client, check_mode=True
            )
        )
        self.assertTrue(success)

    def test_release_address(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, _ = (
            ng.release_address(
                client, 'eipalloc-1234567', check_mode=True
            )
        )
        self.assertTrue(success)

    def test_create(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, results = (
            ng.create(
                client, 'subnet-123456', 'eipalloc-1234567', check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertTrue(changed)

    def test_pre_create(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, results = (
            ng.pre_create(
                client, 'subnet-123456', check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertTrue(changed)

    def test_pre_create_idemptotent_with_allocation_id(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, results = (
            ng.pre_create(
                client, 'subnet-123456789', allocation_id='eipalloc-1234567', check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertFalse(changed)

    def test_pre_create_idemptotent_with_eip_address(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, results = (
            ng.pre_create(
                client, 'subnet-123456789', eip_address='55.55.55.55', check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertFalse(changed)

    def test_pre_create_idemptotent_if_exist_do_not_create(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, results = (
            ng.pre_create(
                client, 'subnet-123456789', if_exist_do_not_create=True, check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertFalse(changed)

    def test_delete(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, _ = (
            ng.remove(
                client, 'nat-123456789', check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertTrue(changed)

    def test_delete_and_release_ip(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, _ = (
            ng.remove(
                client, 'nat-123456789', release_eip=True, check_mode=True
            )
        )
        self.assertTrue(success)
        self.assertTrue(changed)

    def test_delete_if_does_not_exist(self):
        client = boto3.client('ec2', region_name=aws_region)
        success, changed, err_msg, _ = (
            ng.remove(
                client, 'nat-12345', check_mode=True
            )
        )
        self.assertFalse(success)
        self.assertFalse(changed)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
