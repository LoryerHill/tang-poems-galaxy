"""
唐诗星云 - 交互式唐诗可视化网页
将唐诗以微小颗粒形态汇聚成团，形成"星云"效果
"""

import streamlit as st
import json
import random
import plotly.graph_objects as go
import numpy as np

# 页面配置
st.set_page_config(
    page_title="唐诗星云",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 体裁颜色映射
genre_colors = {
    "五言（古诗）绝句": "pink",
    "七言（古诗）绝句": "orange",
    "五言（古诗）律诗": "white",
    "七言（古诗）律诗": "yellowgreen",
    "五言古诗": "skyblue",
    "七言古诗": "cyan",
    "乐府诗": "magenta"
}

genre_names = list(genre_colors.keys())

# ==================== 加载数据 ====================
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

# 加载唐诗数据
poems = load_poems("tang_poems.json")

# ==================== 生成星云坐标 ====================
def generate_nebula_coordinates(poems):
    """为每首诗生成星云坐标"""
    coords = []
    
    # 按体裁分组
    genre_groups = {genre: [] for genre in genre_names}
    for poem in poems:
        genre_groups[poem['genre']].append(poem)
    
    # 为每个体裁分配一个中心区域
    genre_centers = {}
    for i, genre in enumerate(genre_names):
        angle = (i / len(genre_names)) * 2 * np.pi
        radius = 3.0
        genre_centers[genre] = {
            'x': radius * np.cos(angle),
            'y': radius * np.sin(angle)
        }
    
    # 为每首诗生成坐标，相同体裁聚集在一起
    for genre in genre_names:
        group_poems = genre_groups[genre]
        center = genre_centers[genre]
        
        # 计算该体裁的密度
        density = len(group_poems) / max(len(poems) / len(genre_names), 1)
        
        for i, poem in enumerate(group_poems):
            # 在体裁中心周围生成聚集分布
            # 使用高斯分布使点聚集在中心附近
            cluster_spread = 1.2 + density * 0.5  # 密度高的体裁分布范围稍大
            
            # 添加螺旋偏移使分布更自然
            angle_offset = (i / max(len(group_poems), 1)) * 2 * np.pi * 0.3
            angle_noise = random.gauss(0, 0.5)
            
            # 距离中心的位置，使用高斯分布
            distance = abs(random.gauss(0, cluster_spread * 0.6))
            distance = min(distance, cluster_spread * 2)  # 限制最大距离
            
            # 计算相对位置
            local_angle = angle_offset + angle_noise
            local_x = distance * np.cos(local_angle)
            local_y = distance * np.sin(local_angle)
            
            # 最终坐标 = 中心坐标 + 相对偏移
            x = center['x'] + local_x + random.gauss(0, 0.2)
            y = center['y'] + local_y + random.gauss(0, 0.2)
            
            # 根据密度和位置调整大小
            base_size = random.uniform(4, 9)
            # 靠近中心的点稍大
            center_proximity = 1 - (distance / (cluster_spread * 2))
            size = base_size + center_proximity * 3 + random.uniform(-1, 1)
            
            coords.append({
                'x': x,
                'y': y,
                'size': max(3, min(14, size)),
                'poem': poem
            })
        
    return coords

coordinates = generate_nebula_coordinates(poems)

# ==================== 会话状态 ====================
if "selected_poem" not in st.session_state:
    st.session_state.selected_poem = None

# ==================== 创建星云图 ====================
def create_nebula_figure():
    fig = go.Figure()
    
    for genre in genre_names:
        genre_data = [c for c in coordinates if c['poem']['genre'] == genre]
        
        if not genre_data:
            continue
        
        x_vals = [c['x'] for c in genre_data]
        y_vals = [c['y'] for c in genre_data]
        sizes = [c['size'] for c in genre_data]
        titles = [c['poem']['title'] for c in genre_data]
        authors = [c['poem']['author'] for c in genre_data]
        
        # 创建悬停文本
        hover_texts = [f"<b>{title}</b><br>作者: {author}<br>体裁: {genre}" 
                      for title, author in zip(titles, authors)]
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers',
            marker=dict(
                color=genre_colors[genre],
                size=sizes,
                opacity=0.7,
                line=dict(
                    width=1,
                    color='rgba(255,255,255,0.3)'
                ),
                symbol='circle'
            ),
            text=hover_texts,
            hoverinfo='text',
            name=genre,
            customdata=[i for i, _ in enumerate(genre_data)],
            hovertemplate='%{text}<extra></extra>'
        ))
    
    # 更新布局
    fig.update_layout(
        title={
            'text': '✨ 唐诗星云',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 28, 'color': '#fff', 'family': 'Microsoft YaHei'}
        },
        showlegend=True,
        legend={
            'title': {'text': '诗体分类', 'font': {'color': '#fff', 'size': 14}},
            'font': {'color': '#fff', 'size': 12},
            'bgcolor': 'rgba(0,0,0,0.5)',
            'bordercolor': 'rgba(255,255,255,0.2)',
            'borderwidth': 1
        },
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.8, 7.8]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.8, 3.8]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=60, b=0),
        hovermode='closest',
        height=700
    )
    
    # 添加自定义点击事件
    fig.update_layout(
        clickmode='event+select'
    )
    
    return fig

# ==================== 主页面 ====================
# 背景样式
st.markdown("""
    <style>
    body {
        background: radial-gradient(ellipse at center, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
        background-attachment: fixed;
        color: #fff;
    }
    .stApp {
        background: transparent;
    }
    .poem-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .poem-title {
        font-size: 24px;
        font-weight: bold;
        color: #FFE66D;
        margin-bottom: 8px;
        font-family: 'Microsoft YaHei', serif;
    }
    .poem-author {
        font-size: 16px;
        color: #95E1D3;
        margin-bottom: 20px;
        font-family: 'Microsoft YaHei', serif;
    }
    .poem-content {
        font-size: 18px;
        line-height: 2;
        color: #fff;
        font-family: 'KaiTi', 'STKaiti', serif;
        text-align: center;
        white-space: pre-wrap;
    }
    .poem-genre {
        font-size: 14px;
        color: #aaa;
        margin-top: 16px;
        text-align: center;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    .legend-color {
        width: 16px;
        height: 16px;
        border-radius: 50%;
    }
    </style>
""", unsafe_allow_html=True)

# 标题区域
st.markdown("""
    <div style="text-align: center; padding-top: 20px;">
        <h1 style="font-size: 42px; font-family: 'Microsoft YaHei'; color: #fff; text-shadow: 0 0 30px rgba(255,230,109,0.5);">
            ✨ 唐诗星云 ✨
        </h1>
        <p style="color: #aaa; margin-top: 8px;">点击星云中的微粒，探索千年诗韵</p>
    </div>
""", unsafe_allow_html=True)

# 主布局 - 左右两栏
col_map, col_info = st.columns([2.5, 1], gap="medium")

with col_map:
    st.plotly_chart(create_nebula_figure(), use_container_width=True, key='nebula_plot')

with col_info:
    # 图例说明
    st.markdown("""
        <div class="poem-card">
            <h3 style="color: #fff; margin-bottom: 16px;">📖 诗体图例</h3>
    """, unsafe_allow_html=True)
    
    for genre, color in genre_colors.items():
        st.markdown(f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span style="color: #ddd;">{genre}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 诗词详情卡片
    if st.session_state.selected_poem:
        poem = st.session_state.selected_poem
        content_text = "\n".join(poem['content'])
        
        st.markdown(f"""
            <div class="poem-card" style="margin-top: 20px;">
                <div class="poem-title">{poem['title']}</div>
                <div class="poem-author">—— {poem['author']}</div>
                <div class="poem-content">{content_text}</div>
                <div class="poem-genre">【{poem['genre']}】</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="poem-card" style="margin-top: 20px; text-align: center; padding: 60px 24px;">
                <div style="font-size: 48px; margin-bottom: 16px;">🌟</div>
                <div style="color: #aaa; font-size: 16px;">点击星云中的微粒<br>查看诗词详情</div>
            </div>
        """, unsafe_allow_html=True)

# ==================== 点击交互处理 ====================
# 获取点击事件
selected_points = st.session_state.get('nebula_plot', {}).get('clickData')

if selected_points:
    point = selected_points['points'][0]
    genre = point['fullData']['name']
    
    # 找到对应的诗词
    genre_poems = [c for c in coordinates if c['poem']['genre'] == genre]
    idx = point['customdata'][0]
    
    if idx < len(genre_poems):
        st.session_state.selected_poem = genre_poems[idx]['poem']
        st.rerun()

# 底部统计信息
st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 14px;">
        共收录 {} 首唐诗 · 包含 {} 种诗体
    </div>
""".format(len(poems), len(genre_names)), unsafe_allow_html=True)