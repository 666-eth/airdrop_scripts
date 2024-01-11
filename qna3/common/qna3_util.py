from eth_account.messages import encode_defunct
import requests
import json
import logging
import time

from web3 import Web3

logging.basicConfig(level=logging.INFO)


def get_base_info(private_key):
    message = encode_defunct(text="AI + DYOR = Ultimate Answer to Unlock Web3 Universe")
    web3 = Web3(Web3.WebsocketProvider('wss://opbnb.publicnode.com'))
    account = web3.eth.account
    signed_message = account.sign_message(message, private_key=private_key)
    # signature_hex and address
    signature_hex = signed_message.signature.hex()
    address = account.from_key(private_key).address
    # step2. get accessToken
    access_token_data = {
        'signature': signature_hex,
        'wallet_address': address
    }
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'authority': 'api.qna3.ai',
        'Origin': 'https://qna3.ai'
    }
    access_token = ''
    user_id = ''
    auth_response = requests.post('https://api.qna3.ai/api/v2/auth/login?via=wallet',
                                  data=json.dumps(access_token_data),
                                  headers=headers)
    if auth_response.status_code in [200, 201]:
        auth_response_data = auth_response.json()
        logging.info(f'req auth successful, json : {auth_response_data}')
        access_token = auth_response_data['data']['accessToken']
        user_id = auth_response_data['data']['user']['id']
    # step3. get me info
    headers['Authorization'] = 'Bearer ' + access_token
    headers['X-Id'] = user_id
    return address, headers


# 执行签到合约交互
def exec_tx(_from, contract, input_data, nonce, chain_id, private_key, web3):
    contract_address = Web3.to_checksum_address(contract)
    # 估计gas
    estimated_gas = web3.eth.estimate_gas({
        'from': _from,
        'to': contract_address,
        'data': input_data
    })
    gas_limit = int(estimated_gas * 1.1)
    # gas_limit = estimated_gas
    logging.info(f'estimated gas: {estimated_gas}, with buffer: {gas_limit}')
    # 获取当前的gas价格
    gas_price = web3.eth.gas_price
    # logging.info(f'current gas price: {gas_price}')
    # 构造交易
    tx = {
        'from': _from,
        'to': contract_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': input_data,
        'chainId': chain_id
    }
    # 签名交易
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    # 发送交易
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = None
    max_polling_attempts = 5
    delay_between_attempts = 3
    for attempt in range(max_polling_attempts):
        try:
            # 尝试获取交易收据
            time.sleep(delay_between_attempts)
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                # 如果收据存在，则打印信息并退出循环
                logging.info(f"transaction receipt found in attempt {attempt + 1}")
                break
        except Exception as e:
            # 如果发生异常，则打印错误消息
            logging.info(f"attempt {attempt + 1} failed: {e}")
        # 如果没有找到收据，则等待指定的延迟时间
        logging.error(f"waiting for {delay_between_attempts} seconds before next attempt...")
        time.sleep(delay_between_attempts)
    tx_hash_id = receipt.transactionHash.hex()
    logging.info(f'transaction successful txId: {tx_hash_id}')
    return tx_hash_id


# 检查并修复input data
def check_and_reset_input_data(input_data):
    if not input_data.startswith('0x'):
        return '0x' + input_data
    elif input_data.count('0x') > 1:
        return '0x' + input_data.replace('0x', '')
    else:
        raise Exception("format input_data err")
