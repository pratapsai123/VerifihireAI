from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which OpenAI API is primarily used for text generation and reasoning?",
    "options": {
      "A": "Images API",
      "B": "Embeddings API",
      "C": "Responses API",
      "D": "Files API"
    },
    "answer": "C"
  },
  {
    "question": "True or False: The Responses API replaces both Chat Completions and Assistants APIs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO input types can be sent to the Responses API?",
    "options": {
      "A": "Text",
      "B": "Image",
      "C": "CSV",
      "D": "Audio"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the purpose of the Embeddings API?",
    "options": {
      "A": "Generate images",
      "B": "Convert text into numerical vectors",
      "C": "Fine-tune models",
      "D": "Store files"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Embeddings are commonly used for semantic search.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO use cases rely heavily on embeddings?",
    "options": {
      "A": "Recommendation systems",
      "B": "Document similarity",
      "C": "Image generation",
      "D": "Speech synthesis"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "Which model family is optimized for multimodal inputs?",
    "options": {
      "A": "GPT-3",
      "B": "GPT-4o",
      "C": "Ada",
      "D": "Whisper"
    },
    "answer": "B"
  },
  {
    "question": "True or False: GPT-4o can accept both text and images as input.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of the Files API?",
    "options": {
      "A": "Store datasets and documents for use with other APIs",
      "B": "Generate embeddings",
      "C": "Execute code",
      "D": "Handle authentication"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO APIs can directly use uploaded files?",
    "options": {
      "A": "Fine-tuning",
      "B": "Responses",
      "C": "Moderation",
      "D": "Billing"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The Moderation API generates text responses.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does the Moderation API return?",
    "options": {
      "A": "Generated answers",
      "B": "Policy violation scores",
      "C": "Embeddings",
      "D": "Images"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO categories are checked by the Moderation API?",
    "options": {
      "A": "Hate",
      "B": "Self-harm",
      "C": "Latency",
      "D": "Token usage"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Moderation should be applied only after content is generated.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is token usage primarily used for?",
    "options": {
      "A": "Model selection",
      "B": "Billing and cost calculation",
      "C": "Security validation",
      "D": "Prompt tuning"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors affect token count?",
    "options": {
      "A": "Prompt length",
      "B": "Response length",
      "C": "API key name",
      "D": "Request headers"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Images count toward token usage in multimodal models.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is rate limiting in OpenAI APIs?",
    "options": {
      "A": "Limiting response length",
      "B": "Restricting number of requests per time window",
      "C": "Reducing model accuracy",
      "D": "Token compression"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO strategies help handle rate limits?",
    "options": {
      "A": "Exponential backoff",
      "B": "Request batching",
      "C": "Increasing temperature",
      "D": "Using longer prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Rate limits are the same for all OpenAI accounts.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is function calling in the Responses API?",
    "options": {
      "A": "Calling Python functions directly",
      "B": "Structured output that maps to a predefined schema",
      "C": "Running serverless code",
      "D": "Executing SQL queries"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO benefits does function calling provide?",
    "options": {
      "A": "Reliable structured output",
      "B": "Easier tool integration",
      "C": "Lower token cost",
      "D": "Faster training"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Function calling guarantees correct tool execution.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI API endpoint is currently recommended for building conversational AI interfaces using models like GPT-4o?",
    "options": {
      "A": "/v1/completions",
      "B": "/v1/chat/completions",
      "C": "/v1/engines",
      "D": "/v1/conversations"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'top_p' parameter (Nucleus Sampling) control in an API request?",
    "options": {
      "A": "The maximum number of tokens allowed in the response.",
      "B": "The model's creativity by limiting the token pool to a cumulative probability threshold.",
      "C": "The physical priority of the request on OpenAI's servers.",
      "D": "The number of best-of-N completions to return."
    },
    "answer": "B"
  },
  {
    "question": "When using the Embeddings API (e.g., text-embedding-3-small), what is the primary purpose of the output vector?",
    "options": {
      "A": "To provide a translated version of the text.",
      "B": "To represent the semantic meaning of the text as a list of numbers for tasks like similarity search.",
      "C": "To act as a unique password for the user's session.",
      "D": "To compress the text for faster database storage."
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'seed' parameter in Chat Completions?",
    "options": {
      "A": "To start a new database for the model.",
      "B": "To encourage deterministic outputs by ensuring the model samples tokens in a more reproducible way.",
      "C": "To provide the model with a list of forbidden words.",
      "D": "To increase the speed of the model's response."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'max_tokens' parameter in the API limits the sum of both the input prompt tokens and the generated output tokens.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'frequency_penalty' parameter specifically target?",
    "options": {
      "A": "The speed at which the API is called.",
      "B": "The likelihood of the model repeating the exact same verbatim text within a completion.",
      "C": "The cost of the API request.",
      "D": "The number of users accessing the model simultaneously."
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI model is specifically optimized for high-volume, low-latency, and cost-efficient tasks?",
    "options": {
      "A": "GPT-4o",
      "B": "GPT-4o-mini",
      "C": "o1-preview",
      "D": "DALL-E 3"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'System Fingerprint' in the API response metadata?",
    "options": {
      "A": "To track the biometrics of the developer.",
      "B": "To identify the specific backend configuration used to generate the response, aiding in reproducibility tracking.",
      "C": "To provide a digital signature for legal copyright.",
      "D": "To show the GPU temperature of the OpenAI server."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO valid roles in the 'messages' array for a Chat Completion request:",
    "options": {
      "A": "developer",
      "B": "assistant",
      "C": "moderator",
      "D": "admin"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "How should a developer handle a '429 Too Many Requests' error from the OpenAI API?",
    "options": {
      "A": "Immediately retry the request every 100ms.",
      "B": "Implement exponential backoff and check the 'RateLimit' headers in the response.",
      "C": "Delete their API key and create a new one.",
      "D": "Switch to an older model like text-davinci-003."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of the 'o1' series of models compared to GPT-4o?",
    "options": {
      "A": "They are cheaper for simple tasks.",
      "B": "They use 'Reasoning Tokens' to perform complex problem-solving through internal chain-of-thought before answering.",
      "C": "They are the only models that support image generation.",
      "D": "They do not require an API key to access."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Using 'logit_bias' allows developers to either force or absolutely ban specific tokens from appearing in the output.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'n' parameter in the Chat Completion API do?",
    "options": {
      "A": "Sets the number of threads for the CPU.",
      "B": "Determines how many separate chat completions to generate for a single prompt.",
      "C": "Calculates the total number of nouns in the output.",
      "D": "Specifies the number of GPUs to use for the request."
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI tool is best suited for developers wanting to build agents that can maintain long-term state, use threads, and call tools like a Code Interpreter?",
    "options": {
      "A": "Chat Completions API",
      "B": "Assistants API",
      "C": "Moderation API",
      "D": "Realtime API"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Moderation API' used for?",
    "options": {
      "A": "To check if the API is currently online.",
      "B": "To identify and filter content that violates OpenAI's usage policies (e.g., hate, violence, self-harm).",
      "C": "To manage the billing and subscription of the account.",
      "D": "To speed up the generation of responses."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the OpenAI Responses API?",
    "options": {
      "A": "Only chat-based conversations",
      "B": "Unified API for text, vision, and tool usage",
      "C": "Image storage",
      "D": "API key management"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The Responses API supports streaming outputs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO output types can a Responses API call return?",
    "options": {
      "A": "Text",
      "B": "Tool calls",
      "C": "CSV files",
      "D": "Binary executables"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the role of the temperature parameter?",
    "options": {
      "A": "Controls randomness of output",
      "B": "Limits token count",
      "C": "Improves security",
      "D": "Controls latency"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Setting temperature to 0 makes output deterministic.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO parameters influence output diversity?",
    "options": {
      "A": "temperature",
      "B": "top_p",
      "C": "max_tokens",
      "D": "model"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is top_p (nucleus sampling)?",
    "options": {
      "A": "Limits response length",
      "B": "Samples from tokens whose cumulative probability exceeds p",
      "C": "Controls batch size",
      "D": "Caches responses"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Using both temperature and top_p together is recommended.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does max_tokens control?",
    "options": {
      "A": "Prompt size",
      "B": "Maximum length of generated output",
      "C": "Model size",
      "D": "Token price"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors can cause responses to be truncated?",
    "options": {
      "A": "max_tokens limit",
      "B": "Context window limit",
      "C": "Low temperature",
      "D": "High top_p"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Truncated responses always indicate an error.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is context window in OpenAI models?",
    "options": {
      "A": "Maximum request rate",
      "B": "Maximum number of tokens in prompt + response",
      "C": "Prompt memory duration",
      "D": "Cache size"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO actions help stay within context limits?",
    "options": {
      "A": "Prompt summarization",
      "B": "Chunking inputs",
      "C": "Higher temperature",
      "D": "Longer system prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: System messages count toward the context window.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is streaming in OpenAI APIs?",
    "options": {
      "A": "Downloading models",
      "B": "Receiving partial responses token-by-token",
      "C": "Batching requests",
      "D": "Caching outputs"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO benefits does streaming provide?",
    "options": {
      "A": "Lower perceived latency",
      "B": "Improved UX",
      "C": "Lower token usage",
      "D": "Higher accuracy"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Streaming reduces total compute cost.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is function/tool calling best suited for?",
    "options": {
      "A": "Free-form text generation",
      "B": "Structured outputs and API integration",
      "C": "Reducing latency",
      "D": "Model training"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO components are required for tool calling?",
    "options": {
      "A": "Tool schema",
      "B": "Model support",
      "C": "Fine-tuning",
      "D": "Embeddings"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Tool calling ensures the model will always select the correct tool.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the main security risk when exposing tools to models?",
    "options": {
      "A": "Prompt injection",
      "B": "Token overflow",
      "C": "Higher latency",
      "D": "Rate limiting"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO mitigations reduce tool abuse risk?",
    "options": {
      "A": "Strict schema validation",
      "B": "Tool access control",
      "C": "Higher temperature",
      "D": "Longer prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Tool outputs should be treated as untrusted input.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "When using 'Parallel Function Calling' in the Chat Completions API, how does the model signal multiple tool requests in a single response?",
    "options": {
      "A": "It returns a single JSON object containing a list of function names.",
      "B": "The 'tool_calls' array in the message object contains multiple tool call objects, each with a unique 'id' and specific 'arguments'.",
      "C": "It sends a separate HTTP response for each function call.",
      "D": "It uses the 'system' role to announce the functions sequentially."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'Reasoning Tokens' in OpenAI's o1-preview and o1-mini models?",
    "options": {
      "A": "They are used to translate the output into different programming languages.",
      "B": "They represent the internal 'chain-of-thought' the model generates to solve complex problems; these are billed but not visible in the final API response.",
      "C": "They are tokens that the user must provide to enable 'High Intelligence' mode.",
      "D": "They act as a security layer to verify the user's prompt."
    },
    "answer": "B"
  },
  {
    "question": "In the OpenAI Realtime API (GA), which protocol is recommended for low-latency, bidirectional voice agents in a browser environment?",
    "options": {
      "A": "Standard HTTP Long Polling",
      "B": "WebRTC using the 'v1/realtime/calls' unified interface",
      "C": "gRPC over HTTP/2",
      "D": "MQTT"
    },
    "answer": "B"
  },
  {
    "question": "What is the key advantage of the 'Batch API' for non-time-sensitive tasks like bulk data classification?",
    "options": {
      "A": "It guarantees a response time under 5 seconds.",
      "B": "It offers a 50% discount on costs and provides a separate, significantly higher rate limit pool, with a 24-hour completion SLA.",
      "C": "It allows the model to access the live internet.",
      "D": "It removes the need for any token limits."
    },
    "answer": "B"
  },
  {
    "question": "When implementing the Assistants API (v2) 'File Search' tool, what is the default chunking strategy used by OpenAI?",
    "options": {
      "A": "1000 tokens per chunk with 0 overlap.",
      "B": "800 tokens per chunk with a 400-token overlap, using text-embedding-3-large.",
      "C": "Chunking by paragraph regardless of token count.",
      "D": "One chunk per entire document."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In the Realtime API, the 'semantic_vad' (Voice Activity Detection) mode uses the model's understanding of the conversation to decide when a user has finished speaking, rather than just silence detection.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What happens to the 'Context Window' when a Run in the Assistants API exceeds the model's limit?",
    "options": {
      "A": "The Run fails with a 'ContextExceeded' error.",
      "B": "The API automatically manages truncation of older messages to fit the most relevant content within the model's maximum context length.",
      "C": "The user is automatically charged for a larger context window.",
      "D": "The model starts ignoring all system instructions."
    },
    "answer": "B"
  },
  {
    "question": "Which header was mandatory during the Realtime API beta but should be removed for the General Availability (GA) interface unless seeking legacy behavior?",
    "options": {
      "A": "OpenAI-Organization",
      "B": "OpenAI-Beta: realtime=v1",
      "C": "OpenAI-Project-ID",
      "D": "X-API-Key"
    },
    "answer": "B"
  },
  {
    "question": "In the context of 'Structured Outputs', what is the purpose of the 'json_schema' response format?",
    "options": {
      "A": "To make the response look pretty in a web browser.",
      "B": "To guarantee that the model's output strictly adheres to a developer-defined JSON schema, ensuring 100% reliability for programmatic parsing.",
      "C": "To encrypt the JSON output for security.",
      "D": "To force the model to use only numerical data."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lockdown Mode' in the 2026 OpenAI security updates?",
    "options": {
      "A": "A mode that turns off the API entirely during a cyberattack.",
      "B": "An advanced security setting for high-risk users designed to mitigate prompt injection attacks and URL-based data exfiltration.",
      "C": "A feature that prevents the developer from changing the model version.",
      "D": "A hardware-level lock on the OpenAI data center."
    },
    "answer": "B"
  },
  {
    "question": "Which parameter in the o3-mini and o1 series allows a developer to control the trade-off between reasoning depth and response latency?",
    "options": {
      "A": "thinking_budget",
      "B": "reasoning_effort (low, medium, high)",
      "C": "logic_depth_penalty",
      "D": "max_thought_tokens"
    },
    "answer": "B"
  },
  {
    "question": "As of early 2026, which API is designated as the long-term, unified replacement for the deprecated Assistants API?",
    "options": {
      "A": "Chat Completions v2",
      "B": "Responses API (v1/responses)",
      "C": "Agentic Workflow API",
      "D": "Threads & Runs v3"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary technical advantage of using WebRTC over WebSockets for the OpenAI Realtime API in mobile applications?",
    "options": {
      "A": "It allows for 100% deterministic text output.",
      "B": "It provides superior NAT traversal and lower-latency bidirectional audio streaming by using UDP-based transport.",
      "C": "It removes the need for an API key.",
      "D": "It automatically translates the audio to 50+ languages."
    },
    "answer": "B"
  },
  {
    "question": "In the Responses API, how does a developer implement a 'tool loop' for an agent that needs to call multiple functions before answering?",
    "options": {
      "A": "By manually recursive calling the /v1/chat endpoint.",
      "B": "By setting 'run_steps' to automatic, allowing the API to handle the orchestration of tool outputs back into the model until a final response is generated.",
      "C": "By using a while-loop in the client-code to check for 'requires_action' status.",
      "D": "The Responses API does not support multi-step tool use."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'thinking' parameter (introduced for GPT-5.2 and o3) provide to the developer in the API response?",
    "options": {
      "A": "A summary of the model's training data.",
      "B": "Access to the raw, unredacted chain-of-thought tokens, allowing for easier debugging of complex logical errors.",
      "C": "A countdown of how many seconds the model 'thought'.",
      "D": "A list of alternative answers the model considered."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o3' model series natively supports vision-based reasoning, whereas 'o3-mini' is optimized strictly for text-based STEM and coding tasks.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "When migrating from Assistants to the Responses/Conversations API, what replaces the 'Thread' as the durable, server-side store for message history?",
    "options": {
      "A": "The Memory Store",
      "B": "Conversation ID (v1/conversations)",
      "C": "Context Object",
      "D": "Session Token"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Semantic VAD' in the Realtime API?",
    "options": {
      "A": "A way to check if the user's speech makes sense.",
      "B": "An AI-powered Voice Activity Detection that uses context to understand if a user has finished a thought, rather than just relying on silence duration.",
      "C": "A method for detecting if the user is lying.",
      "D": "A filter that removes background noise from the audio."
    },
    "answer": "B"
  },
  {
    "question": "Which new security feature in the 2026 API allows organizations to flag 'Elevated Risk' prompts before they are processed by a model?",
    "options": {
      "A": "Moderation v2",
      "B": "Lockdown Mode & Elevated Risk Labels",
      "C": "Prompt Firewall",
      "D": "Safe-Input Header"
    },
    "answer": "B"
  },
  {
    "question": "How does the 'o1-pro' model differ from the standard 'o1' in the API?",
    "options": {
      "A": "It is cheaper for high-volume tasks.",
      "B": "It utilizes significantly more compute and thinking time to achieve higher consistency on research-level mathematics and PhD-level science problems.",
      "C": "It is the only model that supports 100 different languages.",
      "D": "It allows for full-parameter fine-tuning by the user."
    },
    "answer": "B"
  },
  {
    "question": "In the Realtime API (GA), what must a developer use to generate a short-lived 'client_secret' for secure frontend WebRTC initialization?",
    "options": {
      "A": "POST /v1/realtime/sessions",
      "B": "POST /v1/realtime/client_secrets",
      "C": "GET /v1/keys/temporary",
      "D": "POST /v1/chat/completions/voice_key"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO built-in tools that can be called directly via the Responses API without external implementation:",
    "options": {
      "A": "Web Search",
      "B": "File Search (Vector Store based)",
      "C": "SQL Executor",
      "D": "Email Sender"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The 'o4-mini' model (released April 2025) provides reasoning capabilities that exceed GPT-4o while maintaining the pricing structure of previous 'mini' models.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of the 'Agents SDK' launched by OpenAI in late 2025?",
    "options": {
      "A": "To replace the Python programming language for AI.",
      "B": "An orchestration framework that provides Tracing, ChatKit, and multi-agent handoff logic to build complex production-grade AI systems.",
      "C": "To allow AI models to run locally on the user's hardware.",
      "D": "To provide a marketplace for buying and selling custom GPTs."
    },
    "answer": "B"
  },
  {
    "question": "Which protocol is utilized for 'SIP Connection' in the OpenAI Realtime API to enable direct VoIP telephony integrations?",
    "options": {
      "A": "WebSocket Secure (WSS)",
      "B": "Session Initiation Protocol (SIP)",
      "C": "Direct Fiber Link",
      "D": "FTP"
    },
    "answer": "B"
  },
  {
    "question": "What happens if a request exceeds the model’s context window?",
    "options": {
      "A": "Request is auto-summarized",
      "B": "Oldest tokens are dropped",
      "C": "The request fails or is truncated",
      "D": "Model switches automatically"
    },
    "answer": "C"
  },
  {
    "question": "True or False: Both prompt and response tokens count toward the context limit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO strategies reduce OpenAI API costs?",
    "options": {
      "A": "Prompt compression",
      "B": "Response length limits",
      "C": "Higher temperature",
      "D": "More system messages"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is prompt injection?",
    "options": {
      "A": "Adding embeddings to prompts",
      "B": "Malicious user input altering model behavior",
      "C": "Increasing context size",
      "D": "Token overflow"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Prompt injection can affect tool calls.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO practices help mitigate prompt injection?",
    "options": {
      "A": "Input sanitization",
      "B": "Strong system prompts",
      "C": "Higher temperature",
      "D": "Longer outputs"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a system message used for?",
    "options": {
      "A": "Billing control",
      "B": "Setting model behavior and rules",
      "C": "Reducing latency",
      "D": "Token compression"
    },
    "answer": "B"
  },
  {
    "question": "True or False: System messages override user messages.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO roles exist in structured conversations?",
    "options": {
      "A": "system",
      "B": "user",
      "C": "admin",
      "D": "scheduler"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is deterministic output best achieved with?",
    "options": {
      "A": "High temperature",
      "B": "temperature = 0",
      "C": "High top_p",
      "D": "Streaming enabled"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Deterministic outputs guarantee factual correctness.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does exponential backoff handle?",
    "options": {
      "A": "Token overflow",
      "B": "Rate limit errors",
      "C": "Model hallucination",
      "D": "Prompt injection"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO HTTP status codes are commonly returned for rate limiting?",
    "options": {
      "A": "429",
      "B": "503",
      "C": "200",
      "D": "401"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Retrying immediately after a 429 error is recommended.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is response validation?",
    "options": {
      "A": "Checking grammar",
      "B": "Ensuring output conforms to expected schema",
      "C": "Reducing token count",
      "D": "Embedding verification"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO outputs benefit most from validation?",
    "options": {
      "A": "JSON",
      "B": "Tool calls",
      "C": "Free text",
      "D": "Poetry"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Validation should be done client-side.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a hallucination in OpenAI API outputs?",
    "options": {
      "A": "Creative writing",
      "B": "Confident but incorrect information",
      "C": "Long responses",
      "D": "High temperature output"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques reduce hallucinations?",
    "options": {
      "A": "Grounding with context",
      "B": "Tool usage",
      "C": "Higher temperature",
      "D": "Longer prompts only"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The Moderation API can be used before and after generation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is one-shot prompting?",
    "options": {
      "A": "No examples",
      "B": "Single example in prompt",
      "C": "Multiple examples",
      "D": "Streaming output"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO prompting styles improve consistency?",
    "options": {
      "A": "Few-shot prompting",
      "B": "Clear instructions",
      "C": "Random examples",
      "D": "High temperature"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Few-shot prompting increases token usage.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
   {
    "question": "What is the main purpose of request idempotency in OpenAI APIs?",
    "options": {
      "A": "Improve latency",
      "B": "Prevent duplicate operations on retries",
      "C": "Reduce token usage",
      "D": "Increase throughput"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Idempotency keys are useful when retrying failed requests.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO failures should be retried safely?",
    "options": {
      "A": "Network timeouts",
      "B": "429 rate limit errors",
      "C": "Invalid API key",
      "D": "Malformed JSON"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is cold start latency?",
    "options": {
      "A": "Delay caused by model warm-up",
      "B": "Tokenization overhead",
      "C": "High temperature output",
      "D": "Streaming delay"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Cold starts are more noticeable in serverless deployments.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO metrics are critical for monitoring OpenAI API usage?",
    "options": {
      "A": "Latency",
      "B": "Token consumption",
      "C": "Prompt creativity",
      "D": "Grammar accuracy"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is observability in AI systems?",
    "options": {
      "A": "Model explainability only",
      "B": "Ability to monitor, trace, and debug systems",
      "C": "Prompt tuning",
      "D": "Token compression"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Logs alone are sufficient for full observability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO observability signals are commonly used?",
    "options": {
      "A": "Logs",
      "B": "Metrics",
      "C": "Prompts",
      "D": "Embeddings"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is prompt versioning?",
    "options": {
      "A": "Storing prompt history",
      "B": "Managing changes to prompts over time",
      "C": "Increasing context length",
      "D": "Embedding prompts"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Prompt versioning helps with rollback during failures.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO practices support safe prompt versioning?",
    "options": {
      "A": "A/B testing",
      "B": "Change logs",
      "C": "Random edits",
      "D": "Hardcoding prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is data residency concern in OpenAI API usage?",
    "options": {
      "A": "Token pricing",
      "B": "Where data is processed and stored",
      "C": "Model size",
      "D": "Prompt length"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Data residency requirements vary by region.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO steps help meet compliance requirements?",
    "options": {
      "A": "Data minimization",
      "B": "Access control",
      "C": "Higher temperature",
      "D": "Streaming outputs"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is shadow testing?",
    "options": {
      "A": "Testing with fake users",
      "B": "Sending production traffic to a new version without affecting users",
      "C": "Offline prompt testing",
      "D": "Unit testing prompts"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Shadow testing helps detect regressions safely.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is fallback strategy in OpenAI-powered systems?",
    "options": {
      "A": "Using longer prompts",
      "B": "Switching to alternative logic when API fails",
      "C": "Increasing max_tokens",
      "D": "Retrying infinitely"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO fallback options are common?",
    "options": {
      "A": "Cached responses",
      "B": "Rule-based logic",
      "C": "Higher temperature",
      "D": "Streaming mode"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Fallback strategies improve system reliability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is prompt leakage?",
    "options": {
      "A": "Losing tokens",
      "B": "Exposure of system or hidden prompts",
      "C": "Embedding failure",
      "D": "Streaming bug"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO practices reduce prompt leakage?",
    "options": {
      "A": "Strict role separation",
      "B": "Output filtering",
      "C": "Longer prompts",
      "D": "Higher top_p"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Prompt leakage is a security concern.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "OpenAI has announced the deprecation of the Assistants API in favor of the Responses API. What is the final shutdown date for the Assistants API?",
    "options": {
      "A": "August 26, 2026",
      "B": "December 31, 2025",
      "C": "January 1, 2027",
      "D": "June 15, 2026"
    },
    "answer": "A"
  },
  {
    "question": "In the new Responses API, what replaces 'Threads' as the primary mechanism for maintaining conversation state?",
    "options": {
      "A": "Session Tokens",
      "B": "Conversations (v1/conversations)",
      "C": "Prompt Contexts",
      "D": "Memory Clusters"
    },
    "answer": "B"
  },
  {
    "question": "When using o3-mini, the 'reasoning_effort' parameter allows developers to choose between which three levels?",
    "options": {
      "A": "fast, balanced, thorough",
      "B": "low, medium, high",
      "C": "draft, standard, expert",
      "D": "minimal, optimized, maximal"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o3-mini' model with 'high' reasoning effort is specifically designed to outperform o1-mini in STEM tasks while maintaining similar latency.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In the OpenAI Agents SDK (released March 2025), what are 'Handoffs' used for?",
    "options": {
      "A": "Transferring the API key from one developer to another.",
      "B": "Allowing one specialized agent to delegate a task to another agent better suited for the query without manual state wiring.",
      "C": "Moving a model from a testing environment to production.",
      "D": "Passing audio data to a text-to-speech engine."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary architectural benefit of the 'Responses API' compared to the older 'Assistants API'?",
    "options": {
      "A": "It requires more API calls to ensure accuracy.",
      "B": "It consolidates complex multi-step workflows (messages, runs, tool outputs) into a single, unified request/response loop.",
      "C": "It removes support for Python tools.",
      "D": "It only works with small models like GPT-4o-mini."
    },
    "answer": "B"
  },
  {
    "question": "Which security feature in the OpenAI Enterprise Dashboard allows admins to detect 'Shadow AI' usage within their organization?",
    "options": {
      "A": "Prompt Firewall",
      "B": "Discovery & Domain Verification",
      "C": "Token Scrubber",
      "D": "Identity Shield"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o3-deep-research' model is a specialized version of the o3 series optimized for long-horizon tasks and cross-referencing vast amounts of documentation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In the context of the Realtime API, what does the 'unified interface' (WebRTC) allow you to skip compared to the WebSocket implementation?",
    "options": {
      "A": "You no longer need an API key.",
      "B": "You don't have to manually handle granular audio buffer events; the WebRTC peer connection handles the media stream automatically.",
      "C": "You can use the API without an internet connection.",
      "D": "It removes the need for a server-side backend entirely."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Guardrails' in the OpenAI Agents SDK?",
    "options": {
      "A": "To increase the model's speed.",
      "B": "To provide input and output validation checks that run in parallel with the agent, failing fast if safety or logic constraints are violated.",
      "C": "To prevent the user from seeing the model's thinking tokens.",
      "D": "To encrypt the conversation history."
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI API feature enables 'Project-based' access control, allowing teams to isolate API keys and usage tracking by specific internal projects?",
    "options": {
      "A": "OpenAI Projects & RBAC",
      "B": "Team Threads",
      "C": "Organization Units",
      "D": "Billing Silos"
    },
    "answer": "A"
  },
  {
    "question": "When migrating a 'Thread' to a 'Conversation', which parameter must be set to 'true' to ensure session persistence across multiple Responses API calls?",
    "options": {
      "A": "persist: true",
      "B": "store: true",
      "C": "save_history: true",
      "D": "remember: true"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o1-pro' model in the API allows for 'high' reasoning effort by default and is restricted to Tier 5 developers due to its high compute requirements.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does 'Tracing' in the Agents SDK provide to developers?",
    "options": {
      "A": "A way to trace the physical location of the OpenAI data center.",
      "B": "A comprehensive record of LLM generations, tool calls, handoffs, and guardrail triggers for debugging and optimization.",
      "C": "A method for tracing the origin of the training data.",
      "D": "A tool for drawing diagrams of the agent's logic."
    },
    "answer": "B"
  },
  {
    "question": "Which API endpoint is used to generate an ephemeral token for a client-side Realtime session using the 'unified interface'?",
    "options": {
      "A": "/v1/realtime/sessions",
      "B": "/v1/realtime/calls",
      "C": "/v1/tokens/ephemeral",
      "D": "/v1/chat/completions/voice"
    },
    "answer": "B"
  },
  {
    "question": "Which specific model should be used in the Responses API to conduct autonomous, multi-step web research and generate comprehensive analyst-level reports?",
    "options": {
      "A": "gpt-4o-research",
      "B": "o3-deep-research",
      "C": "o1-preview-web",
      "D": "gpt-5-analyst"
    },
    "answer": "B"
  },
  {
    "question": "In the OpenAI Realtime API's 'unified interface' (WebRTC), what is the purpose of the '/v1/realtime/calls' endpoint?",
    "options": {
      "A": "To record phone calls made by the AI.",
      "B": "To initialize a session by exchanging SDP (Session Description Protocol) data directly between the client/server and OpenAI.",
      "C": "To pay for the minutes used during a voice session.",
      "D": "To list all active voice sessions in an organization."
    },
    "answer": "B"
  },
  {
    "question": "When using the OpenAI Agents SDK, what is a 'Handoff' primitive designed to do?",
    "options": {
      "A": "Switch the API key from a trial to a paid version.",
      "B": "Enable a specialist agent to transfer the entire conversation state and control to another agent without manual developer intervention.",
      "C": "Move the model weights from the GPU to the CPU.",
      "D": "Send a summary of the chat to the user's email."
    },
    "answer": "B"
  },
  {
    "question": "How do 'Guardrails' in the OpenAI Agents SDK differ from standard system prompts?",
    "options": {
      "A": "Guardrails are only used for image generation.",
      "B": "Guardrails are separate, parallel checks that run on inputs or outputs and can 'trip' (halt the run) if specific safety or logic violations are detected.",
      "C": "Guardrails are translated into multiple languages automatically.",
      "D": "Guardrails cannot be bypassed by the model, whereas prompts can."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o3-mini' model supports the 'reasoning_effort' parameter (low, medium, high), but it does not support 'temperature' or 'top_p' as these are managed by its internal reasoning loop.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Background Mode' in the context of the o3-deep-research model?",
    "options": {
      "A": "A mode that allows the model to work while the user is sleeping.",
      "B": "A feature that executes long-running research tasks (which can take minutes) asynchronously to prevent HTTP timeouts and connectivity issues.",
      "C": "Changing the color of the model's interface.",
      "D": "A way to hide the model's activities from the admin dashboard."
    },
    "answer": "B"
  },
  {
    "question": "Which parameter allows you to limit the cost and depth of an o3-deep-research task by capping the number of external tools it can use?",
    "options": {
      "A": "max_budget",
      "B": "max_tool_calls",
      "C": "search_limit",
      "D": "stop_after_steps"
    },
    "answer": "B"
  },
  {
    "question": "Identify the primary benefit of 'Semantic VAD' (Voice Activity Detection) in the 2026 Realtime API:",
    "options": {
      "A": "It translates the user's voice in real-time.",
      "B": "It uses the model's understanding of sentence structure and intent to know when a user is done speaking, significantly reducing accidental interruptions.",
      "C": "It removes background music from the audio stream.",
      "D": "It identifies the specific person speaking by their voiceprint."
    },
    "answer": "B"
  },
  {
    "question": "In the Agents SDK, which component is responsible for persisting conversation history without manual 'Thread' management?",
    "options": {
      "A": "AgentLoop",
      "B": "Sessions (e.g., SQLiteSession or Conversations API)",
      "C": "MemoryManager",
      "D": "HistoryHub"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'o1-pro' is a high-compute version of the o1 model that is optimized for solving PhD-level science and research-level mathematics problems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which specific OpenAI model is designed to handle long-horizon research tasks by autonomously navigating the web and synthesizing multi-step findings into a report?",
    "options": {
      "A": "gpt-5.2-instant",
      "B": "o3-deep-research",
      "C": "o1-pro-mode",
      "D": "gpt-4o-realtime"
    },
    "answer": "B"
  },
  {
    "question": "When migrating from the deprecated Assistants API to the Responses API, what is the primary structural change regarding 'Threads'?",
    "options": {
      "A": "Threads are renamed to 'Streams' and require manual polling.",
      "B": "Threads are replaced by 'Conversations' (v1/conversations), which store generalized 'items' like messages, tool calls, and outputs.",
      "C": "Threads are now handled entirely on the client-side via LocalStorage.",
      "D": "Threads are deprecated without a replacement; state must be passed in every request."
    },
    "answer": "B"
  },
  {
    "question": "In the o3-series models, the 'reasoning_effort' parameter allows a developer to select between which levels?",
    "options": {
      "A": "light, standard, extended",
      "B": "low, medium, high",
      "C": "draft, analyst, expert",
      "D": "fast, balanced, thorough"
    },
    "answer": "B"
  },
  {
    "question": "The OpenAI Agents SDK (2025/2026) uses which primitive to delegate a task from a 'triage agent' to a 'specialist agent'?",
    "options": {
      "A": "Function Call",
      "B": "Handoff",
      "C": "Sub-routine",
      "D": "Model Swap"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of 'Guardrails' within the OpenAI Agents SDK orchestration?",
    "options": {
      "A": "To increase the model's token generation speed.",
      "B": "To run parallel validation checks on inputs and outputs, allowing the system to 'fail fast' if safety or logic policies are violated.",
      "C": "To encrypt the conversation history at rest.",
      "D": "To prevent the model from using more than one tool at a time."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o1-pro' model in the API is restricted to Tier 5 developers and provides a version of o1 that uses enhanced compute for research-grade accuracy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Unified Interface' for the OpenAI Realtime API?",
    "options": {
      "A": "A single UI dashboard for all OpenAI models.",
      "B": "A WebRTC-based connection method that simplifies session initialization by using a standard API key on the backend to facilitate a client-side peer connection.",
      "C": "An API that combines text, image, and video generation into one endpoint.",
      "D": "A hardware-only interface for specialized AI servers."
    },
    "answer": "B"
  },
  {
    "question": "Which API endpoint is used to exchange Session Description Protocol (SDP) data when initializing a WebRTC session via the Unified Interface?",
    "options": {
      "A": "/v1/realtime/sessions",
      "B": "/v1/realtime/calls",
      "C": "/v1/realtime/connect",
      "D": "/v1/chat/completions/webrtc"
    },
    "answer": "B"
  },
  {
    "question": "In the context of the 2026 'Lockdown Mode' safety update, what does an 'Elevated Risk' label indicate?",
    "options": {
      "A": "The user's credit card is about to expire.",
      "B": "A prompt has been flagged by safety classifiers as having a high probability of violating content policies, requiring stricter output constraints.",
      "C": "The server's physical temperature is too high.",
      "D": "The model is currently over-capacity and may provide lower-quality answers."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of the 'Responses API' over the legacy Chat Completions API for building agents?",
    "options": {
      "A": "It is cheaper for small tasks.",
      "B": "It natively handles multi-step tool call loops (auto-executing tool outputs) and state management in a single Request/Response lifecycle.",
      "C": "It allows for unlimited output tokens.",
      "D": "It supports older models like GPT-3.5."
    },
    "answer": "B"
  },
  {
    "question": "Launched in February 2026, what is the primary capability of 'OpenAI Operator' compared to standard models?",
    "options": {
      "A": "It only works for voice-based customer support.",
      "B": "It is a full-stack orchestration layer designed to autonomously navigate software interfaces, manage databases, and execute multi-step business logic across different applications.",
      "C": "It is a specialized model for generating 4K video from text.",
      "D": "It acts as a human moderator for chat rooms."
    },
    "answer": "B"
  },
  {
    "question": "When using the o3-deep-research model, which parameter must be set to 'True' to prevent timeouts during long-running (multi-minute) research tasks?",
    "options": {
      "A": "async_mode",
      "B": "background",
      "C": "persist_session",
      "D": "stream_research"
    },
    "answer": "B"
  },
  {
    "question": "In the OpenAI Agents SDK, what is the purpose of a 'Tripwire' in a Guardrail configuration?",
    "options": {
      "A": "To speed up the model's inference by 2x.",
      "B": "To trigger an immediate exception and halt the agentic loop if a safety violation or logical boundary (e.g., off-topic query) is detected.",
      "C": "To record the physical location of the user.",
      "D": "To automatically clear the conversation history."
    },
    "answer": "B"
  },
  {
    "question": "Which specific tool is mandatory when calling the 'o3-deep-research' model via the Responses API?",
    "options": {
      "A": "code_interpreter",
      "B": "web_search (or web_search_preview)",
      "C": "dalle_3",
      "D": "file_storage"
    },
    "answer": "B"
  },
  {
    "question": "OpenAI recently announced the 'SaaSpocalypse' update for enterprise customers. What does the 'Operator' agent use to interact with third-party SaaS tools?",
    "options": {
      "A": "Manual mouse clicking on a virtual desktop.",
      "B": "Computer Use primitives and specialized MCP (Model Context Protocol) connectors to securely interface with software APIs and UIs.",
      "C": "A shared password database.",
      "D": "It requires the software to be rewritten in Python."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Deliberative Alignment' as applied to the o3-series models?",
    "options": {
      "A": "A method to make the model slower on purpose to save costs.",
      "B": "Training the model to reason about human-written safety specifications and ethical guidelines internally before generating a final response.",
      "C": "Ensuring the model always agrees with the user's opinion.",
      "D": "A way to force the model to use more tokens."
    },
    "answer": "B"
  },
  {
    "question": "In the OpenAI Agents SDK, what is the role of the 'Runner' object?",
    "options": {
      "A": "To physically move data between servers.",
      "B": "To manage the execution loop of an agent, handling tool calls, handoffs, and context persistence automatically.",
      "C": "To track the developer's typing speed.",
      "D": "To act as a firewall for the API key."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO types of guardrails available in the 2026 Agents SDK:",
    "options": {
      "A": "Input Guardrails (validated before processing)",
      "B": "Output Guardrails (validated before responding)",
      "C": "Hardware Guardrails (thermal protection)",
      "D": "Financial Guardrails (automatic bank transfers)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does the 'MCP' (Model Context Protocol) allow the o3-deep-research model to do?",
    "options": {
      "A": "Change its own programming language.",
      "B": "Securely query private organizational knowledge stores and 3rd-party services as if they were native model tools.",
      "C": "Compress its neural network into a smaller size.",
      "D": "Connect directly to the user's brain."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'o4-mini' and 'o4-mini-deep-research' models (released late 2025) are designed to provide GPT-4o-level intelligence with the latency and cost structure of previous 'mini' versions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Launched in February 2026, which model is the first to combine Codex and GPT-5 training stacks for 'general-purpose coding agent' capabilities?",
    "options": {
      "A": "GPT-5.1-Turbo",
      "B": "GPT-5.3-Codex",
      "C": "o3-mini-coder",
      "D": "GPT-4.5-Codex"
    },
    "answer": "B"
  },
  {
    "question": "In the February 2026 update for reasoning models, which 'thinking_level' setting provides the deepest reasoning for complex problems at the cost of higher latency?",
    "options": {
      "A": "Light",
      "B": "Standard",
      "C": "Extended",
      "D": "Maximal"
    },
    "answer": "C"
  },
  {
    "question": "What is the primary purpose of the 'OpenAI Operator' (research preview 2025/2026)?",
    "options": {
      "A": "To act as a human-in-the-loop moderator for API calls.",
      "B": "To autonomously execute multi-step tasks within a web browser, such as booking reservations and orchestrating schedules.",
      "C": "To manage the physical cooling systems of OpenAI data centers.",
      "D": "To provide real-time translation for international phone calls."
    },
    "answer": "B"
  },
  {
    "question": "When using the new 'Responses API', which status indicates the model is waiting for a developer to provide tool outputs (formerly 'requires_action' in Assistants)?",
    "options": {
      "A": "waiting_on_tools",
      "B": "requires_output",
      "C": "tool_pending",
      "D": "awaiting_developer"
    },
    "answer": "B"
  },
  {
    "question": "True or False: As of February 2026, ChatGPT Thinking models support a total context window of 256k tokens (128k input and 128k max output).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'js_repl' experimental feature in the 2026 API allow an agent to do?",
    "options": {
      "A": "Translate JavaScript code into Python.",
      "B": "Persist state across different tool calls using a JavaScript REPL runtime.",
      "C": "Encrypt the API responses using a Node.js library.",
      "D": "Host a website directly from the OpenAI servers."
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI security feature introduced in 2026 allows for 'sandboxing' and protection against URL-based data exfiltration in agentic workflows?",
    "options": {
      "A": "Lockdown Mode",
      "B": "Firewall v2",
      "C": "Safety Tunnel",
      "D": "Agent Shield"
    },
    "answer": "A"
  },
  {
    "question": "In the context of 'OpenAI Operator', what is the function of the 'Accounts Websites' tab?",
    "options": {
      "A": "To track the developer's billing history.",
      "B": "To securely manage and store credentials for websites where the AI performs authenticated actions like logging in.",
      "C": "To list the websites used for the model's training data.",
      "D": "To provide a list of recommended AI tools for users."
    },
    "answer": "B"
  },
  {
    "question": "Which parameter in the 2026 API response indicates a 40% to 80% improvement in internal cache utilization compared to Chat Completions?",
    "options": {
      "A": "cache_boost",
      "B": "usage.prompt_tokens_cached",
      "C": "efficiency_index",
      "D": "tokens_saved"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Interactive Code Blocks' in the 2026 ChatGPT/API ecosystem?",
    "options": {
      "A": "A way to play games inside the code editor.",
      "B": "An interface that allows writing, editing, and previewing diagrams or mini-apps in real-time within the chat.",
      "C": "A feature that makes code blocks change color based on the model's mood.",
      "D": "A tool that translates code into voice commands."
    },
    "answer": "B"
  },
  {
    "question": "Launched in February 2026, what is the primary architectural shift in GPT-5.3-Codex compared to previous coding models?",
    "options": {
      "A": "It uses a larger vocabulary of 500k tokens.",
      "B": "It merges the 'coding agent' and 'reasoning LLM' stacks into a single unified model, enabling it to understand professional work context alongside code.",
      "C": "It is an encoder-only model designed for faster compilation.",
      "D": "It requires a separate GPU for the code execution environment."
    },
    "answer": "B"
  },
  {
    "question": "In the new Responses API, which parameter is used to maintain session persistence, effectively replacing the 'Thread ID' from the Assistants API?",
    "options": {
      "A": "session_id",
      "B": "conversation_id",
      "C": "persist_state: true",
      "D": "thread_context"
    },
    "answer": "B"
  },
  {
    "question": "When using the o3-mini model, which 'reasoning_effort' setting is recommended for real-time customer support bots to balance speed and accuracy?",
    "options": {
      "A": "low",
      "B": "medium",
      "C": "high",
      "D": "maximal"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Real-Time Steering' in the GPT-5.3-Codex API/App?",
    "options": {
      "A": "Changing the model's temperature while it is generating text.",
      "B": "The ability for a developer to intervene, ask questions, or provide feedback mid-task while the agent is executing long-running code.",
      "C": "Moving the model weights between different cloud regions during inference.",
      "D": "Using a joystick to control the AI's cursor."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'Responses API' consolidates the multi-step 'Thread -> Message -> Run -> Status Check' loop of the Assistants API into a single, unified request/response.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of the 'Computer-Using Agent' (CUA) model that powers OpenAI Operator?",
    "options": {
      "A": "To translate legacy COBOL code into Python.",
      "B": "To interpret graphical user interfaces (GUIs) and perform actions like clicking and typing across various web and desktop applications.",
      "C": "To manage the hardware cooling systems in OpenAI data centers.",
      "D": "To act as a firewall for incoming API requests."
    },
    "answer": "B"
  },
  {
    "question": "In the context of the 2026 'Lockdown Mode' update, what happens when a prompt is labeled as 'Elevated Risk'?",
    "options": {
      "A": "The user's account is immediately banned.",
      "B": "The model activates a specialized defensive stack designed to prevent adversarial prompt injection and data exfiltration.",
      "C": "The API request is routed to a human moderator for review.",
      "D": "The model provides a response in encrypted code only."
    },
    "answer": "B"
  },
  {
    "question": "Which benchmark saw a significant 26.5% jump with the release of GPT-5.3-Codex due to its improved visual desktop navigation?",
    "options": {
      "A": "MMLU",
      "B": "OSWorld-Verified",
      "C": "HumanEval",
      "D": "GSM8K"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'store: true' parameter do in a Responses API call?",
    "options": {
      "A": "It saves the model's weights to the local disk.",
      "B": "It enables session persistence, allowing the conversation to be continued in future calls using a conversation_id.",
      "C": "It purchases extra tokens for the user's account.",
      "D": "It stores the output in a public GitHub repository."
    },
    "answer": "B"
  },
  {
    "question": "Which OpenAI safety framework classifies GPT-5.3-Codex as its first 'High capability' model in the Cybersecurity domain?",
    "options": {
      "A": "Safety First Initiative",
      "B": "Preparedness Framework",
      "C": "Guardrail Protocol",
      "D": "Ethical AI Charter"
    },
    "answer": "B"
  },
  {
    "question": "Launched in February 2026, what is the 'step-change' capability of GPT-5.3-Codex compared to earlier code generation models?",
    "options": {
      "A": "It can only write code in Python and JavaScript.",
      "B": "It shifts from a code generator to a 'general-purpose coding agent' that autonomously handles end-to-end tasks like debugging and updating documentation.",
      "C": "It requires a human to verify every line of code before execution.",
      "D": "It is a specialized model for generating 3D game assets only."
    },
    "answer": "B"
  },
  {
    "question": "In the new Responses API, which parameter replaced the 'Thread' as the mechanism for managing durable conversation state?",
    "options": {
      "A": "context_id",
      "B": "conversation_id",
      "C": "session_persistence",
      "D": "history_token"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'reasoning_effort' parameter in models like o3-mini and GPT-5?",
    "options": {
      "A": "To set the physical temperature of the server.",
      "B": "To control the 'thinking time' (low, medium, high) the model spends on internal deliberation before generating a response.",
      "C": "To determine the number of GPUs used for a single request.",
      "D": "To adjust the font size of the output text."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The Assistants API is scheduled to be fully retired on August 26, 2026, in favor of the more flexible Responses API.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'GPT-5.3-Codex-Spark' designed for?",
    "options": {
      "A": "Offline data analysis on massive datasets.",
      "B": "Ultra-low latency, real-time interactive coding collaboration, delivering over 1000 tokens per second.",
      "C": "Generating high-resolution video from text prompts.",
      "D": "Protecting models from physical hardware theft."
    },
    "answer": "B"
  },
  {
    "question": "Which benchmark saw a massive 26.5% jump with GPT-5.3-Codex, indicating its superior ability to navigate visual desktop environments?",
    "options": {
      "A": "MMLU",
      "B": "OSWorld-Verified",
      "C": "GSM8K",
      "D": "HumanEval"
    },
    "answer": "B"
  },
]
    
      

def remove_duplicates(questions):
    seen = set()
    unique = []

    for q in questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique.append(q)

    return unique


def generate_pdf(skill_name, questions):
    doc = SimpleDocTemplate(
        f"{skill_name}_Question_Bank.pdf",
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{skill_name} Question Bank ({len(questions)} Questions)", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for i, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{i}. {q['question']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            elements.append(Paragraph(f"{key}) {value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "OpenAIAPIs"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
