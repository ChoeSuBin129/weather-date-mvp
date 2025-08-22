from datetime import date
import json, os

print("Creating posts directory...")
os.makedirs("docs/posts", exist_ok=True)
today = str(date.today())
print("Today:", today)
top3 = []
print("Checking for top3 data...")
if os.path.exists("data/tmp_top3.json"):
    print("Loading top3 data...")
    top3 = json.load(open("data/tmp_top3.json", encoding="utf-8"))
    print("Top3 data:", top3)
else:
    print("No top3 data found!")

def create_html(top3, today):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>오늘의 추천 | 행운 상점</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #FF6B6B;
            --secondary-color: #4ECDC4;
            --accent-color: #A5B4FC;
            --background-color: #F8F9FA;
            --text-color: #495057;
            --border-radius: 20px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: var(--border-radius);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: var(--primary-color);
            margin-bottom: 10px;
            text-align: center;
            font-weight: 700;
            font-size: 2.5em;
            letter-spacing: -0.5px;
        }}

        .subtitle {{
            text-align: center;
            color: var(--text-color);
            margin: 0 0 30px;
            font-size: 1.1em;
            opacity: 0.8;
        }}
        
        .tabs {{
            display: flex;
            gap: 15px;
            margin: -20px -20px 30px -20px;
            padding: 20px;
            background: linear-gradient(to right, #fff3f3, #e9fffd);
            border-radius: var(--border-radius) var(--border-radius) 0 0;
        }}
        
        .tab {{
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            transition: var(--transition);
            background-color: white;
            border: none;
            font-size: 16px;
            color: var(--text-color);
            font-weight: 500;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            flex: 1;
            text-align: center;
        }}
        
        .tab:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .tab.active {{
            background-color: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }}
        
        .tab-content {{
            display: none;
            padding: 20px 0;
            animation: fadeIn 0.5s ease-in-out;
        }}
        
        .tab-content.active {{
            display: block;
        }}

        .recommendation {{
            margin: 0 0 25px;
            padding: 25px;
            border-radius: var(--border-radius);
            background: white;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: var(--transition);
            animation: fadeIn 0.5s ease-in-out;
        }}
        
        .recommendation:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }}
        
        .recommendation h2 {{
            color: var(--primary-color);
            margin: 0 0 15px 0;
            font-size: 1.5em;
            font-weight: 700;
        }}
        
        .score {{
            display: inline-block;
            padding: 5px 12px;
            background-color: #e8f5e9;
            color: #2e7d32;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        
        .type {{
            display: inline-block;
            padding: 5px 12px;
            background-color: #fff3f3;
            border-radius: 20px;
            font-size: 0.9em;
            color: var(--primary-color);
            font-weight: 500;
        }}
        
        .reason {{
            margin: 15px 0 0;
            color: var(--text-color);
            font-size: 0.95em;
            opacity: 0.9;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background-color: white;
            color: var(--text-color);
            text-decoration: none;
            border-radius: 20px;
            margin-top: 30px;
            transition: var(--transition);
            font-weight: 500;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        
        .back-link:before {{
            content: "←";
            font-size: 1.2em;
            line-height: 1;
        }}
        
        .back-link:hover {{
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            transform: translateX(-5px);
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 40px;
            color: var(--text-color);
            background: linear-gradient(135deg, #fff3f3, #e9fffd);
            border-radius: var(--border-radius);
            margin-top: 40px;
        }}
        
        .no-results h3 {{
            color: var(--primary-color);
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
            }}
            
            .tabs {{
                padding: 15px;
            }}
            
            .tab {{
                padding: 10px 15px;
                font-size: 14px;
            }}
            
            .recommendation {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>오늘의 추천</h1>
        <p class="subtitle">{today}의 날씨와 분위기를 고려했어요</p>

        <div class="tabs">
            <button class="tab active" onclick="showTab('places')">맛집/카페</button>
            <button class="tab" onclick="showTab('events')">전시/공연</button>
        </div>

        <!-- 맛집/카페 탭 -->
        <div id="places-tab" class="tab-content active">"""

    # 장소 추천 (기존 top3)
    for i, item in enumerate(top3, start=1):
        html += f"""
            <div class="recommendation">
                <h2>{i}. {item['name']}</h2>
                <span class="score">점수 {int(float(item['score'])*100)}%</span>
                <span class="type">{item['type']}</span>
                <p class="reason">{item['reason']}</p>
            </div>"""

    # 전시/공연 탭 (임시 데이터)
    html += """
        </div>

        <!-- 전시/공연 탭 -->
        <div id="events-tab" class="tab-content">
            <div class="recommendation">
                <h2>1. 광복 80주년 특별전</h2>
                <span class="score">점수 95%</span>
                <span class="type">전시</span>
                <p class="reason">현재 진행 중인 특별 전시예요</p>
            </div>

            <div class="recommendation">
                <h2>2. 재즈 페스티벌 2025</h2>
                <span class="score">점수 90%</span>
                <span class="type">공연</span>
                <p class="reason">오늘 저녁에 진행되는 특별 공연이에요</p>
            </div>
        </div>

        <a href="../index.html" class="back-link">메인으로 돌아가기</a>
    </div>

    <script>
    function showTab(tabName) {
        // 모든 탭 컨텐츠 숨기기
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // 모든 탭 버튼 비활성화
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // 선택된 탭 컨텐츠와 버튼 활성화
        document.getElementById(tabName + '-tab').classList.add('active');
        document.querySelector(`.tab[onclick="showTab('${tabName}')"]`).classList.add('active');
    }
    </script>
</body>
</html>"""
    return html

# Create markdown version
lines = [f"# 오늘의 데이트 추천 ({today})", "", "날씨와 취향을 반영해 추천했어요.", ""]
for i, item in enumerate(top3, start=1):
    lines.append(f"**{i}. {item['name']}** ({item['type']}) — 점수 {item['score']}  \n이유: {item['reason']}")
open("docs/posts/today.md","w",encoding="utf-8").write("\n".join(lines))
print("built: site/posts/today.md")

# Create HTML version
html_content = create_html(top3, today)
open("docs/posts/today.html","w",encoding="utf-8").write(html_content)
print("built: site/posts/today.html")