import fs from "fs";
import https from "https";

const SOURCE_URL =
  "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json";

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

/** 清洗 name：去 emoji / 特殊符号 */
function cleanName(name = "") {
  return name
    .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "")
    .replace(/[-—🎬\s]+/g, "")
    .trim();
}

/** 生成 key：域名 → 英文字母 */
function genKey(domain) {
  return domain.replace(/[^a-zA-Z]/g, "").toLowerCase();
}

(async () => {
  const source = await fetchJson(SOURCE_URL);

  const apiSite = source.api_site || {};
  const usedKeys = new Set();

  const sites = Object.entries(apiSite).map(([domain, info]) => {
    let key = genKey(domain);

    // 防止极端情况下 key 冲突
    let suffix = 1;
    while (usedKeys.has(key)) {
      key = `${key}${suffix++}`;
    }
    usedKeys.add(key);

    return {
      key,
      name: cleanName(info.name),
      api: info.api,
      active: true
    };
  });

  const output = { sites };

  fs.writeFileSync(
    "output.json",
    JSON.stringify(output, null, 2),
    "utf-8"
  );

  console.log(`✅ 已生成 ${sites.length} 个站点`);
})();
