var tips = [
    "Try the pomodoro technique",
    "Use a calendar",
    "Silence your phone",
    "Create  a study group with set days",
    "Give yourself an earlier deadline",
    "Record yourself talking about the material",
    "Teach the material to someone",
    "Break down the problem step-by-step",
    "Go to office hours",
    "Ask for help",
    "Create a distraction-free study space",
    "Space out tasks over a certain time period",
    "Create a mnemonic device (like PEMDAS)",
    "Try writing it down instead of typing #ZoomUni",
    "Quiz yourself on Quizlet or asking yourself questions",
    "Talk it out",
    "Walk backward (just try)",
    "Switch up the topics or subjects you're studying",
    "Treat yourself!",
    "Hydrate with refreshing water",
    "Take a short break",
    "Exercise before studying",
    "Learn a TikTok dance or your favorite song's choreography",
    "Meditate",
    "Take a nap",
    "Do yoga",
    "Try a different study spot"
]

function newTip() {
    var randomNumber = Math.floor(Math.random() * (tips.length));
    document.getElementById('tipDisplay').innerHTML = tips[randomNumber];
}