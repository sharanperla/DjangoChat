document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket('ws://' + window.location.host + '/ws/audio_call/');

    const localAudio = document.getElementById('localAudio');
    const remoteAudio = document.getElementById('remoteAudio');
    const startCallButton = document.getElementById('startCallButton');
    const endCallButton = document.getElementById('endCallButton');

    let localConnection;
    let remoteConnection;

    startCallButton.addEventListener('click', () => {
        initiateCall();
    });

    function initiateCall() {
        localConnection = new RTCPeerConnection();
        remoteConnection = new RTCPeerConnection();

        localConnection.onicecandidate = event => {
            if (event.candidate) {
                sendIceCandidate(event.candidate);
            }
        };

        remoteConnection.onicecandidate = event => {
            if (event.candidate) {
                sendIceCandidate(event.candidate);
            }
        };

        remoteConnection.ontrack = event => {
            remoteAudio.srcObject = event.streams[0];
        };

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                localAudio.srcObject = stream;
                stream.getTracks().forEach(track => localConnection.addTrack(track, stream));
                return localConnection.createOffer();
            })
            .then(offer => {
                localConnection.setLocalDescription(offer);
                sendOffer(offer);
            })
            .catch(error => {
                console.error('Error accessing media devices.', error);
            });
    }

    function sendIceCandidate(candidate) {
        socket.send(JSON.stringify({
            type: 'ice_candidate',
            ice_candidate: candidate
        }));
    }

    function sendOffer(offer) {
        socket.send(JSON.stringify({
            type: 'offer',
            offer: offer
        }));
    }

    function sendAnswer(answer) {
        socket.send(JSON.stringify({
            type: 'answer',
            answer: answer
        }));
    }

    function handleOffer(offer) {
        remoteConnection.setRemoteDescription(new RTCSessionDescription(offer));
        remoteConnection.createAnswer().then(answer => {
            remoteConnection.setLocalDescription(answer);
            sendAnswer(answer);
        });
    }

    function handleAnswer(answer) {
        localConnection.setRemoteDescription(new RTCSessionDescription(answer));
    }

    function handleIceCandidate(candidate) {
        localConnection.addIceCandidate(new RTCIceCandidate(candidate));
        remoteConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const type = data.type;

        switch (type) {
            case 'ice_candidate':
                handleIceCandidate(data.ice_candidate);
                break;
            case 'offer':
                handleOffer(data.offer);
                break;
            case 'answer':
                handleAnswer(data.answer);
                break;
        }
    };

    endCallButton.addEventListener('click', () => {
        if (localConnection) {
            localConnection.close();
        }
        if (remoteConnection) {
            remoteConnection.close();
        }
        // Optionally, notify the server that the call ended
    });

    // Additional functionalities to handle incoming calls would be added here
});
