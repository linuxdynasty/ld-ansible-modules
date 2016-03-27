#!/usr/bin/python

import boto3
import unittest

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager

import cloud.amazon.ec2_vpc_nat_gateway as ng

Options = (
    namedtuple(
        'Options', [
            'connection', 'module_path', 'forks', 'become', 'become_method',
            'become_user', 'remote_user', 'private_key_file', 'ssh_common_args',
            'sftp_extra_args', 'scp_extra_args', 'ssh_extra_args', 'verbosity',
            'check'
        ]
    )
)
# initialize needed objects
variable_manager = VariableManager()
loader = DataLoader()
options = (
    Options(
        connection='local',
        module_path='cloud/amazon',
        forks=1, become=None, become_method=None, become_user=None, check=True,
        remote_user=None, private_key_file=None, ssh_common_args=None,
        sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None,
        verbosity=3
    )
)
passwords = dict(vault_pass='')

aws_region = 'us-west-2'

# create inventory and pass to var manager
inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list='localhost')
variable_manager.set_inventory(inventory)

def run(play):
    tqm = None
    results = None
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=passwords,
                stdout_callback='default',
            )
        results = tqm.run(play)
        print tqm._stats.__dict__
    finally:
        if tqm is not None:
            tqm.cleanup()
    return tqm, results

class AnsibleVpcNatGatewayTasks(unittest.TestCase):

    def test_create_gateway_using_allocation_id(self):
        play_source =  dict(
            name = "Create new nat gateway with eip allocation-id",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            subnet_id='subnet-12345678',
                            allocation_id='eipalloc-12345678',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.failUnless(tqm._stats.changed['localhost'] == 1)

    def test_create_gateway_using_allocation_id_idempotent(self):
        play_source =  dict(
            name = "Create new nat gateway with eip allocation-id",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            subnet_id='subnet-123456789',
                            allocation_id='eipalloc-1234567',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.assertFalse(tqm._stats.changed.has_key('localhost'))

    def test_create_gateway_using_eip_address(self):
        play_source =  dict(
            name = "Create new nat gateway with eip address",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            subnet_id='subnet-12345678',
                            eip_address='55.55.55.55',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.failUnless(tqm._stats.changed['localhost'] == 1)

    def test_create_gateway_using_eip_address_idempotent(self):
        play_source =  dict(
            name = "Create new nat gateway with eip address",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            subnet_id='subnet-123456789',
                            eip_address='55.55.55.55',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.assertFalse(tqm._stats.changed.has_key('localhost'))

    def test_create_gateway_in_subnet_only_if_one_does_not_exist_already(self):
        play_source =  dict(
            name = "Create new nat gateway only if one does not exist already",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            if_exist_do_not_create='yes',
                            subnet_id='subnet-123456789',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.assertFalse(tqm._stats.changed.has_key('localhost'))

    def test_delete_gateway(self):
        play_source =  dict(
            name = "Delete Nat Gateway",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [
                dict(
                    action=dict(
                        module='ec2_vpc_nat_gateway',
                        args=dict(
                            nat_gateway_id='nat-123456789',
                            state='absent',
                            wait='yes',
                            region=aws_region,
                        )
                    ),
                    register='nat_gateway',
                ),
                dict(
                    action=dict(
                        module='debug',
                        args=dict(
                            msg='{{nat_gateway}}'
                        )
                    )
                )
            ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm, results = run(play)
        self.failUnless(tqm._stats.ok['localhost'] == 2)
        self.assertTrue(tqm._stats.changed.has_key('localhost'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
