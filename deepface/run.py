"""
DeepFace Proctoring Microservice — Entry Point

Usage:
    python run.py
    python run.py --host 0.0.0.0 --port 8500 --reload
"""

import argparse

import uvicorn

from app.config import HOST, PORT


def main():
    parser = argparse.ArgumentParser(description="DeepFace Proctoring Microservice")
    parser.add_argument("--host", default=HOST, help=f"Host to bind to (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to bind to (default: {PORT})")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers (default: 1)")
    args = parser.parse_args()

    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║   DeepFace Proctoring Microservice               ║
    ║   Starting on http://{args.host}:{args.port}          ║
    ║   Docs: http://{args.host}:{args.port}/api/v1/docs    ║
    ╚══════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
