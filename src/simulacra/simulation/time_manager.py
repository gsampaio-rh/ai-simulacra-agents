"""Time management for discrete simulation ticks."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class TimeManager:
    """Manages simulation time and tick progression."""
    
    def __init__(self, tick_duration_minutes: int = 5):
        """Initialize time manager.
        
        Args:
            tick_duration_minutes: Duration of each simulation tick in minutes
        """
        self.tick_duration_minutes = tick_duration_minutes
        self.current_tick = 0
        self.start_time: Optional[datetime] = None
        self.is_running = False
        self._simulation_task: Optional[asyncio.Task] = None
        self._tick_callbacks: list[Callable[[int], Any]] = []
    
    def add_tick_callback(self, callback: Callable[[int], Any]) -> None:
        """Add a callback to be called on each tick.
        
        Args:
            callback: Function to call with tick number
        """
        self._tick_callbacks.append(callback)
    
    def remove_tick_callback(self, callback: Callable[[int], Any]) -> None:
        """Remove a tick callback.
        
        Args:
            callback: Function to remove
        """
        if callback in self._tick_callbacks:
            self._tick_callbacks.remove(callback)
    
    async def start_simulation(self) -> None:
        """Start the simulation loop."""
        if self.is_running:
            logger.warning("Simulation is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        logger.info(f"Starting simulation at tick {self.current_tick}")
        
        # Start simulation loop in background
        self._simulation_task = asyncio.create_task(self._simulation_loop())
    
    async def pause_simulation(self) -> None:
        """Pause the simulation."""
        if not self.is_running:
            logger.warning("Simulation is not running")
            return
        
        self.is_running = False
        
        if self._simulation_task:
            self._simulation_task.cancel()
            try:
                await self._simulation_task
            except asyncio.CancelledError:
                pass
            self._simulation_task = None
        
        logger.info(f"Paused simulation at tick {self.current_tick}")
    
    async def advance_tick(self) -> None:
        """Advance by one tick."""
        self.current_tick += 1
        
        logger.debug(f"Advanced to tick {self.current_tick}")
        
        # Call all tick callbacks
        for callback in self._tick_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_tick)
                else:
                    callback(self.current_tick)
            except Exception as e:
                logger.error(f"Error in tick callback: {e}")
    
    async def fast_forward(self, ticks: int) -> None:
        """Fast forward by multiple ticks.
        
        Args:
            ticks: Number of ticks to advance
        """
        logger.info(f"Fast forwarding {ticks} ticks from {self.current_tick}")
        
        for _ in range(ticks):
            await self.advance_tick()
        
        logger.info(f"Fast forward complete, now at tick {self.current_tick}")
    
    async def _simulation_loop(self) -> None:
        """Main simulation loop."""
        try:
            while self.is_running:
                await self.advance_tick()
                
                # Sleep for a short interval (simulation runs faster than real time)
                # In a real simulation, you might want this to be longer
                await asyncio.sleep(0.5)  # Half second per tick for now
                
        except asyncio.CancelledError:
            logger.debug("Simulation loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            self.is_running = False
            raise
    
    def get_simulation_time(self) -> datetime:
        """Get the current simulation time.
        
        Returns:
            Current simulation time based on tick progression
        """
        if self.start_time is None:
            return datetime.utcnow()
        
        elapsed_minutes = self.current_tick * self.tick_duration_minutes
        return self.start_time + timedelta(minutes=elapsed_minutes)
    
    def get_elapsed_time(self) -> timedelta:
        """Get elapsed simulation time.
        
        Returns:
            Time elapsed since simulation start
        """
        if self.start_time is None:
            return timedelta(0)
        
        return timedelta(minutes=self.current_tick * self.tick_duration_minutes)
    
    def get_status(self) -> dict:
        """Get current time manager status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "current_tick": self.current_tick,
            "is_running": self.is_running,
            "tick_duration_minutes": self.tick_duration_minutes,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "simulation_time": self.get_simulation_time().isoformat(),
            "elapsed_time": str(self.get_elapsed_time()),
            "elapsed_minutes": self.current_tick * self.tick_duration_minutes
        }
    
    def format_tick_time(self, tick: Optional[int] = None) -> str:
        """Format a tick as a readable time string.
        
        Args:
            tick: Tick number to format (uses current tick if None)
            
        Returns:
            Formatted time string like "T+15 (75 minutes)"
        """
        if tick is None:
            tick = self.current_tick
        
        minutes = tick * self.tick_duration_minutes
        return f"T+{tick} ({minutes} minutes)"
