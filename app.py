from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# Gemini API Anahtarını buraya yapıştır
GEMINI_API_KEY = "AQ.Ab8RN6JeWF4Wmw1qo6mH6YxNKF_iTW6TbhfjoT60jlEbrVlJcg"
client = genai.Client(api_key=GEMINI_API_KEY)

# HTML arayüzünü doğrudan kodun içine gömdük (Klasör hatası riski sıfır!)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YASOP V1 - Yapay Zeka Asistanı</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --chat-bg: #1e293b;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --bot-bubble: #334155;
            --user-bubble: #6366f1;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .chat-container { width: 100%; max-width: 800px; height: 90vh; background: var(--chat-bg); border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .chat-header { padding: 20px; background: rgba(15, 23, 42, 0.7); border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; }
        .chat-header h1 { font-size: 1.25rem; font-weight: 600; letter-spacing: 1px; color: var(--text-main); display: flex; align-items: center; gap: 10px; }
        .status-dot { width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; font-size: 0.95rem; word-wrap: break-word; }
        .message.user { background: var(--user-bubble); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .message.bot { background: var(--bot-bubble); color: var(--text-main); align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(255,255,255,0.05); }
        .chat-input-area { padding: 20px; background: rgba(15, 23, 42, 0.7); border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #0f172a; color: white; font-size: 1rem; outline: none; transition: border 0.3s; }
        input[type="text"]:focus { border-color: var(--primary); }
        button { padding: 0 24px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
        button:hover { background: var(--primary-hover); }
        .typing { font-style: italic; color: var(--text-muted); font-size: 0.9rem; display: none; padding: 5px 10px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1><span class="status-dot"></span> YASOP V1 (Orkestratör)</h1>
            <span style="font-size: 0.8rem; color: #94a3b8;">Çevrim içi</span>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">Merhaba! Ben **YASOP V1**. Senin özel yapay zeka asistanınım. Bana dilediğini sorabilirsin!</div>
        </div>
        <div class="typing" id="typingIndicator">YASOP V1 düşünüyor...</div>
        <div class="chat-input-area">
            <input type="text" id="userInput" placeholder="YASOP V1'e bir şeyler yaz..." autofocus>
            <button onclick="sendMessage()">Gönder</button>
        </div>
    </div>
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const typingIndicator = document.getElementById('typingIndicator');
        userInput.addEventListener('keypress', function (e) { if (e.key === 'Enter') { sendMessage(); } });
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            appendMessage(text, 'user');
            userInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;
            typingIndicator.style.display = 'block';
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                typingIndicator.style.display = 'none';
                appendMessage(data.response, 'bot');
            } catch (err) {
                typingIndicator.style.display = 'none';
                appendMessage('Bir bağlantı hatası oluştu baboli!', 'bot');
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        function appendMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            if (sender === 'bot') { div.innerHTML = marked.parse(text); } else { div.textContent = text; }
            chatMessages.appendChild(div);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Boş bir mesaj gönderdiniz."})
    try:
        prompt = (
            "Sen YASOP V1 adlı gelişmiş, akıllı ve karizmatik bir yapay zeka asistanısın. "
            "Kullanıcının sorularına en mantıklı, akıcı ve net Türkçe ile yanıt ver.\n\n"
            f"Kullanıcı: {user_message}"
        )
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        yasop_cevap = response.text
    except Exception as e:
        yasop_cevap = f"YASOP V1 sistem hatası: {str(e)}"
    return jsonify({"response": yasop_cevap})

if __name__ == "__main__":
    app.run(debug=True, port=5000)