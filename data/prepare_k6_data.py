from web3 import Web3
import csv

# --- Cấu hình ---
BESU_NODE_URL = "https://rpc.sotatek.works" # URL từ MetaMask của bạn
INPUT_FILE = 'data/test_keys.csv' 
OUTPUT_FILE = 'data/signed_transactions_bulk.csv' 

# Địa chỉ nhận (nhớ checksum)
RAW_RECEIVER = "0x85c06471d71b5609c40c170bec58d6efddf7c572" 
AMOUNT = 0.000001
TX_PER_ACCOUNT = 1000 # <--- SỐ LƯỢNG GIAO DỊCH MUỐN GỬI MỖI VÍ

w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))

def generate_bulk_signed_txs():
    receiver_address = w3.to_checksum_address(RAW_RECEIVER)

    accounts = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(row)

    total_tx_expect = len(accounts) * TX_PER_ACCOUNT
    print(f"🔄 Đang chuẩn bị {total_tx_expect} giao dịch (Mỗi ví {TX_PER_ACCOUNT} Tx)...")
    
    signed_data = []
    chain_id = w3.eth.chain_id
    gas_price = w3.eth.gas_price

    for i, acc in enumerate(accounts):
        private_key = acc['PrivateKey']
        sender_address = w3.to_checksum_address(acc['Address'])
        
        # 1. Lấy Nonce khởi điểm của ví trên mạng lưới
        start_nonce = w3.eth.get_transaction_count(sender_address)
        
        # 2. Vòng lặp tạo 100 giao dịch cho ví này
        for j in range(TX_PER_ACCOUNT):
            # Tính toán nonce cho giao dịch thứ j
            current_nonce = start_nonce + j 
            
            tx = {
                'nonce': current_nonce, # <--- QUAN TRỌNG NHẤT
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
                print(f"❌ Lỗi tạo Tx {j} cho ví {sender_address}: {e}")

        # In tiến độ để đỡ sốt ruột
        if (i + 1) % 10 == 0:
            print(f"   -> Đã xử lý xong {i + 1}/{len(accounts)} ví...")

    # Lưu tất cả vào file CSV
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['signed_tx']) 
        for tx in signed_data:
            writer.writerow([tx])

    print(f"✅ Đã tạo xong file '{OUTPUT_FILE}' với {len(signed_data)} giao dịch.")

if __name__ == "__main__":
    generate_bulk_signed_txs()