from web3 import Web3
import csv
import random

# --- Cấu hình ---
BESU_NODE_URL = "https://rpc.sotatek.works" # URL từ MetaMask của bạn
INPUT_FILE = 'data/test_keys.csv' 
OUTPUT_FILE = 'data/signed_transactions_bulk.csv' 

# Địa chỉ nhận (nhớ checksum)
RAW_RECEIVER = "0x85c06471d71b5609c40c170bec58d6efddf7c572" 
AMOUNT = 0.000001
TX_PER_ACCOUNT = 100 # <--- SỐ LƯỢNG GIAO DỊCH MUỐN GỬI MỖI VÍ

w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))

def generate_bulk_signed_txs():
    # receiver_address = w3.to_checksum_address(RAW_RECEIVER) # This is no longer needed as receiver will be random

    accounts = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(row)

    # 1. Khởi tạo nonce tracker cho từng ví
    nonce_tracker = {}
    print("Dang lay nonce khoi diem cho tat ca cac vi...")
    for acc in accounts:
        sender_address = w3.to_checksum_address(acc['Address'])
        nonce_tracker[sender_address] = w3.eth.get_transaction_count(sender_address)

    # 2. Tạo pool người gửi (mỗi người gửi xuất hiện TX_PER_ACCOUNT lần)
    sender_pool = []
    for acc in accounts:
        sender_pool.extend([acc] * TX_PER_ACCOUNT)
    
    # 3. Xáo trộn thứ tự người gửi
    random.shuffle(sender_pool) 

    total_tx_expect = len(sender_pool)
    print(f"Dang chuan bi {total_tx_expect} giao dich (Ngau nhien hoa nguoi gui va nguoi nhan)...")
    
    signed_data = []
    chain_id = w3.eth.chain_id
    gas_price = w3.eth.gas_price

    for i, sender_acc in enumerate(sender_pool):
        private_key = sender_acc['PrivateKey']
        sender_address = w3.to_checksum_address(sender_acc['Address'])
        
        # Chọn ngẫu nhiên người nhận từ danh sách accounts
        receiver_acc = random.choice(accounts)
        receiver_address = w3.to_checksum_address(receiver_acc['Address'])

        # Lấy nonce hiện tại từ tracker và tăng lên
        current_nonce = nonce_tracker[sender_address]
        nonce_tracker[sender_address] += 1
            
        tx = {
            'nonce': current_nonce,
            'to': receiver_address,
            'value': w3.to_wei(AMOUNT, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
        
        try:
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            raw_tx_hex = w3.to_hex(signed_tx.raw_transaction)
            signed_data.append(raw_tx_hex)
        except Exception as e:
            print(f"Loi tao Tx {i} tu {sender_address}: {e}")

        # In tiến độ
        if (i + 1) % 100 == 0:
            print(f"   -> Đã xử lý xong {i + 1}/{total_tx_expect} giao dịch...")

    # Lưu tất cả vào file CSV
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['signed_tx']) 
        for tx in signed_data:
            writer.writerow([tx])

    print(f"✅ Đã tạo xong file '{OUTPUT_FILE}' với {len(signed_data)} giao dịch.")

if __name__ == "__main__":
    generate_bulk_signed_txs()