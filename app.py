// --- THÊM NHẠC NỀN BẰNG FILE MP3 THỰC TẾ ---
// Thay thế đoạn link dưới đây bằng link file .mp3 của bạn
const bgm = new Audio('https://duong-dan-toi-file-mp3-cua-ban.mp3');
bgm.loop = true; // Lặp lại liên tục khi nhạc chạy hết
bgm.volume = 0.3; // Điều chỉnh âm lượng từ 0.0 đến 1.0 (0.3 là vừa nghe)

function startBGM() {
    if (gameState === "PLAYING") {
        bgm.play().catch(e => console.log("Trình duyệt chặn phát tự động:", e));
    }
}

// Khi thua cuộc (Game Over), dừng nhạc nền lại
function gameOver() {
    if (gameState !== "GAMEOVER") {
        gameState = "GAMEOVER";
        bgm.pause(); // Dừng nhạc nền
        bgm.currentTime = 0; // Đưa bài hát về từ đầu
        playDieSound();
    }
}

// Khi bấm chơi lại, cho phép phát lại nhạc
function action() {
    initAudio();
    
    if (gameState === "START") {
        gameState = "PLAYING";
        startBGM();
        bird.flap();
    } else if (gameState === "PLAYING") {
        bird.flap();
    } else if (gameState === "GAMEOVER") {
        bird.reset();
        pipes.reset();
        score = 0;
        gameState = "PLAYING";
        startBGM(); // Phát lại nhạc khi chơi lại
        bird.flap();
    }
}
