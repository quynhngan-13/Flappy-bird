import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Flappy Bird - Streamlit",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Game Flappy Bird")
st.markdown("Nhấn **Space** hoặc **Click chuột** vào màn hình game để điều khiển chú chim bay qua ống cống!")

# Mã HTML/JS/CSS game Flappy Bird chuẩn ống cống & có âm thanh
flappy_bird_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #70c5ce;
            font-family: Arial, sans-serif;
        }
        canvas {
            border: 3px solid #333;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            background-color: #70c5ce;
        }
    </style>
</head>
<body>

<canvas id="birdCanvas" width="360" height="500"></canvas>

<script>
const canvas = document.getElementById("birdCanvas");
const ctx = canvas.getContext("2d");

let frames = 0;
let score = 0;
let highScore = 0;
let gameState = "START";

// --- HỆ THỐNG ÂM THANH (Web Audio API) ---
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playJumpSound() {
    initAudio();
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(400, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

function playScoreSound() {
    initAudio();
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(600, audioCtx.currentTime);
    osc.frequency.setValueAtTime(900, audioCtx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
}

function playDieSound() {
    initAudio();
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(200, audioCtx.currentTime);
    osc.frequency.linearRampToValueAtTime(50, audioCtx.currentTime + 0.3);
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
}

// --- CON CHIM ---
const bird = {
    x: 50,
    y: 150,
    radius: 12,
    gravity: 0.25,
    jump: 4.6,
    velocity: 0,
    
    draw: function() {
        ctx.fillStyle = "#FFD700";
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = "#FFF";
        ctx.beginPath();
        ctx.arc(this.x + 4, this.y - 3, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#000";
        ctx.beginPath();
        ctx.arc(this.x + 6, this.y - 3, 1.5, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#FF4500";
        ctx.beginPath();
        ctx.moveTo(this.x + 8, this.y);
        ctx.lineTo(this.x + 16, this.y + 3);
        ctx.lineTo(this.x + 8, this.y + 6);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    },
    
    flap: function() {
        this.velocity = -this.jump;
        playJumpSound();
    },
    
    update: function() {
        if (gameState === "PLAYING") {
            this.velocity += this.gravity;
            this.y += this.velocity;

            if (this.y + this.radius >= canvas.height - 50) {
                this.y = canvas.height - 50 - this.radius;
                gameOver();
            }

            if (this.y - this.radius <= 0) {
                this.y = this.radius;
                this.velocity = 0;
            }
        }
    },
    
    reset: function() {
        this.y = 150;
        this.velocity = 0;
    }
};

// --- QUẢN LÝ ỐNG CỐNG ---
const pipes = {
    position: [],
    topGap: 120,
    dx: 2,
    width: 52,

    draw: function() {
        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            let topY = p.y;
            let bottomY = p.y + this.topGap;
            let totalHeight = canvas.height - 50;

            let pipeColor = "#73BF2E";
            let pipeBorder = "#558022";
            let capHeight = 24;
            let capOverhang = 4;

            // Ống trên
            ctx.fillStyle = pipeColor;
            ctx.fillRect(p.x, 0, this.width, topY - capHeight);
            ctx.strokeStyle = pipeBorder;
            ctx.lineWidth = 2;
            ctx.strokeRect(p.x, 0, this.width, topY - capHeight);

            ctx.fillRect(p.x - capOverhang, topY - capHeight, this.width + (capOverhang * 2), capHeight);
            ctx.strokeRect(p.x - capOverhang, topY - capHeight, this.width + (capOverhang * 2), capHeight);

            // Ống dưới
            let bottomPipeY = bottomY + capHeight;
            let bottomPipeHeight = totalHeight - bottomPipeY;

            ctx.fillStyle = pipeColor;
            ctx.fillRect(p.x - capOverhang, bottomY, this.width + (capOverhang * 2), capHeight);
            ctx.strokeStyle = pipeBorder;
            ctx.strokeRect(p.x - capOverhang, bottomY, this.width + (capOverhang * 2), capHeight);

            ctx.fillRect(p.x, bottomPipeY, this.width, bottomPipeHeight);
            ctx.strokeRect(p.x, bottomPipeY, this.width, bottomPipeHeight);
        }
    },

    update: function() {
        if (gameState !== "PLAYING") return;

        if (frames % 100 === 0) {
            this.position.push({
                x: canvas.width,
                y: Math.floor(Math.random() * (200 - 50 + 1)) + 50
            });
        }

        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            p.x -= this.dx;

            let capOverhang = 4;
            let hitBoxX = p.x - capOverhang;
            let hitBoxWidth = this.width + (capOverhang * 2);

            if (
                bird.x + bird.radius > hitBoxX &&
                bird.x - bird.radius < hitBoxX + hitBoxWidth &&
                (bird.y - bird.radius < p.y || bird.y + bird.radius > p.y + this.topGap)
            ) {
                gameOver();
            }

            if (p.x + this.width < bird.x && !p.passed) {
                score++;
                p.passed = true;
                if (score > highScore) highScore = score;
                playScoreSound();
            }

            if (p.x + this.width <= 0) {
                this.position.shift();
                i--;
            }
        }
    },

    reset: function() {
        this.position = [];
    }
};

function drawGround() {
    ctx.fillStyle = "#D2B48C";
    ctx.fillRect(0, canvas.height - 50, canvas.width, 50);
    ctx.fillStyle = "#558022";
    ctx.fillRect(0, canvas.height - 50, canvas.width, 10);
}

function gameOver() {
    if (gameState !== "GAMEOVER") {
        gameState = "GAMEOVER";
        playDieSound();
    }
}

function drawUI() {
    ctx.fillStyle = "#FFF";
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 3;

    if (gameState === "PLAYING") {
        ctx.font = "bold 35px Arial";
        ctx.textAlign = "center";
        ctx.fillText(score, canvas.width / 2, 60);
        ctx.strokeText(score, canvas.width / 2, 60);
    } else if (gameState === "START") {
        ctx.font = "bold 20px Arial";
        ctx.textAlign = "center";
        ctx.fillText("Nhấn SPACE hoặc CLICK để chơi", canvas.width / 2, canvas.height / 2);
    } else if (gameState === "GAMEOVER") {
        ctx.font = "bold 30px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", canvas.width / 2, 180);
        ctx.strokeText("GAME OVER", canvas.width / 2, 180);

        ctx.font = "20px Arial";
        ctx.fillText("Điểm: " + score, canvas.width / 2, 230);
        ctx.fillText("Kỷ lục: " + highScore, canvas.width / 2, 260);
        
        ctx.font = "bold 16px Arial";
        ctx.fillText("Nhấn SPACE để chơi lại", canvas.width / 2, 310);
    }
}

function action() {
    initAudio();
    if (gameState === "START") {
        gameState = "PLAYING";
        bird.flap();
    } else if (gameState === "PLAYING") {
        bird.flap();
    } else if (gameState === "GAMEOVER") {
        bird.reset();
        pipes.reset();
        score = 0;
        gameState = "PLAYING";
        bird.flap();
    }
}

document.addEventListener("keydown", function(e) {
    if (e.code === "Space") {
        e.preventDefault();
        action();
    }
});

canvas.addEventListener("click", function() {
    action();
});

function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    bird.update();
    pipes.update();

    pipes.draw();
    bird.draw();
    drawGround();
    drawUI();

    frames++;
    requestAnimationFrame(loop);
}

loop();
</script>
</body>
</html>
"""

# Hiển thị game trong ứng dụng Streamlit
components.html(flappy_bird_html, height=520)
