"""
Position State Management
Persists position state to JSON for recovery after restart
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PositionState:
    """Current position state"""
    symbol: str
    strategy: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    entry_time: str
    quantity: float
    tp_price: float
    sl_price: float
    atr_value: float
    order_value_usd: float
    
    # Optional fields
    entry_reason: Optional[str] = None
    indicators: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PositionState':
        """Create from dictionary"""
        return cls(**data)


class PositionStateManager:
    """
    Manages position state persistence
    """
    
    def __init__(self, state_file: str = './state/position_state.json'):
        """
        Initialize state manager
        
        Args:
            state_file: Path to JSON state file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_position: Optional[PositionState] = None
        
        # Load existing state
        self.load()
        
    def save(self):
        """Save current position to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'has_position': self.current_position is not None,
                'position': self.current_position.to_dict() if self.current_position else None
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"State saved to {self.state_file}")
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def load(self):
        """Load position from file"""
        try:
            if not self.state_file.exists():
                logger.info("No existing state file found")
                return
            
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            if data.get('has_position') and data.get('position'):
                self.current_position = PositionState.from_dict(data['position'])
                logger.info(f"✅ Loaded position: {self.current_position.symbol} "
                          f"{self.current_position.side} @ ${self.current_position.entry_price}")
            else:
                self.current_position = None
                logger.info("No active position in state")
                
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            self.current_position = None
    
    def has_position(self) -> bool:
        """Check if there's an active position"""
        return self.current_position is not None
    
    def open_position(self, position: PositionState):
        """
        Open a new position
        
        Args:
            position: PositionState object
        """
        if self.has_position():
            logger.warning(f"Overwriting existing position: {self.current_position.symbol}")
        
        self.current_position = position
        self.save()
        
        logger.info(f"📈 Position opened: {position.symbol} {position.side} @ ${position.entry_price}")
    
    def close_position(self) -> Optional[PositionState]:
        """
        Close current position
        
        Returns:
            The closed position state, or None
        """
        if not self.has_position():
            logger.warning("No position to close")
            return None
        
        closed = self.current_position
        self.current_position = None
        self.save()
        
        logger.info(f"📉 Position closed: {closed.symbol} {closed.side}")
        
        return closed
    
    def get_position(self) -> Optional[PositionState]:
        """Get current position"""
        return self.current_position
    
    def update_position(self, **kwargs):
        """
        Update current position fields
        
        Args:
            **kwargs: Fields to update
        """
        if not self.has_position():
            logger.warning("No position to update")
            return
        
        for key, value in kwargs.items():
            if hasattr(self.current_position, key):
                setattr(self.current_position, key, value)
        
        self.save()
        logger.debug(f"Position updated: {kwargs}")
    
    def clear(self):
        """Clear state (for emergency)"""
        self.current_position = None
        self.save()
        logger.warning("State cleared")
