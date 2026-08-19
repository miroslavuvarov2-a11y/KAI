const chat = document.getElementById('chat');
const composer = document.getElementById('composer');
const input = document.getElementById('message');
const voiceBtn = document.getElementById('voiceBtn');
const voiceStatus = document.getElementById('voiceStatus');

const history = [];
const KEY_NAME = 'kai_mistral_api_key';

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

function getApiKey() {
  let key = localStorage.getItem(KEY_NAME);
  if (!key) {
    key = window.prompt('🔑 Введи свой Mistral API Key. Он сохранится только в этом браузере:');
    if (key) localStorage.setItem(KEY_NAME, key.trim());
  }
  return key ? key.trim() : '';
}

async function askKAI(text) {
  const apiKey = getApiKey();
  if (!apiKey) throw new Error('Mistral API Key не введён.');

  history.push({ role: 'user', content: text });
  const response = await fetch('https://api.mistral.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({ model: 'mistral-small-latest', messages: history, temperature: 0.7 })
  });

  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) localStorage.removeItem(KEY_NAME);
    throw new Error(data?.message || data?.error?.message || `Mistral HTTP ${response.status}`);
  }

  const answer = data.choices?.[0]?.message?.content;
  if (!answer) throw new Error('Mistral не вернул ответ.');
  history.push({ role: 'assistant', content: answer });
  return answer;
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
    addMessage(`Ошибка: ${error.message}`, 'ai');
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
  recognition.onerror = () => { voiceStatus.textContent = 'Не удалось распознать речь.'; };
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
