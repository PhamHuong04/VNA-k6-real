from web3 import Web3
import csv
import time
import json
import os
# --- Cấu hình Mạng và Tài khoản Gửi ---
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
SENDER_PRIVATE_KEY = config['senderPrivateKey']  # Private Key của tài khoản CÓ TIỀN (tài khoản nguồn)
INPUT_FILE = 'data/test_keys.csv' # Tên file CSV chứa danh sách địa chỉ nhận
AMOUNT_TO_TRANSFER_ETH = 0.01 # Số lượng Ether muốn chuyển đến MỖI tài khoản



# --- Khởi tạo Web3 ---
w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))

if not w3.is_connected():
    print("❌ Lỗi: Không thể kết nối đến node Besu.")
    exit()

sender_account = w3.eth.account.from_key(SENDER_PRIVATE_KEY)
sender_address = sender_account.address
amount_in_wei = w3.to_wei(AMOUNT_TO_TRANSFER_ETH, 'ether')

print(f"✅ Đã kết nối. Tài khoản gửi: {sender_address}")
def read_receiver_addresses(file_path):
    receiver_addresses = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Địa chỉ nằm trong cột 'Address' (theo định dạng file đã tạo trước)
                receiver_addresses.append(row['Address'])
        print(f"✅ Đã đọc thành công {len(receiver_addresses)} địa chỉ từ {file_path}")
        return receiver_addresses
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {file_path}. Vui lòng kiểm tra lại đường dẫn.")
        return []
def send_batch_transactions():
    receiver_list = read_receiver_addresses(INPUT_FILE)
    if not receiver_list:
        return

    # Lấy nonce ban đầu
    start_nonce = w3.eth.get_transaction_count(sender_address) 
    current_nonce = start_nonce
    
    list_of_tx_hashes = []
    
    print("-" * 50)
    print(f"📤 Bắt đầu gửi tiền đến {len(receiver_list)} tài khoản, bắt đầu từ Nonce: {start_nonce}")
    print("-" * 50)

    for i, receiver_address in enumerate(receiver_list):
        try:
            # 1. Tạo Transaction với Nonce TĂNG DẦN
            transaction = {
                'nonce': current_nonce,
                'to': receiver_address,
                'value': amount_in_wei,
                'gas': 21000, 
                'gasPrice': w3.eth.gas_price, 
                'chainId': w3.eth.chain_id
            }

            # 2. Ký Giao dịch
            signed_txn = w3.eth.account.sign_transaction(transaction, SENDER_PRIVATE_KEY)

            # 3. Gửi Giao dịch
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            list_of_tx_hashes.append(w3.to_hex(tx_hash))
            
            print(f"[{i + 1}/{len(receiver_list)}] Gửi đến {receiver_address[-6:]}... - Nonce: {current_nonce}")
            
            # 4. TĂNG NONCE cho giao dịch tiếp theo
            current_nonce += 1
            
            # Đợi một chút để giảm áp lực lên node (tùy chọn)
            # time.sleep(0.01) 

        except Exception as e:
            print(f"❌ Lỗi khi gửi giao dịch {i+1} đến {receiver_address}: {e}")
            # Dừng lại nếu lỗi nghiêm trọng (ví dụ: không đủ gas/tiền)
            # Nếu chỉ là lỗi tạm thời, có thể continue để thử giao dịch tiếp theo
            break 
            
    # Chờ xác nhận và báo cáo tổng kết (giống ví dụ trước)
    # ... (Bạn có thể thêm phần theo dõi xác nhận như ví dụ 100 giao dịch) ...
    
    print("-" * 50)
    print(f"🎉 Đã hoàn thành gửi {len(list_of_tx_hashes)} giao dịch. Nonce cuối cùng được sử dụng: {current_nonce - 1}")
    print(f"Các hash giao dịch đã gửi: {list_of_tx_hashes}")

if __name__ == "__main__":
    send_batch_transactions()