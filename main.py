from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
from dotenv import load_dotenv
import os
import shutil
import uuid
import markdown

# --- Custom Imports ---
from pipeline_logic import load_and_clean_data, predict_categories, generate_strategic_insights

# --- Load Environment Variables ---
load_dotenv()

# --- FastAPI App Configuration ---
app = FastAPI(title="Product Insight Generator")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="results"), name="output")

templates = Jinja2Templates(directory="templates")

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- Helper Function ---
def cleanup_files(session_dir: str):
    """Background task to clean up a session's result files."""
    print(f"🧹 Cleaning up results directory: {session_dir}")
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-and-process/")
async def upload_and_process(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(RESULTS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    input_filepath = os.path.join(session_dir, "input.csv")

    try:
        # Save uploaded file
        with open(input_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Data processing and prediction
        df = load_and_clean_data(input_filepath)
        predicted_df = predict_categories(df)
        predicted_df.to_csv(os.path.join(session_dir, "tagged_products.csv"), index=False)

        # Step 2: Generate charts and insights (includes Gemini feedback)
        result = generate_strategic_insights(predicted_df, session_dir)  # REMOVED .copy()
        
        print(f"✅ Processing complete for session: {session_id}")
        if result:
            print(f"✅ Feedback length: {len(result.get('feedback', ''))} characters")

    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        cleanup_files(session_dir)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return RedirectResponse(url=f"/results/{session_id}", status_code=303)

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def get_results_page(request: Request, session_id: str):
    session_dir = os.path.join(RESULTS_DIR, session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Results not found.")

    # Read feedback file
    feedback_file = os.path.join(session_dir, "client_feedback.md")
    feedback_content = ""
    feedback_html = ""
    
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                feedback_content = f.read()
            
            # Convert markdown to HTML for proper rendering
            feedback_html = markdown.markdown(feedback_content, extensions=['extra', 'nl2br'])
            
            print(f"✅ Loaded feedback: {len(feedback_content)} characters")
        except Exception as e:
            feedback_html = f"<p>Error loading feedback: {str(e)}</p>"
            print(f"❌ Error reading feedback: {str(e)}")
    else:
        print(f"⚠️ Feedback file not found: {feedback_file}")
        feedback_html = "<p><em>No AI feedback generated yet. Please refresh the page.</em></p>"

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "session_id": session_id,
            "feedback": feedback_html  # Pass HTML-rendered markdown
        },
    )

@app.get("/download/{session_id}")
async def download_results(session_id: str):
    session_dir = os.path.join(RESULTS_DIR, session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Results not found.")

    zip_path_base = os.path.join(RESULTS_DIR, f"results_{session_id}")
    shutil.make_archive(base_name=zip_path_base, format="zip", root_dir=session_dir)
    zip_filepath = f"{zip_path_base}.zip"

    cleanup_task = BackgroundTask(lambda: (cleanup_files(session_dir), os.remove(zip_filepath)))

    return FileResponse(
        path=zip_filepath,
        media_type="application/zip",
        filename="product_attribution_results.zip",
        background=cleanup_task,
    )
