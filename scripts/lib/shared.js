export const loadTestStages = [
  { duration: "10s", target: 5 },
  { duration: "30s", target: 5 },
  { duration: "10s", target: 0 },
];

export const strictThresholds = {
  http_req_failed: ["rate<0.05"],
  http_req_duration: ["p(95)<1000"],
  checks: ["rate==1.0"],
};

export const loadTestOptions = {
  stages: loadTestStages,
  thresholds: strictThresholds,
};
