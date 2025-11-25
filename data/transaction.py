from web3 import Web3
import csv
import time
import random
from typing import List, Dict
import json
import os
# --- Cấu hình Mạng và Tài khoản ---
CONFIG_FILE = 'config/config.json'

def load_config(file_path):
    """Đọc và trả về dữ liệu cấu hình từ file JSON."""
    try:
        # Sử dụng 'with open' để đảm bảo file được đóng sau khi đọc
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            print(f"✅ Đã tải thành công cấu hình từ {os.path.abspath(file_path)}")
            return config_data
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file cấu hình tại {os.path.abspath(file_path)}")
        exit()
    except json.JSONDecodeError:
        print(f"❌ Lỗi: File cấu hình {file_path} không hợp lệ (lỗi cú pháp JSON).")
        exit()
        
# --- Bắt đầu Script ---
config = load_config(CONFIG_FILE)

BESU_NODE_URL = config['basuNodeUrl']
INPUT_FILE = 'data/test_keys.csv' # File chứa Private Key của các ví đã có tiền
AMOUNT_TO_TRANSFER_ETH = 0.00001 
TRANSACTIONS_PER_ACCOUNT = 5  # Số giao dịch mỗi ví sẽ thực hiện

# --- Khởi tạo Web3 ---
w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))

if not w3.is_connected():
    print("❌ Lỗi: Không thể kết nối đến node Besu.")
    exit()

amount_in_wei = w3.to_wei(AMOUNT_TO_TRANSFER_ETH, 'ether')
print(f"✅ Đã kết nối. Chuẩn bị thực hiện chuyển khoản nội bộ.")

# Kiểu dữ liệu để lưu trữ thông tin ví
AccountInfo = Dict[str, str]

def load_accounts_from_csv(file_path: str) -> List[AccountInfo]:
    """Đọc Address và Private Key từ file CSV."""
    accounts = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts.append({
                    'address': row['Address'],
                    'privateKey': row['PrivateKey']
                })
        print(f"✅ Đã tải thành công {len(accounts)} tài khoản từ {file_path}")
        # 
        return accounts
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {file_path}. Vui lòng kiểm tra lại đường dẫn.")
        return []

# Tải danh sách các ví đã có tiền
all_accounts = load_accounts_from_csv(INPUT_FILE)
if not all_accounts:
    exit()
def send_internal_transfers(accounts: List[AccountInfo]):
    
    # Khởi tạo Nonce cho TẤT CẢ các tài khoản
    nonce_tracker = {}
    total_transactions_to_send = 0

    print("🔍 Bắt đầu lấy Nonce hiện tại của từng ví...")
    for account in accounts:
        address = account['address']
        # Lấy nonce hiện tại từ mạng lưới
        current_nonce = w3.eth.get_transaction_count(address)
        nonce_tracker[address] = current_nonce
        total_transactions_to_send += TRANSACTIONS_PER_ACCOUNT
    
    print(f"Tất cả {len(accounts)} ví sẽ tạo tổng cộng {total_transactions_to_send} giao dịch.")
    print("-" * 50)

    # Lặp để tạo và gửi giao dịch
    for tx_count in range(TRANSACTIONS_PER_ACCOUNT):
        print(f"\n--- Bắt đầu Vòng Gửi #{tx_count + 1} ---")
        
        for i, sender_info in enumerate(accounts):
            sender_address = sender_info['address']
            sender_private_key = sender_info['privateKey']
            
            # Chọn NGẪU NHIÊN một ví khác làm người nhận
            receiver_info = random.choice([acc for acc in accounts if acc != sender_info])
            receiver_address = receiver_info['address']
            
            # Lấy Nonce hiện tại của tài khoản gửi này
            current_nonce = nonce_tracker[sender_address]
            
            try:
                # 1. Tạo Transaction
                transaction = {
                    'nonce': current_nonce,
                    'to': receiver_address,
                    'value': amount_in_wei,
                    'gas': 21000, 
                    'gasPrice': w3.eth.gas_price, 
                    'chainId': w3.eth.chain_id
                }

                # 2. Ký và Gửi Giao dịch
                signed_txn = w3.eth.account.sign_transaction(transaction, sender_private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
                print(f"  Gửi từ: {sender_address[-4:]} (Nonce: {current_nonce}) -> Nhận: {receiver_address[-4:]} | Tx Hash: {w3.to_hex(tx_hash)[-6:]}...")
                
                # 3. Cập nhật Nonce cho lần gửi tiếp theo của ví này
                nonce_tracker[sender_address] += 1
                
            except Exception as e:
                print(f"❌ Lỗi giao dịch từ {sender_address[-4:]} (Nonce: {current_nonce}): {e}")
                # Nếu giao dịch lỗi (ví dụ: không đủ gas), tài khoản này có thể bị bỏ qua trong các vòng lặp sau.
                # Cần xử lý cẩn thận nếu muốn tiếp tục.

            # time.sleep(0.01) # Giãn cách nhỏ giữa các giao dịch

    print("-" * 50)
    print("🎉 Hoàn thành gửi tất cả các giao dịch theo kịch bản.")
    print("Vui lòng kiểm tra trạng thái các giao dịch trên Besu node.")

if __name__ == "__main__":
    send_internal_transfers(all_accounts)
