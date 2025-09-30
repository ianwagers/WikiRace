# Example Fixes for Critical Multiplayer Issues

This document provides concrete code examples for fixing the most critical issues identified in the review.

## Fix #1: Port Mismatch

### Current Code (BROKEN)
```python
# src/logic/Network.py line 41
def __init__(self, server_url: str = "http://127.0.0.1:8000"):  # Wrong port!
    super().__init__()
    self.server_url = server_url
    # ...
```

### Fixed Code
```python
# src/logic/Network.py line 41
def __init__(self, server_url: str = "http://127.0.0.1:8001"):  # Match server port
    super().__init__()
    self.server_url = server_url
    # ...
```

**Alternative**: Update the comment in config.py if 8000 was intended:
```python
# server/config.py line 16
PORT: int = 8000  # Changed back to 8000
```

---

## Fix #2: Rejoin During Active Games

### Current Code (BROKEN)
```python
# server/room_manager.py - join_room method
def join_room(self, room_code: str, player_socket_id: str, display_name: str) -> Optional[GameRoom]:
    room = self.get_room(room_code)
    if not room:
        return None
    
    # BLOCKS all IN_PROGRESS joins
    if room.game_state not in [GameState.LOBBY, GameState.COMPLETED]:
        logger.warning(f"Room {room_code} is in {room.game_state.value} state, cannot join")
        return None
    
    # Check if player name already exists in room
    existing_player = room.get_player_by_name(display_name)
    # ...
```

### Fixed Code
```python
# server/room_manager.py - join_room method
def join_room(self, room_code: str, player_socket_id: str, display_name: str) -> Optional[GameRoom]:
    room = self.get_room(room_code)
    if not room:
        return None
    
    # Check if player name already exists (for rejoin handling)
    existing_player = room.get_player_by_name(display_name)
    
    # ALLOW IN_PROGRESS if player is rejoining (was disconnected)
    if room.game_state not in [GameState.LOBBY, GameState.COMPLETED, GameState.IN_PROGRESS]:
        logger.warning(f"Room {room_code} is in {room.game_state.value} state, cannot join")
        return None
    
    # Additional check: for IN_PROGRESS, only allow if rejoining
    if room.game_state == GameState.IN_PROGRESS:
        if not existing_player or not existing_player.disconnected:
            logger.warning(f"Room {room_code} is IN_PROGRESS, only disconnected players can rejoin")
            return None
    
    # Rest of existing rejoin logic...
    if existing_player:
        if existing_player.socket_id == player_socket_id:
            # Same socket, just update mapping
            self.player_to_room[player_socket_id] = room_code
            return room
        elif existing_player.disconnected:
            # Rejoining with new socket
            logger.info(f"Player {display_name} rejoining room {room_code} with new socket ID")
            self.player_to_room.pop(existing_player.socket_id, None)
            existing_player.socket_id = player_socket_id
            existing_player.disconnected = False
            existing_player.last_activity = datetime.utcnow()
            self.player_to_room[player_socket_id] = room_code
            return room
        else:
            logger.warning(f"Player name '{display_name}' already exists in room {room_code}")
            return None
    
    # Rest of method for new joins...
```

---

## Fix #3: Blocking time.sleep() Calls

### Current Code (BROKEN)
```python
# src/logic/Network.py - connect_to_server method
def connect_to_server(self) -> bool:
    try:
        if not self.connected_to_server or not self.sio.connected:
            # ...
            self.sio.connect(self.server_url, wait_timeout=15)
            
            import time
            max_wait = 3.0
            wait_interval = 0.1
            waited = 0.0
            
            while waited < max_wait:
                if self.connected_to_server and self.sio.connected:
                    return True
                time.sleep(wait_interval)  # BLOCKS UI!
                waited += wait_interval
            # ...
```

### Fixed Code (Option 1: Use QEventLoop)
```python
# src/logic/Network.py - connect_to_server method
def connect_to_server(self) -> bool:
    try:
        if not self.connected_to_server or not self.sio.connected:
            from PyQt6.QtCore import QEventLoop, QTimer
            
            self.sio.connect(self.server_url, wait_timeout=15)
            
            # Use QEventLoop instead of blocking sleep
            loop = QEventLoop()
            max_wait_ms = 3000  # 3 seconds
            elapsed = 0
            check_interval = 100  # 100ms
            
            def check_connection():
                nonlocal elapsed
                if self.connected_to_server and self.sio.connected:
                    loop.quit()
                else:
                    elapsed += check_interval
                    if elapsed >= max_wait_ms:
                        loop.quit()
                    else:
                        QTimer.singleShot(check_interval, check_connection)
            
            # Start checking
            QTimer.singleShot(0, check_connection)
            loop.exec()  # Process events without blocking
            
            if self.connected_to_server and self.sio.connected:
                return True
            # ...
```

### Fixed Code (Option 2: Make Async/Callback Based)
```python
# src/logic/Network.py - Better approach: don't wait synchronously at all
def connect_to_server(self, callback=None):
    """Connect to server asynchronously"""
    try:
        if not self.connected_to_server or not self.sio.connected:
            self.sio.connect(self.server_url, wait_timeout=15)
            
            # Set up timeout to check if connected
            self._connect_callback = callback
            QTimer.singleShot(3000, self._check_connection_timeout)
            
            # Return immediately, connection will be confirmed via signal
            return True
    except Exception as e:
        print(f"❌ Failed to initiate connection: {e}")
        return False

def _check_connection_timeout(self):
    """Called after connection timeout"""
    if self.connected_to_server and self.sio.connected:
        if self._connect_callback:
            self._connect_callback(True)
    else:
        print(f"⚠️ Connection timeout")
        if self._connect_callback:
            self._connect_callback(False)
```

---

## Fix #4: sio Set to None Causing Crashes

### Current Code (BROKEN)
```python
# src/logic/Network.py
def cleanup_network_resources(self):
    try:
        # ...
        self.sio = None  # DANGER!
    except Exception as e:
        # ...

def send_heartbeat(self):
    if self.connected_to_server and self.sio.connected:  # Crashes if sio is None!
        # ...
```

### Fixed Code
```python
# src/logic/Network.py
def cleanup_network_resources(self):
    try:
        # ...
        # Don't set to None, just disconnect
        # self.sio = None  # REMOVED
        print(f"✅ Network resources cleaned up")
    except Exception as e:
        # ...

def send_heartbeat(self):
    # Check sio exists first
    if self.sio is not None and self.connected_to_server and self.sio.connected:
        try:
            import time
            self.sio.emit('ping', {'timestamp': time.time()})
            print("💓 Heartbeat sent")
        except Exception as e:
            print(f"💓 Heartbeat failed: {e}")
```

**Alternative**: Keep sio=None but check everywhere:
```python
def _is_connection_healthy(self) -> bool:
    try:
        # Add sio None check
        if self.sio is None:
            return False
            
        if not self.connected_to_server:
            return False
        # ... rest of checks
```

---

## Fix #5: Consolidate Duplicate Methods

### Current Code (CONFUSING)
```python
# src/logic/Network.py
def send_player_progress(self, page_url: str, page_title: str):
    """Send detailed player progress update to server"""
    # Implementation 1
    
def send_player_progress_update(self, current_page: str, links_used: int):
    """Send player progress update to server"""
    # Implementation 2 (similar but different!)
```

### Fixed Code
```python
# src/logic/Network.py
def send_player_progress(self, page_url: str, page_title: str, links_used: int = 0):
    """Send player progress update to server
    
    Args:
        page_url: URL of current page
        page_title: Title of current page
        links_used: Number of links clicked (optional)
    """
    try:
        if not self._is_connection_healthy():
            print(f"⚠️ Cannot send progress - connection unhealthy")
            return
        
        self.sio.emit('player_progress', {
            'room_code': self.current_room,
            'player_name': self.player_name,
            'page_url': page_url,
            'page_title': page_title,
            'links_used': links_used
        })
        print(f"📊 Sent progress: {page_title} ({links_used} links)")
    except Exception as e:
        print(f"❌ Failed to send progress: {e}")

# Remove send_player_progress_update completely, or make it an alias:
def send_player_progress_update(self, current_page: str, links_used: int):
    """Deprecated: Use send_player_progress instead"""
    return self.send_player_progress(current_page, current_page, links_used)
```

---

## Fix #6: Add Rate Limiting to Socket Handlers

### New Code to Add
```python
# server/socket_handlers.py - Add at top of file
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# Rate limiting state
_rate_limit_state = defaultdict(lambda: {'count': 0, 'reset_time': datetime.utcnow()})
_RATE_LIMIT_WINDOW = 1.0  # 1 second
_RATE_LIMIT_MAX_REQUESTS = 10  # Max requests per window

def rate_limit(max_requests=10, window_seconds=1.0):
    """Decorator to rate limit socket events per client"""
    def decorator(func):
        async def wrapper(sid, *args, **kwargs):
            # Check rate limit
            now = datetime.utcnow()
            state = _rate_limit_state[sid]
            
            # Reset counter if window expired
            if now > state['reset_time']:
                state['count'] = 0
                state['reset_time'] = now + timedelta(seconds=window_seconds)
            
            # Check if over limit
            if state['count'] >= max_requests:
                logger.warning(f"Rate limit exceeded for {sid}")
                await sio.emit('error', {
                    'message': 'Rate limit exceeded',
                    'retry_after': (state['reset_time'] - now).total_seconds()
                }, room=sid)
                return
            
            # Increment counter
            state['count'] += 1
            
            # Call actual handler
            return await func(sid, *args, **kwargs)
        return wrapper
    return decorator

# Apply to handlers
@sio.event
@rate_limit(max_requests=30, window_seconds=1.0)  # 30 progress updates per second max
async def player_progress(sid, data):
    """Handle player progress update"""
    # ... existing implementation

@sio.event
@rate_limit(max_requests=5, window_seconds=1.0)  # 5 color changes per second max
async def player_color_update(sid, data):
    """Handle player color update"""
    # ... existing implementation
```

---

## Testing the Fixes

After applying fixes, run:
```bash
python3 test_multiplayer_issues.py
```

Expected output:
```
✅ PASSED: Port Mismatch
✅ PASSED: Duplicate Methods
✅ PASSED: Blocking Sleep Calls
✅ PASSED: Rejoin Logic
✅ PASSED: Connection Health Check
✅ PASSED: Cleanup Sets sio to None
```

## Summary

These fixes address:
1. ✅ Port mismatch (1 line change)
2. ✅ Rejoin logic (add IN_PROGRESS to allowed states)
3. ✅ Blocking sleep (replace with QTimer/async)
4. ✅ sio=None crashes (add None checks or don't set to None)
5. ✅ Duplicate methods (consolidate)
6. ✅ Rate limiting (add decorator)

Total effort: ~4-5 hours to implement and test all fixes.
