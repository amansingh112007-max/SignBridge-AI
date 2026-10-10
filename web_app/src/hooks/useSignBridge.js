import { useRef, useState, useCallback, useEffect } from 'react';

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

  // ✏️ EDIT 1: a ref mirror of the language, so the WebSocket callback
  // always reads the CURRENT language (even if switched mid-session)
  const langRef = useRef('en');

  // State that the UI reacts to
  const [connected, setConnected] = useState(false);
  const [running, setRunning] = useState(false);
  const [tracking, setTracking] = useState(false);
  const [currentText, setCurrentText] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [landmarks, setLandmarks] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);
  const [lang, setLangState] = useState('en');
  const [seconds, setSeconds] = useState(0);

  // Session timer (mm:ss shown in the studio header)
  useEffect(() => {
    if (!running) return undefined;
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [running]);

  // Grab one video frame, squash it into a JPEG, ship it to the backend
  const sendFrame = useCallback(() => {
    const ws = wsRef.current;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!video || video.readyState < 2 || video.videoWidth === 0) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    // toBlob gives us real JPEG bytes (exactly what cv2.imdecode expects)
    canvas.toBlob((blob) => {
      if (blob && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        blob.arrayBuffer().then((buf) => wsRef.current.send(buf));
      }
    }, 'image/jpeg', 0.6);
  }, []);

  // ✏️ EDIT 3: speak using the browser's built-in on-device voice engine
  const speakText = useCallback((text) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();          // don't queue up old words
    const u = new SpeechSynthesisUtterance(text);
    u.lang = langRef.current === 'hi' ? 'hi-IN' : 'en-US';
    u.rate = 1.0;
    window.speechSynthesis.speak(u);
  }, []);

  // Switch spoken/caption language mid-session
  const setLang = useCallback((code) => {
    langRef.current = code;                   // ✏️ EDIT 2: keep the ref in sync
    setLangState(code);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ lang: code }));
    }
  }, []);

  // One-click start: camera ON + WebSocket ON + frame loop ON
  const start = useCallback(async () => {
    setError(null);
    setSeconds(0);
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
        ws.send(JSON.stringify({ lang: lang }));
        // 3. Start the frame pump
        intervalRef.current = setInterval(sendFrame, FRAME_INTERVAL_MS);
      };

      ws.onmessage = (event) => {
        try {
          const d = JSON.parse(event.data);
          setTracking(!!d.tracking);
          setLandmarks(d.landmarks || null);
          setConfidence(d.confidence || 0);
          if (d.text) {
            const label = d.text || d.gesture;
            setCurrentText(label);
            speakText(label);                 // ✏️ EDIT 4: speak every recognized word
            setTranscript((prev) => [...prev, {
              text: label,
              confidence: d.confidence,
              time: new Date().toLocaleTimeString(),
            }]);
          } else {
            setCurrentText(null); // graceful uncertainty: show "watching…"
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
  }, [sendFrame, lang, speakText]);

  // Clean shutdown: stop camera, close socket, clear timer, silence voice
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
    // Bonus: if a word is mid-speech, silence it when the session ends
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setRunning(false); setConnected(false);
    setTracking(false); setLandmarks(null);
    setCurrentText(null); setConfidence(0);
  }, []);

  const clearTranscript = useCallback(() => setTranscript([]), []);

  return {
    videoRef, canvasRef,
    connected, running, tracking, currentText, confidence, landmarks,
    transcript, error, lang, setLang, seconds,
    start, stop, clearTranscript,
  };
}