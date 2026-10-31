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
        return available
