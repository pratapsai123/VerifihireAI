from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is Generative AI?",
    "options": {
      "A": "AI that classifies data",
      "B": "AI that generates new data similar to training data",
      "C": "AI that only performs predictions",
      "D": "AI that stores data"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Generative AI models can create text, images, audio, and code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are examples of Generative AI models?",
    "options": {
      "A": "GANs",
      "B": "Transformers",
      "C": "Logistic Regression",
      "D": "K-Means"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the main goal of a Generative Adversarial Network (GAN)?",
    "options": {
      "A": "Minimize classification error",
      "B": "Generate data indistinguishable from real data",
      "C": "Cluster unlabeled data",
      "D": "Reduce dimensionality"
    },
    "answer": "B"
  },
  {
    "question": "True or False: GANs consist of a generator and a discriminator.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components are part of a GAN?",
    "options": {
      "A": "Generator",
      "B": "Discriminator",
      "C": "Encoder",
      "D": "Optimizer"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a Large Language Model (LLM)?",
    "options": {
      "A": "A model trained only on images",
      "B": "A model trained on massive text data to generate language",
      "C": "A clustering algorithm",
      "D": "A rule-based system"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Transformers are the foundation of most modern LLMs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO tasks are commonly performed by LLMs?",
    "options": {
      "A": "Text summarization",
      "B": "Text generation",
      "C": "Image segmentation",
      "D": "Signal filtering"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is tokenization in Generative AI?",
    "options": {
      "A": "Encrypting data",
      "B": "Breaking text into smaller units",
      "C": "Training a model",
      "D": "Compressing files"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Tokens can represent words, subwords, or characters.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is prompt engineering?",
    "options": {
      "A": "Training models from scratch",
      "B": "Designing inputs to guide model outputs",
      "C": "Deploying models",
      "D": "Optimizing hardware"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques improve prompt effectiveness?",
    "options": {
      "A": "Few-shot prompting",
      "B": "Clear instructions",
      "C": "Random noise",
      "D": "Lower learning rate"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Few-shot prompting provides examples within the prompt.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is temperature in text generation?",
    "options": {
      "A": "Model training speed",
      "B": "Controls randomness of output",
      "C": "Dataset size",
      "D": "GPU usage"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Higher temperature increases output randomness.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO sampling methods are used in text generation?",
    "options": {
      "A": "Top-k sampling",
      "B": "Top-p (nucleus) sampling",
      "C": "Gradient descent",
      "D": "Backpropagation"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is hallucination in Generative AI?",
    "options": {
      "A": "High-quality output",
      "B": "Confident but incorrect output",
      "C": "Model optimization",
      "D": "Data augmentation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Hallucinations are a known limitation of LLMs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is fine-tuning?",
    "options": {
      "A": "Training a model from scratch",
      "B": "Adapting a pretrained model to a specific task",
      "C": "Reducing model size",
      "D": "Deploying models"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO benefits does fine-tuning provide?",
    "options": {
      "A": "Task specialization",
      "B": "Improved performance",
      "C": "Guaranteed fairness",
      "D": "Lower latency always"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Fine-tuning requires labeled data.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is transfer learning?",
    "options": {
      "A": "Moving data between servers",
      "B": "Reusing knowledge from one task to another",
      "C": "Model compression",
      "D": "Random initialization"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Most Generative AI models rely on transfer learning.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is an embedding in Generative AI?",
    "options": {
      "A": "A compressed numerical representation of data",
      "B": "A loss function",
      "C": "A deployment strategy",
      "D": "A training schedule"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO use cases rely heavily on embeddings?",
    "options": {
      "A": "Semantic search",
      "B": "Recommendation systems",
      "C": "Image resizing",
      "D": "File compression"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Embeddings capture semantic meaning.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In a Transformer model, what is the primary function of the 'Self-Attention' mechanism?",
    "options": {
      "A": "To compress the input text into a smaller file size.",
      "B": "To allow the model to weigh the importance of different words in a sequence regardless of their distance from each other.",
      "C": "To randomly shuffle tokens to improve learning.",
      "D": "To translate the text into multiple languages simultaneously."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Temperature' control in the context of LLM text generation?",
    "options": {
      "A": "The physical heat of the GPU during processing.",
      "B": "The randomness of the output; lower values make the model more deterministic, while higher values make it more creative.",
      "C": "The speed at which tokens are generated per second.",
      "D": "The maximum number of words allowed in a response."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Retrieval-Augmented Generation' (RAG)?",
    "options": {
      "A": "A method of training a model from scratch using only private data.",
      "B": "An architecture that retrieves relevant documents from an external knowledge base to provide context to the LLM before it generates a response.",
      "C": "A technique to speed up the model's inference time on mobile devices.",
      "D": "A way to generate images from text descriptions."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Few-Shot Prompting' involves providing the model with a few examples of the task within the prompt to guide its behavior.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of 'Positional Encoding' in a Transformer?",
    "options": {
      "A": "To identify the geographical location of the user.",
      "B": "To provide the model with information about the order of words in a sequence, since Transformers process tokens in parallel.",
      "C": "To define the font style of the output text.",
      "D": "To manage the memory allocation for each neuron."
    },
    "answer": "B"
  },
  {
    "question": "In LLM training, what is 'RLHF' (Reinforcement Learning from Human Feedback)?",
    "options": {
      "A": "A method where humans write all the code for the model.",
      "B": "A process where human rankings of model outputs are used to fine-tune the model to be more helpful, honest, and harmless.",
      "C": "A way to teach the model how to play video games.",
      "D": "A technique for compressing models to run on CPUs."
    },
    "answer": "B"
  },
  {
    "question": "What are 'Hallucinations' in Large Language Models?",
    "options": {
      "A": "When the model stops responding due to high traffic.",
      "B": "Instances where the model generates factually incorrect or nonsensical information with high confidence.",
      "C": "A visual glitch in the user interface.",
      "D": "When the model uses too many emojis in its response."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following describes 'Chain-of-Thought' (CoT) prompting?",
    "options": {
      "A": "Linking multiple LLMs together in a series.",
      "B": "Encouraging the model to break down complex problems into intermediate steps before providing a final answer.",
      "C": "Using a chain of keywords to bypass safety filters.",
      "D": "Generating a list of related ideas for a blog post."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Token' in the context of NLP and Generative AI?",
    "options": {
      "A": "A digital currency used to pay for API access.",
      "B": "The basic unit of text (words, sub-words, or characters) that the model processes.",
      "C": "A security key used for authentication.",
      "D": "A specific layer within the neural network."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Diffusion Models, like Stable Diffusion, work by gradually removing 'noise' from a random starting point to generate an image.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common open-source LLM families:",
    "options": {
      "A": "Llama (by Meta)",
      "B": "Mistral (by Mistral AI)",
      "C": "Excel (by Microsoft)",
      "D": "Photoshop (by Adobe)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the 'Context Window' of an LLM?",
    "options": {
      "A": "The size of the chat interface on the screen.",
      "B": "The maximum number of tokens the model can consider at one time (including input and output history).",
      "C": "The time frame during which the model was trained.",
      "D": "The number of users currently talking to the model."
    },
    "answer": "B"
  },
  {
    "question": "In Generative AI, what is 'Parameter-Efficient Fine-Tuning' (PEFT)?",
    "options": {
      "A": "A way to make the model run faster during inference.",
      "B": "Techniques like LoRA that allow fine-tuning of a model by updating only a small subset of parameters, saving time and compute.",
      "C": "Deleting parameters that the model doesn't use.",
      "D": "Adding more layers to the model during training."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Encoder' part of a Transformer-based model typically do?",
    "options": {
      "A": "Generates the final translated text.",
      "B": "Processes the input sequence to create a hidden representation that captures context and meaning.",
      "C": "Converts the output into a JPG image.",
      "D": "Manages the API connection to the server."
    },
    "answer": "B"
  },
  {
    "question": "What is 'System Prompt' (or System Message) used for?",
    "options": {
      "A": "To tell the user that the system is rebooting.",
      "B": "To set the overarching persona, behavior, and constraints of the AI assistant before the user interaction begins.",
      "C": "To update the operating system of the server.",
      "D": "To show the current CPU usage of the AI."
    },
    "answer": "B"
  },
   {
    "question": "What is Retrieval-Augmented Generation (RAG)?",
    "options": {
      "A": "Training models from scratch",
      "B": "Combining external knowledge retrieval with text generation",
      "C": "Compressing large models",
      "D": "Reducing hallucinations by temperature tuning"
    },
    "answer": "B"
  },
  {
    "question": "True or False: RAG helps reduce hallucinations in LLM outputs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components are essential in a RAG pipeline?",
    "options": {
      "A": "Vector database",
      "B": "Retriever",
      "C": "Optimizer",
      "D": "Data labeler"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a vector database primarily used for?",
    "options": {
      "A": "Storing raw text",
      "B": "Storing and searching embeddings",
      "C": "Training LLMs",
      "D": "Model deployment"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Cosine similarity is commonly used in vector search.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are popular vector databases?",
    "options": {
      "A": "FAISS",
      "B": "Pinecone",
      "C": "PostgreSQL",
      "D": "MongoDB"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is prompt chaining?",
    "options": {
      "A": "Training multiple models together",
      "B": "Breaking a task into sequential prompts",
      "C": "Increasing context length",
      "D": "Fine-tuning"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Prompt chaining helps solve complex multi-step tasks.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO benefits does prompt chaining provide?",
    "options": {
      "A": "Improved reasoning",
      "B": "Better control of output",
      "C": "Lower training cost",
      "D": "Faster GPU performance"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is chain-of-thought prompting?",
    "options": {
      "A": "A fine-tuning method",
      "B": "Encouraging models to reason step-by-step",
      "C": "A vector search technique",
      "D": "Model compression"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Chain-of-thought prompting can improve reasoning tasks.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is context window in LLMs?",
    "options": {
      "A": "Training time",
      "B": "Maximum number of tokens a model can process at once",
      "C": "Model depth",
      "D": "Embedding size"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Exceeding the context window can cause earlier information to be dropped.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO techniques help manage long contexts?",
    "options": {
      "A": "Chunking",
      "B": "Summarization",
      "C": "Higher temperature",
      "D": "Random sampling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is multimodal Generative AI?",
    "options": {
      "A": "Models trained on one data type",
      "B": "Models that handle multiple data types like text and images",
      "C": "Only image generation",
      "D": "Only audio generation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Multimodal models can accept both text and images as input.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are examples of multimodal tasks?",
    "options": {
      "A": "Image captioning",
      "B": "Visual question answering",
      "C": "Text classification",
      "D": "Clustering"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is diffusion in generative models?",
    "options": {
      "A": "Removing features",
      "B": "Gradually adding and removing noise to generate data",
      "C": "Compressing images",
      "D": "Tokenization"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Diffusion models are commonly used for image generation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO diffusion models are widely known?",
    "options": {
      "A": "Stable Diffusion",
      "B": "DALL·E",
      "C": "BERT",
      "D": "XGBoost"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is latent space?",
    "options": {
      "A": "Raw data space",
      "B": "Compressed representation where generation occurs",
      "C": "Deployment environment",
      "D": "Inference API"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Latent space enables interpolation between generated outputs.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is parameter-efficient fine-tuning (PEFT)?",
    "options": {
      "A": "Training all model parameters",
      "B": "Fine-tuning a small subset of parameters",
      "C": "Increasing model size",
      "D": "Training without data"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO PEFT techniques are commonly used?",
    "options": {
      "A": "LoRA",
      "B": "Adapters",
      "C": "Dropout",
      "D": "Batch normalization"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: PEFT reduces compute and memory requirements.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
  "question": "In the context of scaling laws for LLMs, what is the 'Chinchilla Optimal' point?",
    "options": {
      "A": "The point where the model reaches human-level reasoning.",
      "B": "The observation that for a fixed compute budget, model size and the number of training tokens should be scaled in equal proportions.",
      "C": "The maximum temperature a GPU can reach before performance throttles.",
      "D": "The optimal ratio of dropout to learning rate in a Transformer."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rotary Positional Embedding' (RoPE) and why is it preferred in models like Llama?",
    "options": {
      "A": "It rotates the tokens in a circle to save memory.",
      "B": "It encodes absolute position with a rotation matrix and naturally incorporates relative position, allowing for better context window extension.",
      "C": "It is a method of encrypting prompts before they reach the encoder.",
      "D": "It allows the model to process text from right-to-left more efficiently."
    },
    "answer": "B"
  },
  {
    "question": "Identify the primary mechanism of 'QLoRA' (Quantized LoRA):",
    "options": {
      "A": "It quantizes the entire model to 1-bit for mobile deployment.",
      "B": "It backpropagates gradients through a frozen, 4-bit quantized pretrained language model into Low-Rank Adapters (LoRA).",
      "C": "It removes 75% of the attention heads to speed up inference.",
      "D": "It uses a quantum computer to calculate the loss function."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'FlashAttention' improves performance by reducing the number of FLOPs required for the attention calculation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'KV Cache' (Key-Value Cache) and how does it optimize inference?",
    "options": {
      "A": "It is a database for storing user passwords.",
      "B": "It stores previously calculated Key and Value vectors for tokens in the prompt, avoiding redundant computations during auto-regressive decoding.",
      "C": "It is a cache for the most frequent search queries.",
      "D": "It caches the final output of the model to serve it faster to the next user."
    },
    "answer": "B"
  },
  {
    "question": "Which RAG optimization technique involves re-ranking the top-K retrieved documents using a cross-encoder before passing them to the LLM?",
    "options": {
      "A": "Vector Indexing",
      "B": "Reranking (Cross-encoding)",
      "C": "Query Expansion",
      "D": "Recursive Summarization"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Grouped-Query Attention' (GQA) achieve compared to Multi-Head Attention (MHA)?",
    "options": {
      "A": "It increases the number of parameters to improve reasoning.",
      "B": "It reduces memory bandwidth overhead by sharing keys and values across groups of query heads, offering a middle ground between MHA and MQA.",
      "C": "It allows the model to process multiple prompts simultaneously.",
      "D": "It forces the model to only use 4 attention heads at a time."
    },
    "answer": "B"
  },
  {
    "question": "In LLM training, what is 'Gradient Checkpointing' used for?",
    "options": {
      "A": "To save the model every 10 minutes in case of power failure.",
      "B": "To trade compute for memory by recomputing activations during the backward pass instead of storing them all.",
      "C": "To ensure the gradients never reach zero.",
      "D": "To verify the integrity of the training data."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Speculative Decoding'?",
    "options": {
      "A": "The model guessing the next word without looking at the context.",
      "B": "Using a smaller, faster draft model to generate candidate tokens, which are then verified in parallel by the larger target model.",
      "C": "Predicting the stock market using LLMs.",
      "D": "A way to generate text in a hidden 'speculative' layer before showing it to the user."
    },
    "answer": "B"
  },
  {
    "question": "In the 'Attention is All You Need' architecture, what is the purpose of the 'Scaled Dot-Product' in the attention score calculation?",
    "options": {
      "A": "To make the model run on larger screens.",
      "B": "To prevent the dot product from growing too large in magnitude, which would push the softmax function into regions with extremely small gradients.",
      "C": "To count the number of dots in the input text.",
      "D": "To multiply the weights by the learning rate."
    },
    "answer": "B"
  },
{
    "question": "What problem does exposure bias refer to in autoregressive language models?",
    "options": {
      "A": "Bias in training data",
      "B": "Mismatch between training with teacher forcing and inference generation",
      "C": "Overfitting to prompts",
      "D": "Gradient explosion"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Exposure bias can cause error accumulation during long text generation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO techniques help mitigate exposure bias?",
    "options": {
      "A": "Scheduled sampling",
      "B": "Reinforcement learning from human feedback",
      "C": "Tokenization",
      "D": "Dropout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is Reinforcement Learning from Human Feedback (RLHF)?",
    "options": {
      "A": "Supervised learning with labels",
      "B": "Optimizing model behavior using human preference signals",
      "C": "Training models with rewards only",
      "D": "Unsupervised fine-tuning"
    },
    "answer": "B"
  },
  {
    "question": "True or False: RLHF commonly uses a reward model trained on human comparisons.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components are essential in RLHF?",
    "options": {
      "A": "Reward model",
      "B": "Policy model",
      "C": "Vector database",
      "D": "Tokenizer"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is catastrophic forgetting in fine-tuned generative models?",
    "options": {
      "A": "Model forgetting old data due to small batch size",
      "B": "Loss of previously learned capabilities after fine-tuning",
      "C": "Overfitting during pretraining",
      "D": "Gradient vanishing"
    },
    "answer": "B"
  },
  {
    "question": "True or False: PEFT methods help reduce catastrophic forgetting.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO strategies reduce catastrophic forgetting?",
    "options": {
      "A": "Freezing base model weights",
      "B": "Adapter layers",
      "C": "Increasing temperature",
      "D": "Random initialization"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is alignment in Generative AI?",
    "options": {
      "A": "Aligning embeddings",
      "B": "Ensuring model behavior matches human values and intent",
      "C": "Reducing inference latency",
      "D": "Optimizing GPU usage"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Alignment is only a technical problem.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO risks arise from misaligned generative models?",
    "options": {
      "A": "Harmful outputs",
      "B": "Unintended behavior",
      "C": "Faster inference",
      "D": "Lower compute cost"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is prompt injection?",
    "options": {
      "A": "Embedding prompts in vectors",
      "B": "Manipulating prompts to bypass model safeguards",
      "C": "Prompt optimization technique",
      "D": "Model fine-tuning"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Prompt injection is a security concern in GenAI systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO defenses help mitigate prompt injection?",
    "options": {
      "A": "Input sanitization",
      "B": "Output filtering",
      "C": "Higher temperature",
      "D": "Larger context window"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is jailbreak prompting?",
    "options": {
      "A": "Optimizing prompts for speed",
      "B": "Attempts to bypass safety constraints",
      "C": "Few-shot prompting",
      "D": "Chain-of-thought prompting"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Jailbreak prompts exploit weaknesses in alignment mechanisms.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is evaluation leakage in Generative AI?",
    "options": {
      "A": "Training on test data",
      "B": "Using evaluation data during prompt tuning or fine-tuning",
      "C": "Overfitting embeddings",
      "D": "Model compression error"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO practices help avoid evaluation leakage?",
    "options": {
      "A": "Strict dataset separation",
      "B": "Blind evaluation",
      "C": "Higher learning rate",
      "D": "Prompt chaining"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Evaluation leakage inflates perceived model performance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is zero-shot generalization?",
    "options": {
      "A": "Training without data",
      "B": "Performing tasks without explicit task-specific examples",
      "C": "Fine-tuning with few samples",
      "D": "Model distillation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Large foundation models exhibit strong zero-shot capabilities.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO factors improve zero-shot performance?",
    "options": {
      "A": "Scale of pretraining data",
      "B": "Clear task instructions",
      "C": "Higher dropout",
      "D": "Random prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is model distillation in Generative AI?",
    "options": {
      "A": "Reducing model depth",
      "B": "Training a smaller model using a larger model’s outputs",
      "C": "Fine-tuning with labels",
      "D": "Vector compression"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Distillation can reduce inference cost while preserving performance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO challenges are common in Generative AI evaluation?",
    "options": {
      "A": "Subjectivity of outputs",
      "B": "Lack of ground truth",
      "C": "GPU memory limits",
      "D": "Tokenization speed"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the primary difference between 'ReAct' (Reason + Act) prompting and standard Chain-of-Thought (CoT)?",
    "options": {
      "A": "ReAct requires a larger GPU to run than CoT.",
      "B": "ReAct combines reasoning traces with task-specific actions, allowing the model to interact with external tools and update its reasoning based on observations.",
      "C": "CoT is only for math problems, while ReAct is only for coding.",
      "D": "ReAct removes the reasoning step to save tokens."
    },
    "answer": "B"
  },
  {
    "question": "In Vector Databases, what is the 'HNSW' (Hierarchical Navigable Small World) algorithm used for?",
    "options": {
      "A": "To compress text into a smaller format.",
      "B": "To perform efficient Approximate Nearest Neighbor (ANN) searches in high-dimensional vector spaces.",
      "C": "To encrypt the vectors for cloud storage.",
      "D": "To translate vectors back into human-readable text."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Function Calling' (or Tool Use) in an LLM API context?",
    "options": {
      "A": "The model physically calling a phone number.",
      "B": "The model's ability to output structured JSON that describes a function call, which the developer then executes to provide external data.",
      "C": "A way to call the OpenAI support team.",
      "D": "Defining variables inside the LLM's neural network."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Lost in the Middle' phenomenon refer to in long-context LLMs?",
    "options": {
      "A": "The model forgetting its own name.",
      "B": "The tendency of models to perform better when relevant information is at the very beginning or end of the input, while struggling with info in the middle.",
      "C": "A network error during data transmission.",
      "D": "The model's inability to generate text between 500 and 1000 tokens."
    },
    "answer": "B"
  },
  {
    "question": "In a RAG pipeline, what is 'Query Expansion' (or Hypothetical Document Embeddings - HyDE)?",
    "options": {
      "A": "Making the user's font larger in the UI.",
      "B": "Generating a pseudo-response or multiple variations of a query to improve the chances of retrieving high-quality, relevant documents.",
      "C": "Adding more documents to the vector database.",
      "D": "Storing the query history for analytics."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Semantic Chunking' strategy in RAG?",
    "options": {
      "A": "Breaking text into chunks of exactly 512 characters.",
      "B": "Splitting text based on meaning and context (e.g., at sentence or paragraph boundaries) rather than fixed character counts, ensuring cohesive retrieval.",
      "C": "Removing all adjectives from the text.",
      "D": "Translating chunks into different languages."
    },
    "answer": "B"
  },
  {
    "question": "Identify the primary benefit of 'Multi-Vector Retrieval':",
    "options": {
      "A": "It uses multiple GPUs to find one document.",
      "B": "It allows representing a single document with multiple vectors (e.g., summaries, sub-sections) to improve retrieval precision for diverse queries.",
      "C": "It doubles the speed of the internet connection.",
      "D": "It stores the same vector in three different databases."
    },
    "answer": "B"
  },
  {
    "question": "What is 'LLM-as-a-Judge' (or G-Eval)?",
    "options": {
      "A": "Using a lawyer to review model outputs.",
      "B": "Using a highly capable model (like GPT-4o) to evaluate the quality, coherence, and accuracy of another model's output based on a specific rubric.",
      "C": "The model's ability to provide legal advice.",
      "D": "A system where the model decides its own learning rate."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In 'Agentic Workflows', the LLM acts as the central controller, making iterative decisions on which tools to use and when to stop.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Embedding Model's' role in a GenAI system?",
    "options": {
      "A": "To host the model on a website.",
      "B": "To convert high-dimensional text data into numerical vectors that capture semantic meaning for search and retrieval.",
      "C": "To correct grammar in the final output.",
      "D": "To manage the user's session data."
    },
    "answer": "B"
  },
   {
    "question": "What is model collapse in Generative AI?",
    "options": {
      "A": "Sudden model failure during inference",
      "B": "Degradation of generative quality when models train on their own outputs",
      "C": "GPU memory overflow",
      "D": "Vanishing gradients"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Training generative models on synthetic data repeatedly can cause model collapse.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO practices help reduce model collapse?",
    "options": {
      "A": "Mixing real and synthetic data",
      "B": "Data provenance tracking",
      "C": "Increasing temperature",
      "D": "Prompt chaining"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is data provenance in Generative AI?",
    "options": {
      "A": "Data compression technique",
      "B": "Tracking the origin and transformation history of data",
      "C": "A training algorithm",
      "D": "A deployment strategy"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Data provenance supports auditability and trust.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is synthetic data?",
    "options": {
      "A": "Corrupted data",
      "B": "Artificially generated data resembling real data",
      "C": "Compressed datasets",
      "D": "Encrypted data"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO risks are associated with synthetic data?",
    "options": {
      "A": "Bias amplification",
      "B": "Loss of diversity",
      "C": "Guaranteed fairness",
      "D": "Lower storage cost"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Synthetic data always improves model generalization.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is controllable generation?",
    "options": {
      "A": "Limiting output length",
      "B": "Guiding generated content using constraints or attributes",
      "C": "Reducing randomness",
      "D": "Compressing outputs"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques enable controllable generation?",
    "options": {
      "A": "Conditional prompts",
      "B": "Control tokens",
      "C": "Random sampling",
      "D": "Dropout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Controllable generation is important for enterprise applications.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a foundation model?",
    "options": {
      "A": "A small task-specific model",
      "B": "A large pretrained model adaptable to many tasks",
      "C": "A rule-based system",
      "D": "A deployment framework"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Foundation models rely heavily on transfer learning.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO challenges are unique to foundation models?",
    "options": {
      "A": "High training cost",
      "B": "Alignment complexity",
      "C": "Simple deployment",
      "D": "Low inference cost"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is red teaming in Generative AI?",
    "options": {
      "A": "Optimizing training speed",
      "B": "Actively testing models for failures and harmful behavior",
      "C": "Model compression",
      "D": "Fine-tuning"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Red teaming is a proactive safety practice.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO goals does red teaming target?",
    "options": {
      "A": "Identify misuse risks",
      "B": "Find safety gaps",
      "C": "Improve GPU throughput",
      "D": "Reduce context length"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is watermarking in Generative AI?",
    "options": {
      "A": "Encrypting datasets",
      "B": "Embedding signals to identify AI-generated content",
      "C": "Reducing hallucinations",
      "D": "Optimizing prompts"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Watermarking can help detect AI-generated media.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO challenges exist with watermarking?",
    "options": {
      "A": "Robustness to modifications",
      "B": "Impact on output quality",
      "C": "Guaranteed legal compliance",
      "D": "Faster inference"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is model serving optimization?",
    "options": {
      "A": "Improving training accuracy",
      "B": "Reducing latency and cost during inference",
      "C": "Labeling data",
      "D": "Increasing dataset size"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques improve LLM serving efficiency?",
    "options": {
      "A": "Quantization",
      "B": "KV caching",
      "C": "Higher temperature",
      "D": "Prompt injection"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Quantization reduces model size with minimal accuracy loss.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is governance in Generative AI?",
    "options": {
      "A": "Improving creativity",
      "B": "Policies and controls over model development and usage",
      "C": "Optimizing embeddings",
      "D": "Training speed optimization"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO aspects are part of GenAI governance?",
    "options": {
      "A": "Compliance",
      "B": "Risk management",
      "C": "Prompt creativity",
      "D": "GPU scheduling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Governance becomes more critical as Generative AI scales.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "How do Vision-Language Models (VLMs) like GPT-4o typically process images?",
    "options": {
      "A": "They convert the image to text descriptions first using OCR.",
      "B": "They use a Vision Transformer (ViT) or similar encoder to convert image patches into visual tokens that are projected into the same embedding space as text tokens.",
      "C": "They treat the image as a single large token without internal structure.",
      "D": "They use a separate database of images to find the closest match to the user's prompt."
    },
    "answer": "B"
  },
  {
    "question": "In Diffusion models, what is the 'U-Net' architecture primarily used for?",
    "options": {
      "A": "To store the final image in a database.",
      "B": "To predict and remove the noise added to an image at each timestep during the reverse diffusion process.",
      "C": "To translate text prompts into different languages.",
      "D": "To increase the brightness of the generated pixels."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Jailbreak' in the context of LLM safety?",
    "options": {
      "A": "Breaking the physical server housing the AI.",
      "B": "The use of specific prompt engineering techniques (like 'DAN' or roleplay) to bypass a model's safety filters and ethical guardrails.",
      "C": "Updating the model's firmware to a newer version.",
      "D": "Connecting an offline LLM to the internet."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Correction' in an LLM agentic workflow?",
    "options": {
      "A": "The developer manually fixing the model's mistakes.",
      "B": "A process where the model reviews its own output or the results of its actions and iteratively refines the response to correct errors.",
      "C": "The model automatically deleting its own training data.",
      "D": "A system that forces the model to use fewer tokens."
    },
    "answer": "B"
  },
  {
    "question": "In Video Generation models (e.g., Sora), what is a 'Spacetime Patch'?",
    "options": {
      "A": "A physical patch applied to the GPU.",
      "B": "A 3D volume of video data (compressing both space and time) that is tokenized, allowing Transformers to process video similarly to text.",
      "C": "A way to fix glitches in the background of a video.",
      "D": "The frame rate of the generated video."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'LlamaGuard' or 'NeMo Guardrails'?",
    "options": {
      "A": "To make the model generate text faster.",
      "B": "To act as a programmable safety layer that monitors inputs and outputs for toxic, biased, or restricted content in real-time.",
      "C": "To manage the cloud billing for the AI system.",
      "D": "To provide a GUI for the model's parameters."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Cross-Attention' in Stable Diffusion allows the text prompt tokens to interact with the image latent representations to guide the generation process.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Constitutional AI' (pioneered by Anthropic)?",
    "options": {
      "A": "A model that only answers questions about the US Constitution.",
      "B": "A method of training models to follow a set of high-level principles (a 'constitution') during self-improvement and RLHF.",
      "C": "A law that governs how AI models are built.",
      "D": "An AI system that can vote in elections."
    },
    "answer": "B"
  },
  {
    "question": "Which metric is commonly used to evaluate the similarity between a generated image and the original data distribution?",
    "options": {
      "A": "F1-Score",
      "B": "Fréchet Inception Distance (FID)",
      "C": "ROUGE Score",
      "D": "BLEU Score"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Prompt Injection'?",
    "options": {
      "A": "Adding more RAM to the server to handle longer prompts.",
      "B": "An attack where a user provides input that tricks the LLM into executing unintended instructions or revealing sensitive data.",
      "C": "Translating a prompt into machine code.",
      "D": "Storing prompts in a SQL database."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Direct Preference Optimization' (DPO) aim to replace in the alignment process?",
    "options": {
      "A": "The Tokenizer.",
      "B": "The complex Reward Model training step in standard RLHF, allowing the model to learn directly from preference data.",
      "C": "The GPU drivers.",
      "D": "The vector database."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'ControlNet' is an extension for diffusion models that allows users to add extra conditions (like Canny edges or human poses) to control image structure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Multi-modal Fusion'?",
    "options": {
      "A": "Melting different types of hardware together.",
      "B": "The process of integrating information from different modalities (e.g., text, image, audio) into a single coherent representation.",
      "C": "Running two models at the same time on different servers.",
      "D": "Converting a model from Python to JavaScript."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Red Teaming' in Generative AI development?",
    "options": {
      "A": "Hiring people to wear red shirts while coding.",
      "B": "Adversarial testing where experts try to provoke the model into producing harmful or restricted content to identify vulnerabilities.",
      "C": "A method of coloring the model's output graphs.",
      "D": "A team-building exercise for data scientists."
    },
    "answer": "B"
  },
  {
    "question": "In Diffusion, what is the 'Latent Space'?",
    "options": {
      "A": "A space where the model weights are stored.",
      "B": "A compressed, lower-dimensional representation of an image where the diffusion process occurs (as in Stable Diffusion), saving compute.",
      "C": "The period of time the model is idle.",
      "D": "The empty space between neurons in a network."
    },
    "answer": "B"
  },
  {
    "question": "What is speculative decoding in LLM inference?",
    "options": {
      "A": "Generating random tokens",
      "B": "Using a smaller model to accelerate decoding of a larger model",
      "C": "Increasing temperature dynamically",
      "D": "Compressing embeddings"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Speculative decoding reduces latency without changing model quality.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO benefits does speculative decoding provide?",
    "options": {
      "A": "Lower inference latency",
      "B": "Reduced compute cost",
      "C": "Higher hallucination rate",
      "D": "Longer context window"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is KV cache in transformer models?",
    "options": {
      "A": "Training dataset cache",
      "B": "Cached key-value attention states for faster decoding",
      "C": "Embedding storage",
      "D": "Optimizer state"
    },
    "answer": "B"
  },
  {
    "question": "True or False: KV caching is primarily useful during training.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is long-context attention optimization?",
    "options": {
      "A": "Increasing batch size",
      "B": "Techniques to scale attention efficiently for long sequences",
      "C": "Token compression",
      "D": "Model distillation"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO methods help scale long-context attention?",
    "options": {
      "A": "Sparse attention",
      "B": "Sliding window attention",
      "C": "Full quadratic attention",
      "D": "Dropout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Quadratic attention limits maximum context length.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is instruction tuning?",
    "options": {
      "A": "Training with unlabeled data",
      "B": "Fine-tuning models on instruction–response pairs",
      "C": "Prompt chaining",
      "D": "Token pruning"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO outcomes result from instruction tuning?",
    "options": {
      "A": "Better task-following",
      "B": "Improved zero-shot behavior",
      "C": "Guaranteed factual accuracy",
      "D": "Reduced parameter count"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Instruction tuning is often combined with RLHF.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is reward hacking in RL-based GenAI systems?",
    "options": {
      "A": "Improving reward functions",
      "B": "Model exploiting reward signals in unintended ways",
      "C": "Human feedback optimization",
      "D": "Bias mitigation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Reward hacking indicates misaligned objectives.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO practices reduce reward hacking?",
    "options": {
      "A": "Robust reward design",
      "B": "Human-in-the-loop evaluation",
      "C": "Higher temperature",
      "D": "Random prompts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is prompt overfitting?",
    "options": {
      "A": "Overfitting during training",
      "B": "Prompts working only for specific wording",
      "C": "Excessive token generation",
      "D": "Context window overflow"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Prompt overfitting reduces generalization.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is self-consistency decoding?",
    "options": {
      "A": "Using a single deterministic output",
      "B": "Sampling multiple outputs and selecting the most consistent answer",
      "C": "Fine-tuning with labels",
      "D": "Reducing model size"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO tasks benefit most from self-consistency?",
    "options": {
      "A": "Reasoning tasks",
      "B": "Math problems",
      "C": "Image resizing",
      "D": "Data normalization"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Self-consistency increases inference cost.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is tool augmentation in LLM systems?",
    "options": {
      "A": "Adding more parameters",
      "B": "Allowing models to call external tools or APIs",
      "C": "Prompt compression",
      "D": "Embedding tuning"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO tools are commonly integrated with LLMs?",
    "options": {
      "A": "Search engines",
      "B": "Calculators",
      "C": "GPUs",
      "D": "Tokenizers"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Tool augmentation improves factual accuracy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is agentic Generative AI?",
    "options": {
      "A": "Single-step text generation",
      "B": "Models that plan, act, and use tools autonomously",
      "C": "Image-only generation",
      "D": "Static prompt execution"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO capabilities define agentic systems?",
    "options": {
      "A": "Planning",
      "B": "Tool usage",
      "C": "Tokenization",
      "D": "Dropout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Agentic systems increase complexity and risk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is Retrieval-Augmented Generation (RAG)?",
    "options": {
      "A": "Training LLMs with more parameters",
      "B": "Combining external knowledge retrieval with text generation",
      "C": "Fine-tuning models using reinforcement learning",
      "D": "Compressing prompts"
    },
    "answer": "B"
  },
  {
    "question": "True or False: RAG helps reduce hallucinations by grounding responses in retrieved data.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components are essential in a RAG pipeline?",
    "options": {
      "A": "Vector database",
      "B": "Retriever",
      "C": "Optimizer",
      "D": "Tokenizer"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is tokenization in LLMs?",
    "options": {
      "A": "Splitting text into semantic chunks",
      "B": "Converting text into numerical units called tokens",
      "C": "Removing stop words",
      "D": "Compressing text"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Tokenization is language-dependent.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does temperature control in text generation?",
    "options": {
      "A": "Model size",
      "B": "Randomness of token sampling",
      "C": "Context length",
      "D": "Inference speed"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO effects occur when temperature is increased?",
    "options": {
      "A": "More diverse outputs",
      "B": "More deterministic outputs",
      "C": "Higher creativity",
      "D": "Lower randomness"
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: A temperature of 0 makes the model fully deterministic.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is top-k sampling?",
    "options": {
      "A": "Sampling from all tokens",
      "B": "Sampling only from the k most probable tokens",
      "C": "Removing rare tokens",
      "D": "Increasing context window"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO sampling strategies help control randomness?",
    "options": {
      "A": "Top-k sampling",
      "B": "Top-p (nucleus) sampling",
      "C": "Batch normalization",
      "D": "Dropout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Top-p sampling adapts the number of candidate tokens dynamically.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is hallucination in Generative AI?",
    "options": {
      "A": "Creative storytelling",
      "B": "Generation of factually incorrect or unsupported content",
      "C": "Overfitting during training",
      "D": "High-temperature output"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques reduce hallucinations?",
    "options": {
      "A": "RAG",
      "B": "Tool augmentation",
      "C": "Higher temperature",
      "D": "Random sampling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Hallucinations can occur even in large, well-trained models.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is fine-tuning in Generative AI?",
    "options": {
      "A": "Training from scratch",
      "B": "Adjusting a pre-trained model on task-specific data",
      "C": "Prompt engineering",
      "D": "Inference optimization"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO risks are associated with fine-tuning?",
    "options": {
      "A": "Overfitting",
      "B": "Catastrophic forgetting",
      "C": "Improved generalization",
      "D": "Larger context window"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Fine-tuning always improves zero-shot performance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is context window in LLMs?",
    "options": {
      "A": "Training dataset size",
      "B": "Maximum number of tokens a model can process at once",
      "C": "Batch size",
      "D": "Embedding dimension"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors limit context window usage?",
    "options": {
      "A": "Memory constraints",
      "B": "Quadratic attention cost",
      "C": "Optimizer choice",
      "D": "Loss function"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Increasing context window always improves model accuracy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is parameter-efficient fine-tuning (PEFT) in Generative AI?",
    "options": {
      "A": "Training all model parameters",
      "B": "Fine-tuning only a small subset of parameters",
      "C": "Reducing dataset size",
      "D": "Increasing inference speed"
    },
    "answer": "B"
  },
  {
    "question": "True or False: LoRA (Low-Rank Adaptation) is a PEFT technique.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO advantages does PEFT provide?",
    "options": {
      "A": "Lower memory usage",
      "B": "Faster training",
      "C": "Guaranteed elimination of hallucinations",
      "D": "Unlimited context length"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is catastrophic forgetting in fine-tuned LLMs?",
    "options": {
      "A": "Loss of training data",
      "B": "Model forgetting previously learned knowledge",
      "C": "Increase in inference latency",
      "D": "Prompt overfitting"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Using adapters can help mitigate catastrophic forgetting.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  }
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
    skill = "GenerativeAI"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
