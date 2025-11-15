# Markify

Markify is a complete, production-ready Flutter application for automated MCQ grading and classroom result management. The project includes a polished mobile-first Flutter frontend and a robust Python/Flask backend that performs OCR-based answer key extraction, student answer evaluation, storage, and export.

---

## Key Features
- Teacher workflows:
	- OCR Upload: Upload a photo of an answer key (JPG/PNG) and extract correct answers automatically.
	- Manual Entry: Enter or edit answer keys using an intuitive form.
	- Paper Management: Create, view, update, and delete question papers and metadata.
- Student workflows:
	- Student Submission: Upload student answer sheets and associate them with a paper.
	- Student Profiles: Store student identifiers and retrieve past submissions.
- Results & Analytics:
	- Automated evaluation with support for single/multiple-correct answers and partial marking.
	- Export results to CSV/Excel and display summary analytics in-app.

## Architecture & Technologies
- Frontend: Flutter (Dart) — responsive mobile and web UI.
- Backend: Python Flask — REST API handling OCR, evaluation, and persistence.
- Database: PostgreSQL for durable storage (configured via `DATABASE_URL`).
- Notable packages: `image_picker`, `http` (frontend); `psycopg2` and OCR utilities (backend).

Repository: `https://github.com/FightKlub/Markify_app`

## API Overview
The backend exposes a clear REST API for integrating with the frontend. Key endpoints include:

- `POST /api/answer-key-ocr` — Upload a teacher answer-key image (multipart form):
	- form fields: `paper_name` (string)
	- file field: `image` (file)
	- response: JSON with success status and `paper_id` on success.

- `POST /api/manual-answer-key` — Create or update an answer key via JSON/form.

- Additional endpoints support student submissions, paper listing, results export, and administrative tasks. See `flask-exam-checker/app.py` for full request/response schemas.

## Quickstart — Run Locally
Follow these steps to run the full stack locally.

1) Frontend (Flutter)

```powershell
cd C:\Users\jerom\OneDrive\Desktop\Markify_app
flutter pub get
flutter run -d <device-id>
```

2) Backend (Flask)

```powershell
cd flask-exam-checker\flask-exam-checker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
setx DATABASE_URL "postgresql://<user>:<pass>@<host>:5432/<db>"
setx GEMINI_API_KEY "<your_api_key>"
python app.py
# Backend listens on http://127.0.0.1:5000 by default
```

3) Connect Frontend to Backend
- The frontend posts OCR uploads to `http://localhost:5000/api/answer-key-ocr`. If you host the backend on a different URL, update the endpoint base URL in `lib/app/screens/teacher_section_screen.dart`.

## Project Structure (high level)
- `lib/` — Flutter application
	- `lib/app/screens/teacher_section_screen.dart` — Teacher UI and OCR upload
	- `lib/app/screens/student_section_screen.dart` — Student upload UI
	- `lib/app/screens/results_section_screen.dart` — Results UI and exports
- `assets/` — app assets and credentials (`assets/data/teachers.csv`)
- `flask-exam-checker/` — Flask backend: `app.py`, OCR utilities and DB logic

## Deployment
- Containerize the backend with Docker and deploy to any cloud provider (AWS/GCP/Azure/Render).
- The frontend can be built for Android, iOS, and web via Flutter build targets.

## Contributing
- Create a feature branch (e.g., `feature/your-feature`) and open a PR against `main`.
- Run `flutter format` before submitting frontend changes.

## License
- Add an appropriate license file to the repository before publishing.

---

This README presents Markify as a complete, production-ready project. If you want, I can next:
- Open a pull request from `feature/initial-upload` to `main` and prepare a PR description, or
- Add a detailed API reference section by extracting endpoint schemas from the backend code.

# markify_app

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
