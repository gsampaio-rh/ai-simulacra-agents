"""Beautiful terminal logging with modern UX using Rich library."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.align import Align


class RichTerminalLogger:
    """Beautiful terminal logger with modern UX using Rich library."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize Rich terminal logger.
        
        Args:
            console: Rich console instance (creates new one if None)
        """
        self.console = console or Console()
        self._simulation_state = {}
        self._agent_actions = []
        self._tick_count = 0
        
    def log_simulation_start(self, agent_count: int, world_info: Dict[str, Any]) -> None:
        """Log simulation start with beautiful banner."""
        # Create simple but beautiful banner
        banner_text = f"""🤖 AI Simulacra Agents
Autonomous Agent Simulation

✨ {agent_count} agents initialized
🌍 {world_info.get('total_places', 0)} places loaded
📦 {world_info.get('total_objects', 0)} objects available
⏰ Started at {datetime.now().strftime('%H:%M:%S')}"""
        
        self.console.print(Panel(
            banner_text,
            title="🚀 Simulation Starting",
            border_style="bright_blue",
            padding=(1, 2)
        ))
        self.console.print()
    
    def log_tick_start(self, tick: int, elapsed_minutes: int) -> None:
        """Log start of simulation tick."""
        self._tick_count = tick
        
        # Create beautiful tick header with clear separation
        self.console.print()
        self.console.print("═" * 80, style="bright_blue")
        
        tick_panel = Panel(
            Text(f"⏰ TICK {tick} • {elapsed_minutes} minutes elapsed", justify="center", style="bold bright_white"),
            border_style="bright_blue",
            padding=(0, 2)
        )
        self.console.print(tick_panel)
        self.console.print()
        
    def log_agent_thinking(
        self,
        agent_name: str,
        current_location: str,
        available_actions: List[str],
        chosen_action: str,
        reasoning: Optional[str] = None
    ) -> None:
        """Log agent's thinking process before action."""
        # Create thinking panel for the agent
        thinking_content = Text()
        thinking_content.append(f"🧠 {agent_name} is thinking...\n", style="bold cyan")
        thinking_content.append(f"📍 Currently at: {current_location}\n", style="dim")
        
        if reasoning:
            thinking_content.append(f"💭 Reasoning: {reasoning}\n", style="italic bright_magenta")
        
        thinking_content.append("🎯 Available actions:\n", style="bold")
        for i, action in enumerate(available_actions[:3], 1):  # Show first 3
            style = "bold green" if action.lower() == chosen_action.lower() else "dim"
            prefix = "→ " if action.lower() == chosen_action.lower() else "  "
            thinking_content.append(f"{prefix}{i}. {action}\n", style=style)
        
        if len(available_actions) > 3:
            thinking_content.append(f"  ... and {len(available_actions) - 3} more options\n", style="dim")
        
        thinking_content.append(f"\n✨ Decision: {chosen_action}", style="bold bright_green")
        
        # Display thinking panel
        self.console.print(Panel(
            thinking_content,
            title=f"🤔 {agent_name}",
            border_style="cyan",
            padding=(1, 2),
            width=100
        ))

    def log_agent_action(
        self, 
        agent_name: str, 
        action: str, 
        result_message: str, 
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log agent action execution with clear visual distinction."""
        # Choose icon and colors based on action type
        action_configs = {
            "move": {"icon": "🚶‍♂️", "color": "bright_green", "bg": "on_green"},
            "wait": {"icon": "⏸️", "color": "bright_yellow", "bg": "on_yellow"},
            "observe": {"icon": "👁️", "color": "bright_blue", "bg": "on_blue"},
            "interact": {"icon": "🤝", "color": "bright_magenta", "bg": "on_magenta"},
            "error": {"icon": "❌", "color": "bright_red", "bg": "on_red"}
        }
        
        # Determine action type from result or action
        action_type = "error" if not success else action.lower()
        if "moved" in result_message.lower():
            action_type = "move"
        elif "waited" in result_message.lower():
            action_type = "wait"
        elif "observed" in result_message.lower():
            action_type = "observe"
        elif "interact" in result_message.lower():
            action_type = "interact"
        
        config = action_configs.get(action_type, {"icon": "✨", "color": "white", "bg": "on_white"})
        
        # Create action result panel
        result_content = Text()
        result_content.append(f"{config['icon']} ACTION EXECUTED\n", style=f"bold {config['color']}")
        result_content.append(f"📋 Result: {result_message}\n", style="white")
        
        # Add contextual metadata
        if metadata:
            if "location" in metadata:
                result_content.append(f"📍 Location: {metadata['location']}\n", style="dim")
            if "energy" in metadata:
                energy = metadata["energy"]
                energy_bar = self._create_mini_energy_bar(energy)
                result_content.append(f"⚡ Energy: {energy_bar}\n", style="white")
            if "mood" in metadata:
                mood = metadata["mood"]
                mood_emoji = self._get_mood_emoji(mood)
                result_content.append(f"😊 Mood: {mood_emoji} {mood:.1f}/10", style="white")
        
        # Display with appropriate border color
        self.console.print(Panel(
            result_content,
            title=f"✅ {agent_name}" if success else f"❌ {agent_name}",
            border_style=config['color'],
            padding=(1, 2),
            width=100
        ))
        self.console.print()  # Add spacing
        
        # Store for data export
        self._agent_actions.append({
            "tick": self._tick_count,
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": action,
            "result": result_message,
            "success": success,
            "metadata": metadata or {}
        })
    
    def log_agent_reflection(
        self,
        agent_name: str,
        reflection_count: int,
        reflection_insights: List[str]
    ) -> None:
        """Log agent reflection generation with beautiful formatting."""
        # Create reflection content
        reflection_content = Text()
        reflection_content.append(f"🧠 REFLECTION GENERATED\n", style="bold bright_cyan")
        reflection_content.append(f"💭 Generated {reflection_count} new insights:\n\n", style="white")
        
        # Add each insight with numbering
        for i, insight in enumerate(reflection_insights, 1):
            reflection_content.append(f"{i}. ", style="bold bright_white")
            reflection_content.append(f"{insight}\n", style="italic bright_cyan")
            if i < len(reflection_insights):
                reflection_content.append("\n")
        
        # Display with cyan theme for reflections
        self.console.print(Panel(
            reflection_content,
            title=f"💡 {agent_name}",
            border_style="bright_cyan",
            padding=(1, 2),
            width=100
        ))
        self.console.print()  # Add spacing
        
        # Store for data export
        self._agent_actions.append({
            "tick": self._tick_count,
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": "reflection",
            "result": f"Generated {reflection_count} reflections",
            "success": True,
            "metadata": {
                "reflection_count": reflection_count,
                "insights": reflection_insights
            }
        })
    
    def log_agent_planning(
        self,
        agent_name: str,
        blocks_count: int,
        plan_summary: Optional[str] = None
    ) -> None:
        """Log agent planning generation with beautiful formatting."""
        # Create planning content
        planning_content = Text()
        
        if plan_summary:
            # Show the rich plan summary instead of generic message
            planning_content.append("🎯 DAILY PLAN GENERATED\n\n", style="bold bright_yellow")
            planning_content.append(f"{plan_summary}", style="white")
        else:
            # Fallback to basic message if no summary
            planning_content.append(f"🎯 DAILY PLAN GENERATED\n", style="bold bright_yellow")
            planning_content.append(f"📋 Created plan with {blocks_count} time blocks", style="white")
        
        # Display with yellow theme for planning
        self.console.print(Panel(
            planning_content,
            title=f"🗓️ {agent_name}",
            border_style="bright_yellow",
            padding=(1, 2),
            width=100
        ))
        self.console.print()  # Add spacing
        
        # Store for data export
        self._agent_actions.append({
            "tick": self._tick_count,
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": "planning",
            "result": f"Generated daily plan with {blocks_count} blocks",
            "success": True,
            "metadata": {
                "blocks_count": blocks_count,
                "plan_summary": plan_summary
            }
        })
    
    def _create_mini_energy_bar(self, energy: float) -> Text:
        """Create a compact energy bar."""
        bar_length = 8
        filled = int((energy / 100) * bar_length)
        
        bar = Text()
        if energy > 70:
            color = "bright_green"
        elif energy > 30:
            color = "bright_yellow"
        else:
            color = "bright_red"
            
        bar.append("█" * filled, style=color)
        bar.append("░" * (bar_length - filled), style="dim")
        bar.append(f" {energy:.0f}%", style="white")
        return bar
    
    def _get_mood_emoji(self, mood: float) -> str:
        """Get emoji for mood level."""
        if mood >= 8:
            return "😄"
        elif mood >= 6:
            return "😊"
        elif mood >= 4:
            return "😐"
        elif mood >= 2:
            return "😔"
        else:
            return "😢"
    
    def log_tick_complete(self, agent_summaries: Dict[str, Any]) -> None:
        """Log completion of tick with agent status summary."""
        # Update simulation state
        self._simulation_state[self._tick_count] = {
            "timestamp": datetime.now().isoformat(),
            "agents": agent_summaries
        }
        
        # Create beautiful status table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Agent", style="cyan", min_width=15)
        table.add_column("Location", style="green", min_width=15)
        table.add_column("Energy", style="yellow", justify="right")
        table.add_column("Plan", style="bright_yellow", min_width=20)
        
        for agent_id, agent_data in agent_summaries.items():
            energy = agent_data.get('energy', 100)
            energy_bar = self._create_energy_bar(energy)
            
            # Create compact planning info
            planning_info = self._create_planning_status(agent_data.get('planning', {}))
            
            table.add_row(
                agent_data.get('name', agent_id),
                agent_data.get('location_name', 'unknown'),
                energy_bar,
                planning_info
            )
        
        self.console.print()
        self.console.print("📊 Agent Status:")
        self.console.print(table)
        self.console.print()
        
    def _create_energy_bar(self, energy: float) -> Text:
        """Create a beautiful energy bar."""
        # Create energy bar with colors
        bar_length = 10
        filled = int((energy / 100) * bar_length)
        
        bar = Text()
        
        # Add filled portion
        if energy > 70:
            color = "green"
        elif energy > 30:
            color = "yellow"
        else:
            color = "red"
            
        bar.append("█" * filled, style=color)
        bar.append("░" * (bar_length - filled), style="dim")
        bar.append(f" {energy:.0f}%", style="white")
        
        return bar
    
    def _create_planning_status(self, planning_data: Dict[str, Any]) -> Text:
        """Create compact planning status display."""
        status = Text()
        
        if planning_data.get('error'):
            status.append("❌ Error", style="red")
        elif planning_data.get('has_plan'):
            # Show plan status with current activity
            status.append("📋 ", style="bright_yellow")
            
            if planning_data.get('current_task'):
                # Truncate task to fit in column
                task = planning_data['current_task']
                if len(task) > 18:
                    task = task[:15] + "..."
                status.append(task, style="green")
            else:
                status.append("Planning", style="dim yellow")
        else:
            status.append("📋 No plan", style="dim")
        
        return status
    
    def log_agent_detail(self, agent_details: Dict[str, Any]) -> None:
        """Log detailed agent information beautifully."""
        name = agent_details.get('name', 'Unknown Agent')
        
        # Create beautiful agent detail panel
        detail_text = Text()
        
        # Basic info
        detail_text.append(f"🆔 ID: {agent_details.get('id', 'unknown')}\n", style="dim")
        detail_text.append(f"🏠 Home: {agent_details.get('home_location', 'unknown')}\n", style="blue")
        detail_text.append(f"📍 Current: {agent_details.get('current_location_name', 'unknown')}\n", style="green")
        
        # State info
        state = agent_details.get('state', {})
        energy = state.get('energy', 0)
        mood = state.get('mood', 0)
        
        detail_text.append(f"\n⚡ Energy: {self._create_energy_bar(energy)}\n")
        detail_text.append(f"😊 Mood: {self._create_mood_indicator(mood)}\n")
        detail_text.append(f"🔄 Status: {state.get('status', 'unknown')}\n", style="yellow")
        
        if state.get('current_task'):
            detail_text.append(f"📋 Task: {state['current_task']}\n", style="magenta")
        
        # Bio and personality
        detail_text.append(f"\n📝 {agent_details.get('bio', 'No bio available')}\n", style="dim")
        detail_text.append(f"🎭 Personality: {agent_details.get('personality', 'undefined')}\n", style="cyan")
        
        # Available actions
        actions = agent_details.get('available_actions', [])
        if actions:
            detail_text.append(f"\n🎯 Available Actions ({len(actions)}):\n", style="bold")
            for i, action in enumerate(actions[:5], 1):  # Show first 5
                detail_text.append(f"  {i}. {action}\n", style="white")
            if len(actions) > 5:
                detail_text.append(f"  ... and {len(actions) - 5} more\n", style="dim")
        
        self.console.print(Panel(
            detail_text,
            title=f"🤖 {name}",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
    
    def _create_mood_indicator(self, mood: float) -> Text:
        """Create a beautiful mood indicator."""
        # Convert 0-10 mood to emoji and color
        mood_text = Text()
        
        if mood >= 8:
            emoji = "😄"
            color = "bright_green"
        elif mood >= 6:
            emoji = "😊"
            color = "green"
        elif mood >= 4:
            emoji = "😐"
            color = "yellow"
        elif mood >= 2:
            emoji = "😔"
            color = "red"
        else:
            emoji = "😢"
            color = "bright_red"
        
        mood_text.append(f"{emoji} {mood:.1f}/10", style=color)
        return mood_text
    
    def log_world_status(self, world_summary: Dict[str, Any]) -> None:
        """Log world status with beautiful visualization."""
        # Create world overview table
        table = Table(title="🌍 World Overview", show_header=True, header_style="bold blue")
        table.add_column("Place", style="green", min_width=20)
        table.add_column("Occupancy", style="yellow", justify="center")
        table.add_column("Agents Present", style="cyan")
        
        place_occupancy = world_summary.get('place_occupancy', {})
        for place_id, place_data in place_occupancy.items():
            place_name = place_data.get('name', place_id)
            agent_count = place_data.get('agent_count', 0)
            agents = place_data.get('agents', [])
            
            # Create occupancy indicator
            if agent_count == 0:
                occupancy = "🔹 Empty"
                occupancy_style = "dim"
            elif agent_count == 1:
                occupancy = "🔸 1 agent"
                occupancy_style = "green"
            else:
                occupancy = f"🔶 {agent_count} agents"
                occupancy_style = "bright_green"
            
            agents_text = ", ".join(agents) if agents else "—"
            
            table.add_row(
                place_name,
                Text(occupancy, style=occupancy_style),
                agents_text
            )
        
        self.console.print(table)
        self.console.print()
    
    def log_simulation_pause(self) -> None:
        """Log simulation pause."""
        pause_text = Text("⏸️  Simulation Paused", style="bold yellow")
        self.console.print(Panel(
            Align.center(pause_text),
            border_style="yellow",
            padding=(0, 2)
        ))
        self.console.print()
    
    def log_simulation_end(self, total_ticks: int, duration: str) -> None:
        """Log simulation end with summary."""
        summary_text = Text()
        summary_text.append("🏁 Simulation Complete\n\n", style="bold bright_green")
        summary_text.append(f"⏰ Total ticks: {total_ticks}\n", style="white")
        summary_text.append(f"⌚ Duration: {duration}\n", style="white")
        summary_text.append(f"📊 Actions logged: {len(self._agent_actions)}\n", style="white")
        summary_text.append(f"🤖 Agents tracked: {len(set(a['agent_name'] for a in self._agent_actions))}\n", style="white")
        
        self.console.print(Panel(
            Align.center(summary_text),
            title="✨ Simulation Summary",
            border_style="bright_green",
            padding=(1, 2)
        ))
    
    def get_logged_data(self) -> Dict[str, Any]:
        """Get all logged data for export."""
        return {
            "simulation_state": self._simulation_state,
            "agent_actions": self._agent_actions,
            "total_ticks": self._tick_count
        }
