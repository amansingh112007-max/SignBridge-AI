import { useRef, useState, useCallback } from 'react';

// Where our FastAPI backend lives
const BACKEND_URL = 'ws://localhost:8000/ws';
// Send ~10 frames per second (keeps laptop CPU happy)
const FRAME_INTERVAL_MS = 100;

export default function useSignBridge() {
  // Refs point to real DOM / network objects
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // State that the UI reacts to
  const [connected, setConnected] = useState(false);
  const [running, setRunning] = useState(false);
  const [currentGesture, setCurrentGesture] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);

  // Grab one video frame, squash it into a JPEG, ship it to the backend
  const sendFrame = useCallback(() => {
    const ws = wsRef.current;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!video || video.readyState < 2 || video.videoWidth === 0) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // toBlob gives us real JPEG bytes (exactly what cv2.imdecode expects)
    canvas.toBlob((blob) => {
      if (blob && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        blob.arrayBuffer().then((buf) => wsRef.current.send(buf));
      }
    }, 'image/jpeg', 0.6);
  }, []);

  // One-click start: camera ON + WebSocket ON + frame loop ON
  const start = useCallback(async () => {
    setError(null);
    try {
      // 1. Ask the browser for camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      // 2. Open the WebSocket to the AI backend
      const ws = new WebSocket(BACKEND_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setRunning(true);
        // 3. Start the frame pump
        intervalRef.current = setInterval(sendFrame, FRAME_INTERVAL_MS);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.gesture && data.gesture !== 'None') {
            setCurrentGesture(data.gesture);
            setTranscript((prev) => [
              ...prev,
              { text: data.gesture, time: new Date().toLocaleTimeString() },
            ]);
          } else {
            setCurrentGesture(null); // graceful uncertainty: show "watching…"
          }
        } catch (e) {
          console.warn('Unexpected message from backend:', event.data);
        }
      };

      ws.onclose = () => setConnected(false);
      ws.onerror = () =>
        setError('Cannot reach the AI backend. Is uvicorn running on port 8000?');
    } catch (err) {
      setError('Camera permission denied, or no webcam found.');
    }
  }, [sendFrame]);

  // Clean shutdown: stop camera, close socket, clear timer
  const stop = useCallback(() => {
    clearInterval(intervalRef.current);
    intervalRef.current = null;
    if (wsRef.current) wsRef.current.close();
    wsRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setRunning(false);
    setConnected(false);
    setCurrentGesture(null);
  }, []);

  const clearTranscript = useCallback(() => setTranscript([]), []);

  return {
    videoRef, canvasRef,
    connected, running, currentGesture, transcript, error,
    start, stop, clearTranscript,
  };
}