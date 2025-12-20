import fs from "fs";
import https from "https";
import http from "http";

const SOURCE_URL =
  "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json";
const TIMEOUT = 5000;

/* ---------- 工具函数 ---------- */

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve(JSON.parse(data)));
      })
      .on("error", reject);
  });
}

function checkApi(url) {
  return new Promise((resolve) => {
    if (!url) return resolve(false);
    const lib = url.startsWith("https") ? http
