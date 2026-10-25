import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web Streamlit
st.set_page_config(
    page_title="Flappy Bird - Streamlit Edition",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird Game trên Streamlit")
st.markdown("Nhấn phím **Space** hoặc **Click chuột trực tiếp vào màn hình game** để điều khiển chú chim bay qua các ống cống!")

# Đoạn mã HTML/JS/CSS của game Flappy Bird
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
let gameState = "START";

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
    },
    
    flap: function() {
        this.velocity = -this.jump;
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

const pipes = {
    position: [],
    topGap: 120,
    dx: 2,

    draw: function() {
        ctx.fillStyle = "#2ECC71";
        ctx.strokeStyle = "#27AE60";
        ctx.lineWidth = 2;

        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            let topY = p.y;
            let bottomY = p.y + this.topGap;

            ctx.fillRect(p.x, 0, 50, topY);
            ctx.strokeRect(p.x, 0, 50, topY);

            ctx.fillRect(p.x, bottomY, 50, canvas.height - bottomY - 50);
            ctx.strokeRect(p.x, bottomY, 50, canvas.height - bottomY - 50);
        }
    },

    update: function() {
        if (gameState !== "PLAYING") return;

        if (frames % 100 === 0) {
            this.position.push({
                x: canvas.width,
                y: Math.floor(Math.random() * (220 - 50 + 1)) + 50
            });
        }

        for (let i = 0; i < this.position.length; i++) {
            let p = this.position[i];
            p.x -= this.dx;

            if (
                bird.x + bird.radius > p.x &&
                bird.x - bird.radius < p.x + 50 &&
                (bird.y - bird.radius < p.y || bird.y + bird.radius > p.y + this.topGap)
            ) {
                gameOver();
            }

            if (p.x + 50 < bird.x && !p.passed) {
                score++;
                p.passed = true;
                if (score > highScore) highScore = score;
            }

            if (p.x + 50 <= 0) {
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
    ctx.fillStyle = "#8B5A2B";
    ctx.fillRect(0, canvas.height - 50, canvas.width, 8);
}

function gameOver() {
    gameState = "GAMEOVER";
}

function drawUI() {
    ctx.fillStyle = "#FFF";
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;

    if (gameState === "PLAYING") {
        ctx.font = "35px Arial";
        ctx.fillText(score, canvas.width / 2 - 10, 50);
        ctx.strokeText(score, canvas.width / 2 - 10, 50);
    } else if (gameState === "START") {
        ctx.font = "20px Arial";
        ctx.fillText("Nhấn SPACE hoặc CLICK để chơi", 30, canvas.height / 2);
    } else if (gameState === "GAMEOVER") {
        ctx.font = "30px Arial";
        ctx.fillText("GAME OVER", 90, 180);
        ctx.strokeText("GAME OVER", 90, 180);

        ctx.font = "20px Arial";
        ctx.fillText("Điểm: " + score, 140, 230);
        ctx.fillText("Kỷ lục: " + highScore, 130, 260);
        ctx.fillText("Nhấn SPACE để chơi lại", 70, 310);
    }
}

function action() {
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
    bird.draw();
    pipes.draw();
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

# Hiển thị game bên trong giao diện Streamlit
components.html(flappy_bird_html, height=520)
