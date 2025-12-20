import fs from "fs";
import https from "https";
import http from "http";

const SOURCE_URL =
  "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json";

const TIMEOUT = 5000;

/** 拉取 JSON */
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, res => {
        let data = "";
        res.on("data", chunk => (data += chunk));
        res.on("end", () => resolve(JSON.parse(data)));
      })
      .on("error", reject);
  });
}

/** 探测 API 是否 200 */
function checkApi(url) {
  return new Promise(resolve => {
    const lib = url.startsWith("https") ? https : http;

    const req = lib.get(url, { timeout: TIMEOUT }, res => {
      res.destroy();
      resolve(res.statusCode === 200);
    });

    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });

    req.on("error", () => resolve(false));
  });
}

/** 清洗 name */
function cleanName(name = "") {
  return name
    .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "")
    .replace(/[-—🎬\s]+/g, "")
    .trim();
}

/** 生成 key */
function genKey(domain) {
  return domain.replace(/[^a-zA-Z]/g, "").toLowerCase();
}

(async () => {
  const source = await fetchJson(SOURCE_URL);
  const apiSite = source.api_site || {};

  const usedKeys = new Set();
  const sites = [];

  for (const [domain, info] of Object.entries(apiSite)) {
    const ok = await checkApi(info.api);

    if (!ok) {
      console.log(`❌ API 不可用，已跳过: ${info.api}`);
      continue;
    }

    let key = genKey(domain);
    let i = 1;
