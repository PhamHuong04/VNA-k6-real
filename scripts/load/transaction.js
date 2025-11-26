import http from "k6/http";
import { check } from "k6";
import { SharedArray } from "k6/data";
import { scenario } from "k6/execution";

// 1. Đọc file mới (bulk)
const signedTxs = new SharedArray("signed transactions", function () {
  return open("../../data/signed_transactions_bulk.csv").split("\n").slice(1);
});

export const options = {
  scenarios: {
    ramping_rate_test: {
      executor: "ramping-arrival-rate",
      startRate: 0, // Bắt đầu từ 0 TPS
      timeUnit: "1s", // Đơn vị tính là giây

      preAllocatedVUs: 10,
      maxVUs: 100, // Cho phép tối đa 50 VUs nếu cần thiết

      stages: [
        { target: 100, duration: "3m" }, // Tăng từ 0 lên 1 TPS trong 10s
        { target: 100, duration: "5m" }, // Giữ đều 1 TPS trong 1 phút (Yêu cầu của bạn)
        { target: 200, duration: "5m" }, // Sau đó tăng tốc lên 10 TPS
        { target: 0, duration: "3m" }, // Giảm về 0
      ],
    },
  },
};

const BASE_URL = "https://rpc.sotatek.works"; // URL RPC của bạn

export default function () {
  //   console.log(`👷 VU số ${__VU} đang gửi giao dịch thứ ${__ITER}...`);
  // Lấy đúng hàng dựa trên số thứ tự thực thi
  const currentTxIndex = scenario.iterationInTest;

  if (currentTxIndex >= signedTxs.length) return;

  const rawTx = signedTxs[currentTxIndex].replace(/"/g, "").trim();
  if (!rawTx) return;

  const payload = JSON.stringify({
    jsonrpc: "2.0",
    method: "eth_sendRawTransaction",
    params: [rawTx],
    id: 1,
  });

  const params = { headers: { "Content-Type": "application/json" } };
  const res = http.post(BASE_URL, payload, params);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "no error": (r) => !r.body.includes("error"),
  });
}
