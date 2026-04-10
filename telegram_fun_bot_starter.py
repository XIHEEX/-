import os
import threading
from flask import Flask, Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN', 'PUT_YOUR_BOT_TOKEN_HERE')
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', 'https://YOUR-DOMAIN.com')
PORT = int(os.getenv('PORT', '8080'))

app = Flask(__name__)

HOME_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <title>世界杯小游戏中心</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card: rgba(255,255,255,.08);
      --text: #f8fafc;
      --muted: #cbd5e1;
      --accent: #22c55e;
      --accent2: #f59e0b;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: radial-gradient(circle at top, #1e293b, #0f172a 55%);
      color: var(--text);
      min-height: 100vh;
      padding: 20px;
    }
    .wrap { max-width: 760px; margin: 0 auto; }
    .hero {
      background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(245,158,11,.16));
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 24px;
      padding: 20px;
      box-shadow: 0 16px 40px rgba(0,0,0,.22);
    }
    h1 { margin: 0 0 8px; font-size: 28px; }
    p { margin: 0; color: var(--muted); line-height: 1.6; }
    .grid {
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
    }
    .card {
      background: var(--card);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 22px;
      padding: 18px;
    }
    .card h2 { margin: 0 0 8px; font-size: 22px; }
    .meta { font-size: 14px; color: var(--muted); min-height: 46px; }
    .btns { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 14px; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 120px;
      padding: 12px 16px;
      border-radius: 14px;
      text-decoration: none;
      color: #fff;
      font-weight: 700;
      box-shadow: 0 10px 22px rgba(0,0,0,.18);
    }
    .green { background: linear-gradient(135deg, #16a34a, #22c55e); }
    .gold { background: linear-gradient(135deg, #d97706, #f59e0b); }
    .tips {
      margin-top: 18px;
      font-size: 14px;
      color: var(--muted);
      background: rgba(255,255,255,.05);
      border: 1px dashed rgba(255,255,255,.12);
      border-radius: 16px;
      padding: 14px;
      line-height: 1.7;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>⚽ 世界杯小游戏中心</h1>
      <p>给群机器人挂一个轻量版小游戏入口：一个是贪吃蛇吃球，一个是转盘小惊喜。这个版本适合先跑起来，再慢慢升级。</p>
    </div>

    <div class="grid">
      <div class="card">
        <h2>🐍 贪吃蛇吃球</h2>
        <div class="meta">方向键控制，手机端支持屏幕按钮。每吃到一个球，加 1 分，撞墙或撞到自己结束。</div>
        <div class="btns">
          <a class="btn green" href="/snake">进入游戏</a>
        </div>
      </div>

      <div class="card">
        <h2>🎡 转盘小惊喜</h2>
        <div class="meta">点击开始转盘，抽一个轻量彩蛋结果。可以改成你自己的文案和奖励。</div>
        <div class="btns">
          <a class="btn gold" href="/wheel">开始抽奖</a>
        </div>
      </div>
    </div>

    <div class="tips">
      小提示：这个首页很适合设置成 Telegram 机器人的 Menu Button 入口。<br>
      你后续只要把文案、颜色、奖励项、背景图，按你自己的世界杯风格换掉就行。
    </div>
  </div>
  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }
  </script>
</body>
</html>
"""

SNAKE_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <title>贪吃蛇吃球</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #0b1220;
      --panel: rgba(255,255,255,.08);
      --text: #f8fafc;
      --muted: #cbd5e1;
      --accent: #22c55e;
      --danger: #ef4444;
      --gold: #f59e0b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at top, #15304b, #0b1220 60%);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      min-height: 100vh;
      padding: 18px;
    }
    .wrap { max-width: 760px; margin: 0 auto; }
    .top {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 14px;
    }
    .title { font-size: 26px; font-weight: 800; }
    .panel {
      background: var(--panel);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 20px;
      padding: 14px;
      backdrop-filter: blur(8px);
      box-shadow: 0 14px 32px rgba(0,0,0,.2);
    }
    .stats {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }
    .chip {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 14px;
      padding: 10px 14px;
      font-weight: 700;
    }
    canvas {
      width: 100%;
      max-width: 420px;
      aspect-ratio: 1 / 1;
      display: block;
      margin: 0 auto;
      border-radius: 18px;
      background: linear-gradient(180deg, #0a5a2d, #064e3b);
      border: 2px solid rgba(255,255,255,.15);
    }
    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 14px;
    }
    button {
      border: 0;
      border-radius: 14px;
      padding: 12px 16px;
      color: #fff;
      font-weight: 800;
      cursor: pointer;
      min-width: 110px;
    }
    .start { background: linear-gradient(135deg, #16a34a, #22c55e); }
    .back { background: linear-gradient(135deg, #334155, #475569); }
    .mobile-pad {
      margin-top: 16px;
      display: grid;
      gap: 10px;
      justify-content: center;
    }
    .row { display: flex; justify-content: center; gap: 10px; }
    .dir { width: 74px; height: 56px; background: linear-gradient(135deg, #1e293b, #334155); }
    .tips { color: var(--muted); text-align: center; margin-top: 12px; line-height: 1.6; }
    .result {
      margin-top: 12px;
      text-align: center;
      font-weight: 800;
      color: #fde68a;
      min-height: 24px;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="title">🐍 贪吃蛇吃球</div>
      <div style="color:#cbd5e1;">世界杯轻量彩蛋版</div>
    </div>

    <div class="panel">
      <div class="stats">
        <div class="chip">当前分数：<span id="score">0</span></div>
        <div class="chip">最高分：<span id="best">0</span></div>
      </div>

      <canvas id="board" width="420" height="420"></canvas>

      <div class="actions">
        <button class="start" id="restartBtn">开始 / 重开</button>
        <button class="back" onclick="location.href='/'">返回首页</button>
      </div>

      <div class="mobile-pad">
        <div class="row"><button class="dir" data-dir="up">⬆️</button></div>
        <div class="row">
          <button class="dir" data-dir="left">⬅️</button>
          <button class="dir" data-dir="down">⬇️</button>
          <button class="dir" data-dir="right">➡️</button>
        </div>
      </div>

      <div class="tips">电脑端用键盘方向键；手机端点下面方向按钮。<br>每吃到一个球加 1 分，撞墙或撞到自己就结束。</div>
      <div class="result" id="result"></div>
    </div>
  </div>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) { tg.ready(); tg.expand(); }

    const canvas = document.getElementById('board');
    const ctx = canvas.getContext('2d');
    const gridCount = 21;
    const size = canvas.width / gridCount;

    let snake = [];
    let food = {x: 10, y: 10};
    let dir = {x: 1, y: 0};
    let nextDir = {x: 1, y: 0};
    let score = 0;
    let best = Number(localStorage.getItem('snake_best') || 0);
    let timer = null;
    let running = false;

    document.getElementById('best').textContent = best;

    function randomCell() {
      let x, y;
      do {
        x = Math.floor(Math.random() * gridCount);
        y = Math.floor(Math.random() * gridCount);
      } while (snake.some(p => p.x === x && p.y === y));
      return {x, y};
    }

    function resetGame() {
      snake = [
        {x: 7, y: 10},
        {x: 6, y: 10},
        {x: 5, y: 10}
      ];
      dir = {x: 1, y: 0};
      nextDir = {x: 1, y: 0};
      score = 0;
      running = true;
      food = randomCell();
      document.getElementById('score').textContent = score;
      document.getElementById('result').textContent = '';
      if (timer) clearInterval(timer);
      timer = setInterval(loop, 120);
      draw();
    }

    function loop() {
      if (!running) return;
      dir = nextDir;
      const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};

      if (
        head.x < 0 || head.x >= gridCount ||
        head.y < 0 || head.y >= gridCount ||
        snake.some(p => p.x === head.x && p.y === head.y)
      ) {
        running = false;
        clearInterval(timer);
        if (score > best) {
          best = score;
          localStorage.setItem('snake_best', String(best));
          document.getElementById('best').textContent = best;
        }
        document.getElementById('result').textContent = `比赛结束，本场拿到 ${score} 分。`;
        return;
      }

      snake.unshift(head);

      if (head.x === food.x && head.y === food.y) {
        score += 1;
        document.getElementById('score').textContent = score;
        food = randomCell();
      } else {
        snake.pop();
      }
      draw();
    }

    function drawField() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let x = 0; x < gridCount; x++) {
        for (let y = 0; y < gridCount; y++) {
          ctx.fillStyle = (x + y) % 2 === 0 ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.03)';
          ctx.fillRect(x * size, y * size, size, size);
        }
      }
    }

    function drawBall() {
      const cx = food.x * size + size / 2;
      const cy = food.y * size + size / 2;
      ctx.beginPath();
      ctx.arc(cx, cy, size * 0.36, 0, Math.PI * 2);
      ctx.fillStyle = '#f8fafc';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(cx, cy, size * 0.18, 0, Math.PI * 2);
      ctx.fillStyle = '#111827';
      ctx.fill();
    }

    function drawSnake() {
      snake.forEach((p, i) => {
        const radius = i === 0 ? 8 : 6;
        ctx.fillStyle = i === 0 ? '#fde68a' : '#22c55e';
        roundRect(ctx, p.x * size + 2, p.y * size + 2, size - 4, size - 4, radius);
        ctx.fill();
      });
    }

    function roundRect(ctx, x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
    }

    function draw() {
      drawField();
      drawBall();
      drawSnake();
    }

    function setDirection(name) {
      if (name === 'up' && dir.y !== 1) nextDir = {x: 0, y: -1};
      if (name === 'down' && dir.y !== -1) nextDir = {x: 0, y: 1};
      if (name === 'left' && dir.x !== 1) nextDir = {x: -1, y: 0};
      if (name === 'right' && dir.x !== -1) nextDir = {x: 1, y: 0};
    }

    window.addEventListener('keydown', e => {
      if (e.key === 'ArrowUp') setDirection('up');
      if (e.key === 'ArrowDown') setDirection('down');
      if (e.key === 'ArrowLeft') setDirection('left');
      if (e.key === 'ArrowRight') setDirection('right');
    });

    document.querySelectorAll('.dir').forEach(btn => {
      btn.addEventListener('click', () => setDirection(btn.dataset.dir));
    });

    document.getElementById('restartBtn').addEventListener('click', resetGame);
    draw();
  </script>
</body>
</html>
"""

WHEEL_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <title>转盘小惊喜</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #111827;
      --panel: rgba(255,255,255,.08);
      --text: #f9fafb;
      --muted: #cbd5e1;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top, #3b0764, #111827 60%);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      padding: 18px;
    }
    .wrap { max-width: 760px; margin: 0 auto; }
    .panel {
      background: var(--panel);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 24px;
      padding: 18px;
      backdrop-filter: blur(8px);
      box-shadow: 0 14px 32px rgba(0,0,0,.22);
    }
    .title { font-size: 28px; font-weight: 800; margin-bottom: 8px; }
    .desc { color: var(--muted); line-height: 1.6; }
    .wheel-wrap {
      position: relative;
      width: min(86vw, 360px);
      height: min(86vw, 360px);
      margin: 24px auto 10px;
    }
    .pointer {
      position: absolute;
      left: 50%;
      top: -6px;
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: 16px solid transparent;
      border-right: 16px solid transparent;
      border-top: 0;
      border-bottom: 28px solid #f8fafc;
      z-index: 3;
      filter: drop-shadow(0 6px 10px rgba(0,0,0,.25));
    }
    .wheel {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 10px solid rgba(255,255,255,.18);
      box-shadow: 0 18px 38px rgba(0,0,0,.24);
      transition: transform 4.6s cubic-bezier(.12,.95,.12,1);
      background: conic-gradient(
        #ef4444 0deg 45deg,
        #f59e0b 45deg 90deg,
        #22c55e 90deg 135deg,
        #06b6d4 135deg 180deg,
        #3b82f6 180deg 225deg,
        #8b5cf6 225deg 270deg,
        #ec4899 270deg 315deg,
        #14b8a6 315deg 360deg
      );
      position: relative;
      overflow: hidden;
    }
    .wheel::after {
      content: "抽";
      position: absolute;
      inset: 50%;
      transform: translate(-50%, -50%);
      width: 84px;
      height: 84px;
      border-radius: 999px;
      background: rgba(17,24,39,.92);
      border: 5px solid rgba(255,255,255,.16);
      display: grid;
      place-items: center;
      font-weight: 900;
      font-size: 26px;
    }
    .labels span {
      position: absolute;
      left: 50%;
      top: 50%;
      transform-origin: 0 0;
      font-size: 13px;
      font-weight: 800;
      color: white;
      text-shadow: 0 2px 6px rgba(0,0,0,.28);
      white-space: nowrap;
    }
    .actions {
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
      margin-top: 18px;
    }
    button {
      border: 0;
      border-radius: 14px;
      padding: 12px 18px;
      color: #fff;
      font-weight: 800;
      cursor: pointer;
      min-width: 120px;
    }
    .spin { background: linear-gradient(135deg, #d946ef, #8b5cf6); }
    .back { background: linear-gradient(135deg, #334155, #475569); }
    .result {
      margin-top: 16px;
      text-align: center;
      font-size: 18px;
      font-weight: 900;
      min-height: 28px;
      color: #fde68a;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <div class="title">🎡 转盘小惊喜</div>
      <div class="desc">这是一个轻量版彩蛋转盘。你后续可以把每一项文案，换成你自己的欢迎彩蛋、世界杯冷知识、任务奖励、趣味惩罚。</div>

      <div class="wheel-wrap">
        <div class="pointer"></div>
        <div class="wheel" id="wheel"></div>
        <div class="labels" id="labels"></div>
      </div>

      <div class="actions">
        <button class="spin" id="spinBtn">开始转盘</button>
        <button class="back" onclick="location.href='/'">返回首页</button>
      </div>
      <div class="result" id="result"></div>
    </div>
  </div>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) { tg.ready(); tg.expand(); }

    const rewards = [
      '🍀 今日好运签',
      '⚽ 世界杯冷知识',
      '☕ 奶茶好运卡',
      '🎉 任务加鸡腿',
      '📣 发一条欢迎词',
      '😄 今日免催一次',
      '🎁 隐藏彩蛋',
      '💪 幸运值 +1'
    ];

    const wheel = document.getElementById('wheel');
    const labels = document.getElementById('labels');
    const result = document.getElementById('result');
    const spinBtn = document.getElementById('spinBtn');
    const sector = 360 / rewards.length;
    let currentDeg = 0;
    let spinning = false;

    rewards.forEach((text, i) => {
      const span = document.createElement('span');
      const angle = i * sector + sector / 2 - 90;
      span.textContent = text;
      span.style.transform = `rotate(${angle}deg) translate(94px, -4px) rotate(90deg)`;
      labels.appendChild(span);
    });

    spinBtn.addEventListener('click', () => {
      if (spinning) return;
      spinning = true;
      result.textContent = '转盘启动中...';
      const winnerIndex = Math.floor(Math.random() * rewards.length);
      const offsetToPointer = 360 - (winnerIndex * sector + sector / 2);
      const extra = 360 * (5 + Math.floor(Math.random() * 2));
      currentDeg += extra + offsetToPointer + (Math.random() * (sector * 0.7) - sector * 0.35);
      wheel.style.transform = `rotate(${currentDeg}deg)`;

      setTimeout(() => {
        const prize = rewards[winnerIndex];
        result.textContent = `你抽中了：${prize}`;
        spinning = false;
      }, 4700);
    });
  </script>
</body>
</html>
"""


def page_response(html: str) -> Response:
    return Response(html, mimetype='text/html; charset=utf-8')


@app.route('/')
def home_page():
    return page_response(HOME_HTML)


@app.route('/snake')
def snake_page():
    return page_response(SNAKE_HTML)


@app.route('/wheel')
def wheel_page():
    return page_response(WHEEL_HTML)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    base = PUBLIC_BASE_URL.rstrip('/')
    keyboard = [
        [InlineKeyboardButton('🐍 贪吃蛇·吃球', web_app=WebAppInfo(url=f'{base}/snake'))],
        [InlineKeyboardButton('🎡 转盘小惊喜', web_app=WebAppInfo(url=f'{base}/wheel'))],
        [InlineKeyboardButton('🏠 小游戏首页', web_app=WebAppInfo(url=f'{base}/'))],
    ]
    text = (
        '世界杯小游戏入口已经准备好了。\n\n'
        '1. 点“贪吃蛇·吃球”进入蛇蛇小游戏\n'
        '2. 点“转盘小惊喜”进入彩蛋转盘\n'
        '3. 你也可以把首页挂到 Telegram 的菜单按钮里，用户随时都能点开\n\n'
        '这个 starter 版本适合先上线测试，再慢慢美化。'
    )
    await update.effective_chat.send_message(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


async def games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        '可用命令：\n'
        '/start - 打开小游戏入口\n'
        '/games - 再次显示小游戏按钮\n'
        '/help - 查看帮助\n\n'
        '部署前请先改好：\n'
        'BOT_TOKEN\n'
        'PUBLIC_BASE_URL\n'
        '并确保你的域名是公网可访问的 HTTPS 地址。'
    )
    await update.effective_chat.send_message(help_text)


def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False)


def main():
    if BOT_TOKEN == 'PUT_YOUR_BOT_TOKEN_HERE':
        raise RuntimeError('请先设置环境变量 BOT_TOKEN。')
    if PUBLIC_BASE_URL == 'https://YOUR-DOMAIN.com':
        raise RuntimeError('请先设置环境变量 PUBLIC_BASE_URL。')

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('games', games))
    application.add_handler(CommandHandler('help', help_command))
    application.run_polling(close_loop=False)


if __name__ == '__main__':
    main()
