from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is MLOps primarily concerned with?",
    "options": {
      "A": "Model accuracy only",
      "B": "Deploying, monitoring, and maintaining ML models in production",
      "C": "Data visualization",
      "D": "Feature engineering only"
    },
    "answer": "B"
  },
  {
    "question": "True or False: MLOps is an extension of DevOps for machine learning systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO components are core pillars of MLOps?",
    "options": {
      "A": "Model versioning",
      "B": "Continuous training",
      "C": "Manual deployment",
      "D": "Static data pipelines"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is a model registry used for?",
    "options": {
      "A": "Storing raw datasets",
      "B": "Tracking and versioning trained models",
      "C": "Monitoring hardware",
      "D": "Feature scaling"
    },
    "answer": "B"
  },

  {
    "question": "True or False: MLflow provides experiment tracking and model registry.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which stage comes immediately after model training in an MLOps pipeline?",
    "options": {
      "A": "Data ingestion",
      "B": "Model evaluation",
      "C": "Feature engineering",
      "D": "Data labeling"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO metrics are commonly monitored in production ML systems?",
    "options": {
      "A": "Latency",
      "B": "Prediction accuracy",
      "C": "Learning rate",
      "D": "Batch size"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Model performance in production can degrade even if code does not change.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is data drift?",
    "options": {
      "A": "Change in model architecture",
      "B": "Change in input data distribution",
      "C": "Change in learning rate",
      "D": "Change in loss function"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO types of drift exist?",
    "options": {
      "A": "Data drift",
      "B": "Concept drift",
      "C": "Gradient drift",
      "D": "Memory drift"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Concept drift occurs when the relationship between inputs and outputs changes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which deployment strategy releases models gradually?",
    "options": {
      "A": "Blue-Green deployment",
      "B": "Canary deployment",
      "C": "Shadow deployment",
      "D": "Rollback deployment"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO deployment strategies reduce deployment risk?",
    "options": {
      "A": "Canary deployment",
      "B": "Shadow deployment",
      "C": "Big-bang deployment",
      "D": "Manual release"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Shadow deployment affects real users’ predictions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "What is CI/CD in MLOps?",
    "options": {
      "A": "Continuous Integration / Continuous Deployment",
      "B": "Continuous Inference / Continuous Data",
      "C": "Centralized Infrastructure / Centralized Data",
      "D": "Cloud Integration / Cloud Deployment"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO steps are typically automated in MLOps CI/CD?",
    "options": {
      "A": "Model training",
      "B": "Model testing",
      "C": "Manual labeling",
      "D": "Business decisions"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Feature stores help ensure training-serving consistency.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is training-serving skew?",
    "options": {
      "A": "Mismatch between training and inference data",
      "B": "Overfitting during training",
      "C": "Underfitting during serving",
      "D": "Model latency increase"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO tools are commonly used in MLOps?",
    "options": {
      "A": "MLflow",
      "B": "Kubeflow",
      "C": "Photoshop",
      "D": "Excel"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Kubernetes is commonly used to orchestrate ML workloads.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is model monitoring?",
    "options": {
      "A": "Tracking model training time",
      "B": "Tracking model behavior in production",
      "C": "Tracking hardware usage only",
      "D": "Tracking code changes"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO signals indicate model degradation?",
    "options": {
      "A": "Accuracy drop",
      "B": "Increase in prediction latency",
      "C": "Lower training loss",
      "D": "Higher learning rate"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Retraining is always triggered manually in MLOps.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between DevOps and MLOps?",
    "options": {
      "A": "MLOps only involves writing Python code.",
      "B": "DevOps focuses on software code versions, while MLOps adds versioning for data and model parameters.",
      "C": "MLOps does not require CI/CD pipelines.",
      "D": "DevOps is only for frontend development."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Data Version Control' (DVC) primarily solve?",
    "options": {
      "A": "It compresses large datasets into ZIP files.",
      "B": "It allows teams to track and version large datasets and ML models similarly to how Git tracks code.",
      "C": "It automatically cleans missing values in a dataset.",
      "D": "It visualizes data in a dashboard."
    },
    "answer": "B"
  },
  {
    "question": "In MLOps, what is a 'Feature Store' used for?",
    "options": {
      "A": "A place to buy pre-trained models.",
      "B": "A centralized repository that allows teams to store, discover, and share curated features for training and serving.",
      "C": "A database used exclusively for storing logs.",
      "D": "A tool for frontend feature flagging."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Model Drift'?",
    "options": {
      "A": "When a model's file size increases over time.",
      "B": "The degradation of model performance due to changes in the underlying data distribution in production.",
      "C": "When the training process takes longer than expected.",
      "D": "A technique for moving models between different cloud providers."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 'Shadow Deployment', the new model receives real traffic and its predictions are served to the user, but not logged.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of a 'Model Registry'?",
    "options": {
      "A": "To list the names of all data scientists in a company.",
      "B": "A central repository for managing the lifecycle of ML models, including versioning, stage transitions (Staging to Production), and lineage.",
      "C": "A tool to register for ML conferences.",
      "D": "A database of all hyperparameter combinations."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is a key component of 'Continuous Training' (CT) in MLOps?",
    "options": {
      "A": "Manually retraining the model every Friday.",
      "B": "An automated pipeline that triggers model retraining based on new data or performance degradation.",
      "C": "Writing code without any breaks.",
      "D": "Using a server that never turns off."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Inference Latency'?",
    "options": {
      "A": "The time it takes to train a model from scratch.",
      "B": "The time taken for a model to generate a prediction after receiving an input request.",
      "C": "The delay in collecting training data.",
      "D": "The number of errors a model makes per second."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common tools used for orchestration in MLOps pipelines:",
    "options": {
      "A": "Apache Airflow",
      "B": "Kubeflow",
      "C": "Microsoft Word",
      "D": "Postman"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Blue-Green Deployment' in the context of ML?",
    "options": {
      "A": "Changing the color scheme of the model dashboard.",
      "B": "A strategy where two identical production environments exist, allowing for a switch from an old model (Blue) to a new one (Green) with zero downtime.",
      "C": "A method for training models on environmental data.",
      "D": "Categorizing models by their power consumption."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'A/B Testing' for ML models involves routing a portion of users to Model A and another portion to Model B to compare business metrics.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Containerization' (e.g., using Docker) primarily used for in MLOps?",
    "options": {
      "A": "Reducing the size of image datasets.",
      "B": "Ensuring the ML model and its dependencies run consistently across different environments (Dev, Staging, Prod).",
      "C": "Encrypting the model weights.",
      "D": "Storing data in a physical container."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Model Lineage' track?",
    "options": {
      "A": "The family tree of the researchers who built the model.",
      "B": "The history of a model, including which data, code, and hyperparameters were used to produce it.",
      "C": "The geographical location of the servers.",
      "D": "The number of lines of code in the model file."
    },
    "answer": "B"
  },
  {
    "question": "Which metric is most important for monitoring the 'Health' of a deployed ML API?",
    "options": {
      "A": "R-Squared",
      "B": "HTTP 500 Error Rate and Response Time",
      "C": "Gini Impurity",
      "D": "Mean Squared Error"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cold Start' in the context of serverless model serving?",
    "options": {
      "A": "The delay that occurs when a serverless function is triggered after being idle.",
      "B": "Training a model in a cold environment to prevent overheating.",
      "C": "Initializing a model with random weights.",
      "D": "The process of rebooting the entire data center."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Canary Deployment' in the context of ML model rollouts?",
    "options": {
      "A": "Deploying the model to an environment with no internet access.",
      "B": "Gradually rolling out the new model to a small subset of users before deploying it to the entire population.",
      "C": "A method of testing the model using bird-related data.",
      "D": "Automated deletion of old models every 24 hours."
    },
    "answer": "B"
  },
  {
    "question": "Which tool is commonly used for 'Infrastructure as Code' (IaC) to provision cloud resources for ML pipelines?",
    "options": {
      "A": "TensorFlow",
      "B": "Terraform",
      "C": "Pandas",
      "D": "Jupyter"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Training-Serving Skew'?",
    "options": {
      "A": "A difference in performance between the training data and the serving data due to different data handling or processing logic.",
      "B": "When the model is trained on a GPU but served on a CPU.",
      "C": "The time delay between training a model and deploying it.",
      "D": "When the model weights are corrupted during transfer."
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Model Explainability' (e.g., using SHAP or LIME) is crucial in MLOps for debugging and ensuring regulatory compliance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of 'Prometheus' in an MLOps stack?",
    "options": {
      "A": "To version control the data.",
      "B": "An open-source monitoring and alerting toolkit used to collect metrics from deployed model services.",
      "C": "To train deep learning models.",
      "D": "To manage the feature store."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Data Validation' at the ingest stage of a pipeline prevent?",
    "options": {
      "A": "The server from crashing.",
      "B": "Malformed or unexpected data from entering the training pipeline and degrading model quality.",
      "C": "The developer from making typos in the code.",
      "D": "Duplicate model registrations."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common types of Model Monitoring metrics:",
    "options": {
      "A": "Operational metrics (Latency, Throughput)",
      "B": "Statistical metrics (Prediction drift, Accuracy)",
      "C": "Color metrics (RGB values of graphs)",
      "D": "Typing metrics (Words per minute of developers)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Horizontal Scaling' for model serving?",
    "options": {
      "A": "Increasing the CPU power of a single server.",
      "B": "Adding more instances (replicas) of a model service to handle increased traffic.",
      "C": "Stretching the UI of the dashboard.",
      "D": "Reducing the number of features in the model."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 'Shadow' deployment, the 'shadow' model's output is what the end-user actually sees.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Kubeflow'?",
    "options": {
      "A": "A JavaScript library for data visualization.",
      "B": "A platform for making deployments of machine learning (ML) workflows on Kubernetes simple, portable, and scalable.",
      "C": "A database for storing audio files.",
      "D": "A specialized programming language for ML."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Batch Inference'?",
    "options": {
      "A": "Generating predictions for a large set of inputs at once, usually on a scheduled basis (offline).",
      "B": "Processing one request at a time in real-time.",
      "C": "Training a model using mini-batches.",
      "D": "Deleting data in batches to save space."
    },
    "answer": "A"
  },
  {
    "question": "In the context of MLOps, what is a 'DAG' (Directed Acyclic Graph)?",
    "options": {
      "A": "A type of neural network layer.",
      "B": "A mathematical representation of a pipeline's tasks and their dependencies, ensuring they run in the correct order.",
      "C": "A way to encrypt model keys.",
      "D": "A method for clustering users."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metadata Tracking' in experiment management?",
    "options": {
      "A": "Recording the date the data was created.",
      "B": "Capturing parameters, metrics, and artifacts for every run to ensure experiments are reproducible.",
      "C": "Tracking the GPS location of the data scientists.",
      "D": "Counting the number of characters in the documentation."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following describes 'Model Decay'?",
    "options": {
      "A": "The model file becoming unreadable due to disk errors.",
      "B": "The slow decrease in a model's predictive power as the real-world data evolves away from the training data.",
      "C": "The model getting smaller in size over time.",
      "D": "A hardware failure in the GPU cluster."
    },
    "answer": "B"
  },
  {
    "question": "What is 'TFX' (TensorFlow Extended)?",
    "options": {
      "A": "A premium version of TensorFlow that costs money.",
      "B": "An end-to-end platform for deploying production ML pipelines developed by Google.",
      "C": "A tool for converting models to Excel sheets.",
      "D": "A plugin for Photoshop."
    },
    "answer": "B"
  },
   {
    "question": "What is experiment tracking in MLOps?",
    "options": {
      "A": "Tracking model predictions in production",
      "B": "Logging parameters, metrics, and artifacts of ML experiments",
      "C": "Tracking user behavior",
      "D": "Tracking cloud costs only"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Experiment tracking helps reproduce ML results.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO artifacts are typically logged during ML experiments?",
    "options": {
      "A": "Model weights",
      "B": "Evaluation metrics",
      "C": "User credentials",
      "D": "Operating system"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is a feature store?",
    "options": {
      "A": "A database for raw logs",
      "B": "Centralized storage for curated ML features",
      "C": "A model repository",
      "D": "A monitoring tool"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Feature stores reduce duplicate feature engineering.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO components are part of a feature store?",
    "options": {
      "A": "Offline store",
      "B": "Online store",
      "C": "Model server",
      "D": "GPU scheduler"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is model versioning?",
    "options": {
      "A": "Updating model parameters",
      "B": "Assigning unique identifiers to trained models",
      "C": "Scaling models horizontally",
      "D": "Monitoring predictions"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Model versioning helps rollback faulty models.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which deployment pattern runs old and new models simultaneously without affecting users?",
    "options": {
      "A": "Canary",
      "B": "Blue-Green",
      "C": "Shadow",
      "D": "A/B Testing"
    },
    "answer": "C"
  },

  {
    "question": "Which TWO deployment strategies compare model performance in real traffic?",
    "options": {
      "A": "A/B testing",
      "B": "Canary deployment",
      "C": "Batch deployment",
      "D": "Offline evaluation"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: A/B testing sends traffic to multiple model versions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is batch inference?",
    "options": {
      "A": "Real-time prediction per request",
      "B": "Scheduled predictions on large datasets",
      "C": "Training multiple models",
      "D": "Streaming inference"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Batch inference is suitable for low-latency use cases.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO systems are commonly used for workflow orchestration in MLOps?",
    "options": {
      "A": "Apache Airflow",
      "B": "Kubeflow Pipelines",
      "C": "Docker",
      "D": "NumPy"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is pipeline orchestration?",
    "options": {
      "A": "Manual execution of scripts",
      "B": "Automated coordination of ML workflow steps",
      "C": "GPU allocation",
      "D": "Data visualization"
    },
    "answer": "B"
  },

  {
    "question": "True or False: DAGs are commonly used to represent ML pipelines.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is model serving?",
    "options": {
      "A": "Training models continuously",
      "B": "Exposing models via APIs for inference",
      "C": "Evaluating models offline",
      "D": "Storing models"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO factors are critical in model serving?",
    "options": {
      "A": "Latency",
      "B": "Scalability",
      "C": "Training loss",
      "D": "Batch size"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Autoscaling helps handle variable inference traffic.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is model governance?",
    "options": {
      "A": "Model deployment strategy",
      "B": "Policies for compliance, auditing, and control",
      "C": "Hyperparameter tuning",
      "D": "Feature selection"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO aspects are part of responsible MLOps?",
    "options": {
      "A": "Model explainability",
      "B": "Fairness monitoring",
      "C": "Faster GPUs",
      "D": "Higher batch size"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Model explainability is optional in regulated industries.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "What is reproducibility in MLOps?",
    "options": {
      "A": "Training faster models",
      "B": "Ability to recreate the same results",
      "C": "Deploying models automatically",
      "D": "Monitoring inference"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO elements are required for reproducible ML experiments?",
    "options": {
      "A": "Fixed random seeds",
      "B": "Versioned data and code",
      "C": "More epochs",
      "D": "Higher learning rate"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is continuous training (CT) in MLOps?",
    "options": {
      "A": "Training models manually",
      "B": "Automatically retraining models when data or performance changes",
      "C": "Training models once",
      "D": "Hyperparameter tuning only"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Continuous training helps address concept drift.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO triggers can start model retraining?",
    "options": {
      "A": "Data drift detection",
      "B": "Performance degradation",
      "C": "Code formatting change",
      "D": "UI update"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is data versioning?",
    "options": {
      "A": "Storing only raw data",
      "B": "Tracking changes in datasets over time",
      "C": "Deleting old data",
      "D": "Compressing datasets"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Git is sufficient alone for large dataset versioning.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO tools support data versioning?",
    "options": {
      "A": "DVC",
      "B": "LakeFS",
      "C": "NumPy",
      "D": "Matplotlib"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is pipeline caching?",
    "options": {
      "A": "Deleting old pipeline runs",
      "B": "Reusing previous step outputs to save computation",
      "C": "Running pipelines faster using GPUs",
      "D": "Skipping evaluation"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Pipeline caching improves pipeline efficiency.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is model rollback?",
    "options": {
      "A": "Retraining a model",
      "B": "Reverting to a previous stable model version",
      "C": "Deleting a model",
      "D": "Scaling a model"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO scenarios require model rollback?",
    "options": {
      "A": "Sudden accuracy drop",
      "B": "Production errors",
      "C": "Improved metrics",
      "D": "Lower latency"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Rollback should be manual only.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "What is online inference?",
    "options": {
      "A": "Scheduled batch predictions",
      "B": "Real-time prediction per request",
      "C": "Offline evaluation",
      "D": "Model training"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Online inference prioritizes low latency.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "Which TWO challenges are common in online inference?",
    "options": {
      "A": "Latency constraints",
      "B": "Scalability",
      "C": "Hyperparameter tuning",
      "D": "Labeling delay"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "What is training-serving skew?",
    "options": {
      "A": "Model underfitting",
      "B": "Mismatch between training and inference pipelines",
      "C": "Over-regularization",
      "D": "Hardware failure"
    },
    "answer": "B"
  },

  {
    "question": "True or False: Feature stores help reduce training-serving skew.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },

  {
    "question": "What is model observability?",
    "options": {
      "A": "Tracking training loss only",
      "B": "Monitoring predictions, inputs, and system metrics",
      "C": "Data labeling",
      "D": "Model compression"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO observability signals are ML-specific?",
    "options": {
      "A": "Prediction distribution",
      "B": "Feature drift",
      "C": "CPU utilization",
      "D": "Memory usage"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: System metrics alone are enough for ML observability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "What is model fairness monitoring?",
    "options": {
      "A": "Monitoring inference speed",
      "B": "Detecting bias across sensitive groups",
      "C": "Hyperparameter tuning",
      "D": "Model compression"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO attributes are commonly monitored for fairness?",
    "options": {
      "A": "Gender",
      "B": "Age",
      "C": "Batch size",
      "D": "Learning rate"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Fairness monitoring is only needed during training.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },

  {
    "question": "What is model explainability?",
    "options": {
      "A": "Improving accuracy",
      "B": "Understanding why a model makes predictions",
      "C": "Reducing latency",
      "D": "Compressing models"
    },
    "answer": "B"
  },

  {
    "question": "Which TWO tools are commonly used for explainability?",
    "options": {
      "A": "SHAP",
      "B": "LIME",
      "C": "Docker",
      "D": "Kubernetes"
    },
    "answer": ["A", "B"]
  },

  {
    "question": "True or False: Explainability is critical for regulated industries.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of a 'Kubernetes Operator' in an MLOps context?",
    "options": {
      "A": "To manually restart servers when they fail.",
      "B": "To automate the management of complex, stateful ML applications (like training jobs or model servers) by extending the Kubernetes API.",
      "C": "To write Python scripts for data cleaning.",
      "D": "To monitor the electricity usage of the data center."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Model Quantization' primarily used for?",
    "options": {
      "A": "Increasing the number of layers in a neural network.",
      "B": "Reducing the precision of the model weights (e.g., from FP32 to INT8) to decrease model size and speed up inference, especially on edge devices.",
      "C": "Counting the total number of users of the model.",
      "D": "Improving the accuracy of the model on small datasets."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'LIME' (Local Interpretable Model-agnostic Explanations) is used to explain the predictions of any machine learning classifier by approximating it locally with an interpretable model.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In MLOps, what does 'Agnostic Model Serving' refer to?",
    "options": {
      "A": "Serving models only from one specific cloud provider.",
      "B": "A serving infrastructure that can host models built with any framework (TensorFlow, PyTorch, Scikit-learn, etc.) using a unified API.",
      "C": "Serving models that have no specific target audience.",
      "D": "Serving models without any metadata tracking."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Integrity Testing' in a machine learning pipeline?",
    "options": {
      "A": "To ensure the developers are being honest.",
      "B": "To verify that the input data follows expected schemas and that feature engineering logic remains consistent over time.",
      "C": "To check if the server hardware is physically damaged.",
      "D": "To test the model's performance on the training set only."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common techniques for 'Model Distillation' in production environments:",
    "options": {
      "A": "Teacher-Student training",
      "B": "Feature-based distillation",
      "C": "Hyperparameter deletion",
      "D": "Manual weight adjustment"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Namespace Isolation' in a multi-tenant MLOps platform (like Kubeflow)?",
    "options": {
      "A": "Giving every user a different name.",
      "B": "Using Kubernetes namespaces to separate resources, pipelines, and data between different teams or projects for security and organization.",
      "C": "Restricting the model to only use English words.",
      "D": "A way to prevent the model from accessing the internet."
    },
    "answer": "B"
  },
  {
    "question": "Which tool is specifically designed for tracking machine learning experiments, including code, data, and hyperparameters?",
    "options": {
      "A": "MLflow",
      "B": "Jenkins",
      "C": "Slack",
      "D": "VLC Media Player"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Concept Drift' specifically refers to changes in the relationship between input features and the target variable, while 'Data Drift' refers to changes in the distribution of the input features themselves.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Automated Resource Provisioning' in an ML pipeline?",
    "options": {
      "A": "The system automatically buying new hardware from a store.",
      "B": "The pipeline dynamically requesting and releasing cloud resources (like GPU instances) based on the task requirements (Training vs Inference).",
      "C": "A developer manually setting up a server for every run.",
      "D": "Deleting all resources after a model fails."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Seldon Core' help achieve in MLOps?",
    "options": {
      "A": "Building front-end dashboards.",
      "B": "An open-source platform to deploy, scale, and manage thousands of machine learning models on Kubernetes.",
      "C": "Cleaning large CSV files.",
      "D": "Translating models between Python and R."
    },
    "answer": "B"
  },
  {
    "question": "In the context of 'Model Monitoring', what is 'KL Divergence' used for?",
    "options": {
      "A": "Measuring the distance between the training data distribution and the production data distribution to detect drift.",
      "B": "Calculating the speed of the GPU.",
      "C": "Estimating the cost of cloud storage.",
      "D": "Determining the number of hidden layers in a model."
    },
    "answer": "A"
  },
  {
    "question": "What is 'Pre-computation' in a Feature Store architecture?",
    "options": {
      "A": "Calculating features in real-time for every request.",
      "B": "Calculating features in advance (offline) and storing them in the Feature Store for fast retrieval during inference.",
      "C": "Calculating the model's accuracy before it is trained.",
      "D": "A method for predicting the future values of a feature."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following describes 'Model Pruning'?",
    "options": {
      "A": "Removing irrelevant columns from the input CSV.",
      "B": "Reducing the size of a neural network by removing neurons or connections that contribute little to the final output, minimizing latency.",
      "C": "Deleting old versions of the model from the registry.",
      "D": "Cleaning the model's documentation."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Circuit Breakers' in model serving architectures?",
    "options": {
      "A": "To physically shut down the server during a storm.",
      "B": "A design pattern that prevents a service from trying to perform an operation that is likely to fail (e.g., if a model service is down), avoiding cascading failures.",
      "C": "To limit the number of users who can access the model.",
      "D": "To reset the model weights to zero if accuracy drops."
    },
    "answer": "B"
  },
    {
        "question": "True or False: 'Model Ensembling' is a technique where multiple models are combined to improve overall performance and robustness.",
        "options": {
        "A": "True",
        "B": "False"
        },
        "answer": "A"
    },
    {
    "question": "What is shadow deployment in MLOps?",
    "options": {
      "A": "Replacing the production model immediately",
      "B": "Running a new model in parallel without affecting user output",
      "C": "Disabling the old model",
      "D": "Training models offline"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Shadow deployment allows safe performance comparison.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO metrics are typically compared during shadow deployment?",
    "options": {
      "A": "Prediction accuracy",
      "B": "Latency",
      "C": "Learning rate",
      "D": "Batch size"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is canary deployment?",
    "options": {
      "A": "Deploying models only in staging",
      "B": "Gradually rolling out a new model to a subset of users",
      "C": "Training multiple models",
      "D": "Offline evaluation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Canary deployment reduces deployment risk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is model lineage?",
    "options": {
      "A": "Tracking model accuracy",
      "B": "Tracking model dependencies, data, code, and versions",
      "C": "Model compression",
      "D": "Hyperparameter tuning"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO components are part of model lineage?",
    "options": {
      "A": "Training data version",
      "B": "Feature transformations",
      "C": "CPU clock speed",
      "D": "Screen resolution"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Model lineage supports auditability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is automated model validation?",
    "options": {
      "A": "Manual testing by data scientists",
      "B": "Automatically verifying model performance before deployment",
      "C": "Hyperparameter optimization",
      "D": "Data labeling"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO checks are part of model validation?",
    "options": {
      "A": "Performance threshold checks",
      "B": "Bias checks",
      "C": "GPU temperature",
      "D": "Keyboard layout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Automated validation prevents bad models from reaching production.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is feature drift?",
    "options": {
      "A": "Change in feature importance",
      "B": "Change in feature distribution over time",
      "C": "Model underfitting",
      "D": "Label noise"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Feature drift always leads to performance degradation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO techniques detect feature drift?",
    "options": {
      "A": "Statistical tests",
      "B": "Distribution comparison",
      "C": "Grid search",
      "D": "Backpropagation"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is label drift?",
    "options": {
      "A": "Change in feature values",
      "B": "Change in target variable distribution",
      "C": "Overfitting",
      "D": "Underfitting"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Label drift is harder to detect than feature drift.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is delayed labeling?",
    "options": {
      "A": "Incorrect labels",
      "B": "Labels becoming available long after predictions",
      "C": "Missing features",
      "D": "Data duplication"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO domains commonly face delayed labeling?",
    "options": {
      "A": "Fraud detection",
      "B": "Credit scoring",
      "C": "Image resizing",
      "D": "Text tokenization"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Delayed labeling complicates model monitoring.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is infrastructure drift?",
    "options": {
      "A": "Change in model architecture",
      "B": "Changes in hardware or software affecting performance",
      "C": "Concept drift",
      "D": "Feature drift"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO changes can cause infrastructure drift?",
    "options": {
      "A": "Library version updates",
      "B": "Hardware upgrades",
      "C": "Data normalization",
      "D": "Feature scaling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Infrastructure drift can affect model latency.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is reproducibility in MLOps?",
    "options": {
      "A": "Training faster models",
      "B": "Ability to recreate the same model results consistently",
      "C": "Reducing latency",
      "D": "Scaling deployments"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors improve reproducibility?",
    "options": {
      "A": "Versioned data",
      "B": "Fixed random seeds",
      "C": "Auto-scaling",
      "D": "Load balancing"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Reproducibility is critical for debugging ML systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is an MLOps maturity model?",
    "options": {
      "A": "A deployment strategy",
      "B": "A framework describing stages of MLOps adoption",
      "C": "A model architecture",
      "D": "A cloud service"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO stages are common in MLOps maturity models?",
    "options": {
      "A": "Manual",
      "B": "Automated",
      "C": "Random",
      "D": "Unstructured"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Higher MLOps maturity reduces operational risk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary benefit of using 'Terraform' or 'Ansible' in an MLOps environment?",
    "options": {
      "A": "They automatically clean and label image datasets.",
      "B": "They enable 'Infrastructure as Code' (IaC), allowing for reproducible and version-controlled provisioning of ML compute resources.",
      "C": "They are specialized programming languages for writing Neural Networks.",
      "D": "They act as a replacement for the Python programming language."
    },
    "answer": "B"
  },
  {
    "question": "In Kubernetes, what are 'Taints' and 'Tolerations' used for in an ML cluster?",
    "options": {
      "A": "To track which developers are allowed to delete models.",
      "B": "To ensure that specialized hardware (like GPUs) are only used by specific ML workloads that 'tolerate' those nodes.",
      "C": "To measure the amount of heat generated by the server rack.",
      "D": "To automatically encrypt data at rest."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Differential Privacy' in the context of ML model training?",
    "options": {
      "A": "A method of training models on different types of private clouds.",
      "B": "A system for adding mathematical noise to the data or gradients to ensure that individual user data cannot be reconstructed from the model weights.",
      "C": "A way to hide the model's accuracy from competitors.",
      "D": "The process of moving a database from a public to a private subnet."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Model Fingerprinting' is used to verify the integrity and version of a model file to ensure the correct artifact is running in production.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does 'Feature Attribution' (e.g. Integrated Gradients) help an MLOps engineer identify?",
    "options": {
      "A": "The cost of storing each feature in a database.",
      "B": "The specific contribution of each input feature to an individual prediction made by the model.",
      "C": "The name of the data engineer who created the feature.",
      "D": "The optimal learning rate for the training job."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is a primary goal of a 'Dry Run' in a CI/CD pipeline for ML?",
    "options": {
      "A": "To train the model on a completely empty dataset.",
      "B": "To test the deployment scripts and infrastructure configuration without actually serving traffic or changing production state.",
      "C": "To wipe the server clean before a fresh install.",
      "D": "To verify that the model can work without an internet connection."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO metrics used to measure 'Data Integrity' at the beginning of an MLOps pipeline:",
    "options": {
      "A": "Missing value ratios per feature",
      "B": "Schema drift (type mismatch)",
      "C": "GPU memory utilization",
      "D": "Model F1-score"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'TFX Resolver' used for in a TensorFlow Extended pipeline?",
    "options": {
      "A": "To resolve conflicts between different versions of Python.",
      "B": "To find and retrieve specific artifacts (like the latest 'blessed' model or the latest data split) from the Metadata Store.",
      "C": "To automatically fix bugs in the model code.",
      "D": "To increase the resolution of input images."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Horizontal Pod Autoscaling' (HPA) in Kubernetes can be triggered by custom metrics like 'Inference Latency' rather than just CPU/Memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'Model Serialization' (e.g., using ONNX or Pickle)?",
    "options": {
      "A": "To assign a serial number to every model for warranty purposes.",
      "B": "To convert a trained model object into a format that can be easily stored on disk or transmitted over a network for serving.",
      "C": "To train a model on a series of time-stamped data.",
      "D": "To ensure the model only processes data one row at a time."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary goal of MLOps?",
    "options": {
      "A": "Improve model accuracy only",
      "B": "Automate and manage the ML lifecycle in production",
      "C": "Replace data scientists",
      "D": "Eliminate model retraining"
    },
    "answer": "B"
  },
  {
    "question": "True or False: MLOps combines machine learning, DevOps, and data engineering practices.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components are core pillars of MLOps?",
    "options": {
      "A": "Model versioning",
      "B": "Monitoring",
      "C": "Graphic design",
      "D": "Manual testing"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a model registry used for?",
    "options": {
      "A": "Storing raw datasets",
      "B": "Tracking and managing model versions",
      "C": "Scheduling pipelines",
      "D": "Visualizing metrics"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Model registries support model rollback.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is CI/CD in the context of MLOps?",
    "options": {
      "A": "Continuous Integration and Continuous Deployment for ML workflows",
      "B": "Customer Interaction and Data Collection",
      "C": "Code Inspection and Debugging",
      "D": "Cloud Infrastructure Design"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO steps are commonly automated in ML CI/CD pipelines?",
    "options": {
      "A": "Model training",
      "B": "Model testing",
      "C": "Manual labeling",
      "D": "Stakeholder approval"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: CI/CD pipelines reduce human error in ML deployments.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is data drift?",
    "options": {
      "A": "Change in data storage format",
      "B": "Change in input data distribution over time",
      "C": "Increase in dataset size",
      "D": "Loss of data"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO types of drift are commonly monitored?",
    "options": {
      "A": "Data drift",
      "B": "Concept drift",
      "C": "Gradient drift",
      "D": "Memory drift"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Concept drift refers to changes in the relationship between features and labels.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is batch inference?",
    "options": {
      "A": "Real-time prediction per request",
      "B": "Offline predictions on large datasets",
      "C": "Model retraining",
      "D": "Feature extraction"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Batch inference is typically less latency-sensitive than online inference.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a feature store?",
    "options": {
      "A": "A database for raw data only",
      "B": "A centralized system for managing ML features",
      "C": "A model deployment service",
      "D": "A visualization dashboard"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO benefits does a feature store provide?",
    "options": {
      "A": "Feature reuse",
      "B": "Consistency between training and serving",
      "C": "Automatic labeling",
      "D": "GPU optimization"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Feature stores help prevent training-serving skew.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is model monitoring?",
    "options": {
      "A": "Tracking only system uptime",
      "B": "Observing model performance and behavior in production",
      "C": "Training models continuously",
      "D": "Optimizing hyperparameters"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO metrics are ML-specific monitoring metrics?",
    "options": {
      "A": "Prediction accuracy",
      "B": "Feature distribution",
      "C": "Disk space",
      "D": "Network bandwidth"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Monitoring helps detect silent model failures.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is model retraining?",
    "options": {
      "A": "Reusing the same model indefinitely",
      "B": "Training a model again with new or updated data",
      "C": "Deploying a model",
      "D": "Scaling inference"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO triggers can initiate retraining?",
    "options": {
      "A": "Performance degradation",
      "B": "Detected drift",
      "C": "UI changes",
      "D": "Hardware upgrades"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Automated retraining is a common MLOps practice.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is model explainability?",
    "options": {
      "A": "Improving inference speed",
      "B": "Understanding how a model makes predictions",
      "C": "Reducing model size",
      "D": "Increasing accuracy"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO tools are commonly used for explainability?",
    "options": {
      "A": "SHAP",
      "B": "LIME",
      "C": "Docker",
      "D": "Airflow"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Explainability is important for regulated industries.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is reproducibility in MLOps?",
    "options": {
      "A": "Training faster models",
      "B": "Ability to recreate experiments and results",
      "C": "Scaling deployments",
      "D": "Monitoring latency"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO practices improve reproducibility?",
    "options": {
      "A": "Versioning data",
      "B": "Versioning code",
      "C": "Random deployment",
      "D": "Manual execution"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Reproducibility is essential for debugging ML systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary advantage of 'TensorFlow Lite' or 'CoreML' in an MLOps pipeline?",
    "options": {
      "A": "They allow for faster training on large GPU clusters.",
      "B": "They provide optimized model formats for low-power edge devices and mobile phones with reduced latency.",
      "C": "They automatically label data using crowdsourcing.",
      "D": "They act as a replacement for standard Python libraries."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Hydra' or 'OmegaConf' help manage in a production ML project?",
    "options": {
      "A": "The cooling systems of the data center.",
      "B": "Complex configuration files and hyperparameter overrides for reproducible experiments.",
      "C": "The versioning of large video files.",
      "D": "The encryption of user passwords."
    },
    "answer": "B"
  },
  {
    "question": "In 'Federated Learning', where does the model training primarily occur?",
    "options": {
      "A": "On a central cloud server with all user data.",
      "B": "On decentralized edge devices (like smartphones) using local data, with only weight updates sent to a central server.",
      "C": "In a physical laboratory environment.",
      "D": "Inside a secure government database."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cold Start' latency in the context of serverless model inference (e.g., AWS Lambda)?",
    "options": {
      "A": "The time it takes for a model to learn from zero data.",
      "B": "The delay experienced when a function is invoked for the first time or after a period of inactivity while the container initializes.",
      "C": "The performance drop of a model in winter environments.",
      "D": "The time required to reboot the main database."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Data Contracts' are agreements between data producers and consumers that define the schema, quality, and SLA of the data entering the ML pipeline.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of 'Model Cards' in MLOps governance?",
    "options": {
      "A": "They are physical identity cards for data scientists.",
      "B": "Standardized documents providing essential information about a model's performance, intended use, and limitations to ensure transparency.",
      "C": "Credit cards used to pay for cloud computing resources.",
      "D": "A way to play games during training downtime."
    },
    "answer": "B"
  },
  {
    "question": "Which technique is used to combat 'Adversarial Attacks' on a deployed model?",
    "options": {
      "A": "Increasing the learning rate.",
      "B": "Adversarial Training, where the model is trained on perturbed examples to improve its robustness.",
      "C": "Deleting the model and starting over.",
      "D": "Limiting the model's access to the public internet."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stochastic Weight Averaging' (SWA) used for in production models?",
    "options": {
      "A": "To randomly delete weights to save space.",
      "B": "To improve generalization by averaging weights from multiple points in the training trajectory.",
      "C": "To calculate the probability of a server failure.",
      "D": "To ensure the model only uses integers."
    },
    "answer": "B"
  },
  {
    "question": "What does 'Backtesting' in an MLOps pipeline involve?",
    "options": {
      "A": "Testing the model on data it has already seen.",
      "B": "Simulating a model's performance by running it on historical data to see how it would have behaved in the past.",
      "C": "Checking the hardware on the back of the server rack.",
      "D": "The process of reverting to a previous version of Git."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'KServe' provides a serverless environment on Kubernetes that supports advanced deployment patterns like 'Autoscaling to Zero'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is experiment tracking in MLOps?",
    "options": {
      "A": "Tracking system logs",
      "B": "Recording parameters, metrics, and artifacts of ML experiments",
      "C": "Monitoring GPU usage",
      "D": "Tracking user behavior"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Experiment tracking helps compare different model versions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO items are commonly logged during experiment tracking?",
    "options": {
      "A": "Hyperparameters",
      "B": "Evaluation metrics",
      "C": "Screen resolution",
      "D": "Keyboard shortcuts"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is pipeline orchestration?",
    "options": {
      "A": "Manual execution of scripts",
      "B": "Coordinating and automating ML workflow steps",
      "C": "Model monitoring",
      "D": "Data labeling"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Pipeline orchestration improves scalability and reliability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO tools are commonly used for ML pipeline orchestration?",
    "options": {
      "A": "Airflow",
      "B": "Kubeflow Pipelines",
      "C": "Excel",
      "D": "PowerPoint"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is model packaging?",
    "options": {
      "A": "Compressing datasets",
      "B": "Bundling a trained model with its dependencies",
      "C": "Hyperparameter tuning",
      "D": "Feature engineering"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Docker is commonly used for model packaging.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is inference latency?",
    "options": {
      "A": "Training time",
      "B": "Time taken to generate a prediction",
      "C": "Model size",
      "D": "Accuracy score"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors can increase inference latency?",
    "options": {
      "A": "Large model size",
      "B": "Network overhead",
      "C": "Feature normalization",
      "D": "Data labeling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Lower latency is critical for real-time ML systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is autoscaling in MLOps?",
    "options": {
      "A": "Manually increasing servers",
      "B": "Automatically adjusting resources based on load",
      "C": "Model retraining",
      "D": "Feature selection"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO metrics are commonly used to trigger autoscaling?",
    "options": {
      "A": "CPU utilization",
      "B": "Request rate",
      "C": "Accuracy",
      "D": "Precision"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Autoscaling helps maintain service availability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is technical debt in MLOps?",
    "options": {
      "A": "Financial cost of cloud usage",
      "B": "Accumulated complexity from quick ML solutions",
      "C": "Model accuracy loss",
      "D": "Hardware failure"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO practices help reduce MLOps technical debt?",
    "options": {
      "A": "Automation",
      "B": "Documentation",
      "C": "Hardcoding logic",
      "D": "Manual deployments"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is model governance in MLOps?",
    "options": {
      "A": "Improving model accuracy",
      "B": "Defining policies and controls for model usage and lifecycle",
      "C": "Scaling infrastructure",
      "D": "Optimizing hyperparameters"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Model governance is especially important in regulated industries like finance and healthcare.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO elements are typically part of model governance?",
    "options": {
      "A": "Audit trails",
      "B": "Approval workflows",
      "C": "GPU memory allocation",
      "D": "Data visualization themes"
    },
    "answer": ["A", "B"]
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
    skill = "MLOps"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
