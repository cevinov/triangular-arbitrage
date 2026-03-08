from fastapi import FastAPI, Query
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import os
import sys
import asyncio
import json
from backend.logger import log_manager

app = FastAPI(title="Triangular Arbitrage Bot API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/app", StaticFiles(directory=static_dir, html=True), name="static")

from fastapi import Request

@app.get("/api/logs")
async def get_logs(request: Request):
    async def event_generator():
        try:
            while True:
                # Check for client disconnection
                if await request.is_disconnected():
                    break
                    
                # Check for shutdown flag as a fallback
                if is_shutting_down:
                    break

                # Get all available messages to reduce latency/overhead
                messages = []
                while not log_manager.log_queue.empty():
                    messages.append(log_manager.log_queue.get_nowait())
                
                if messages:
                    for msg in messages:
                        # SSE format: "data: <content>\n\n"
                        # Handle multi-line messages by splitting them
                        for line in msg.splitlines():
                            if line.strip(): # Only yield non-empty lines
                                yield f"data: {line}\n\n"
                
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            # Handle client disconnection or server shutdown
            pass
        except Exception as e:
            print(f"Error in log stream: {e}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# JSON Data Viewer Endpoints
ALLOWED_FILES = {
    "binance_groups": {
        "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../binance/triangular_groups.json")),
        "name": "Binance Triangular Groups"
    },
    "indodax_triangles": {
        "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../indodax/triangles.json")),
        "name": "Indodax Triangles"
    }
}

@app.get("/api/data/files")
def get_data_files():
    files = []
    
    # Add static allowed files
    for k, v in ALLOWED_FILES.items():
        file_info = {"id": k, "name": v["name"], "last_modified": "N/A"}
        try:
            if os.path.exists(v["path"]):
                mtime = os.path.getmtime(v["path"])
                import datetime
                dt = datetime.datetime.fromtimestamp(mtime)
                file_info["last_modified"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        files.append(file_info)
    
    # Add dynamic session files from results directory
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results"))
    if os.path.exists(results_dir):
        try:
            for filename in os.listdir(results_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(results_dir, filename)
                    mtime = os.path.getmtime(file_path)
                    import datetime
                    dt = datetime.datetime.fromtimestamp(mtime)
                    
                    # Create a readable name from filename
                    name = filename.replace(".json", "").replace("_", " ").title()
                    
                    files.append({
                        "id": f"result:{filename}", # Prefix to distinguish from static files
                        "name": name,
                        "last_modified": dt.strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            print(f"Error listing results files: {e}")
            
    # Sort files by last modified (newest first)
    files.sort(key=lambda x: x["last_modified"], reverse=True)
    
    return files

@app.get("/api/data/content")
def get_data_content(file_id: str):
    file_path = None
    
    if file_id.startswith("result:"):
        # Handle dynamic result files
        filename = file_id.split(":", 1)[1]
        # Security check: ensure no directory traversal
        if "/" in filename or "\\" in filename or ".." in filename:
             return {"error": "Invalid filename"}
             
        results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results"))
        file_path = os.path.join(results_dir, filename)
    elif file_id in ALLOWED_FILES:
        # Handle static allowed files
        file_path = ALLOWED_FILES[file_id]["path"]
    else:
        return {"error": "Invalid file ID"}
    
    try:
        if not os.path.exists(file_path):
             return {"error": "File not found"}
        
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}

@app.get("/api/analysis")
def get_analysis(files: Optional[List[str]] = Query(None)):
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results"))
    
    stats = {
        "binance": {
            "total_profit_usd": 0.0,
            "trade_count": 0,
            "profit_history": [], # {date: str, profit: float}
            "top_pairs": {} # {pair_str: count}
        },
        "indodax": {
            "total_profit_idr": 0.0,
            "trade_count": 0,
            "profit_history": [],
            "top_pairs": {}
        }
    }
    
    if not os.path.exists(results_dir):
        return stats
        
    try:
        for filename in os.listdir(results_dir):
            if not filename.endswith(".json"):
                continue
            
            # Filter by selected files if provided
            if files and filename not in files:
                continue
                
            file_path = os.path.join(results_dir, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    
                # Handle list of opportunities (standard format)
                if isinstance(data, list):
                    items = data
                else:
                    items = [data] # Handle single object if any
                    
                for item in items:
                    # Determine exchange based on filename or content
                    is_binance = "binance" in filename.lower()
                    is_indodax = "indodax" in filename.lower()
                    
                    if is_binance:
                        profit = float(item.get("profit_loss", 0))
                        stats["binance"]["total_profit_usd"] += profit
                        stats["binance"]["trade_count"] += 1
                        
                        # Extract date
                        found_at = item.get("foundAt", "")
                        if found_at:
                            stats["binance"]["profit_history"].append({"date": found_at, "profit": profit})
                            
                        # Extract pair path
                        path = f"{item.get('contract_1', ['',''])[0]}->{item.get('contract_2', ['',''])[0]}->{item.get('contract_3', ['',''])[0]}"
                        stats["binance"]["top_pairs"][path] = stats["binance"]["top_pairs"].get(path, 0) + 1
                        
                    elif is_indodax:
                        profit = float(item.get("profit_loss", 0))
                        stats["indodax"]["total_profit_idr"] += profit
                        stats["indodax"]["trade_count"] += 1
                        
                        found_at = item.get("foundAt", "")
                        if found_at:
                            stats["indodax"]["profit_history"].append({"date": found_at, "profit": profit})
                            
                        # Extract pair path (Indodax format might vary slightly in JSON)
                        # Trying to reconstruct from contracts if available, or use a generic key
                        c1 = item.get('contract_1', ['',''])
                        c2 = item.get('contract_2', ['',''])
                        c3 = item.get('contract_3', ['',''])
                        if isinstance(c1, list) and len(c1) > 0:
                             path = f"{c1[0]}->{c2[0]}->{c3[0]}"
                        else:
                             path = "Unknown Path"
                        stats["indodax"]["top_pairs"][path] = stats["indodax"]["top_pairs"].get(path, 0) + 1

            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue
                
        # Sort history by date
        stats["binance"]["profit_history"].sort(key=lambda x: x["date"])
        stats["indodax"]["profit_history"].sort(key=lambda x: x["date"])
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        
    return stats

from pydantic import BaseModel
from backend.bots.binance_bot import bot as binance_bot
from backend.bots.indodax_bot import bot as indodax_bot

class ConfigRequest(BaseModel):
    amount: Optional[float] = None
    fee: Optional[float] = None

@app.get("/")
def read_root():
    return {"status": "online", "message": "Triangular Arbitrage Bot API is running"}

@app.get("/api/bot/{exchange}/status")
def get_status(exchange: str):
    if exchange.lower() == "binance":
        return binance_bot.get_status()
    elif exchange.lower() == "indodax":
        return indodax_bot.get_status()
    return {"error": "Invalid exchange"}

@app.post("/api/bot/{exchange}/start")
def start_bot(exchange: str):
    if exchange.lower() == "binance":
        return {"message": binance_bot.start()}
    elif exchange.lower() == "indodax":
        return {"message": indodax_bot.start()}
    return {"error": "Invalid exchange"}

@app.post("/api/bot/{exchange}/stop")
def stop_bot(exchange: str):
    if exchange.lower() == "binance":
        return {"message": binance_bot.stop()}
    elif exchange.lower() == "indodax":
        return {"message": indodax_bot.stop()}
    return {"error": "Invalid exchange"}

@app.post("/api/bot/{exchange}/config")
def config_bot(exchange: str, config: ConfigRequest):
    if exchange.lower() == "binance":
        if config.amount is not None:
            binance_bot.initial_amount = config.amount
        if config.fee is not None:
            binance_bot.fee = config.fee
        return {"message": f"Binance config updated."}
    elif exchange.lower() == "indodax":
        if config.amount is not None:
            indodax_bot.initial_amount = config.amount
        if config.fee is not None:
            indodax_bot.fee = config.fee
        return {"message": f"Indodax config updated."}
    return {"error": "Invalid exchange"}

# Global shutdown flag
is_shutting_down = False

import signal
import subprocess

def force_shutdown(signum, frame):
    print("\nReceived signal to stop. Force killing processes...")
    try:
        # Kill uvicorn process
        cmd = "ps -ef | grep 'uvicorn backend.main:app --reload' | grep -v grep | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True).decode()
        pids = result.strip().split('\n')
        
        for pid in pids:
            if pid:
                print(f"Killing PID: {pid}")
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
    except Exception as e:
        print(f"Error during force shutdown: {e}")
    finally:
        # Ensure this process exits
        os.kill(os.getpid(), signal.SIGKILL)

@app.on_event("startup")
async def startup_event():
    # Redirect stdout to capture logs when app starts
    sys.stdout = log_manager
    
    # Register aggressive signal handler for CTRL+C
    signal.signal(signal.SIGINT, force_shutdown)

@app.on_event("shutdown")
def shutdown_event():
    global is_shutting_down
    is_shutting_down = True
    
    # Stop log manager and restore stdout
    log_manager.stop()
    sys.stdout = log_manager.terminal

if __name__ == "__main__":
    # Run with: pyenv activate triarb && uvicorn backend.main:app --reload 
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, timeout_graceful_shutdown=1)