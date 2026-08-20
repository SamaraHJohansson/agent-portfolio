"""
Search Visibility Agent
=======================
Audits any website for traditional SEO health and AI search visibility.

Usage:
    python agent.py --url https://yourwebsite.com
    python agent.py --url https://yourwebsite.com --mode audit
    python agent.py --url https://yourwebsite.com --mode full
    python agent.py --url https://yourwebsite.com --module technical_health

Author: Samara H. Johansson
GitHub: https://github.com/SamaraHJohansson/agent-portfolio
"""

import argparse
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()


def print_banner():
    """Print the agent banner on startup."""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║           SEARCH VISIBILITY AGENT                        ║
║           Traditional SEO + AI Search Intelligence       ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)


def validate_environment():
    """Check that required API keys are present."""
    missing = []

    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")

    if not os.getenv("PERPLEXITY_API_KEY"):
        missing.append("PERPLEXITY_API_KEY")

    if missing:
        print(f"{Fore.YELLOW}⚠️  Warning: Missing API keys: {', '.join(missing)}")
        print(f"   AI search modules will be skipped.")
        print(f"   Add keys to your .env file to enable full functionality.{Style.RESET_ALL}\n")
        return False

    return True


def validate_url(url):
    """Basic URL validation and normalization."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def create_output_dirs():
    """Ensure output directories exist."""
    dirs = [
        "outputs",
        "outputs/briefs",
        "outputs/rewrites"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def run_module(module_name, url, results):
    """Dynamically import and run a single module."""
    try:
        print(f"{Fore.CYAN}▶ Running: {module_name}{Style.RESET_ALL}")
        module = __import__(f"modules.{module_name}", fromlist=[module_name])
        result = module.run(url)
        results[module_name] = result
        print(f"{Fore.GREEN}✓ Complete: {module_name}{Style.RESET_ALL}\n")
        return result
    except ModuleNotFoundError:
        print(f"{Fore.YELLOW}⚠ Module not yet built: {module_name} — skipping{Style.RESET_ALL}\n")
        results[module_name] = {"status": "skipped", "reason": "module not yet built"}
        return None
    except Exception as e:
        print(f"{Fore.RED}✗ Error in {module_name}: {str(e)}{Style.RESET_ALL}\n")
        results[module_name] = {"status": "error", "reason": str(e)}
        return None


def run_audit_mode(url, results, has_api_keys):
    """Run audit-only pipeline: crawl + technical health + answer readiness."""
    print(f"{Fore.WHITE}Mode: Audit Only{Style.RESET_ALL}\n")

    run_module("site_crawler", url, results)
    run_module("technical_health", url, results)

    if has_api_keys:
        run_module("answer_readiness", url, results)
    else:
        print(f"{Fore.YELLOW}⚠ Skipping answer_readiness — API keys required{Style.RESET_ALL}\n")

    return results


def run_full_mode(url, results, has_api_keys):
    """Run full pipeline: all modules."""
    print(f"{Fore.WHITE}Mode: Full Pipeline{Style.RESET_ALL}\n")

    # Layer 1: Foundation (no API keys needed)
    run_module("site_crawler", url, results)
    run_module("technical_health", url, results)

    if has_api_keys:
        # Layer 2: AI Search Intelligence
        run_module("answer_readiness", url, results)
        run_module("ai_search_gap", url, results)

        # Layer 3: Output Generation
        run_module("brief_generator", url, results)
        run_module("rewrite_engine", url, results)
    else:
        print(f"{Fore.YELLOW}⚠ Skipping AI modules — API keys required{Style.RESET_ALL}\n")
        print(f"  Add OPENAI_API_KEY and PERPLEXITY_API_KEY to your .env file")
        print(f"  to enable: answer_readiness, ai_search_gap, brief_generator, rewrite_engine\n")

    return results


def generate_audit_report(url, results, has_api_keys):
    """Generate the HTML audit report from all module results."""
    try:
        print(f"{Fore.CYAN}▶ Generating audit report...{Style.RESET_ALL}")
        from modules.report_generator import generate
        report_path = generate(url, results)
        print(f"{Fore.GREEN}✓ Audit report saved: {report_path}{Style.RESET_ALL}\n")
        return report_path
    except ModuleNotFoundError:
        report_path = "outputs/audit_report.html"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Visibility Audit — {url}</title>
</head>
<body>
    <h1>Search Visibility Audit</h1>
    <p><strong>URL:</strong> {url}</p>
    <p><strong>Generated:</strong> {timestamp}</p>
</body>
</html>"""

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"{Fore.GREEN}✓ Basic audit report saved: {report_path}{Style.RESET_ALL}\n")
        return report_path


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Search Visibility Agent — SEO + AI Search Intelligence"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="The website URL to audit (e.g. https://samaglobal.com)"
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "full"],
        default="full",
        help="audit = crawl + technical health only | full = all modules (default)"
    )
    parser.add_argument(
        "--module",
        help="Run a single module only (e.g. --module technical_health)"
    )

    args = parser.parse_args()

    url = validate_url(args.url)
    print(f"{Fore.WHITE}Target URL: {Fore.CYAN}{url}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Started:    {Fore.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")

    has_api_keys = validate_environment()
    create_output_dirs()
    results = {}

    if args.module:
        print(f"{Fore.WHITE}Mode: Single Module — {args.module}{Style.RESET_ALL}\n")
        run_module(args.module, url, results)
    elif args.mode == "audit":
        run_audit_mode(url, results, has_api_keys)
    else:
        run_full_mode(url, results, has_api_keys)

    report_path = generate_audit_report(url, results, has_api_keys)

    print(f"""
{Fore.CYAN}══════════════════════════════════════════════════════════
  RUN COMPLETE
══════════════════════════════════════════════════════════{Style.RESET_ALL}
  URL audited:   {url}
  Audit report:  {report_path}
  Briefs:        outputs/briefs/
  Rewrites:      outputs/rewrites/

Open outputs/index.html in your browser to view all results.
From there you can access the full audit report and all content briefs.
{Fore.CYAN}══════════════════════════════════════════════════════════{Style.RESET_ALL}
    """)


if __name__ == "__main__":
    main()
