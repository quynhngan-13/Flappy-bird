import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Flappy Bird",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird")
st.markdown("Nhấn **Space** hoặc **Click chuột** vào màn hình game để điều khiển chú chim bay qua các ống cống!")

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

// --- HỆ THỐNG ÂM THANH & ĐIỆP KHÚC "BANG BANG BANG" ---
let audioCtx = null;
let bgmTimer = null;
let bgmNoteIndex = 0;

// Giai điệu điệp khúc "Bang Bang Bang" (BIGBANG)
const bangChorusNotes = [
    523.25, 523.25, 587.33, 659.25, 523.25, 392.00, 440.00, 523.25,
    659.25, 659.25, 587.33, 523.25, 440.00, 523.25, 587.33, 523.25
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
            osc.type = "square";
            osc.frequency.setValueAtTime(bangChorusNotes[bgmNoteIndex], audioCtx.currentTime);
            
            gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.12);
            
            bgmNoteIndex = (bgmNoteIndex + 1) % bangChorusNotes.length;
        }
    }, 150);
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

// --- CON CHIM (Lông chim đổi màu khi bay qua ống cống) ---
const bird = {
    x: 50,
    y: 150,
    radius: 12,
    gravity: 0.25,
    jump: 4.6,
    velocity: 0,
    color: "#FFD700", // Màu bộ lông mặc định ban đầu
    birdColors: ["#FFD700", "#FF1493", "#00BFFF", "#32CD32", "#FF4500", "#9370DB", "#00FFFF", "#FF8C00", "#E67E22", "#E74C3C"],

    // Hàm thay đổi màu bộ lông ngẫu nhiên
    changeColor: function() {
        let available = this.birdColors.filter(c => c !== this.color);
        this.color = available[Math.floor(Math.random() * available.length)];
    },
    
    draw: function() {
        // Thân & Lông chim (đổi đủ thứ màu)
        ctx.fillStyle = this.color;
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
        ctx.arc(this.x + 6, this.y - 3
