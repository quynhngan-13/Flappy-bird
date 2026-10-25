import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web Streamlit
st.set_page_config(
    page_title="Flappy Bird - Streamlit Edition",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird - Đầy đủ Ống Cống, Âm thanh & Nhạc nền")
st.markdown("Nhấn phím **Space** hoặc **Click chuột** vào màn hình để bắt đầu bay và thưởng thức âm nhạc!")

# Mã HTML/JS/CSS hoàn chỉnh của game kèm Nhạc nền
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
            border: 2px solid #333;
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

// --- HỆ THỐNG ÂM THANH & NHẠC NỀN (Web Audio API) ---
let audioCtx = null;
let bgmTimer = null;
let bgmNoteIndex = 0;
// Giai điệu nhạc nền vui tươi (Nốt nhạc tần sốHz)
const bgmNotes = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 440.00, 392.00]; 

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

// Khởi động nhạc nền khi vào game
function startBGM() {
    if (bgmTimer) return;
    bgmTimer = setInterval(() => {
        if (gameState === "PLAYING" && audioCtx) {
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(bgmNotes[bgmNoteIndex], audioCtx.currentTime);
            
            // Âm lượng nhạc nền nhỏ dịu để không lấn át tiếng hiệu ứng
            gain.gain.setValueAtTime(0.015, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.2);
            
            bgmNoteIndex = (bgmNoteIndex + 1) % bgmNotes.length;
        }
    }, 220); // Tốc độ nhịp điệu nhạc nền
}

// Âm thanh khi chú chim nhảy (Flap)
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

// Âm thanh khi ghi điểm
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

// Âm thanh khi thua cuộc (Game Over)
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

// --- ĐỐI TƯỢNG CHIM (BIRD) ---
const bird = {
    x: 50,
    y: 150,
    radius: 12,
    gravity: 0.25,
    jump: 4.6,
    velocity: 0,
    
    draw: function() {
        // Thân chim
        ctx.fillStyle = "#FFD700";
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Mắt chim
        ctx.fillStyle = "#FFF";
        ctx.beginPath();
        ctx.arc(this.x + 4, this.y - 3, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#000";
        ctx.beginPath();
        ctx.arc(this.x + 6, this.y - 3, 1.5, 0, Math.PI * 2);
        ctx.fill();

        // Mỏ chim
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

            // Va chạm đất
            if (this.y + this.radius >= canvas.height - 50) {
                this.y = canvas.height - 50 - this.radius;
                gameOver();
            }

            // Chạm trần
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

// --- QUẢN LÝ ỐNG CỐNG CHUẨN (PIPES) ---
const pipes = {
    position: [],
    topGap: 120,    // Khoảng hở giữa ống trên và dưới
    dx: 2,          // Tốc độ di chuyển
    width: 52,      // Độ rộng thân ống

    draw: function() {
        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            let topY = p.y;
            let bottomY = p.y + this.topGap;
            let groundHeight = 50;
            let totalHeight = canvas.height - groundHeight;

            let pipeColor = "#73BF2E";
            let pipeBorder = "#558022";
            let capHeight = 24;
            let capOverhang = 4; // Phần đầu ống loe rộng ra

            // --- 1. ỐNG TRÊN ---
            ctx.fillStyle = pipeColor;
            ctx.fillRect(p.x, 0, this.width, topY - capHeight);
            ctx.strokeStyle = pipeBorder;
            ctx.lineWidth = 2;
            ctx.strokeRect(p.x, 0, this.width, topY - capHeight);

            // Đầu ống trên
            ctx.fillRect(p.x - capOverhang, topY - capHeight, this.width + (capOverhang * 2), capHeight);
            ctx.strokeRect(p.x - capOverhang, topY - capHeight, this.width + (capOverhang * 2), capHeight);

            // --- 2. ỐNG DƯỚI ---
            let bottomPipeY = bottomY + capHeight;
            let bottomPipeHeight = totalHeight - bottomPipeY;

            // Đầu ống dưới
            ctx.fillStyle = pipeColor;
            ctx.fillRect(p.x - capOverhang, bottomY, this.width + (capOverhang * 2), capHeight);
            ctx.strokeRect(p.x - capOverhang, bottomY, this.width + (capOverhang * 2), capHeight);

            // Thân ống dưới
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

            // Cộng điểm
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

// --- MẶT ĐẤT ---
function drawGround() {
    ctx.fillStyle = "#D2B48C";
    ctx.fillRect(0, canvas.height - 50, canvas.width, 50);
    ctx.fillStyle = "#558022";
    ctx.fillRect(0, canvas.height - 50, canvas.width, 10);
}

function gameOver() {
    if (
