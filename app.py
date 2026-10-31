import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Flappy Bird",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird")
st.markdown("Nhấn **Space** hoặc **Click chuột** vào màn hình game để bắt đầu")

# Mã HTML/JS/CSS hoàn chỉnh của game
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
let gameState = "START"; // START, PLAYING, GAMEOVER

// --- HỆ THỐNG ÂM THANH & NHẠC NỀN EDM SIÊU SÔI ĐỘNG ---
let audioCtx = null;
let bgmTimer = null;
let bgmNoteIndex = 0;

// Chuỗi nốt nhạc EDM tốc độ cao, dồn dập và bốc lửa nhất
const ultraEdmNotes = [
    523.25, 1046.50, 659.25, 1318.51, 783.99, 1567.98, 880.00, 1760.00,
    1174.66, 587.33, 1318.51, 659.25, 1567.98, 783.99, 1760.00, 880.00,
    1046.50, 523.25, 1174.66, 587.33, 1318.51, 659.25, 1567.98, 783.99,
    2093.00, 1760.00, 1567.98, 1318.51, 1174.66, 1046.50, 880.00, 783.99
];

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function startBGM() {
    if (bgmTimer) return;
    bgmTimer = setInterval(() => {
        if (gameState === "PLAYING" && audioCtx) {
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = "sawtooth"; // Sóng răng cưa tạo âm thanh điện tử cực sắc và mạnh
            osc.frequency.setValueAtTime(ultraEdmNotes[bgmNoteIndex], audioCtx.currentTime);
            
            gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);
            
            bgmNoteIndex = (bgmNoteIndex + 1) % ultraEdmNotes.length;
        }
    }, 100); // Tốc độ cực nhanh (100 mili-giây mỗi nốt) tạo cảm giác bốc lửa
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

// --- CON CHIM (Lông chim đổi màu khi qua ống cống) ---
const bird = {
    x: 50,
    y: 150,
    radius: 12,
    gravity: 0.25,
    jump: 4.6,
    velocity: 0,
    color: "#FFD700",
    birdColors: ["#FFD700", "#FF1493", "#00BFFF", "#32CD32", "#FF4500", "#9370DB", "#00FFFF", "#FF8C00", "#E67E22", "#E74C3C"],

    changeColor: function() {
        let available = this.birdColors.filter(c => c !== this.color);
        this.color = available[Math.floor(Math.random() * available.length)];
    },
    
    draw: function() {
        ctx.fillStyle = this.color;
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
        this.color = "#FFD700";
    }
};

// --- QUẢN LÝ ỐNG CỐNG (Mỗi ống cống một màu riêng) ---
const pipes = {
    position: [],
    topGap: 120,
    dx: 2,
    width: 52,
    pipePalette: [
        { main: "#73BF2E", border: "#558022" },
        { main: "#E74C3C", border: "#C0392B" },
        { main: "#3498DB", border: "#2980B9" },
        { main: "#9B59B6", border: "#8E44AD" },
        { main: "#F1C40F", border: "#D4AC0D" },
        { main: "#E67E22", border: "#D35400" },
        { main: "#1ABC9C", border: "#16A085" },
        { main: "#E84393", border: "#B22E6F" }
    ],

    getRandomColor: function(lastColor) {
        let available = this.pipePalette.filter(p => !lastColor || p.main !== lastColor.main);
        return available[Math.floor(Math.random() * available.length)];
    },

    draw: function() {
        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            let topY = p.y;
            let bottomY = p.y + this.topGap;
            let totalHeight = canvas.height - 50;

            let pipeColor = p.color.main;
            let pipeBorder = p.color.border;
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
            let lastPipeColor = this.position.length > 0 ? this.position[this.position.length - 1].color : null;
            this.position.push({
                x: canvas.width,
                y: Math.floor(Math.random() * (200 - 50 + 1)) + 50,
                color: this.getRandomColor(lastPipeColor)
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
                bird.changeColor();
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
        ctx.font = "bold 15px Arial";
        ctx.textAlign = "center";
        ctx.fillText("Nhấn Space hoặc Click chuột", canvas.width / 2, canvas.height / 2 - 10);
        ctx.fillText("vào màn hình game để bắt đầu", canvas.width / 2, canvas.height / 2 + 15);
    } else if (gameState === "GAMEOVER") {
        ctx.font = "bold 30px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", canvas.width / 2, 180);
        ctx.strokeText("GAME OVER", canvas.width / 2, 180);

        ctx.font = "20px Arial";
        ctx.fillText("Điểm: " + score, canvas.width / 2, 230);
        ctx.fillText("Kỷ lục: " + highScore, canvas.width / 2, 260);
        
        ctx.font = "bold 15px Arial";
        ctx.fillText("Nhấn Space hoặc Click chuột", canvas.width / 2, 310);
        ctx.fillText("vào màn hình game để bắt đầu", canvas.width / 2, 330);
    }
}

function action() {
    initAudio();
    startBGM();
    
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
