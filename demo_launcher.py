#!/usr/bin/env python3
"""
EcoBloom P2P Demo Launcher
Starts 3 simulated farms with visual dashboard
"""

import sys
import os
import time
import webbrowser
from multiprocessing import Process

# Add your project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from peer import Peer
from websocket_bridge import WebSocketBridge


def start_farm(farm_id, host, port, bootstrap_peers=None):
    """
    Start a single farm peer with WebSocket bridge
    
    Args:
        farm_id: Farm identifier (A, B, or C)
        host: Host IP
        port: Port number
        bootstrap_peers: List of (host, port) tuples to connect to
    """
    print(f"\n{'='*50}")
    print(f"Starting Farm {farm_id}")
    print(f"Host: {host}:{port}")
    print(f"{'='*50}\n")
    
    # Create peer
    peer = Peer(host, port)
    peer.peer_id = f"Farm_{farm_id}"  # Override peer_id for demo
    peer.start_server()
    
    # Give server time to start
    time.sleep(1)
    
    # Connect to bootstrap peers
    if bootstrap_peers:
        for peer_host, peer_port in bootstrap_peers:
            print(f"[Farm {farm_id}] Connecting to {peer_host}:{peer_port}...")
            success = peer.connect_to_peer(peer_host, peer_port)
            if success:
                print(f"[Farm {farm_id}] ✓ Connected to {peer_host}:{peer_port}")
            else:
                print(f"[Farm {farm_id}] ✗ Failed to connect to {peer_host}:{peer_port}")
            time.sleep(0.5)
    
    # Start WebSocket bridge (only for Farm A - central dashboard)
    if farm_id == 'A':
        print(f"\n[Farm {farm_id}] Starting WebSocket dashboard bridge...")
        bridge = WebSocketBridge(peer, port=8765)
        bridge.run_in_thread()
        print(f"[Farm {farm_id}] ✓ WebSocket server running on ws://localhost:8765")
    
    # Keep peer running
    print(f"\n[Farm {farm_id}] Peer running. Monitoring network...")
    print(f"[Farm {farm_id}] Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
            # Optional: Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                print(f"[Farm {farm_id}] Status: {len(peer.connections)} connections, "
                      f"{len(peer.known_peers)} known peers")
    except KeyboardInterrupt:
        print(f"\n[Farm {farm_id}] Shutting down...")
        peer.close_current_peer()


def launch_demo():
    """
    Launch complete demo with 3 farms
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║            🌱 ECOBLOOM P2P DEMO LAUNCHER 🌱             ║
    ║                                                          ║
    ║         AI-Powered Pest Alert Network Demo              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    Starting 3 farm peers with P2P networking...
    """)
    
    # Farm configurations
    farms_config = [
        {
            'id': 'A',
            'host': 'localhost',
            'port': 5001,
            'bootstrap': []  # First farm, no bootstrap
        },
        {
            'id': 'B',
            'host': 'localhost',
            'port': 5002,
            'bootstrap': [('localhost', 5001)]  # Connect to Farm A
        },
        {
            'id': 'C',
            'host': 'localhost',
            'port': 5003,
            'bootstrap': [('localhost', 5001), ('localhost', 5002)]  # Connect to both
        }
    ]
    
    # Start farms in separate processes
    processes = []
    
    for config in farms_config:
        p = Process(
            target=start_farm,
            args=(
                config['id'],
                config['host'],
                config['port'],
                config['bootstrap']
            )
        )
        p.start()
        processes.append(p)
        time.sleep(2)  # Stagger startup
    
    # Wait for network to stabilize
    print("\n⏳ Waiting for P2P network to establish...")
    time.sleep(3)
    
    # Open dashboard in browser
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    
    if os.path.exists(dashboard_path):
        print("\n🌐 Opening dashboard in browser...")
        webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
    else:
        print("\n⚠️  Dashboard file not found!")
        print(f"Expected location: {dashboard_path}")
        print("Please save the HTML dashboard as 'dashboard.html' in this directory")
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO READY!                           ║
    ╚══════════════════════════════════════════════════════════╝
    
    ✓ Farm A running on localhost:5001
    ✓ Farm B running on localhost:5002
    ✓ Farm C running on localhost:5003
    ✓ P2P network established (mesh topology)
    ✓ WebSocket bridge active on ws://localhost:8765
    
    📊 DASHBOARD: Should open automatically in browser
        If not, open dashboard.html manually
    
    Press Ctrl+C to stop all farms
    """)
    
    # Wait for processes
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all farms...")
        for p in processes:
            p.terminate()
        print("✓ All farms stopped. Demo ended.\n")


def launch_single_farm_demo():
    """
    Simpler demo: One farm with simulated peers (no multiprocessing)
    Useful for quick testing or if multiprocessing has issues
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        🌱 ECOBLOOM SINGLE-FARM DEMO 🌱                  ║
    ╚══════════════════════════════════════════════════════════╝
    
    Starting single farm with simulated P2P network...
    """)
    
    peer = Peer('localhost', 5001)
    peer.peer_id = "Farm_A"
    peer.start_server()
    
    # Simulate known peers (for dashboard display)
    peer.known_peers = {
        'Farm_B': {'host': 'localhost', 'port': 5002},
        'Farm_C': {'host': 'localhost', 'port': 5003}
    }
    
    # Start WebSocket bridge
    bridge = WebSocketBridge(peer, port=8765)
    bridge.run_in_thread()
    
    time.sleep(1)
    
    # Open dashboard
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    if os.path.exists(dashboard_path):
        webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
    
    print("""
    ✓ Farm A running on localhost:5001
    ✓ WebSocket bridge active
    ✓ Dashboard opened
    
    NOTE: This is single-farm mode. Alerts will be simulated.
    For full P2P demo, use multi-farm mode.
    
    Press Ctrl+C to stop
    """)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping farm...")
        peer.close_current_peer()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EcoBloom P2P Demo Launcher')
    parser.add_argument(
        '--mode',
        choices=['full', 'single'],
        default='full',
        help='Demo mode: full (3 farms) or single (1 farm with simulation)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        launch_demo()
    else:
        launch_single_farm_demo()