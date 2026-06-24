"""
唐诗星云 - 粒子星团可视化
每一首诗是一个微粒，同体裁的微粒汇聚成星团，带有轻微波动效果
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import random
import math
import os

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="唐诗星云",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 静态资源路径 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

@st.cache_data
def load_asset(filename):
    """读取 assets 目录下的文本文件"""
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# ==================== 加载数据 ====================
@st.cache_data
def load_poems(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    poems = []
    current_genre = ""
    for item in data:
        if 'genre' in item:
            current_genre = item['genre']
        elif 'title' in item:
            poems.append({
                'title': item['title'],
                'author': item['author'],
                'content': item['content'],
                'genre': current_genre
            })
    return poems

DATA_PATH = os.path.join(os.path.dirname(__file__), "tang_poems.json")
poems = load_poems(DATA_PATH)

# 动态提取体裁和作者
genre_names = sorted(set(p['genre'] for p in poems if p['genre']))
all_authors = sorted(set(p['author'] for p in poems))

# 体裁颜色映射（星云主题色板 — 更柔和、更有宇宙感）
genre_color_pool = [
    "#FF6B9D", "#FFA94D", "#FFD43B", "#51CF66",
    "#4DABF7", "#CC5DE8", "#3BC9DB", "#F783AC",
    "#74C0FC", "#FF8787", "#FFE066", "#A9E34B"
]
genre_colors = {
    g: genre_color_pool[i % len(genre_color_pool)]
    for i, g in enumerate(genre_names)
}

# 为每首诗分配全局 id
for idx, p in enumerate(poems):
    p['global_id'] = idx

# ==================== 生成粒子坐标（星团布局） ====================
def generate_particle_data(poem_list, canvas_w=1200, canvas_h=900):
    """为每首诗生成 2D 粒子坐标，同体裁汇聚成星团"""
    seed = sum(p['global_id'] for p in poem_list) if poem_list else 42
    random.seed(seed)
    particles = []
    genre_groups = {}
    for p in poem_list:
        genre_groups.setdefault(p['genre'], []).append(p)

    margin = 100
    usable_w = canvas_w - margin * 2
    usable_h = canvas_h - margin * 2

    # 为每个体裁分配星团中心（螺旋排列）
    genre_centers = {}
    n_genres = len(genre_groups)
    for i, genre in enumerate(genre_names):
        if genre not in genre_groups:
            continue
        angle = i * 2.399963  # 黄金角 ≈ 137.5°
        radius = (usable_w / 2.2) * math.sqrt((i + 0.5) / n_genres)
        cx = canvas_w / 2 + radius * math.cos(angle)
        cy = canvas_h / 2 + radius * math.sin(angle)
        genre_centers[genre] = (cx, cy)

    # 在每个星团中心周围散布粒子
    for genre, group in genre_groups.items():
        cx, cy = genre_centers.get(genre, (canvas_w / 2, canvas_h / 2))
        n = len(group)
        cluster_radius = 50 + 15 * math.sqrt(n)
        for j, poem in enumerate(group):
            r = abs(random.gauss(0, cluster_radius * 0.6))
            r = min(r, cluster_radius * 1.8)
            theta = random.uniform(0, 2 * math.pi)
            px = cx + r * math.cos(theta)
            py = cy + r * math.sin(theta)
            size = random.uniform(2.5, 6.0)
            float_amp = random.uniform(3, 12)
            float_speed = random.uniform(0.3, 0.8)
            float_phase = random.uniform(0, 2 * math.pi)
            particles.append({
                'id': poem['global_id'],
                'baseX': round(px, 2),
                'baseY': round(py, 2),
                'size': round(size, 2),
                'color': genre_colors[genre],
                'genre': genre,
                'title': poem['title'],
                'author': poem['author'],
                'content': poem['content'],
                'floatAmp': round(float_amp, 2),
                'floatSpeed': round(float_speed, 2),
                'floatPhase': round(float_phase, 2)
            })
    return particles

# ==================== 页面样式 ====================
st.markdown(f"""
<style>
{load_asset('style.css')}
</style>
""", unsafe_allow_html=True)

# ==================== 左侧边栏 ====================
with st.sidebar:
    st.markdown("## 唐诗星云")
    st.markdown("""
        <div style="font-size:0.78rem;color:rgba(180,180,210,0.6);margin-top:-8px;letter-spacing:0.05em;">
        一诗一星辰 · 一体一星团
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 体裁筛选")
    selected_genres = []
    for genre in genre_names:
        if st.checkbox(genre, value=True, key=f"genre_{genre}"):
            selected_genres.append(genre)

    st.markdown("---")
    st.markdown("### 诗人筛选")
    selected_authors = st.multiselect(
        "选择诗人", options=all_authors, default=all_authors,
        key="author_filter", label_visibility="collapsed"
    )

# ==================== 筛选数据 ====================
filtered_poems = [
    p for p in poems
    if p['genre'] in selected_genres and p['author'] in selected_authors
]

particles = generate_particle_data(filtered_poems)

# ==================== 构建 Canvas 粒子动画 HTML ====================
def build_canvas_html(particles_data, genre_colors_map, genre_names_list):
    particles_json = json.dumps(particles_data, ensure_ascii=False)
    genre_colors_json = json.dumps(genre_colors_map, ensure_ascii=False)
    genre_names_json = json.dumps(genre_names_list, ensure_ascii=False)

    canvas_css = load_asset('canvas_style.css')
    canvas_script = load_asset('canvas_script.js')

    html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
__CANVAS_CSS__
</style>
</head>
<body>
<canvas id="galaxyCanvas"></canvas>
<div id="tooltip">
  <div class="tt-title"></div>
  <div class="tt-line"></div>
  <div class="tt-author"></div>
  <div class="tt-genre"></div>
</div>
<div id="detail-panel">
  <div class="dp-deco"></div>
  <span class="dp-close" onclick="closeDetail()">&#10005;</span>
  <div class="dp-title" id="dp-title"></div>
  <div class="dp-author" id="dp-author"></div>
  <div class="dp-content" id="dp-content"></div>
  <div class="dp-line"></div>
  <div class="dp-genre" id="dp-genre"></div>
</div>

<script>
__CANVAS_SCRIPT__
</script>
</body>
</html>'''

    html = html.replace('__CANVAS_CSS__', canvas_css)
    html = html.replace('__CANVAS_SCRIPT__', canvas_script)
    html = html.replace('{particles_json}', particles_json)
    html = html.replace('{genre_colors_json}', genre_colors_json)
    html = html.replace('{genre_names_json}', genre_names_json)
    return html

# ==================== 主区域 ====================
# 标题
st.markdown("""
    <div class="title-container">
        <div class="title-main">唐 诗 星 云</div>
        <div class="title-sub">
            拖拽平移<span>·</span>滚轮缩放<span>·</span>悬停查看<span>·</span>点击读诗
        </div>
    </div>
""", unsafe_allow_html=True)

# 渲染 Canvas（居中容器）
html_content = build_canvas_html(particles, genre_colors, genre_names)
st.markdown('<div class="canvas-wrapper">', unsafe_allow_html=True)
components.html(html_content, height=700, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)

# 图例 — 胶囊式
legend_html = '<div class="legend-wrapper">'
for genre in genre_names:
    color = genre_colors[genre]
    legend_html += (
        f'<div class="legend-chip">'
        f'<span class="legend-dot" style="background:{color};box-shadow:0 0 10px {color};"></span>'
        f'{genre}'
        f'</div>'
    )
legend_html += '</div>'
st.markdown(legend_html, unsafe_allow_html=True)

# 底部信息
st.markdown(
    f'<div class="footer-info">收录 {len(poems)} 首唐诗 &nbsp;·&nbsp; {len(genre_names)} 种诗体 &nbsp;·&nbsp; 一诗一星辰</div>',
    unsafe_allow_html=True
)
