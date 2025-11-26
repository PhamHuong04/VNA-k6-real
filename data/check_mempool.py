from web3 import Web3
import time

# --- Cấu hình ---
BESU_NODE_URL = "https://rpc.sotatek.works" 

w3 = Web3(Web3.HTTPProvider(BESU_NODE_URL))

# --- Thêm Middleware PoA (Để tránh lỗi ExtraData nếu có check block) ---
try:
    from web3.middleware import ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware as ExtraDataToPOAMiddleware
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if not w3.is_connected():
    print("❌ Không kết nối được Node.")
    exit()

def get_mempool_status():
    # Gọi trực tiếp API RPC của Besu: txpool_besuStatistics
    # API này trả về số lượng giao dịch trong pool mà không làm nặng node
    try:
        response = w3.provider.make_request("txpool_besuStatistics", [])
        
        if 'result' in response:
            stats = response['result']
            return stats
        else:
            print(f"⚠️ API không trả về kết quả: {response}")
            return None
    except Exception as e:
        print(f"❌ Lỗi gọi API txpool: {e}")
        return None

print(f"🔍 Đang theo dõi Mempool (Hàng chờ) trên Besu...")
print("-" * 50)
print(f"{'THỜI GIAN':<10} | {'PENDING (Đang chờ)':<20} | {'BLOCK MỚI NHẤT':<15}")
print("-" * 50)

# Vòng lặp theo dõi 10 lần, mỗi lần cách nhau 2 giây
for i in range(20):
    stats = get_mempool_status()
    current_block = w3.eth.block_number
    
    if stats:
        # localCount: Số Tx được gửi từ node này (thường là cái ta quan tâm khi test)
        # remoteCount: Số Tx nhận từ node khác (nếu chạy cluster)
        pending_count = stats.get('localCount', 0) + stats.get('remoteCount', 0)
        
        status_icon = "🟢 Trống" if pending_count == 0 else f"🔴 Ùn ứ ({pending_count})"
        
        print(f"Lần {i+1:<6} | {status_icon:<20} | {current_block}")
    
    else:
        print("⚠️ Không lấy được dữ liệu Mempool. Có thể API chưa bật.")
        break
        
    time.sleep(2)

print("-" * 50)