import requests
import json
import hashlib

def get_unique_key(url):
    # 生成 8 位唯一 Key
    return "site_" + hashlib.md5(url.encode()).hexdigest()[:8]

def main():
    # 源文件 URL
    source_url = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
    
    try:
        print(f"正在从源地址获取数据...")
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        new_sites = []
        unique_urls = set()

        # --- 核心解析逻辑：针对 LunaTV-config 特有结构 ---
        # 源文件是一个字典，其站点信息主要存在 'lives' 键下的各个分类中
        if isinstance(data, dict) and 'lives' in data:
            for category in data['lives']:
                # 获取该分类下的站点列表
                items = category.get('list', [])
                for item in items:
                    name = item.get('name', '未知站点')
                    # 优先取 api，其次取 url 或 ext
                    api_url = item.get('api') or item.get('url') or item.get('ext')
                    
                    # 验证并去重
                    if api_url and isinstance(api_url, str) and api_url.startswith('http'):
                        if api_url not in unique_urls:
                            new_sites.append({
                                "key": get_unique_key(api_url),
                                "name": name,
                                "api": api_url,
                                "active": True
                            })
                            unique_urls.add(api_url)

        # 构建最终输出格式
        output = {"sites": new_sites}
        
        # 保存文件
        output_filename = 'donggua.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"转换成功！共提取 {len(new_sites)} 个站点，已保存到 {output_filename}")
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
