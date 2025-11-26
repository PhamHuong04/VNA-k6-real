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
    send_txs: {
      executor: "shared-iterations",
      vus: 20, // Tăng số lượng VU lên chút để bắn nhanh hơn
      iterations: signedTxs.length, // k6 sẽ tự động chạy đủ 10,000 lần (100 ví * 100 tx)
      maxDuration: "5m",
    },
  },
};

const BASE_URL = "https://rpc.sotatek.works"; // URL RPC của bạn

export default function () {
  console.log(`👷 VU số ${__VU} đang gửi giao dịch thứ ${__ITER}...`);
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
