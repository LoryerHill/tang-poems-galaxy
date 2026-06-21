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
        radius = (usable_w / 2.8) * math.sqrt((i + 0.5) / n_genres)
        cx = canvas_w / 2 + radius * math.cos(angle)
        cy = canvas_h / 2 + radius * math.sin(angle)
        genre_centers[genre] = (cx, cy)

    # 在每个星团中心周围散布粒子
    for genre, group in genre_groups.items():
        cx, cy = genre_centers.get(genre, (canvas_w / 2, canvas_h / 2))
        n = len(group)
        cluster_radius = 30 + 8 * math.sqrt(n)
        for j, poem in enumerate(group):
            r = abs(random.gauss(0, cluster_radius * 0.45))
            r = min(r, cluster_radius * 1.5)
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
st.markdown("""
<style>
    /* ---------- 全局基础 ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap');

    body {
        margin: 0; padding: 0;
        background: #020010;
        color: #e0e0ff;
    }

    /* 主背景 — CSS 星云动画 */
    .stApp {
        background:
            radial-gradient(ellipse at 20% 50%, rgba(72, 49, 212, 0.12) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 20%, rgba(180, 80, 200, 0.08) 0%, transparent 55%),
            radial-gradient(ellipse at 50% 80%, rgba(30, 120, 200, 0.10) 0%, transparent 55%),
            radial-gradient(ellipse at center, #05051a 0%, #020010 100%) !important;
    }

    /* ---------- 侧边栏 — 深空玻璃质感 ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            rgba(15, 12, 50, 0.96) 0%,
            rgba(10, 8, 35, 0.97) 50%,
            rgba(5, 4, 20, 0.98) 100%) !important;
        backdrop-filter: blur(20px) saturate(140%);
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        box-shadow: 4px 0 40px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stSidebar"] * {
        color: #d0d0f0 !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 1.3rem !important;
        letter-spacing: 0.05em;
        background: linear-gradient(135deg, #FFE66D, #FFA94D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    [data-testid="stSidebar"] h3 {
        font-size: 0.95rem !important;
        color: #A0A0D0 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.06) !important;
        margin: 0.8rem 0 !important;
    }
    /* 侧边栏 checkbox 美化 */
    [data-testid="stSidebar"] .stCheckbox label {
        font-size: 0.88rem;
        padding: 0.25rem 0;
        transition: color 0.2s;
    }
    [data-testid="stSidebar"] .stCheckbox label:hover {
        color: #fff !important;
    }
    /* 侧边栏 multiselect */
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
        background: darkslateblue !important;
        border-radius: 12px !important;
        font-size: 0.78rem;
    }

    /* ---------- Streamlit 默认顶栏/工具栏隐藏 ---------- */
    [data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        top: 0px !important;
    }
    [data-testid="stMain"] {
        padding-top: 0 !important;
    }
    [data-testid="stMainViewContainer"] {
        padding-top: 0 !important;
    }

    /* ---------- 主内容区 ---------- */
    section.main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ---------- 标题区域 ---------- */
    .title-container {
        text-align: center;
        padding: 0 0 4px 0;
        position: relative;
    }
    .title-main {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
        letter-spacing: 0.12em;
        background: linear-gradient(180deg, #FFE066 0%, #F0C060 40%, #E0A040 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        filter: drop-shadow(0 0 18px rgba(255, 200, 60, 0.4));
        animation: titleGlow 3s ease-in-out infinite;
    }
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 18px rgba(255, 200, 60, 0.4)); }
        50%      { filter: drop-shadow(0 0 30px rgba(255, 200, 60, 0.7)); }
    }
    .title-sub {
        color: rgba(180, 180, 220, 0.7);
        font-size: 0.82rem;
        letter-spacing: 0.06em;
        margin-top: 2px;
    }
    .title-sub span {
        margin: 0 10px;
        color: rgba(255,255,255,0.25);
    }

    /* ---------- 图例区域 ---------- */
    .legend-wrapper {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px 18px;
        padding: 10px 0 6px 0;
    }
    .legend-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.8rem;
        color: #c0c0e0;
        transition: all 0.25s;
        cursor: default;
    }
    .legend-chip:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(255,255,255,0.18);
        color: #fff;
    }
    .legend-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        box-shadow: 0 0 10px currentColor;
    }

    /* ---------- 页脚 ---------- */
    .footer-info {
        text-align: center;
        color: rgba(180, 180, 210, 0.45);
        font-size: 0.72rem;
        padding: 0 0 4px 0;
        letter-spacing: 0.04em;
    }
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

    st.markdown("---")
    st.markdown(
        f"<div style='color: rgba(180,180,210,0.5); font-size: 0.75rem; text-align: center; "
        f"padding: 8px 0; border-top: 1px solid rgba(255,255,255,0.05);'>"
        f"收录 {len(poems)} 首唐诗 · {len(genre_names)} 种诗体</div>",
        unsafe_allow_html=True
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

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: 100%; height: 100%; overflow: hidden;
    background: #020010;
  }}
  canvas {{ display: block; }}

  /* ---------- 浮动提示 ---------- */
  #tooltip {{
    position: fixed; pointer-events: none; display: none;
    background: rgba(12, 10, 40, 0.94);
    color: #fff;
    padding: 12px 16px;
    border-radius: 12px;
    font-family: 'Noto Serif SC', 'STSong', 'Microsoft YaHei', serif;
    font-size: 14px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 20px rgba(100,120,255,0.1);
    z-index: 999; max-width: 260px; text-align: center;
    backdrop-filter: blur(12px);
    transition: opacity 0.15s;
  }}
  #tooltip .tt-title {{
    font-weight: 700; font-size: 1rem;
    background: linear-gradient(135deg, #FFE66D, #FFA94D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
  }}
  #tooltip .tt-author {{
    color: #95E1D3; font-size: 0.78rem; margin: 3px 0;
  }}
  #tooltip .tt-genre {{
    color: rgba(200,200,220,0.6); font-size: 0.7rem;
    letter-spacing: 0.05em;
  }}
  #tooltip .tt-line {{
    width: 30px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    margin: 6px auto;
  }}

  /* ---------- 详情面板 ---------- */
  #detail-panel {{
    position: fixed;
    right: 24px; top: 50%; transform: translateY(-50%) translateX(20px);
    background: linear-gradient(160deg, rgba(18, 14, 50, 0.94) 0%, rgba(8, 6, 28, 0.96) 100%);
    border-radius: 20px;
    padding: 28px 26px 22px 26px;
    border: 1px solid rgba(255,255,255,0.12);
    font-family: 'Noto Serif SC', 'STKaiti', 'KaiTi', 'Microsoft YaHei', serif;
    color: #e8e8f0;
    display: none; z-index: 1000;
    width: 240px;
    backdrop-filter: blur(20px) saturate(150%);
    box-shadow: 0 16px 48px rgba(0,0,0,0.6), 0 0 40px rgba(100,80,220,0.08);
    opacity: 0;
    transition: opacity 0.35s ease, transform 0.35s ease;
    text-align: center;
  }}
  #detail-panel.visible {{
    opacity: 80%;
    transform: translateY(-50%) translateX(0);
  }}
  #detail-panel .dp-deco {{
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    border-radius: 1px;
  }}
  #detail-panel .dp-title {{
    font-size: 1.25rem; font-weight: 700;
    background: linear-gradient(180deg, #FFE066, #E0A840);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
    letter-spacing: 0.06em;
  }}
  #detail-panel .dp-author {{
    font-size: 0.88rem; color: #95E1D3;
    margin-bottom: 16px;
    letter-spacing: 0.04em;
  }}
  #detail-panel .dp-content {{
    font-size: 1.05rem; line-height: 2.2;
    color: #e0d8f0; letter-spacing: 0.04em;
    max-height: 400px; overflow-y: auto;
    scrollbar-width: thin; scrollbar-color: rgba(255,200,60,0.35) transparent;
    padding-right: 4px;
  }}
  #detail-panel .dp-content::-webkit-scrollbar {{
    width: 4px;
  }}
  #detail-panel .dp-content::-webkit-scrollbar-track {{
    background: transparent;
  }}
  #detail-panel .dp-content::-webkit-scrollbar-thumb {{
    background: rgba(255,200,60,0.35); border-radius: 2px;
  }}
  #detail-panel .dp-genre {{
    font-size: 0.72rem; color: rgba(200,200,220,0.5);
    margin-top: 14px; letter-spacing: 0.06em;
  }}
  #detail-panel .dp-close {{
    position: absolute; top: 10px; right: 14px; cursor: pointer;
    color: rgba(255,255,255,0.35); font-size: 1.1rem;
    width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }}
  #detail-panel .dp-close:hover {{
    color: #fff;
    background: rgba(255,255,255,0.08);
  }}
  #detail-panel .dp-line {{
    width: 40px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    margin: 10px auto 0 auto;
  }}
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
// ==================== 粒子数据 ====================
const particles = {particles_json};
const genreColors = {genre_colors_json};
const genreNames = {genre_names_json};

// ==================== Canvas 初始化 ====================
const canvas = document.getElementById('galaxyCanvas');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');
const detailPanel = document.getElementById('detail-panel');

let W, H;
let mouseX = -999, mouseY = -999;
let hoveredParticle = null;
let time = 0;

// ==================== 相机状态（平移 + 缩放） ====================
let cameraX = 0, cameraY = 0;   // 平移偏移（像素）
let zoom = 1.0;                  // 缩放比例
const ZOOM_MIN = 0.3;
const ZOOM_MAX = 5.0;
const ZOOM_STEP = 0.08;

// 拖拽状态
let isDragging = false;
let dragStartX = 0, dragStartY = 0;
let dragStartCamX = 0, dragStartCamY = 0;
let hasMoved = false;  // 区分拖拽和点击

function resize() {{
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight - 4;
  // 初始居中：让星团中心对齐画布中心
  cameraX = (W - 1200 * zoom) / 2;
  cameraY = (H - 900 * zoom) / 2;
}}
window.addEventListener('resize', resize);
resize();

// ==================== 坐标转换 ====================
function screenToWorld(sx, sy) {{
  return {{
    x: (sx - cameraX) / zoom,
    y: (sy - cameraY) / zoom
  }};
}}

function worldToScreen(wx, wy) {{
  return {{
    x: wx * zoom + cameraX,
    y: wy * zoom + cameraY
  }};
}}

// ==================== 拖拽平移 ====================
canvas.addEventListener('mousedown', (e) => {{
  isDragging = true;
  hasMoved = false;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragStartCamX = cameraX;
  dragStartCamY = cameraY;
  canvas.style.cursor = 'grabbing';
}});

window.addEventListener('mousemove', (e) => {{
  mouseX = e.clientX;
  mouseY = e.clientY;

  if (isDragging) {{
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) hasMoved = true;
    cameraX = dragStartCamX + dx;
    cameraY = dragStartCamY + dy;
    tooltip.style.display = 'none';
    return;
  }}

  // 非拖拽时：hover 检测（用世界坐标）
  const world = screenToWorld(e.clientX, e.clientY);
  let closest = null;
  let minDist = Infinity;
  for (const p of particles) {{
    const offsetX = Math.sin(time * p.floatSpeed + p.floatPhase) * p.floatAmp;
    const offsetY = Math.cos(time * p.floatSpeed * 0.7 + p.floatPhase + 1) * p.floatAmp * 0.8;
    const px = p.baseX + offsetX;
    const py = p.baseY + offsetY;
    const dist = Math.hypot(px - world.x, py - world.y);
    if (dist < 20 / zoom && dist < minDist) {{
      minDist = dist;
      closest = p;
    }}
  }}

  if (closest !== hoveredParticle) {{
    hoveredParticle = closest;
    canvas.style.cursor = closest ? 'pointer' : 'grab';
    if (closest) {{
      tooltip.style.display = 'block';
      tooltip.querySelector('.tt-title').textContent = closest.title;
      tooltip.querySelector('.tt-author').textContent = closest.author;
      tooltip.querySelector('.tt-genre').textContent = '【' + closest.genre + '】';
    }} else {{
      tooltip.style.display = 'none';
    }}
  }}

  if (tooltip.style.display === 'block') {{
    tooltip.style.left = (e.clientX + 20) + 'px';
    tooltip.style.top = (e.clientY - 60) + 'px';
  }}
}});

window.addEventListener('mouseup', () => {{
  isDragging = false;
  canvas.style.cursor = hoveredParticle ? 'pointer' : 'grab';
}});

// ==================== 滚轮缩放 ====================
canvas.addEventListener('wheel', (e) => {{
  e.preventDefault();
  const worldBefore = screenToWorld(e.clientX, e.clientY);
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
  const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoom + delta));
  if (newZoom !== zoom) {{
    zoom = newZoom;
    // 以鼠标位置为中心缩放
    cameraX = e.clientX - worldBefore.x * zoom;
    cameraY = e.clientY - worldBefore.y * zoom;
  }}
}}, {{ passive: false }});

// ==================== 点击事件 ====================
canvas.addEventListener('click', (e) => {{
  if (hasMoved) return;  // 拖拽后不触发点击
  if (hoveredParticle) {{
    showDetail(hoveredParticle);
  }}
}});

function showDetail(p) {{
  document.getElementById('dp-title').textContent = p.title;
  document.getElementById('dp-author').textContent = '—— ' + p.author;
  document.getElementById('dp-content').innerHTML = p.content.join('<br>');
  document.getElementById('dp-genre').textContent = '【' + p.genre + '】';
  detailPanel.style.display = 'block';
  requestAnimationFrame(() => {{
    detailPanel.classList.add('visible');
  }});
}}

function closeDetail() {{
  detailPanel.classList.remove('visible');
  setTimeout(() => {{ detailPanel.style.display = 'none'; }}, 350);
}}

canvas.addEventListener('click', (e) => {{
  if (hasMoved) return;
  if (!hoveredParticle && detailPanel.style.display === 'block') {{
    const rect = detailPanel.getBoundingClientRect();
    const cx = e.clientX, cy = e.clientY;
    if (!(cx >= rect.left && cx <= rect.right && cy >= rect.top && cy <= rect.bottom)) {{
      closeDetail();
    }}
  }}
}});

// ==================== 背景星尘（含星云） ====================
const bgStars = [];
const N_BG = 1200;
for (let i = 0; i < N_BG; i++) {{
  bgStars.push({{
    x: Math.random() * 2500,
    y: Math.random() * 2500,
    r: Math.random() * 1.4 + 0.2,
    twinkle: Math.random() * Math.PI * 2,
    speed: Math.random() * 0.025 + 0.004,
    hue: 200 + Math.random() * 60
  }});
}}

// 星云斑点
const nebulae = [];
for (let i = 0; i < 6; i++) {{
  nebulae.push({{
    x: W * (0.1 + Math.random() * 0.8),
    y: H * (0.1 + Math.random() * 0.8),
    r: 80 + Math.random() * 200,
    hue: [260, 320, 200, 30, 340, 180][i],
    alpha: 0.015 + Math.random() * 0.025,
    driftX: (Math.random() - 0.5) * 0.3,
    driftY: (Math.random() - 0.5) * 0.3
  }});
}}

// 流星
const shootingStars = [];
const MAX_SHOOTERS = 2;

function spawnShootingStar() {{
  if (shootingStars.length >= MAX_SHOOTERS) return;
  shootingStars.push({{
    x: Math.random() * W * 0.8 + W * 0.1,
    y: Math.random() * H * 0.3,
    vx: -(2 + Math.random() * 4),
    vy: 1.5 + Math.random() * 3,
    life: 1.0,
    decay: 0.008 + Math.random() * 0.015,
    length: 40 + Math.random() * 80
  }});
}}
setInterval(() => {{ if (Math.random() < 0.4) spawnShootingStar(); }}, 3000);
spawnShootingStar();

function drawBackground() {{
  // 深空底
  ctx.fillStyle = '#020010';
  ctx.fillRect(0, 0, W, H);

  // 星云
  for (const n of nebulae) {{
    const nx = n.x + Math.sin(time * 0.05 + n.driftX) * 20;
    const ny = n.y + Math.cos(time * 0.04 + n.driftY) * 20;
    const grad = ctx.createRadialGradient(nx, ny, 0, nx, ny, n.r);
    grad.addColorStop(0, `hsla(${{n.hue}}, 60%, 50%, ${{n.alpha * 2}})`);
    grad.addColorStop(0.5, `hsla(${{n.hue}}, 50%, 30%, ${{n.alpha}})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(nx - n.r, ny - n.r, n.r * 2, n.r * 2);
  }}

  // 背景星
  for (const s of bgStars) {{
    const alpha = 0.25 + 0.35 * Math.sin(time * s.speed + s.twinkle);
    ctx.fillStyle = `hsla(${{s.hue}}, 40%, 80%, ${{alpha}})`;
    ctx.beginPath();
    ctx.arc(s.x % W, s.y % H, s.r, 0, Math.PI * 2);
    ctx.fill();
  }}

  // 流星
  for (let i = shootingStars.length - 1; i >= 0; i--) {{
    const ss = shootingStars[i];
    ss.x += ss.vx;
    ss.y += ss.vy;
    ss.life -= ss.decay;
    if (ss.life <= 0) {{ shootingStars.splice(i, 1); continue; }}

    const sx = ss.x, sy = ss.y;
    const angle = Math.atan2(ss.vy, ss.vx);
    const ex = sx - Math.cos(angle) * ss.length;
    const ey = sy - Math.sin(angle) * ss.length;

    const grad = ctx.createLinearGradient(sx, sy, ex, ey);
    grad.addColorStop(0, `rgba(255,255,255,${{ss.life}})`);
    grad.addColorStop(0.15, `rgba(200,220,255,${{ss.life * 0.7}})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.strokeStyle = grad;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(ex, ey);
    ctx.stroke();
  }}
}}

// ==================== 绘制粒子 ====================
function drawParticles() {{
  for (const p of particles) {{
    const offsetX = Math.sin(time * p.floatSpeed + p.floatPhase) * p.floatAmp;
    const offsetY = Math.cos(time * p.floatSpeed * 0.7 + p.floatPhase + 1) * p.floatAmp * 0.8;
    const px = p.baseX + offsetX;
    const py = p.baseY + offsetY;

    // 用世界坐标判断 hover
    const world = screenToWorld(mouseX, mouseY);
    const dx = px - world.x;
    const dy = py - world.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const isHovered = dist < 20 / zoom;
    const drawSize = isHovered ? p.size * 2.2 : p.size;

    // 外层光晕
    const glow = ctx.createRadialGradient(px, py, drawSize * 0.2, px, py, drawSize * 2.5);
    glow.addColorStop(0, p.color);
    glow.addColorStop(0.5, p.color + '88');
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(px, py, drawSize * 2.5, 0, Math.PI * 2);
    ctx.fill();

    // 十字星光
    if (p.size > 3.5) {{
      const sparkAlpha = 0.15 + 0.1 * Math.sin(time * 3 + p.floatPhase);
      ctx.strokeStyle = p.color;
      ctx.globalAlpha = sparkAlpha;
      ctx.lineWidth = 0.6;
      const sparkLen = drawSize * 2.0;
      ctx.beginPath();
      ctx.moveTo(px - sparkLen, py);
      ctx.lineTo(px + sparkLen, py);
      ctx.moveTo(px, py - sparkLen);
      ctx.lineTo(px, py + sparkLen);
      ctx.stroke();
      ctx.globalAlpha = 1.0;
    }}

    // 内核
    const core = ctx.createRadialGradient(px, py, 0, px, py, drawSize * 0.8);
    core.addColorStop(0, '#ffffff');
    core.addColorStop(0.35, p.color);
    core.addColorStop(0.7, p.color + '66');
    core.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = core;
    ctx.beginPath();
    ctx.arc(px, py, drawSize * 0.8, 0, Math.PI * 2);
    ctx.fill();

    // hover 高亮环
    if (isHovered) {{
      const ringAlpha = 0.5 + 0.2 * Math.sin(time * 4);
      ctx.strokeStyle = `rgba(255,255,255,${{ringAlpha}})`;
      ctx.lineWidth = 2 / zoom;
      ctx.beginPath();
      ctx.arc(px, py, drawSize * 1.15, 0, Math.PI * 2);
      ctx.stroke();

      // 外层脉冲
      ctx.strokeStyle = `rgba(255,255,255,${{ringAlpha * 0.3}})`;
      ctx.lineWidth = 1 / zoom;
      ctx.beginPath();
      ctx.arc(px, py, drawSize * 2.0, 0, Math.PI * 2);
      ctx.stroke();
    }}
  }}
}}

// ==================== 动画循环 ====================
function animate() {{
  time += 0.016;
  ctx.clearRect(0, 0, W, H);

  // 绘制背景（不受相机影响 — 始终填满画布）
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  drawBackground();
  ctx.restore();

  // 绘制粒子（受相机变换影响）
  ctx.save();
  ctx.setTransform(zoom, 0, 0, zoom, cameraX, cameraY);
  drawParticles();
  ctx.restore();

  requestAnimationFrame(animate);
}}

animate();
</script>
</body>
</html>'''
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