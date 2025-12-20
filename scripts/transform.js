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
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(url, { timeout: TIMEOUT }, (res) => {
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

function cleanName(name = "") {
  try {
    return name
      .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "")
      .replace(/[-—🎬\s]+/g, "")
      .trim();
  } catch {
    return name.replace(/[-—🎬\s]+/g, "").trim();
  }
}

function genKey(domain = "") {
  return domain.replace(/[^a-zA-Z]/g, "").toLowerCase() || "site";
}

/* ---------- 主流程 ---------- */

(async () => {
  try {
    const source = await fetchJson(SOURCE_URL);
    const apiSite = source?.api_site ?? {};
    const entries = Object.entries(apiSite);

    const results = await Promise.all(
      entries.map(async ([domain, info]) => ({
        domain,
        info,
        ok: await checkApi(info?.api),
      }))
    );

    const usedKeys = new Set();
    const sites = [];

    for (const { domain, info, ok } of results) {
      if (!ok || !info?.api) continue;
      let key = genKey(domain);
      let i = 1;
      while (usedKeys.has(key)) key = `${key}${i++}`;
      usedKeys.add(key);
      sites.push({
        key,
        name: cleanName(info.name),
        api: info.api,
        active: true,
      });
    }

    // 稳定排序
    sites.sort((a, b) => {
      const n = a.name.localeCompare(b.name, "zh-CN");
      return n !== 0 ? n : a.key.localeCompare(b.key);
    });

    // 写入 output.json
    fs.writeFileSync("output.json", JSON.stringify({ sites }, null, 2), "utf-8");

    /* ---------- 生成 README.md ---------- */

    // 确保 repo/owner 有默认值
    const repo = process.env.GITHUB_REPOSITORY || "yourusername/yourrepo"; // <- 改成你的用户名/仓库名
    const [owner, repoName] = repo.split("/");

    const now = new Date().toLocaleString("zh-CN", { hour12: false });

    const readmeContent = `# 📺 LunaTV 订阅源

## 🔗 订阅地址

### Raw
https://raw.githubusercontent.com/${repo}/main/output.json

### GitHub Pages
https://${owner}.github.io/${repoName}/output.json

---

## 📊 当前状态

- 可用站点数：**${sites.length}**
- 最近更新时间：**${now}**
- 自动维护：GitHub Actions

---

⚠️ 仅供学习与技术研究使用，请于 24 小时内删除。
`;

    fs.writeFileSync("README.md", readmeContent, "utf-8");

    console.log(`🎉 成功生成 ${sites.length} 个站点，并更新 README.md`);
  } catch (err) {
    console.error("❌ transform.js 执行失败");
    console.error(err);
    process.exit(1);
  }
})();
