#!/usr/bin/env python3
# Copyright (c) 2016-2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the Alerts changeover logic."""
import os
import shutil

from decimal import Decimal
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import get_datadir_path, hex_str_to_bytes
from test_framework.address import key_to_p2pkh


class AlertsInstantTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 3
        self.extra_args = [
            [
                "-reindex",
                "-txindex",
            ],
            [
                "-reindex",
                "-txindex",
            ],
            [
                "-reindex",
                "-txindex",
            ],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def find_address(self, listreceivedbyaddress, address):
        for addr in listreceivedbyaddress:
            if addr['address'] == address: return addr

    def find_vout_n(self, rawtransaction, amount):
        for vout in rawtransaction['vout']:
            if vout['value'] == amount: return vout['n']

    def reset_blockchain(self):
        self.stop_nodes(wait=1)
        for i in range(self.num_nodes):
            datadir = get_datadir_path(self.options.tmpdir, i)
            if os.path.exists(datadir):
                shutil.rmtree(datadir)
                os.mkdir(datadir)

        self.nodes = []
        self.setup_chain()
        self.start_nodes(extra_args=self.extra_args)
        self.setup_network()
        self.sync_all()

    def reset_node(self, i):
        self.stop_node(i, wait=1)
        datadir = get_datadir_path(self.options.tmpdir, i)
        if os.path.exists(datadir):
            shutil.rmtree(datadir)
            os.mkdir(datadir)

        self.start_node(i, extra_args=self.extra_args)

    def run_test(self):
        self.alert_recovery_pubkey = "02ecec100acb89f3049285ae01e7f03fb469e6b54d44b0f3c8240b1958e893cb8c"
        self.alert_recovery_privkey = "cRfYLWua6WcpGbxuv5rJgA2eDESWxqgzmQjKQuqDFMfgbnEpqhrP"

        self.alert_instant_pubkey = "0263451a52f3d3ae6918969e1c5ce934743185578481ef8130336ad1726ba61ddb"
        self.alert_instant_privkey = "cN1XR72dusJgxpkT2AwENtTviskB96iB2Q6FTvAxqi24fT9DQZiR"

        self.COINBASE_MATURITY = 100
        self.COINBASE_AMOUNT = Decimal(175)

        self.reset_blockchain()
        self.log.info("Test sendtoaddress fails when no coins available on regular addresses")
        self.test_sendtoaddress_fails_when_no_coins_available_on_regular_addresses()

        self.reset_blockchain()
        self.log.info("Test sendtoaddress selects coins on regular addresses only")
        self.test_sendtoaddress_selects_coins_on_regular_addresses_only()

        self.reset_blockchain()
        self.log.info("Test signalerttransaction when both instant and recovery keys imported")
        self.test_signalerttransaction_when_both_recovery_and_instant_keys_imported()

        self.reset_blockchain()
        self.log.info("Test standard signalerttransaction flow")
        self.test_signalerttransaction()

        self.reset_blockchain()
        self.log.info("Test standard signinstanttransaction flow")
        self.test_signinstanttransaction()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when instant key imported")
        self.test_signinstanttransaction_when_instant_key_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when both instant and recovery keys imported")
        self.test_signinstanttransaction_when_both_instant_and_recovery_keys_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction is rejected when missing key")
        self.test_signinstanttransaction_is_rejected_when_missing_key()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when recovery key imported")
        self.test_signinstanttransaction_when_recovery_key_imported()

        self.reset_blockchain()
        self.log.info("Test signinstanttransaction when all keys given")
        self.test_signinstanttransaction_when_all_keys_given()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when missing recovery key")
        self.test_recovery_tx_is_rejected_when_missing_recovery_key()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when missing instant key")
        self.test_recovery_tx_is_rejected_when_missing_instant_key()

        self.reset_blockchain()
        self.log.info("Test recovery tx when all keys imported")
        self.test_recovery_tx_when_all_keys_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when missing both instant and recovery keys")
        self.test_recovery_tx_is_rejected_when_missing_both_instant_and_recovery_keys()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when only recovery key imported")
        self.test_recovery_tx_is_rejected_when_only_recovery_key_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when only instant key imported")
        self.test_recovery_tx_is_rejected_when_only_instant_key_imported()

        self.reset_blockchain()
        self.log.info("Test recovery tx when instant key imported and recovery key given")
        self.test_recovery_tx_when_instant_key_imported_and_recovery_key_given()

        self.reset_blockchain()
        self.log.info("Test recovery tx when recovery key imported and instant key given")
        self.test_recovery_tx_when_recovery_key_imported_and_instant_key_given()

        self.reset_blockchain()
        self.log.info("Test recovery tx when both instant and recovery keys given")
        self.test_recovery_tx_when_both_instant_and_recovery_keys_given()

        self.reset_blockchain()
        self.log.info("Test dumpwallet / importwallet with instant address")
        self.test_dumpwallet()

        self.reset_blockchain()
        self.log.info("Test atx from imported instant address")
        self.test_atx_from_imported_instant_address()

        self.reset_blockchain()
        self.log.info("Test getaddressinfo on instant address")
        self.test_getaddressinfo_on_instant_address()

        self.reset_blockchain()
        self.log.info("Test getaddressinfo on imported instant address")
        self.test_getaddressinfo_on_imported_instant_address()

        self.reset_blockchain()
        self.log.info("Test add watch-only instant address")
        self.test_add_watchonly_instant_address()

        self.reset_blockchain()
        self.log.info("Test import instant address privkey")
        self.test_import_instant_address_privkey()

        self.reset_blockchain()
        self.log.info("Test signrawtransactionwithwallet should reject alert transaction")
        self.test_signrawtransactionwithwallet_should_reject_alert_transaction()

        self.reset_blockchain()
        self.log.info("Test signrawtransactionwithwallet should reject instant transaction")
        self.test_signrawtransactionwithwallet_should_reject_instant_transaction()

        self.reset_blockchain()
        self.log.info("Test sign atx with recovery key")
        self.test_sign_atx_with_recovery_key()

        self.reset_blockchain()
        self.log.info("Test tx from normal address to instant address")
        self.test_tx_from_normal_addr_to_instant_addr()

        self.reset_blockchain()
        self.log.info("Test atx from instant address to normal address")
        self.test_atx_from_instant_addr_to_normal_addr()

        self.reset_blockchain()
        self.log.info("Test atx with multiple inputs from alert address to normal address")
        self.test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr()

        self.reset_blockchain()
        self.log.info("Test atx becomes tx after 144 blocks")
        self.test_atx_becomes_tx()

        self.reset_blockchain()
        self.log.info("Test atx fee is paid to original miner")
        self.test_atx_fee_is_paid_to_original_miner()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by wallet when inputs have different source")
        self.test_atx_is_rejected_by_wallet_when_inputs_have_different_source()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by wallet when contains non-alert type inputs")
        self.test_atx_is_rejected_by_wallet_when_contains_non_alert_inputs()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when inputs have different source")
        self.test_atx_is_rejected_by_node_when_inputs_have_different_source()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when contains non-alert type inputs")
        self.test_atx_is_rejected_by_node_when_contains_non_alert_inputs()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when inputs are spent")
        self.test_atx_is_rejected_by_node_when_inputs_are_spent()

        self.reset_blockchain()
        self.log.info("Test atx is rejected by node when inputs are spent by parallel atx")
        self.test_atx_is_rejected_by_node_when_inputs_are_spent_by_parallel_atx()

        self.reset_blockchain()
        self.log.info("Test standard recovery transaction flow")
        self.test_recovery_tx_flow()

        self.reset_blockchain()
        self.log.info("Test recovery tx is rejected when inputs does not match alert")
        self.test_recovery_tx_is_rejected_when_inputs_does_not_match_alert()

        self.reset_blockchain()
        self.log.info("Test getrawtransaction returns information about unconfirmed atx")
        self.test_getrawtransaction_returns_information_about_unconfirmed_atx()

    def test_sendtoaddress_fails_when_no_coins_available_on_regular_addresses(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])  # coins are available only on instant address ...
        error = None
        try:
            self.nodes[0].sendtoaddress(other_addr, 10)  # ... so this call should fail
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -4
        assert 'Insufficient funds' in error['message']

    def test_sendtoaddress_selects_coins_on_regular_addresses_only(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'

        self.nodes[0].generatetoaddress(200, addr0)
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        coins_to_use = self.nodes[0].listunspent()
        coins_to_use = [c for c in coins_to_use if c['address'] == addr0]
        assert len(coins_to_use) == 200

        txid = self.nodes[0].sendtoaddress(other_addr, self.COINBASE_AMOUNT * 200, '', '', True)
        tx = self.nodes[0].getrawtransaction(txid, True)

        # assert
        self.sync_all()
        assert len(tx['vin']) == 200
        assert {v['txid']: v['vout'] for v in tx['vin']} == {c['txid']: c['vout'] for c in coins_to_use}

    def test_recovery_tx_is_rejected_when_missing_recovery_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-recovery tx, possibly missing keys' in error['message']

    def test_recovery_tx_is_rejected_when_missing_both_instant_and_recovery_keys(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-recovery tx, possibly missing keys' in error['message']

    def test_recovery_tx_is_rejected_when_missing_instant_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_recovery_privkey], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-recovery tx, possibly missing keys' in error['message']

    def test_recovery_tx_when_all_keys_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_recovery_tx_is_rejected_when_only_recovery_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-recovery tx, possibly missing keys' in error['message']

    def test_recovery_tx_is_rejected_when_only_instant_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        error = None
        try:
            self.nodes[0].signrecoverytransaction(recoverytx, [], instant_addr0['redeemScript'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-recovery tx, possibly missing keys' in error['message']

    def test_recovery_tx_when_instant_key_imported_and_recovery_key_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_recovery_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_recovery_tx_when_recovery_key_imported_and_instant_key_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # import keys into wallet
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_recovery_tx_when_both_instant_and_recovery_keys_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr0 = self.nodes[0].getnewaddress()
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # send atx and mine block with this atx
        atxid = self.nodes[0].sendtoaddress(addr1, 10)
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # recover atx
        recoverytx = self.nodes[0].createrecoverytransaction(atxid, [{addr0: 174.99}])
        recoverytx = self.nodes[0].signrecoverytransaction(recoverytx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr0['redeemScript'])

        # assert
        self.sync_all()
        assert recoverytx is not None
        assert recoverytx != ''

    def test_dumpwallet(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # get pubkey
        pubkey = self.nodes[0].getaddressinfo(instant_addr0['address'])['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump wallet
        wallet_path = os.path.join(self.nodes[0].datadir, "wallet.dump")
        result = self.nodes[0].dumpwallet(wallet_path)
        assert result['filename'] == wallet_path

        # import wallet
        self.nodes[1].importwallet(wallet_path)
        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['iswatchonly'] is False
        assert sorted(info['pubkeys']) == sorted([pubkey, self.alert_recovery_pubkey, self.alert_instant_pubkey])

    def test_add_watchonly_instant_address(self):
        instant_addr0 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # import alert_addr1 to node0 as watch-only
        self.nodes[0].importaddress(instant_addr0['redeemScript'], '', True, True)

        # mine some coins to node2 and send tx to instant_addr0
        self.nodes[2].generate(200)
        txid = self.nodes[2].sendtoaddress(instant_addr0['address'], 10)
        self.nodes[2].generate(1)

        # assert
        self.sync_all()
        receivedbyaddress = self.find_address(self.nodes[0].listreceivedbyaddress(), instant_addr0['address'])
        assert self.nodes[0].getbalance() == 0
        assert 'involvesWatchonly' in receivedbyaddress
        assert receivedbyaddress['involvesWatchonly'] is True
        assert receivedbyaddress['amount'] == 10
        assert txid in receivedbyaddress['txids']

    def test_getaddressinfo_on_instant_address(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        info = self.nodes[0].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['solvable'] is True
        assert info['iswatchonly'] is False
        assert info['isscript'] is True
        assert info['script'] == 'vaultinstant'
        assert info['sigsrequired'] == 1
        assert len(info['pubkeys']) == 3
        assert self.alert_recovery_pubkey in info['pubkeys']
        assert self.alert_instant_pubkey in info['pubkeys']

    def test_getaddressinfo_on_imported_instant_address(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # import instant_addr0 to node0 as watch-only
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)

        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is False
        assert info['solvable'] is True  # Whether we know how to spend coins sent to this address, ignoring the possible lack of private keys
        assert info['iswatchonly'] is True
        assert info['isscript'] is True
        assert info['script'] == 'vaultinstant'
        assert info['sigsrequired'] == 1
        assert len(info['pubkeys']) == 3
        assert self.alert_recovery_pubkey in info['pubkeys']
        assert self.alert_instant_pubkey in info['pubkeys']

    def test_import_instant_address_privkey(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # get pubkey
        pubkey = self.nodes[0].getaddressinfo(instant_addr0['address'])['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump privkey
        p2pkh = key_to_p2pkh(pubkey)
        privkey = self.nodes[0].dumpprivkey(p2pkh)

        # import address and privkey on node1
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[1].importprivkey(privkey)

        info = self.nodes[1].getaddressinfo(instant_addr0['address'])

        # assert
        self.sync_all()
        assert info['ismine'] is True
        assert info['iswatchonly'] is False
        assert sorted(info['pubkeys']) == sorted([pubkey, self.alert_recovery_pubkey, self.alert_instant_pubkey])

    def test_atx_from_imported_instant_address(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr = '2N34KyQQj97pAivV59wfTkzksYuPdR2jLfi'  # not owned by test nodes

        # mine some coins to instant_addr0
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # get pubkey
        pubkey = self.nodes[0].getaddressinfo(instant_addr0['address'])['pubkeys']
        pubkey.remove(self.alert_recovery_pubkey)
        pubkey = pubkey[0]

        # dump privkey
        p2pkh = key_to_p2pkh(pubkey)
        privkey = self.nodes[0].dumpprivkey(p2pkh)

        # import address and privkey on node1
        self.nodes[1].importaddress(instant_addr0['redeemScript'], '', True, True)
        self.nodes[1].importprivkey(privkey)

        # send atx from node1 and mine block with this atx
        atxid = self.nodes[1].sendtoaddress(other_addr, 10)
        self.nodes[1].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert atxid is not None
        assert atxid != ''
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_tx_from_normal_addr_to_instant_addr(self):
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to node0
        self.nodes[0].generate(200)

        # send tx from node0 to instant_addr1 and generate block with this tx
        txid = self.nodes[0].sendtoaddress(instant_addr1['address'], 10)
        self.nodes[0].generate(1)

        # assert
        self.sync_all()
        assert self.nodes[1].getbalance() == 10
        assert txid in self.nodes[0].getbestblock()['tx']
        assert txid not in self.nodes[0].getbestblock()['atx']
        assert txid in self.find_address(self.nodes[1].listreceivedbyaddress(), instant_addr1['address'])['txids']

    def test_atx_from_instant_addr_to_normal_addr(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # send atx from instant_addr1 to addr0 and generate block with this atx
        atxid = self.nodes[1].sendtoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 0
        assert atxid in self.nodes[0].getbestblock()['atx']

        # generate more blocks so atx becomes tx
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])
        txid = atxid

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 10
        assert txid in self.find_address(self.nodes[0].listreceivedbyaddress(), addr0)['txids']

    def test_atx_with_multiple_inputs_from_alert_addr_to_normal_addr(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(300, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create atx
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [self.alert_recovery_privkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']}
        ])

        # send atx
        atxid = self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        # assert
        self.sync_all()
        assert atxid in self.nodes[0].getbestblock()['atx']

    def test_atx_becomes_tx(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # send atx from instant_addr1 to addr0 and generate block with this atx
        atxid = self.nodes[1].sendtoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 0
        assert atxid in self.nodes[0].getbestblock()['atx']

        # generate 144 more blocks
        self.nodes[1].generatetoaddress(144, instant_addr1['address'])
        txid = atxid

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == 10
        assert txid in self.nodes[0].getbestblock()['tx']
        assert txid in self.find_address(self.nodes[0].listreceivedbyaddress(), addr0)['txids']

    def test_signrawtransactionwithwallet_should_reject_alert_transaction(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        error = None
        try:
            self.nodes[1].signrawtransactionwithwallet(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 174.99}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Unable to sign transaction from vault address' in error['message']

    def test_signrawtransactionwithwallet_should_reject_instant_transaction(self):
        addr0 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to instant_addr1
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # import instant key
        self.nodes[1].importprivkey(self.alert_instant_privkey)

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign instant tx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        error = None
        try:
            self.nodes[1].signrawtransactionwithwallet(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 174.99}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Unable to sign transaction from vault address' in error['message']

    def test_sign_atx_with_recovery_key(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from instant_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [self.alert_recovery_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript'], 'amount': 174.99}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_signalerttransaction_when_both_recovery_and_instant_keys_imported(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # import key
        self.nodes[1].importprivkey(self.alert_recovery_privkey)
        self.nodes[1].importprivkey(self.alert_instant_privkey)

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from alert_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signalerttransaction(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 174.99}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_signalerttransaction(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and sign atx from alert_addr1 to addr0
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        atxtosend = self.nodes[1].signalerttransaction(atxtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript'], 'amount': 174.99}])
        atxsent = self.nodes[1].decoderawtransaction(atxtosend['hex'])

        # broadcast atx and mine block with this atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        # assert
        self.sync_all()
        assert atxsent['txid'] in self.nodes[0].getbestblock()['atx']

    def test_atx_fee_is_paid_to_original_miner(self):
        mine_addr = self.nodes[0].getnewaddress()
        mine_addr2 = self.nodes[0].getnewaddress()
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine coins and send 10 to instant_addr0
        self.nodes[0].generatetoaddress(200, mine_addr)
        amount = 10
        self.nodes[0].sendtoaddress(instant_addr1['address'], amount)
        self.nodes[0].generatetoaddress(1, mine_addr)

        # send coins back as with tx alert and confirm it
        self.sync_all()
        assert self.nodes[1].getbalance() == amount
        txid = self.nodes[1].sendtoaddress(mine_addr, amount - 1)
        tx = self.nodes[1].getrawtransaction(txid, 1)
        fee = amount - tx['vout'][0]['value'] - tx['vout'][1]['value']
        self.nodes[1].generatetoaddress(1, mine_addr2)  # mine to separate address
        self.nodes[1].generatetoaddress(144, mine_addr)

        # assert
        self.sync_all()
        coinbase_id = self.nodes[1].getbestblock()['tx'][0]
        coinbase = self.nodes[1].getrawtransaction(coinbase_id, 1)
        assert coinbase['vout'][1]['value'] == fee

    def test_atx_is_rejected_by_wallet_when_inputs_have_different_source(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, instant_addr1['address'])
        instant_addr2 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, instant_addr2['address'])
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create and sign atx from instant_addr1 and instant_addr2 to addr0
        txtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        error = ''
        try:
            self.nodes[1].signalerttransaction(txtosend, [
                {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript']},
                {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': instant_addr2['redeemScript']}
            ])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced invalid alert tx, possibly wrong inputs given' in error['message']

    def test_atx_is_rejected_by_wallet_when_contains_non_alert_inputs(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, instant_addr1['address'])
        addr1 = self.nodes[1].getnewaddress()
        self.nodes[1].generatetoaddress(50, addr1)
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create and sign atx from instant_addr1 and alert_addr2 to addr0
        txtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        try:
            self.nodes[1].signalerttransaction(txtosend, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript']}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced invalid alert tx, possibly wrong inputs given' in error['message']

    def test_atx_is_rejected_by_node_when_inputs_have_different_source(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)
        addr1_pubkey = self.nodes[0].getaddressinfo(addr1)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, alert_addr1['address'])
        alert_addr2 = self.nodes[1].createvaultinstantaddress(addr1_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, alert_addr2['address'])
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create atx
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey, addr1_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
            {'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': alert_addr2['redeemScript']}
        ])

        # send atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        error = ''
        try:
            self.nodes[1].generatetoaddress(1, alert_addr1['address'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -1
        assert 'bad-tx-alert-type' in error['message']

    def test_atx_is_rejected_by_node_when_contains_non_alert_inputs(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(50, alert_addr1['address'])
        self.nodes[1].generatetoaddress(50, addr1)
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        txtospendhash2 = self.nodes[1].getblockbyheight(60)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)

        # create atx
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey, addr1_prvkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']}])

        # send atx
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        error = ''
        try:
            self.nodes[1].generatetoaddress(1, alert_addr1['address'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -1
        assert 'bad-tx-alert-type' in error['message']

    def test_signinstanttransaction_when_instant_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import instant key
        self.nodes[0].importprivkey(self.alert_instant_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_recovery_key_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import recovery key
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_all_keys_given(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [self.alert_recovery_privkey, self.alert_instant_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_when_both_instant_and_recovery_keys_imported(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # import keys
        self.nodes[0].importprivkey(self.alert_instant_privkey)
        self.nodes[0].importprivkey(self.alert_recovery_privkey)

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_signinstanttransaction_is_rejected_when_missing_key(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})

        error = None
        try:
            self.nodes[0].signinstanttransaction(instant_tx, [], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -5
        assert 'Produced non-instant tx, possibly missing keys' in error['message']

    def test_signinstanttransaction(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        addr1 = self.nodes[1].getnewaddress()

        self.nodes[0].generatetoaddress(200, instant_addr0['address'])

        # create, sign and mine instant tx from instant_addr0 to addr1
        txtospendhash = self.nodes[0].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[0].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        instant_tx = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr1: 174.99})
        instant_tx = self.nodes[0].signinstanttransaction(instant_tx, [self.alert_instant_privkey], [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr0['redeemScript']}])
        instant_txid = self.nodes[0].sendrawtransaction(instant_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])

        # assert
        self.sync_all()
        assert instant_txid in self.nodes[0].getbestblock()['tx']
        assert instant_txid not in self.nodes[0].getbestblock()['atx']

    def test_atx_is_rejected_by_node_when_inputs_are_spent(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)
        addr1_pubkey = self.nodes[0].getaddressinfo(addr1)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, addr1_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(150, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and send 1st atx
        amount = 174.99
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])
        self.nodes[1].sendrawtransaction(atxtosend['hex'])
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        self.sync_all()

        # create and send 2nd atx
        amount = 174.98
        atxtosend = self.nodes[0].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[0].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])

        error = ''
        try:
            self.nodes[0].sendrawtransaction(atxtosend['hex'])
        except Exception as e:
            error = e.error

        assert error['code'] == -26
        assert 'bad-txn-inputs-spent' in error['message']

    def test_atx_is_rejected_by_node_when_inputs_are_spent_by_parallel_atx(self):
        addr0 = self.nodes[0].getnewaddress()
        addr0_prvkey = self.nodes[0].dumpprivkey(addr0)
        addr0_pubkey = self.nodes[0].getaddressinfo(addr0)['pubkey']
        addr1 = self.nodes[0].getnewaddress()
        addr1_prvkey = self.nodes[0].dumpprivkey(addr1)
        addr1_pubkey = self.nodes[0].getaddressinfo(addr1)['pubkey']

        # mine some coins to alert_addr1
        alert_addr1 = self.nodes[1].createvaultinstantaddress(addr0_pubkey, addr1_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(150, alert_addr1['address'])

        # find vout to spend
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)

        # create and send 1st atx
        amount = 174.99
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])
        self.nodes[1].sendrawtransaction(atxtosend['hex'])

        # create 2nd atx
        amount = 174.69
        atxtosend = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: amount})
        atxtosend = self.nodes[1].signrawtransactionwithkey(atxtosend, [addr0_prvkey], [
            {'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': alert_addr1['redeemScript']},
        ])

        error = ''
        try:
            self.nodes[1].sendrawtransaction(atxtosend['hex'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -26
        assert 'txn-mempool-conflict' in error['message']

    def test_recovery_tx_flow(self):
        instant_addr0 = self.nodes[0].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        other_addr0 = self.nodes[0].getnewaddress()
        attacker_addr1 = self.nodes[1].getnewaddress()

        # mine some coins to node0
        self.nodes[0].generatetoaddress(200, instant_addr0['address'])  # 200
        assert self.nodes[0].getbalance() == (200 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT

        # send atx to node1
        atx_to_recover = self.nodes[0].sendtoaddress(attacker_addr1, 10)
        atx_to_recover = self.nodes[0].gettransaction(atx_to_recover)['hex']
        atx_to_recover = self.nodes[0].decoderawtransaction(atx_to_recover)
        atx_fee = (200 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT - 10 - self.nodes[0].getbalance()

        # generate block with atx above
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 201

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() + 10 < (201 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT
        assert self.nodes[1].getbalance() == 0
        assert atx_to_recover['hash'] in self.nodes[0].getbestblock()['atx']

        # recover atx
        amount_to_recover = sum([vout['value'] for vout in atx_to_recover['vout']])
        assert atx_fee == self.COINBASE_AMOUNT - amount_to_recover

        recovery_tx = self.nodes[0].createrecoverytransaction(atx_to_recover['hash'], {other_addr0: amount_to_recover})
        recovery_tx = self.nodes[0].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr0['redeemScript'])
        recovery_txid = self.nodes[0].sendrawtransaction(recovery_tx['hex'])
        self.nodes[0].generatetoaddress(1, instant_addr0['address'])  # 202

        # assert
        self.sync_all()
        assert recovery_txid in self.nodes[0].getbestblock()['tx']
        assert recovery_txid in self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['txids']
        assert self.nodes[0].getbalance() == (202 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT - atx_fee

        # generate blocks so atx might become tx
        self.nodes[0].generatetoaddress(143, instant_addr0['address'])  # 345

        # assert
        self.sync_all()
        assert self.nodes[0].getbalance() == (345 - self.COINBASE_MATURITY) * self.COINBASE_AMOUNT  # dont subtract atx_fee because node0 takes it as a block miner
        assert atx_to_recover['hash'] not in self.nodes[0].getbestblock()['tx']
        assert self.find_address(self.nodes[1].listreceivedbyaddress(), attacker_addr1)['amount'] == 0
        assert self.find_address(self.nodes[1].listreceivedbyaddress(), attacker_addr1)['txids'] == []
        assert self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['amount'] == self.COINBASE_AMOUNT - atx_fee
        assert self.find_address(self.nodes[0].listreceivedbyaddress(), other_addr0)['txids'] == [recovery_txid]

    def test_recovery_tx_is_rejected_when_inputs_does_not_match_alert(self):
        addr0 = self.nodes[0].getnewaddress()

        # mine some coins to instant_addr1
        instant_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)
        self.nodes[1].generatetoaddress(200, instant_addr1['address'])

        # create, sign and mine 1st atx from instant_addr1 to addr0
        txtospendhash = self.nodes[1].getblockbyheight(10)['tx'][0]
        txtospend = self.nodes[1].getrawtransaction(txtospendhash, True)
        vouttospend = self.find_vout_n(txtospend, 175)
        tx_alert1 = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}], {addr0: 174.99})
        tx_alert1 = self.nodes[1].signalerttransaction(tx_alert1, [{'txid': txtospendhash, 'vout': vouttospend, 'scriptPubKey': txtospend['vout'][vouttospend]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript']}])
        self.nodes[1].sendrawtransaction(tx_alert1['hex'])
        self.nodes[1].generatetoaddress(1, instant_addr1['address'])

        # create, sign and mine 2nd atx from instant_addr1 to addr0
        self.sync_all()
        txtospendhash2 = self.nodes[1].getblockbyheight(20)['tx'][0]
        txtospend2 = self.nodes[1].getrawtransaction(txtospendhash2, True)
        vouttospend2 = self.find_vout_n(txtospend2, 175)
        tx_alert2 = self.nodes[1].createrawtransaction([{'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 174.99})
        tx_alert2 = self.nodes[1].signalerttransaction(tx_alert2, [{'txid': txtospendhash2, 'vout': vouttospend2, 'scriptPubKey': txtospend2['vout'][vouttospend2]['scriptPubKey']['hex'], 'redeemScript': instant_addr1['redeemScript']}])
        self.nodes[1].sendrawtransaction(tx_alert2['hex'])
        self.nodes[1].generatetoaddress(10, instant_addr1['address'])
        self.sync_all()

        # create and sign (invalid) recovery tx spending both alerts inputs
        recovery_tx = self.nodes[1].createrawtransaction([{'txid': txtospendhash, 'vout': vouttospend}, {'txid': txtospendhash2, 'vout': vouttospend2}], {addr0: 349.99})
        recovery_tx = self.nodes[1].signrecoverytransaction(recovery_tx, [self.alert_instant_privkey, self.alert_recovery_privkey], instant_addr1['redeemScript'])

        # broadcast recovery tx and mine block
        tx_id = self.nodes[1].sendrawtransaction(recovery_tx['hex'])
        error = None
        try:
            self.nodes[1].generatetoaddress(1, instant_addr1['address'])
        except Exception as e:
            error = e.error

        # assert
        self.sync_all()
        assert error['code'] == -1
        assert 'Revert transaction check failed' in error['message']
        assert tx_id in error['message']

    def test_getrawtransaction_returns_information_about_unconfirmed_atx(self):
        addr0 = self.nodes[0].getnewaddress()
        alert_addr1 = self.nodes[1].getnewvaultinstantaddress(self.alert_instant_pubkey, self.alert_recovery_pubkey)

        # mine some coins to alert_addr1
        self.nodes[1].generatetoaddress(200, alert_addr1['address'])

        # create atx
        atxid = self.nodes[1].sendtoaddress(addr0, 10)
        self.nodes[1].generatetoaddress(1, alert_addr1['address'])

        # getrawtransaction
        rawtx = self.nodes[1].getrawtransaction(atxid, True)

        # assert
        assert rawtx['txid'] == atxid


if __name__ == '__main__':
    AlertsInstantTest().main()
