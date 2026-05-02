from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer

from contract_guardian.pipeline import ContractRiskPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contract Guardian Agent: review contract risk with a multi-agent pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser("review", help="Review one contract file.")
    review_parser.add_argument("--input", required=True, help="Path to the contract text file.")
    review_parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for generated reports.",
    )

    demo_parser = subparsers.add_parser("demo", help="Run built-in sample contracts.")
    demo_parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for generated reports.",
    )

    serve_parser = subparsers.add_parser("serve-demo", help="Serve the frontend demo locally.")
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for the local demo server.",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=4173,
        help="Port for the local demo server.",
    )
    return parser


def run_review(input_path: str, output_dir: str) -> None:
    pipeline = ContractRiskPipeline()
    result = pipeline.run(Path(input_path), Path(output_dir))
    print(f"Reviewed: {result.contract_name}")
    print(f"Risk level: {result.assessment.risk_level}")
    print(f"Risk score: {result.assessment.risk_score}")
    print(f"Human review required: {result.assessment.requires_human_review}")
    print(f"Markdown report: {result.markdown_path}")
    print(f"JSON summary: {result.json_path}")


def run_demo(output_dir: str) -> None:
    samples = [
        "data/contracts/high_risk_saas_contract.txt",
        "data/contracts/low_risk_saas_contract.txt",
    ]
    for sample in samples:
        run_review(sample, output_dir)
        print("-" * 60)


def run_demo_server(host: str, port: int) -> None:
    demo_dir = Path(__file__).parent / "demo"
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(
        *args,
        directory=str(demo_dir),
        **kwargs,
    )

    with TCPServer((host, port), handler) as httpd:
        print(f"Serving demo at http://{host}:{port}")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "review":
        run_review(args.input, args.output_dir)
    elif args.command == "demo":
        run_demo(args.output_dir)
    elif args.command == "serve-demo":
        run_demo_server(args.host, args.port)


if __name__ == "__main__":
    main()
