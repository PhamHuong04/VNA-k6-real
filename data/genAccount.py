from web3 import Web3
import csv
import os

NUMBER_OF_ACCOUNTS = 100 
OUTPUT_FILE = 'test_keys.csv'

w3 = Web3() 

def generate_and_save_keys():
    print(f"Bắt đầu sinh {NUMBER_OF_ACCOUNTS} cặp khóa và lưu vào file CSV...")

    key_data = []

    for i in range(NUMBER_OF_ACCOUNTS):

        new_account = w3.eth.account.create()

        address = new_account.address
        private_key = w3.to_hex(new_account.key) 

        key_data.append({
            'Index': i + 1,
            'Address': address,
            'PrivateKey': private_key
        })

        if (i + 1) % 10 == 0:
            print(f"Đã sinh được {i + 1} tài khoản...")

    try:
        fieldnames = ['Index', 'Address', 'PrivateKey']
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            writer.writerows(key_data)
            
        print(f"\n🎉 Thành công! Đã lưu {NUMBER_OF_ACCOUNTS} cặp khóa vào file: {os.path.abspath(OUTPUT_FILE)}")
        print("⚠️ Lưu ý: File này chứa Khóa Riêng Tư (Private Key) cho mục đích thử nghiệm. Cần bảo mật.")

    except Exception as e:
        print(f"❌ Lỗi khi ghi file CSV: {e}")

if __name__ == "__main__":
    generate_and_save_keys()