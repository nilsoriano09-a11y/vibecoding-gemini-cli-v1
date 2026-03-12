from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vini Jr. Jungle Edition 🐍🌴</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Montserrat:wght@900&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #0c1a10;
            color: white;
            font-family: 'Montserrat', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
            background: radial-gradient(circle at center, #1b3022 0%, #050a05 100%);
        }

        .header h1 {
            font-family: 'Bangers', cursive;
            font-size: 50px;
            background: linear-gradient(to bottom, #4CAF50, #2E7D32);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 20px rgba(76, 175, 80, 0.2);
            margin: 0 0 10px 0;
            letter-spacing: 3px;
        }

        #game-container {
            position: relative;
            border: 4px solid rgba(76, 175, 80, 0.4);
            border-radius: 20px;
            box-shadow: 0 0 40px rgba(0,0,0,0.8), 0 0 20px rgba(76, 175, 80, 0.2);
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(5px);
            overflow: hidden;
        }

        canvas {
            display: block;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(255,255,255,0.02) 0%, transparent 20%),
                radial-gradient(circle at 80% 70%, rgba(255,255,255,0.02) 0%, transparent 20%);
        }

        .stats {
            display: flex;
            gap: 40px;
            margin-bottom: 20px;
            font-weight: 900;
            font-size: 24px;
            text-transform: uppercase;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 10px;
            text-shadow: 0 0 10px rgba(0,0,0,0.5);
        }

        #goal-msg {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            font-family: 'Bangers', cursive;
            font-size: 90px;
            color: #4CAF50;
            text-shadow: 0 0 30px rgba(76, 175, 80, 0.6), 4px 4px 0 #000;
            pointer-events: none;
            z-index: 20;
            transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        #game-over {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,10,0,0.9);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 30;
            text-align: center;
        }

        .btn-restart {
            background: linear-gradient(45deg, #4CAF50, #2E7D32);
            color: white;
            border: none;
            padding: 18px 45px;
            font-family: 'Montserrat', sans-serif;
            font-weight: 900;
            cursor: pointer;
            margin-top: 25px;
            border-radius: 15px;
            font-size: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.2s;
        }

        .btn-restart:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(76, 175, 80, 0.4); }
    </style>
</head>
<body>

    <div class="header">
        <h1>VINI JUNGLE</h1>
    </div>

    <div class="stats">
        <div class="stat-item">🍌 <span id="current-score">0</span></div>
        <div class="stat-item" style="color: #4CAF50;">🏆 <span id="high-score">0</span></div>
    </div>

    <div id="game-container">
        <div id="goal-msg">¡REY DE LA SELVA!</div>
        <canvas id="snakeGame" width="400" height="400"></canvas>
        <div id="game-over">
            <h2 style="color: #ff5252; font-size: 45px; font-family: 'Bangers'; margin:0;">GAME OVER</h2>
            <p id="final-stats" style="font-size: 22px; margin-top:10px; color: white;"></p>
            <button class="btn-restart" onclick="resetGame()">REINTENTAR</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("snakeGame");
        const ctx = canvas.getContext("2d");
        const scoreElement = document.getElementById("current-score");
        const highScoreElement = document.getElementById("high-score");
        const gameOverScreen = document.getElementById("game-over");
        const goalMsg = document.getElementById("goal-msg");

        // CARGA DE IMAGEN DE VINI
        const viniImg = new Image();
        viniImg.src = "https://www.fifarosters.com/assets/players/fifa24/faces/238794.png";

        const gridSize = 20;
        const tileCount = canvas.width / gridSize;

        let score = 0;
        let highScore = localStorage.getItem("viniSnakeScoreJungle") || 0;
        highScoreElement.innerText = highScore;

        let snake = [{x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12}];
        let food = {x: 5, y: 5};
        let dx = 0;
        let dy = -1;
        let nextDx = 0;
        let nextDy = -1;
        let gameRunning = true;

        function main() {
            if (!gameRunning) return;
            if (didGameEnd()) { endGame(); return; }

            setTimeout(function onTick() {
                clearCanvas();
                drawFood();
                advanceSnake();
                drawSnake();
                main();
            }, 90);
        }

        function clearCanvas() {
            // Fondo de selva oscura
            ctx.fillStyle = "#0b1a0e";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Grid sutil verde
            ctx.strokeStyle = "rgba(76, 175, 80, 0.08)";
            ctx.lineWidth = 1;
            for(let i=0; i<=canvas.width; i+=gridSize) {
                ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke();
            }

            // Decoración aleatoria (hojas sutiles)
            ctx.font = "10px Arial";
            ctx.fillStyle = "rgba(76, 175, 80, 0.1)";
            ctx.fillText("🌿", 40, 40);
            ctx.fillText("🍃", 350, 350);
            ctx.fillText("🌿", 300, 60);
            ctx.fillText("🍃", 50, 320);
        }

        function drawSnake() {
            snake.forEach((part, index) => {
                if (index === 0) {
                    if (viniImg.complete) {
                        ctx.save();
                        // Cara MUCHO más grande (radio 25, diámetro 50 sobre grid de 20)
                        const faceSize = 52;
                        const offset = (faceSize - gridSize) / 2;
                        
                        ctx.beginPath();
                        ctx.arc(part.x * gridSize + gridSize/2, part.y * gridSize + gridSize/2, faceSize/2, 0, Math.PI * 2);
                        ctx.clip();
                        
                        // Centrar la imagen más grande
                        ctx.drawImage(viniImg, part.x * gridSize - offset, part.y * gridSize - offset, faceSize, faceSize);
                        ctx.restore();
                        
                        // Efecto de brillo verde selva
                        ctx.shadowBlur = 15;
                        ctx.shadowColor = "#4CAF50";
                        ctx.strokeStyle = "#4CAF50";
                        ctx.lineWidth = 2;
                        ctx.strokeRect(part.x * gridSize - offset, part.y * gridSize - offset, faceSize, faceSize);
                    }
                } else {
                    ctx.shadowBlur = 0;
                    const gradient = ctx.createLinearGradient(
                        part.x * gridSize, part.y * gridSize, 
                        (part.x + 1) * gridSize, (part.y + 1) * gridSize
                    );
                    if (index % 2 === 0) {
                        gradient.addColorStop(0, "#2E7D32");
                        gradient.addColorStop(1, "#1B5E20");
                    } else {
                        gradient.addColorStop(0, "#4CAF50");
                        gradient.addColorStop(1, "#388E3C");
                    }
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.roundRect(part.x * gridSize + 2, part.y * gridSize + 2, gridSize - 4, gridSize - 4, 6);
                    ctx.fill();
                }
            });
        }

        function advanceSnake() {
            dx = nextDx; dy = nextDy;
            const head = {x: snake[0].x + dx, y: snake[0].y + dy};
            snake.unshift(head);
            if (head.x === food.x && head.y === food.y) {
                score += 1;
                scoreElement.innerText = score;
                triggerGoal();
                createFood();
            } else {
                if (dx !== 0 || dy !== 0) snake.pop();
            }
        }

        function triggerGoal() {
            goalMsg.style.transform = "translate(-50%, -50%) scale(1.1)";
            setTimeout(() => { goalMsg.style.transform = "translate(-50%, -50%) scale(0)"; }, 500);
        }

        function didGameEnd() {
            const head = snake[0];
            if (dx === 0 && dy === 0) return false;
            const hitWall = head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount;
            let hitSelf = false;
            for (let i = 4; i < snake.length; i++) {
                if (snake[i].x === head.x && snake[i].y === head.y) hitSelf = true;
            }
            return hitWall || hitSelf;
        }

        function endGame() {
            gameRunning = false;
            gameOverScreen.style.display = "flex";
            document.getElementById("final-stats").innerText = `TOTAL: ${score} PLÁTANOS 🍌`;
            if (score > highScore) {
                highScore = score;
                localStorage.setItem("viniSnakeScoreGold_v2", highScore);
                highScoreElement.innerText = highScore;
            }
        }

        function createFood() {
            food.x = Math.floor(Math.random() * tileCount);
            food.y = Math.floor(Math.random() * tileCount);
            snake.forEach(part => { if (part.x === food.x && part.y === food.y) createFood(); });
        }

        function drawFood() {
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#fdd835";
            ctx.font = "26px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("🍌", food.x * gridSize + 10, food.y * gridSize + 10);
            ctx.shadowBlur = 0;
        }

        function changeDirection(event) {
            const keyPressed = event.keyCode;
            const LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;
            const W = 87, A = 65, S = 83, D = 68;
            if ((keyPressed === LEFT || keyPressed === A) && dx !== 1) { nextDx = -1; nextDy = 0; }
            if ((keyPressed === UP || keyPressed === W) && dy !== 1) { nextDx = 0; nextDy = -1; }
            if ((keyPressed === RIGHT || keyPressed === D) && dx !== -1) { nextDx = 1; nextDy = 0; }
            if ((keyPressed === DOWN || keyPressed === S) && dy !== -1) { nextDx = 0; nextDy = 1; }
        }

        function resetGame() {
            snake = [{x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12}];
            score = 0; scoreElement.innerText = score;
            nextDx = 0; nextDy = -1; dx = 0; dy = -1;
            gameRunning = true; gameOverScreen.style.display = "none";
            createFood(); main();
        }

        document.addEventListener("keydown", changeDirection);
        viniImg.onload = () => { createFood(); main(); };
        setTimeout(() => { if(gameRunning && score === 0) { createFood(); main(); } }, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
