from web3 import Web3
import time
import json

BESU_NODE_URL = "https://rpc.sotatek.works/" 
RECEIVER_ADDRESS = "0x3c7E09a60b77Bed8Ec13515bc5D9F69A977E8268" 
AMOUNT_TO_TRANSFER_ETH = 0.0001
NUMBER_OF_TRANSACTIONS = 250

w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))
if not w3.is_connected():
    print("Không thể kết nối đến node Besu.")
    exit()



list_of_tx_hashes = []

for i in range(NUMBER_OF_TRANSACTIONS):
    newAccount = w3.eth.accounts.create()
    sender_account = w3.eth.account.from_key(newAccount.privateKey)
    sender_address = sender_account.address
    amount_in_wei = w3.to_wei(AMOUNT_TO_TRANSFER_ETH, 'ether')
    start_nonce = w3.eth.get_transaction_count(sender_address) 
    current_nonce = start_nonce
    try:
        transaction = {
            'nonce': current_nonce,
            'to': RECEIVER_ADDRESS,
            'value': amount_in_wei,
            'gas': 21000, 
            'gasPrice': w3.eth.gas_price, 
            'chainId': w3.eth.chain_id 
        }

        signed_txn = w3.eth.account.sign_transaction(transaction, newAccount.privateKey)

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        list_of_tx_hashes.append(w3.to_hex(tx_hash))
        
        print(f"[{i + 1}/{NUMBER_OF_TRANSACTIONS}] Gửi thành công. Nonce: {current_nonce}, Tx Hash: {w3.to_hex(tx_hash)}")
        
        current_nonce += 1
        
        time.sleep(0.05) 

    except Exception as e:
        print(f"Lỗi khi tạo hoặc gửi giao dịch {i+1}: {e}")
        break 

print("-" * 40)
print(f"Đã hoàn thành gửi {len(list_of_tx_hashes)} giao dịch. Nonce cuối cùng: {current_nonce - 1}")
print("\nĐang chờ xác nhận cho {NUMBER_OF_TRANSACTIONS} giao dịch đã gửi...")
successful_tx_count = 0
failed_tx_count = 0

for tx_hash in list_of_tx_hashes:
    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60) 
        
        if tx_receipt.status == 1:
            successful_tx_count += 1
        else:
            failed_tx_count += 1
        
        print(f"  > Tx Hash {tx_hash[-6:]}... - Trạng thái: {'Thành công' if tx_receipt.status == 1 else 'Thất bại'}")

    except Exception:
        print(f"  > Tx Hash {tx_hash[-6:]}... - Trạng thái: Chưa được xác nhận (Timeout)")
        failed_tx_count += 1

print("-" * 40)
print(f"TỔNG KẾT:")
print(f"  - Thành công: {successful_tx_count}")
print(f"  - Thất bại/Chưa xác nhận: {failed_tx_count}")