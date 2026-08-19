const chat = document.getElementById('chat');
const composer = document.getElementById('composer');
const input = document.getElementById('message');
const voiceBtn = document.getElementById('voiceBtn');
const voiceStatus = document.getElementById('voiceStatus');

const history = [];

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

async function askKAI(text) {
  history.push({ role: 'user', content: text });
  const response = await fetch('http://127.0.0.1:31415/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: history })
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Ошибка AI');

  history.push({ role: 'assistant', content: data.content });
  return data.content;
}

composer.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, 'user');
  input.value = '';
  const typing = addMessage('KAI печатает…', 'ai');
  typing.classList.add('typing');

  try {
    const answer = await askKAI(text);
    typing.remove();
    addMessage(answer, 'ai');
  } catch (error) {
    typing.remove();
    addMessage(`Ошибка подключения к KAI: ${error.message}`, 'ai');
  }
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
