import { loadTestOptions } from "../lib/shared.js";
import { check, sleep } from "k6";
import http from "k6/http";

const config = JSON.parse(open("../../config/config.json"));

export const options = loadTestOptions;

export default function () {
  const blocksRes = http.get(`${config.baseUrl}/api/v2/blocks?type=block`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  check(blocksRes, {
    "Status is 200": (r) => r.status === 200,
  });

  sleep(1);
}
