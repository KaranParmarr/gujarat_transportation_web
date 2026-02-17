
/* Auto-play video when visible */
document.querySelectorAll(".video-card video").forEach(video=>{
    video.play().catch(()=>{})
});

/* Like counter animation */
document.querySelectorAll(".like-btn").forEach(btn=>{
    btn.addEventListener("click",()=>{
        let count = btn.querySelector(".like-count");
        count.textContent = parseInt(count.textContent) + 1;
    });
});

/* Fullscreen reels (Mobile only) */
document.querySelectorAll(".fullscreen-btn").forEach(btn=>{
    btn.addEventListener("click",()=>{
        if(window.innerWidth <= 768){
            btn.closest(".media-card").requestFullscreen();
        }
    });
});

/* Swipe support (Mobile) */
let startY = 0;
document.addEventListener("touchstart",e=>{
    startY = e.touches[0].clientY;
});

document.addEventListener("touchend",e=>{
    let diff = startY - e.changedTouches[0].clientY;
    if(Math.abs(diff) > 80){
        document.exitFullscreen?.();
    }
});

