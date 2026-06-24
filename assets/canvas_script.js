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

function resize() {
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight - 4;
  // 初始居中：让星团中心对齐画布中心
  cameraX = (W - 1200 * zoom) / 2;
  cameraY = (H - 900 * zoom) / 2;
}
window.addEventListener('resize', resize);
resize();

// ==================== 坐标转换 ====================
function screenToWorld(sx, sy) {
  return {
    x: (sx - cameraX) / zoom,
    y: (sy - cameraY) / zoom
  };
}

function worldToScreen(wx, wy) {
  return {
    x: wx * zoom + cameraX,
    y: wy * zoom + cameraY
  };
}

// ==================== 拖拽平移 ====================
canvas.addEventListener('mousedown', (e) => {
  isDragging = true;
  hasMoved = false;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragStartCamX = cameraX;
  dragStartCamY = cameraY;
  canvas.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;

  if (isDragging) {
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) hasMoved = true;
    cameraX = dragStartCamX + dx;
    cameraY = dragStartCamY + dy;
    tooltip.style.display = 'none';
    return;
  }

  // 非拖拽时：hover 检测（用世界坐标）
  const world = screenToWorld(e.clientX, e.clientY);
  let closest = null;
  let minDist = Infinity;
  for (const p of particles) {
    const offsetX = Math.sin(time * p.floatSpeed + p.floatPhase) * p.floatAmp;
    const offsetY = Math.cos(time * p.floatSpeed * 0.7 + p.floatPhase + 1) * p.floatAmp * 0.8;
    const px = p.baseX + offsetX;
    const py = p.baseY + offsetY;
    const dist = Math.hypot(px - world.x, py - world.y);
    if (dist < 20 / zoom && dist < minDist) {
      minDist = dist;
      closest = p;
    }
  }

  if (closest !== hoveredParticle) {
    hoveredParticle = closest;
    canvas.style.cursor = closest ? 'pointer' : 'grab';
    if (closest) {
      tooltip.style.display = 'block';
      tooltip.querySelector('.tt-title').textContent = closest.title;
      tooltip.querySelector('.tt-author').textContent = closest.author;
      tooltip.querySelector('.tt-genre').textContent = '【' + closest.genre + '】';
    } else {
      tooltip.style.display = 'none';
    }
  }

  if (tooltip.style.display === 'block') {
    tooltip.style.left = (e.clientX + 20) + 'px';
    tooltip.style.top = (e.clientY - 60) + 'px';
  }
});

window.addEventListener('mouseup', () => {
  isDragging = false;
  canvas.style.cursor = hoveredParticle ? 'pointer' : 'grab';
});

// ==================== 滚轮缩放 ====================
canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const worldBefore = screenToWorld(e.clientX, e.clientY);
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
  const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoom + delta));
  if (newZoom !== zoom) {
    zoom = newZoom;
    // 以鼠标位置为中心缩放
    cameraX = e.clientX - worldBefore.x * zoom;
    cameraY = e.clientY - worldBefore.y * zoom;
  }
}, { passive: false });

// ==================== 点击事件 ====================
canvas.addEventListener('click', (e) => {
  if (hasMoved) return;  // 拖拽后不触发点击
  if (hoveredParticle) {
    showDetail(hoveredParticle);
  }
});

function showDetail(p) {
  document.getElementById('dp-title').textContent = p.title;
  document.getElementById('dp-author').textContent = '—— ' + p.author;
  document.getElementById('dp-content').innerHTML = p.content.join('<br>');
  document.getElementById('dp-genre').textContent = '【' + p.genre + '】';
  detailPanel.style.display = 'block';
  requestAnimationFrame(() => {
    detailPanel.classList.add('visible');
  });
}

function closeDetail() {
  detailPanel.classList.remove('visible');
  setTimeout(() => { detailPanel.style.display = 'none'; }, 350);
}

canvas.addEventListener('click', (e) => {
  if (hasMoved) return;
  if (!hoveredParticle && detailPanel.style.display === 'block') {
    const rect = detailPanel.getBoundingClientRect();
    const cx = e.clientX, cy = e.clientY;
    if (!(cx >= rect.left && cx <= rect.right && cy >= rect.top && cy <= rect.bottom)) {
      closeDetail();
    }
  }
});

// ==================== 背景星尘（含星云） ====================
const bgStars = [];
const N_BG = 1200;
for (let i = 0; i < N_BG; i++) {
  bgStars.push({
    x: Math.random() * 2500,
    y: Math.random() * 2500,
    r: Math.random() * 1.4 + 0.2,
    twinkle: Math.random() * Math.PI * 2,
    speed: Math.random() * 0.025 + 0.004,
    hue: 200 + Math.random() * 60
  });
}

// 星云斑点
const nebulae = [];
for (let i = 0; i < 6; i++) {
  nebulae.push({
    x: W * (0.1 + Math.random() * 0.8),
    y: H * (0.1 + Math.random() * 0.8),
    r: 80 + Math.random() * 200,
    hue: [260, 320, 200, 30, 340, 180][i],
    alpha: 0.015 + Math.random() * 0.025,
    driftX: (Math.random() - 0.5) * 0.3,
    driftY: (Math.random() - 0.5) * 0.3
  });
}

// 流星
const shootingStars = [];
const MAX_SHOOTERS = 2;

function spawnShootingStar() {
  if (shootingStars.length >= MAX_SHOOTERS) return;
  shootingStars.push({
    x: Math.random() * W * 0.8 + W * 0.1,
    y: Math.random() * H * 0.3,
    vx: -(2 + Math.random() * 4),
    vy: 1.5 + Math.random() * 3,
    life: 1.0,
    decay: 0.008 + Math.random() * 0.015,
    length: 40 + Math.random() * 80
  });
}
setInterval(() => { if (Math.random() < 0.4) spawnShootingStar(); }, 3000);
spawnShootingStar();

function drawBackground() {
  // 深空底
  ctx.fillStyle = '#020010';
  ctx.fillRect(0, 0, W, H);

  // 星云
  for (const n of nebulae) {
    const nx = n.x + Math.sin(time * 0.05 + n.driftX) * 20;
    const ny = n.y + Math.cos(time * 0.04 + n.driftY) * 20;
    const grad = ctx.createRadialGradient(nx, ny, 0, nx, ny, n.r);
    grad.addColorStop(0, `hsla(${n.hue}, 60%, 50%, ${n.alpha * 2})`);
    grad.addColorStop(0.5, `hsla(${n.hue}, 50%, 30%, ${n.alpha})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(nx - n.r, ny - n.r, n.r * 2, n.r * 2);
  }

  // 背景星
  for (const s of bgStars) {
    const alpha = 0.25 + 0.35 * Math.sin(time * s.speed + s.twinkle);
    ctx.fillStyle = `hsla(${s.hue}, 40%, 80%, ${alpha})`;
    ctx.beginPath();
    ctx.arc(s.x % W, s.y % H, s.r, 0, Math.PI * 2);
    ctx.fill();
  }

  // 流星
  for (let i = shootingStars.length - 1; i >= 0; i--) {
    const ss = shootingStars[i];
    ss.x += ss.vx;
    ss.y += ss.vy;
    ss.life -= ss.decay;
    if (ss.life <= 0) { shootingStars.splice(i, 1); continue; }

    const sx = ss.x, sy = ss.y;
    const angle = Math.atan2(ss.vy, ss.vx);
    const ex = sx - Math.cos(angle) * ss.length;
    const ey = sy - Math.sin(angle) * ss.length;

    const grad = ctx.createLinearGradient(sx, sy, ex, ey);
    grad.addColorStop(0, `rgba(255,255,255,${ss.life})`);
    grad.addColorStop(0.15, `rgba(200,220,255,${ss.life * 0.7})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.strokeStyle = grad;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(ex, ey);
    ctx.stroke();
  }
}

// ==================== 绘制粒子 ====================
function drawParticles() {
  for (const p of particles) {
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
    if (p.size > 3.5) {
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
    }

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
    if (isHovered) {
      const ringAlpha = 0.5 + 0.2 * Math.sin(time * 4);
      ctx.strokeStyle = `rgba(255,255,255,${ringAlpha})`;
      ctx.lineWidth = 2 / zoom;
      ctx.beginPath();
      ctx.arc(px, py, drawSize * 1.15, 0, Math.PI * 2);
      ctx.stroke();

      // 外层脉冲
      ctx.strokeStyle = `rgba(255,255,255,${ringAlpha * 0.3})`;
      ctx.lineWidth = 1 / zoom;
      ctx.beginPath();
      ctx.arc(px, py, drawSize * 2.0, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

// ==================== 动画循环 ====================
function animate() {
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
}

animate();
