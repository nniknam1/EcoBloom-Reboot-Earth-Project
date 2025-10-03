#!/usr/bin/env python3
"""
EcoBloom Pest Detection System - Main Entry Point
Multi-location farm monitoring with Raspberry Pi camera integration
"""

import argparse
import sys
from pathlib import Path

# Import modules
from modules.scheduler import PestMonitorScheduler
from modules.pest_detector import PestDetector
from modules.data_logger import DataLogger
from modules.camera_capture import CameraCapture
from modules.alert_system import AlertSystem


def print_banner():
    """Display welcome banner"""
    print("""
===============================================================

         EcoBloom Pest Detection System

      Multi-Location Farm Monitoring System
      Powered by Computer Vision & IoT
      Designed for Raspberry Pi Camera Traps

===============================================================
    """)


def run_scheduler(config_path):
    """Start the automated scheduler"""
    print("\n[*] Starting Automated Scheduler Mode\n")
    scheduler = PestMonitorScheduler(config_path)
    scheduler.start()


def run_manual_capture(config_path):
    """Run a single manual capture and analysis"""
    print("\n[*] Manual Capture Mode\n")
    scheduler = PestMonitorScheduler(config_path)
    result = scheduler.run_manual_cycle()

    if result:
        print("\n[+] Manual capture completed successfully!")
        print(f"   Pests detected: {result['pest_count']}")
        print(f"   Risk level: {result['risk_level']}")
        print(f"   Output image: {result['output_path']}")
    else:
        print("\n[-] Manual capture failed")
        sys.exit(1)


def run_dashboard(config_path):
    """Start the web dashboard"""
    print("\n[*] Starting Web Dashboard\n")
    import subprocess
    subprocess.run([sys.executable, 'dashboard.py'])


def analyze_image(image_path, config_path):
    """Analyze a single image"""
    print(f"\n[*] Analyzing image: {image_path}\n")

    detector = PestDetector(config_path)
    logger = DataLogger(config_path)

    # Detect pests
    result = detector.detect_pests(image_path)

    # Log to database
    logger.log_detection(result)

    print(f"\n[+] Analysis complete!")
    print(f"   Pests detected: {result['pest_count']}")
    print(f"   Risk level: {result['risk_level']}")
    print(f"   Output image: {result['output_path']}")

    logger.close()


def batch_analyze(folder_path, config_path):
    """Analyze all images in a folder"""
    print(f"\n[*] Batch analyzing folder: {folder_path}\n")

    detector = PestDetector(config_path)
    logger = DataLogger(config_path)

    result = detector.batch_detect(folder_path)

    # Log all results
    for detection in result['results']:
        logger.log_detection(detection)

    print(f"\n[+] Batch analysis complete!")
    print(f"   Total images: {result['total_images']}")
    print(f"   Total pests: {result['total_pests_detected']}")
    print(f"   Average pests/image: {result['average_pests_per_image']}")

    logger.close()


def show_statistics(config_path, days=7, camera_id=None):
    """Display statistics"""
    print(f"\n[*] Statistics (Last {days} days)\n")

    logger = DataLogger(config_path)

    # Overall stats
    stats = logger.get_statistics(camera_id=camera_id, days=days)

    if stats:
        print(f"Camera: {stats['camera_id']}")
        print(f"Total Captures: {stats['total_captures']}")
        print(f"Total Pests: {stats['total_pests']}")
        print(f"Average Pests/Capture: {stats['avg_pests']:.2f}")
        print(f"Max Pests (Single Capture): {stats['max_pests']}")
        print(f"Min Pests (Single Capture): {stats['min_pests']}")

        # Trend analysis
        print(f"\n[*] Daily Trends:\n")
        trends = logger.get_trend_analysis(camera_id=camera_id, days=days)

        for trend in trends:
            print(f"{trend['date']}: {trend['total_pests']} pests ({trend['captures']} captures, avg: {trend['avg_pests']:.1f})")
    else:
        print("No data available for the specified period")

    logger.close()


def test_alerts(config_path):
    """Test alert system"""
    print("\n[*] Testing Alert System\n")
    alerts = AlertSystem(config_path)
    alerts.test_alerts()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='EcoBloom Pest Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --scheduler              Start automated monitoring
  python main.py --dashboard              Launch web dashboard
  python main.py --capture                Trigger manual camera capture
  python main.py --analyze image.jpg      Analyze single image
  python main.py --batch ./images/        Analyze folder of images
  python main.py --stats --days 7         Show 7-day statistics
  python main.py --test-alerts            Test email/SMS alerts
        """
    )

    parser.add_argument('--config', default='config.json',
                        help='Path to config file (default: config.json)')

    # Operation modes
    parser.add_argument('--scheduler', action='store_true',
                        help='Start automated scheduler (continuous monitoring)')
    parser.add_argument('--dashboard', action='store_true',
                        help='Start web dashboard')
    parser.add_argument('--capture', action='store_true',
                        help='Trigger single manual capture')
    parser.add_argument('--analyze', metavar='IMAGE',
                        help='Analyze a single image file')
    parser.add_argument('--batch', metavar='FOLDER',
                        help='Batch analyze all images in folder')
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics')
    parser.add_argument('--test-alerts', action='store_true',
                        help='Test alert system')

    # Options
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days for statistics (default: 7)')
    parser.add_argument('--camera-id', type=str,
                        help='Filter by specific camera ID')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Execute based on mode
    if args.scheduler:
        run_scheduler(args.config)

    elif args.dashboard:
        run_dashboard(args.config)

    elif args.capture:
        run_manual_capture(args.config)

    elif args.analyze:
        if not Path(args.analyze).exists():
            print(f"[-] Error: File not found: {args.analyze}")
            sys.exit(1)
        analyze_image(args.analyze, args.config)

    elif args.batch:
        if not Path(args.batch).is_dir():
            print(f"[-] Error: Not a directory: {args.batch}")
            sys.exit(1)
        batch_analyze(args.batch, args.config)

    elif args.stats:
        show_statistics(args.config, args.days, args.camera_id)

    elif args.test_alerts:
        test_alerts(args.config)

    else:
        parser.print_help()
        print("\n[*] Tip: Start with --dashboard for a visual interface")
        print("   or --scheduler for automated monitoring")


if __name__ == "__main__":
    main()
