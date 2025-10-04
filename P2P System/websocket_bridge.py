import asyncio
import websockets
import json
from threading import Thread

class WebSocketBridge:
    """
    Bridges P2P system with web dashboard
    Broadcasts farm state updates to connected browsers
    """
    
    def __init__(self, peer, port=8765):
        self.peer = peer
        self.port = port
        self.connected_clients = set()
        self.running = False
        
    async def handler(self, websocket, path):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        print(f"Dashboard connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                print(f"Received dashboard command: {message}")
                await self.handle_dashboard_command(message)
            # Send initial state
            await self.send_state_update(websocket)
            
            # Listen for commands from dashboard
            async for message in websocket:
                await self.handle_dashboard_command(message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"Dashboard disconnected: {websocket.remote_address}")
    
    async def handle_dashboard_command(self, message):
        """Process commands from web dashboard"""
        try:
            print(f"Processing dashboard command: {message}")
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'trigger_outbreak':
                farm_id = data.get('farm_id')
                print(f"Triggering outbreak for farm {farm_id}")
                await self.trigger_outbreak(farm_id)
                
            elif command == 'request_state':
                print("Handling state request")
                await self.broadcast_state()
                
        except json.JSONDecodeError:
            print(f"Invalid JSON from dashboard: {message}")
    
    async def trigger_outbreak(self, farm_id):
        """Simulate pest outbreak and send P2P alerts"""
        import random
        import time
        
        try:
            print(f"\n[WebSocket] Triggering outbreak for Farm {farm_id}")
            pest_count = random.randint(40, 70)
            print(f"[WebSocket] Generated pest count: {pest_count}")
            
            if not hasattr(self.peer, 'pest_handler'):
                print("[WebSocket] ERROR: PestAlertHandler not initialized!")
                return
                
            peers_alerted = self.peer.pest_handler.broadcast_pest_alert(pest_count, pest_type='whitefly')
            print(f"[WebSocket] Alert broadcasted to {peers_alerted} peers")
            
            # Update dashboard
            await self.broadcast_alert(farm_id, pest_count)
            
        except Exception as e:
            print(f"[WebSocket] Error triggering outbreak: {str(e)}")
        
        # Update dashboard
        await self.broadcast_alert(farm_id, pest_count)
    
    def get_farm_location(self, farm_id):
        """Map farm IDs to locations"""
        locations = {
            'A': 'Al Rayyan',
            'B': 'Al Wakrah', 
            'C': 'Umm Salal'
        }
        return locations.get(farm_id, 'Unknown')
    
    async def broadcast_alert(self, source_farm, pest_count):
        """Broadcast alert to all connected dashboards"""
        alert_data = {
            'type': 'pest_alert',
            'source_farm': source_farm,
            'pest_count': pest_count,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        if self.connected_clients:
            message = json.dumps(alert_data)
            await asyncio.wait([
                client.send(message) 
                for client in self.connected_clients
            ])
    
    async def broadcast_state(self):
        """Send current network state to dashboards"""
        state_data = {
            'type': 'state_update',
            'peer_id': self.peer.peer_id,
            'connections': len(self.peer.connections),
            'known_peers': list(self.peer.known_peers.keys()),
            'routing_table': dict(self.peer.router.routing_graph)
        }
        
        if self.connected_clients:
            message = json.dumps(state_data)
            await asyncio.wait([
                client.send(message) 
                for client in self.connected_clients
            ])
    
    async def send_state_update(self, websocket):
        """Send state to specific client"""
        state_data = {
            'type': 'state_update',
            'peer_id': self.peer.peer_id,
            'connections': len(self.peer.connections),
            'known_peers': list(self.peer.known_peers.keys())
        }
        await websocket.send(json.dumps(state_data))
    
    async def start_server(self):
        """Start WebSocket server"""
        self.running = True
        print(f"WebSocket server starting on ws://localhost:{self.port}")
        async with websockets.serve(self.handler, "localhost", self.port):
            await asyncio.Future()  # Run forever
    
    def run_in_thread(self):
        """Run WebSocket server in separate thread"""
        def run():
            asyncio.run(self.start_server())
        
        thread = Thread(target=run, daemon=True)
        thread.start()
        print(f"WebSocket bridge running on port {self.port}")