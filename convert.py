import requests
import json
import hashlib

def get_unique_key(url):
    return "key_" + hashlib.md5(url.encode()).hexdigest()[:8]

def main():
    # 源文件地址
    source_url = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
    
    try:
        response = requests.get(source_url)
        # 针对该源文件结构的解析逻辑
        data = response.json()
        
        # 假设源数据是 LunaTV 标准格式，提取其站点列表
        # 如果源文件直接是列表，则直接使用；如果是字典，取其 sites 键
        source_sites = data if isinstance(data, list) else data.get('sites', [])
        
        new_sites = []
        for item in source_sites:
            # 提取 API 地址（适配 api 或 ext 字段）
            api_url = item.get('api') or item.get('ext')
            name = item.get('name', '未知站点')
            
            if api_url and isinstance(api_url, str):
                new_sites.append({
                    "key": get_unique_key(api_url),
                    "name": name,
                    "api": api_url,
                    "active": True
                })
        
        # 构建最终格式
        output = {"sites": new_sites}
        
        with open('LunaTV-formatted.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"成功转换 {len(new_sites)} 个站点")
        
    except Exception as e:
        print(f"执行失败: {e}")
        exit(1)

if __name__ == "__main__":
    main()
