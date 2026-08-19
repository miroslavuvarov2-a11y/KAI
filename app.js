const chat = document.getElementById('chat');
const composer = document.getElementById('composer');
const input = document.getElementById('message');
const voiceBtn = document.getElementById('voiceBtn');
const voiceStatus = document.getElementById('voiceStatus');

function addMessage(text, role) {
  const row = document.createElement('div');
  row.className = `message ${role}`;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return row;
}

function localReply(text) {
  const q = text.toLowerCase();
  if (q.includes('привет') || q.includes('здрав')) return 'Привет! 👋 Я KAI. Сейчас я работаю в режиме интерфейса — подключи свой AI backend, чтобы получать настоящие ответы.';
  if (q.includes('кто ты')) return 'Я KAI — интерфейс AI-чата с голосовым вводом. 🤖';
  if (q.includes('голос')) return 'Нажми на 🎙️ и говори. Браузер распознает речь и вставит её в поле сообщения.';
  return 'Сообщение получено! Для настоящих ответов KAI подключи API через безопасный серверный backend. 🔌';
}

composer.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  input.value = '';
  const typing = addMessage('KAI печатает…', 'ai');
  typing.classList.add('typing');
  setTimeout(() => {
    typing.remove();
    addMessage(localReply(text), 'ai');
  }, 450);
});

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'ru-RU';
  recognition.interimResults = true;
  recognition.continuous = false;

  recognition.onstart = () => {
    voiceBtn.classList.add('active');
    voiceStatus.textContent = '🎙️ Слушаю…';
  };
  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) transcript += event.results[i][0].transcript;
    input.value = transcript;
  };
  recognition.onerror = () => {
    voiceStatus.textContent = 'Не удалось распознать речь.';
  };
  recognition.onend = () => {
    voiceBtn.classList.remove('active');
    setTimeout(() => { voiceStatus.textContent = ''; }, 900);
  };
  voiceBtn.addEventListener('click', () => {
    try { recognition.start(); } catch (_) { recognition.stop(); }
  });
} else {
  voiceBtn.addEventListener('click', () => {
    voiceStatus.textContent = 'Голосовой ввод не поддерживается этим браузером.';
  });
}
