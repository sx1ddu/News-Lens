# NewsLens 🔎

### AI-Powered News Perspective Analyzer

NewsLens is a full-stack AI application for analyzing how different news sources cover the same topic. It combines article retrieval, content extraction, summarization, political-bias classification, and stance analysis into a single workflow.

NewsLens helps users compare how different news sources present the same topic by collecting, processing, summarizing, and analyzing articles through a unified AI pipeline.

The application retrieves relevant news articles, extracts their content, generates concise summaries, and runs **two separate, independent classification tasks** on each article:

1. **Political bias** - Left / Center / Right, using a fine-tuned **RoBERTa** model.
2. **Stance** - Supports / Neutral / Questions-Critical, i.e. whether the article supports, stays neutral on, or questions the searched topic. This is a different task from bias - an article can be politically Left-leaning while still questioning the specific topic being searched, and vice versa.

> ⚠️ **Current status of the stance model:** the stance model artifact currently used is a 4-class model (Agree / Discuss / Disagree / Unrelated) left over from an earlier stance-detection experiment. It does **not** produce the required Supports / Neutral / Questions-Critical labels. The backend detects this mismatch at inference time and reports stance as unavailable rather than guessing a label mapping. See Limitations below.

## 🎯 Project Overview

NewsLens is designed as a perspective-comparison tool rather than a fact-checking system. The application processes multiple articles for a user-provided topic and presents the results through two independent analytical dimensions:

- **Political bias:** Left, Center, or Right
- **Topic stance:** Supports, Neutral, or Questions / Critical

The system separates these tasks because political orientation and an article's stance toward a specific topic are not the same property.


The goal is not to determine whether an article is true or false, but to help users **compare different perspectives on the same topic**.

---

## ✨ Features

- 🔎 Search for news topics
- 📰 Retrieve articles from multiple news sources, with duplicate removal
- ✂️ Generate concise article summaries using **BART**
- 🧠 Predict political bias using a fine-tuned **RoBERTa** model
- 🧭 Predict stance toward the topic using a separate fine-tuned **RoBERTa** model (pending a compatible 3-class model artifact)
- ⚖️ Classify articles by bias:
  - Left
  - Center
  - Right
- 🧭 Classify articles by stance:
  - Supports
  - Neutral
  - Questions / Critical
- 📊 Group articles by bias, and separately by stance
- 📝 Generate a short extractive consensus preview per stance group
- 🌐 React-based user interface
- ⚡ FastAPI backend for AI inference and news processing, with per-article error isolation

---

## 🏗️ System Architecture

```text
                          User
                           |
                           v
                    React Frontend
                           |  HTTP Request (POST /search)
                           v
                    FastAPI Backend
                           |
                           v
                       NewsService
                           |
                           v
                    ArticleService
                (extract + dedupe + timeout)
                           |
                           v
                    SummaryService (BART)
                           |
                           v
                    InferenceService
                    +----------+-----------+
                    v                      v
              Bias Model              Stance Model
           (RoBERTa, 3-class)      (RoBERTa, 3-class *)
                    v                      v
         Left / Center / Right   Supports / Neutral /
                                  Questions-Critical
                    +----------+-----------+
                           v
                    GroupingService
                    +----------+---------+
                    v                    v
              Bias Groups          Stance Groups
                                          |
                                          v
                                 ConsensusService
                        (per-group extractive preview)
                           |
                           v
                       JSON Response
                           |
                           v
                    React Frontend
```

\* The stance model slot is architecturally 3-class-ready; the currently
stored artifact is a 4-class placeholder and is treated as unavailable
until replaced - see the note above.

---

## 🤖 AI Pipeline

### 1. Article Retrieval

The user enters a search query through the React frontend.

The backend sends the query to **NewsAPI** and retrieves relevant article metadata and URLs. Near-duplicate articles (same URL or same title) are removed before further processing.

### 2. Article Extraction

The backend downloads each article URL (with a timeout) and extracts the full article text. Extraction failures and suspiciously short pages (paywalls, "enable JavaScript" stubs) are treated as failures for that one article and skipped - they do not fail the whole search.

### 3. Summarization

The extracted article text is passed to **BART (facebook/bart-large-cnn)**.

BART generates a shorter summary containing the main information from the article. The input is truncated once to BART's 1024-token limit before summarization.

### 4. Tokenization

Before text is processed by the transformer models, it is converted into tokens using Hugging Face tokenizers. Each model (bias, stance, and BART) uses its own tokenizer.

```text
Raw Text
   ↓
Tokenizer
   ↓
Token IDs
   ↓
Transformer Model
   ↓
Prediction / Summary
```

### 5. Political Bias Classification

The article text is passed to the fine-tuned **RoBERTa** bias classification model, which predicts one of three categories:

```text
Left
Center
Right
```

### 6. Stance Classification

The article text is separately passed to the RoBERTa stance model, which is intended to predict:

```text
Supports
Neutral
Questions / Critical
```

This is a distinct classification task from bias - it answers "does this article support, stay neutral on, or question the topic?" rather than "what is this article's political leaning?" The backend checks the loaded model's output size against this 3-class scheme before trusting its predictions; if they don't match (true for the current placeholder model artifact), stance is reported as unavailable instead of being guessed.

### 7. Grouping and Consensus

Analyzed articles are grouped two ways - by bias and, separately, by stance. For each stance group, a short extractive consensus preview is built from the first sentence of each article's summary in that group.

---

## 🧠 Models Used

| Model              | Purpose                     | Status |
| ------------------ | ---------------------------- | ------ |
| **BART**            | Abstractive news summarization | Active |
| **RoBERTa (bias)**   | Political bias classification (Left/Center/Right) | Active |
| **RoBERTa (stance)** | Stance classification (Supports/Neutral/Questions-Critical) | Placeholder artifact - not yet a compatible 3-class model, see note above |

### BART

`facebook/bart-large-cnn` is used to generate concise summaries of retrieved news articles.

### RoBERTa (bias)

A RoBERTa-based sequence classification model was fine-tuned using a labeled news-bias dataset to classify articles into Left, Center, and Right political perspectives.

### RoBERTa (stance)

A separate RoBERTa-based sequence classification model is intended to classify articles by stance toward the searched topic (Supports / Neutral / Questions-Critical). The model currently stored in `backend/models/stance_model` was fine-tuned for a different, 4-class stance-detection task and needs to be replaced with a properly trained 3-class model - see the training notebooks and Limitations below.

---

## 📊 Dataset

The political bias classifier was trained using the following dataset:

**News Bias Detection Dataset**

[Hugging Face Dataset](https://huggingface.co/datasets/cmpatino/news-bias-detection-dataset?utm_source=chatgpt.com)

The dataset contains political perspective categories including:

- Political Left
- Political Center
- Political Right

The dataset provides training, validation, and test splits.

A separate dataset and training pass (`training/04_train_stance_model.ipynb`) is needed to produce the 3-class Supports/Neutral/Questions-Critical stance model - this has not yet been done.

---

## 📈 Model Performance

The trained RoBERTa model achieved the following validation results:

| Metric    |      Score |
| --------- | ---------: |
| Accuracy  | **86.60%** |
| Precision | **86.68%** |
| Recall    | **86.60%** |
| F1 Score  | **86.60%** |

---

## 🛠️ Tech Stack

### Frontend

- React
- TypeScript
- Tailwind CSS
- Axios
- Vite

### Backend

- Python
- FastAPI
- Uvicorn
- Requests
- NewsAPI

### Machine Learning

- PyTorch
- Hugging Face Transformers
- RoBERTa
- BART
- Hugging Face Tokenizers

### Development

- Google Colab
- Git
- GitHub
- VS Code

---

## 📁 Project Structure

```text
AI-News-Perspective-Analyzer/
│
├── backend/
│   ├── routes/
│   │   └── search.py
│   │
│   ├── services/
│   │   ├── article_service.py       # download + extract article text, dedupe
│   │   ├── article_analysis_service.py  # orchestrates one article through the full pipeline
│   │   ├── news_service.py           # News API calls
│   │   ├── summary_service.py        # BART summarization
│   │   ├── inference_service.py      # bias + stance model inference
│   │   ├── model_manager.py          # loads both models + tokenizers once
│   │   ├── labels.py                 # centralized label definitions
│   │   ├── grouping_service.py       # groups articles by bias / by stance
│   │   └── consensus_service.py      # extractive per-group consensus preview
│   │
│   ├── tests/
│   │
│   ├── models/
│   │   └── ...
│   │
│   ├── app.py
│   ├── config.py
│   ├── schemas.py
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   │
│   └── package.json
│
├── .gitignore
└── README.md
```

> Trained model weights are excluded from the Git repository because of their large file size.

---

## 🚀 Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-News-Perspective-Analyzer
```

### 2. Backend Setup

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `.env` file inside the backend:

```env
NEWS_API_KEY=your_newsapi_key
```

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## 🔐 Environment Variables

The project requires API credentials that should **not** be committed to Git. Copy `backend/.env.example` to `backend/.env` and fill in your own values:

```env
NEWS_API_KEY=your_newsapi_key_here
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ARTICLE_LIMIT=10
ARTICLE_FETCH_TIMEOUT=8
MIN_ARTICLE_WORDS=50
```

`.env` is already in `.gitignore` - never commit it.

---

## 🧪 Testing

From the `backend/` folder, with dependencies installed:

```bash
pytest
```

Tests cover request validation, article deduplication/extraction error handling, News API error handling, and the bias/stance grouping and consensus logic. Tests that would require the actual model weight files (which are gitignored) are not included - those are best exercised by running the server locally with real models in place.

---

## ⚠️ Limitations

- **The stance model is not yet functional.** The artifact in `backend/models/stance_model` was fine-tuned as a 4-class Agree/Discuss/Disagree/Unrelated stance-detection model, not the required 3-class Supports/Neutral/Questions-Critical scheme. The backend detects this at inference time and returns `stance: null` with `stance_unavailable_reason` set, rather than guessing a label mapping. A real 3-class model needs to be trained and dropped into that folder.
- Political bias classification is a model prediction and should not be treated as an objective fact.
- Classification performance depends on the quality and distribution of the training data.
- Article extraction may fail for websites that restrict automated access; those articles are skipped and reported in `failed_articles` rather than failing the whole search.
- Summarization quality can vary depending on article structure and length.
- Consensus previews are extractive (built from existing summary sentences), not a new AI-generated synthesis of the group.
- The current system primarily supports English-language news content.

---

## 🔮 Future Improvements

- Improve classification accuracy with larger and more diverse datasets
- Add multilingual news analysis
- Add more news sources and APIs
- Provide confidence visualization for predictions
- Improve long-article summarization using chunking
- Deploy the complete application online
- Add article-to-article comparison
- Provide additional transparency about model predictions

---

## 👨‍💻 Author

**Siddharth Kandela**  
B.Tech Computer Science Engineering  
IIITDM Jabalpur  

GitHub: [sx1ddu](https://github.com/sx1ddu)

---

## ⚖️ Disclaimer

NewsLens is an educational and research-oriented project.

The political perspective labels are **AI-generated predictions** based on patterns learned from the training data. They do not represent an absolute judgment of an article's political ideology, factual accuracy, or credibility.

Users should consult the original articles and multiple reliable sources when evaluating news.

---

### Built for learning, experimentation, and better news comparison.
