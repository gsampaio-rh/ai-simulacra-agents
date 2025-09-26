"""Integrated simulation logger combining Apple UX and data export."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .rich_terminal_logger import RichTerminalLogger
from .data_exporter import DataExporter


class SimulationLogger:
    """Integrated logger for beautiful UX and structured data export."""
    
    def __init__(self, session_name: Optional[str] = None, output_dir: str = "output"):
        """Initialize simulation logger.
        
        Args:
            session_name: Name for this simulation session
            output_dir: Directory for data export
        """
        self.session_name = session_name or f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.rich_logger = RichTerminalLogger()
        self.data_exporter = DataExporter(output_dir)
        self._session_start_time = datetime.now()
        
    def log_simulation_start(self, agent_count: int, world_info: Dict[str, Any]) -> None:
        """Log simulation start with beautiful banner and setup data collection."""
        self.rich_logger.log_simulation_start(agent_count, world_info)
        
    def log_tick_start(self, tick: int, elapsed_minutes: int) -> None:
        """Log start of simulation tick."""
        self.rich_logger.log_tick_start(tick, elapsed_minutes)
        
    def log_agent_thinking(
        self,
        agent_name: str,
        current_location: str,
        available_actions: List[str],
        chosen_action: str,
        reasoning: Optional[str] = None
    ) -> None:
        """Log agent's thinking process before action."""
        self.rich_logger.log_agent_thinking(
            agent_name, current_location, available_actions, chosen_action, reasoning
        )
        
    def log_agent_action(
        self, 
        agent_name: str, 
        action: str, 
        result_message: str, 
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log agent action with beautiful formatting and data collection."""
        self.rich_logger.log_agent_action(
            agent_name, action, result_message, success, metadata
        )
        
    def log_tick_complete(self, agent_summaries: Dict[str, Any]) -> None:
        """Log completion of tick with agent status summary."""
        self.rich_logger.log_tick_complete(agent_summaries)
        
    def log_agent_detail(self, agent_details: Dict[str, Any]) -> None:
        """Log detailed agent information beautifully."""
        self.rich_logger.log_agent_detail(agent_details)
        
    def log_world_status(self, world_summary: Dict[str, Any]) -> None:
        """Log world status with beautiful visualization."""
        self.rich_logger.log_world_status(world_summary)
        
    def log_simulation_pause(self) -> None:
        """Log simulation pause."""
        self.rich_logger.log_simulation_pause()
        
    def log_simulation_end(self, total_ticks: int) -> Dict[str, str]:
        """Log simulation end and export all data.
        
        Args:
            total_ticks: Total number of simulation ticks
            
        Returns:
            Dictionary of exported file paths
        """
        # Calculate duration
        duration = datetime.now() - self._session_start_time
        duration_str = str(duration).split('.')[0]  # Remove microseconds
        
        # Log beautiful end message
        self.rich_logger.log_simulation_end(total_ticks, duration_str)
        
        # Export all logged data
        simulation_data = self.rich_logger.get_logged_data()
        exported_files = self.data_exporter.export_simulation_data(
            simulation_data, 
            self.session_name
        )
        
        return exported_files
        
    def get_session_name(self) -> str:
        """Get the current session name."""
        return self.session_name
        
    def get_logged_data(self) -> Dict[str, Any]:
        """Get all logged data without exporting."""
        return self.rich_logger.get_logged_data()
        
    def export_current_data(self) -> Dict[str, str]:
        """Export current data without ending simulation."""
        simulation_data = self.rich_logger.get_logged_data()
        return self.data_exporter.export_simulation_data(
            simulation_data, 
            f"{self.session_name}_checkpoint_{datetime.now().strftime('%H%M%S')}"
        )
