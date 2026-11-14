# EduGenius AI

EduGenius AI creates student study material and teacher-ready lesson plans from a topic.

## Features
- Student and Teacher modes
- Education-level selection
- Student explanations in Easy English, Urdu, or Roman Urdu
- AI-generated explanations, questions, MCQs, activities, and lesson plans
- Download generated material as `.txt` or `.pptx`

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your Gemini API key as an environment variable.

   **Windows PowerShell:**
   ```powershell
   $env:GEMINI_API_KEY="YOUR_API_KEY"
   ```

   **macOS/Linux:**
   ```bash
   export GEMINI_API_KEY="YOUR_API_KEY"
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository, for example `edugenius-ai`.
2. Upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore`.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select your repository, branch, and `app.py`.
5. Before deploying (or from the app's settings), open **Advanced settings / Secrets**.
6. Add this secret:

   ```toml
   GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"
   ```

7. Deploy the app.

## Security
- Do not paste your real API key into `app.py`.
- Do not commit `.streamlit/secrets.toml` or any file containing your key.
- If a key is accidentally published, revoke it and create a new one.

## Model
The default model is `gemini-2.5-flash`. You can change it by setting `GEMINI_MODEL` in your environment.
