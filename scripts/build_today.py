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
    <title>오늘의 데이트 추천</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .recommendation {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fff;
        }}
        .recommendation h2 {{
            color: #007bff;
            margin: 0 0 10px 0;
        }}
        .score {{
            color: #28a745;
            font-weight: bold;
        }}
        .reason {{
            color: #666;
            font-style: italic;
        }}
        .type {{
            display: inline-block;
            padding: 3px 8px;
            background-color: #e9ecef;
            border-radius: 3px;
            font-size: 0.9em;
            color: #495057;
        }}
        .back-link {{
            margin-top: 20px;
            display: block;
            color: #007bff;
            text-decoration: none;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>오늘의 데이트 추천 ({today})</h1>
        <p>날씨와 취향을 반영해 추천했어요.</p>
"""
    
    for i, item in enumerate(top3, start=1):
        html += f"""
        <div class="recommendation">
            <h2>{i}. {item['name']}</h2>
            <span class="type">{item['type']}</span>
            <p><span class="score">점수: {item['score']}</span></p>
            <p class="reason">이유: {item['reason']}</p>
        </div>
"""
    
    html += """
        <a href="../index.html" class="back-link">← 메인으로 돌아가기</a>
    </div>
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

# Create index.html
index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>오늘의 데이트 추천</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .note {
            color: #666;
            font-style: italic;
            margin-top: 20px;
            padding: 10px;
            border-left: 3px solid #007bff;
            background-color: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>오늘의 데이트 추천</h1>
        <p><a href="posts/today.html">오늘 추천 보기</a></p>
        <p class="note">매일 아침 자동으로 갱신됩니다. (GitHub Actions)</p>
    </div>
</body>
</html>"""
open("docs/index.html","w",encoding="utf-8").write(index_html)
print("built: site/index.html")
