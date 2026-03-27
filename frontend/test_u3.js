const { RealtimeTranscriber } = require('assemblyai');

const token = "9df9ae6e7f4a4fcfbf51ef5a3d105997";

console.log("Testing API Key with U3 Model...");

const rt = new RealtimeTranscriber({
    token: token,
    sampleRate: 16000,
    speechModel: "u3-rt-pro" // Adding the new model to bypass the 410 Gone legacy endpoint
});

rt.on('open', ({ sessionId }) => {
    console.log("✅ SUCCESS! Connected to AssemblyAI WebSocket with U3!");
    console.log(`Session ID: ${sessionId}`);
    rt.close();
    process.exit(0);
});

rt.on('error', (error) => {
    console.error(`❌ ERROR during WebSocket stream:`, error);
    process.exit(1);
});

rt.connect().catch((err) => {
    console.error(`❌ Connection ERROR:`, err);
    process.exit(1);
});
