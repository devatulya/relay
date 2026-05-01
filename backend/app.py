import asyncio
from quart import Quart, request, jsonify, render_template
from backend.main import OutreachOrchestrator
from backend.utils.logger import logger

app = Quart(__name__, template_folder="../templates", static_folder="../static")

# Global Orchestrator to maintain state (and browser session)
orchestrator = OutreachOrchestrator()

@app.route('/')
async def welcome():
    return await render_template('welcome.html')

@app.route('/connect')
async def connect():
    return await render_template('whatsapp_check.html')

@app.route('/form')
async def form():
    return await render_template('form.html')

@app.route('/progress')
async def progress():
    return await render_template('progress.html')

@app.route('/preview')
async def preview():
    return await render_template('preview.html')

@app.route('/summary')
async def summary():
    return await render_template('summary.html')


@app.route('/docs')
async def docs():
    return await render_template('docs.html')

@app.route('/security')
async def security():
    return await render_template('security.html')

@app.route('/privacy')
async def privacy():
    return await render_template('privacy.html')

@app.route('/terms')
async def terms():
    return await render_template('terms.html')

@app.route('/help')
async def help_center():
    return await render_template('help.html')

# --- API Endpoints (Async) ---

@app.route('/check-whatsapp', methods=['GET'])
async def check_whatsapp():
    """
    Endpoint to check WhatsApp connection status.
    """
    try:
        launch_param = request.args.get('launch', 'false')
        should_launch = launch_param.lower() == 'true'
        
        # Use global orchestrator await
        status = await orchestrator.check_connection(launch_browser=should_launch)
        return jsonify({"status": status})
    except Exception as e:
        logger.error(f"Check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
async def get_status():
    """
    Returns the real-time status of the outreach process.
    """
    return jsonify(orchestrator.get_status())

@app.route('/verify-sheet', methods=['POST'])
async def verify_sheet():
    """
    Verifies if a Google Sheet URL is accessible and has the correct structure.
    """
    try:
        data = await request.get_json()
        if not data or 'url' not in data:
            return jsonify({"status": "error", "message": "Missing URL"}), 400
            
        url = data['url']
        # Extract Sheet ID from URL
        import re
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            return jsonify({"status": "error", "message": "Invalid Google Sheet URL format"}), 400
            
        sheet_id = match.group(1)
        
        # Use gspread (open_by_key) - NOT the raw service API
        from backend.services.google_sheets import GoogleSheetsService
        sheet_service = GoogleSheetsService()
        sheet_service.connect()  # sets sheet_service.client (gspread client)
        
        # open_by_key will raise if the sheet is not shared / not accessible
        spreadsheet = sheet_service.client.open_by_key(sheet_id)
        title = spreadsheet.title
        
        return jsonify({
            "status": "success", 
            "message": f"Successfully connected to '{title}'",
            "sheet_id": sheet_id
        })
    except Exception as e:
        logger.error(f"Sheet verification failed: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Could not access sheet. Make sure it is shared with: influenze-relay-sa@influenze-487418.iam.gserviceaccount.com"
        }), 400


@app.route('/launch-automation', methods=['POST'])
async def launch_automation():
    """
    Receives brand payload, fetches and filters creators, and returns them for preview.
    """
    data = await request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    logger.info("Received preview generation request")
    
    try:
        results = await orchestrator.start_outreach(data)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop-automation', methods=['POST'])
async def stop_automation():
    """
    Stops the ongoing outreach process.
    """
    orchestrator.stop()
    return jsonify({"status": "success", "message": "Stop request sent"})

@app.route('/execute-automation', methods=['POST'])
async def execute_automation():
    """
    Starts the actual background message sending process using the previewly verified payload.
    """
    data = await request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    logger.info("Received execution request")
    
    async def run_task(payload):
        try:
            await orchestrator.execute_outreach(payload)
        except Exception as e:
            logger.error(f"Background execution failed: {e}")

    # Fire and forget background task
    asyncio.create_task(run_task(data))
    
    return jsonify({"message": "Outreach started", "status": "processing"})

if __name__ == '__main__':
    # Running directly from backend/app.py
    app.run(debug=True, port=5000)
