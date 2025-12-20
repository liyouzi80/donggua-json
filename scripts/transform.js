import fs from "fs";
import https from "https";
import http from "http";

const SOURCE_URL =
  "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json";

const TIMEOUT = 5000;

/** 拉取 JSON */
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let data = "";
      res.on("data", chunk => (data += chunk));
      res.on("end", () => resolve(JSON.parse(data)));
    }).on("error", reject);
  });
}

/** API 探测 */
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

  const entries = Object.entries(apiSite);

  // 并发检测
  const results = await Promise.all(
    entries.map(async ([domain, info]) => {
      const ok = await checkApi(info.api);
      return { domain, info, ok };
    })
  );

  const usedKeys = new Set();
  const sites = [];

  for (const { domain, info, ok } of results) {
    if (!ok) {
      console.log(`❌ 不可用: ${info.api}`);
      continue;
    }

    let key = genKey(domain);
    let i = 1;
    while (usedKeys.has(key)) key = `${key}${i++}`;
    usedKeys.add(key);

    sites.push({
      key,
      name: cleanName(info.name),
      api: info.api,
      active: true
    });

    console.log(`✅ 可用: ${info.api}`);
  }

  // 稳定排序
  sites.sort((a, b) => {
    const nameCompare = a.name.localeCompare(b.name, "zh-CN");
    if (nameCompare !== 0) return nameCompare;
    return a.key.localeCompare(b.key);
  });

  fs.writeFileSync(
    "output.json",
    JSON.stringify({ sites }, null, 2),
    "utf-8"
  );

  // 自动生成 README
  const now = new Date().toLocaleString("zh-CN",
