"""Data export system for agent behavior analysis and EDA."""

import csv
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class DataExporter:
    """Exports simulation data for analysis and EDA."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize data exporter.
        
        Args:
            output_dir: Base directory to save exported data
        """
        self.base_output_dir = Path(output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.console = Console()
    
    def export_simulation_data(
        self, 
        simulation_data: Dict[str, Any],
        session_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Export complete simulation data in multiple formats.
        
        Args:
            simulation_data: Data from AppleLogger.get_logged_data()
            session_name: Name for this session (auto-generated if None)
            
        Returns:
            Dictionary mapping format to file path
        """
        if session_name is None:
            session_name = f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create session-specific directory
        session_dir = self.base_output_dir / session_name
        session_dir.mkdir(exist_ok=True)
        
        exported_files = {}
        
        # Export agent actions as CSV
        actions_file = self._export_agent_actions_csv(
            simulation_data.get('agent_actions', []),
            session_dir
        )
        exported_files['agent_actions_csv'] = actions_file
        
        # Export simulation state as CSV
        state_file = self._export_simulation_state_csv(
            simulation_data.get('simulation_state', {}),
            session_dir
        )
        exported_files['simulation_state_csv'] = state_file
        
        # Export complete data as JSON
        json_file = self._export_complete_json(simulation_data, session_dir)
        exported_files['complete_json'] = json_file
        
        # Create analysis-ready datasets
        analysis_files = self._create_analysis_datasets(simulation_data, session_dir)
        exported_files.update(analysis_files)
        
        # Generate summary report
        report_file = self._generate_summary_report(simulation_data, session_dir, session_name)
        exported_files['summary_report'] = report_file
        
        # Display export summary
        self._display_export_summary(exported_files, session_name)
        
        return exported_files
    
    def _export_agent_actions_csv(self, actions: List[Dict], session_dir: Path) -> str:
        """Export agent actions to CSV for analysis."""
        filename = "agent_actions.csv"
        filepath = session_dir / filename
        
        if not actions:
            return str(filepath)
        
        # Define CSV columns
        fieldnames = [
            'tick', 'timestamp', 'agent_name', 'action', 'result', 'success',
            'location', 'energy', 'mood', 'action_duration', 'target_location',
            'interaction_type', 'reason'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for action in actions:
                metadata = action.get('metadata', {})
                
                row = {
                    'tick': action.get('tick', 0),
                    'timestamp': action.get('timestamp', ''),
                    'agent_name': action.get('agent_name', ''),
                    'action': action.get('action', ''),
                    'result': action.get('result', ''),
                    'success': action.get('success', True),
                    'location': metadata.get('location', ''),
                    'energy': metadata.get('energy', ''),
                    'mood': metadata.get('mood', ''),
                    'action_duration': metadata.get('duration_minutes', ''),
                    'target_location': metadata.get('new_location', ''),
                    'interaction_type': metadata.get('interaction_type', ''),
                    'reason': metadata.get('reason', '')
                }
                
                writer.writerow(row)
        
        return str(filepath)
    
    def _export_simulation_state_csv(self, state_data: Dict, session_dir: Path) -> str:
        """Export simulation state snapshots to CSV."""
        filename = "simulation_state.csv"
        filepath = session_dir / filename
        
        if not state_data:
            return str(filepath)
        
        fieldnames = [
            'tick', 'timestamp', 'agent_id', 'agent_name', 'location',
            'location_name', 'energy', 'mood', 'status', 'current_task'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for tick, tick_data in state_data.items():
                timestamp = tick_data.get('timestamp', '')
                agents = tick_data.get('agents', {})
                
                for agent_id, agent_data in agents.items():
                    row = {
                        'tick': tick,
                        'timestamp': timestamp,
                        'agent_id': agent_id,
                        'agent_name': agent_data.get('name', agent_id),
                        'location': agent_data.get('location', ''),
                        'location_name': agent_data.get('location_name', ''),
                        'energy': agent_data.get('energy', 100),
                        'mood': agent_data.get('mood', 5.0),
                        'status': agent_data.get('status', 'active'),
                        'current_task': agent_data.get('current_task', '')
                    }
                    
                    writer.writerow(row)
        
        return str(filepath)
    
    def _export_complete_json(self, data: Dict[str, Any], session_dir: Path) -> str:
        """Export complete simulation data as JSON."""
        filename = "complete_simulation.json"
        filepath = session_dir / filename
        
        # Add metadata
        export_data = {
            "metadata": {
                "session_name": session_dir.name,
                "export_timestamp": datetime.now().isoformat(),
                "total_ticks": data.get('total_ticks', 0),
                "total_actions": len(data.get('agent_actions', [])),
                "agent_count": len(set(a['agent_name'] for a in data.get('agent_actions', [])))
            },
            "simulation_data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _create_analysis_datasets(self, data: Dict[str, Any], session_dir: Path) -> Dict[str, str]:
        """Create specialized datasets for different types of analysis."""
        files = {}
        
        # Movement analysis dataset
        movement_file = self._create_movement_dataset(data, session_dir)
        files['movement_analysis'] = movement_file
        
        # Social interaction dataset
        social_file = self._create_social_dataset(data, session_dir)
        files['social_analysis'] = social_file
        
        # Energy and mood tracking dataset
        vitals_file = self._create_vitals_dataset(data, session_dir)
        files['vitals_analysis'] = vitals_file
        
        # Time series dataset for temporal analysis
        timeseries_file = self._create_timeseries_dataset(data, session_dir)
        files['timeseries_analysis'] = timeseries_file
        
        return files
    
    def _create_movement_dataset(self, data: Dict[str, Any], session_dir: Path) -> str:
        """Create dataset focused on agent movement patterns."""
        filename = "movement_analysis.csv"
        filepath = session_dir / filename
        
        actions = data.get('agent_actions', [])
        movement_actions = [a for a in actions if 'moved' in a.get('result', '').lower()]
        
        fieldnames = [
            'tick', 'timestamp', 'agent_name', 'from_location', 'to_location',
            'movement_reason', 'energy_before', 'time_spent_at_previous'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for action in movement_actions:
                metadata = action.get('metadata', {})
                
                # Extract locations from result message
                result = action.get('result', '')
                if 'from' in result and 'to' in result:
                    parts = result.split(' from ')
                    if len(parts) > 1:
                        location_part = parts[1]
                        if ' to ' in location_part:
                            from_loc, to_loc = location_part.split(' to ', 1)
                        else:
                            from_loc, to_loc = metadata.get('previous_location', ''), metadata.get('new_location', '')
                    else:
                        from_loc, to_loc = '', metadata.get('new_location', '')
                else:
                    from_loc, to_loc = metadata.get('previous_location', ''), metadata.get('new_location', '')
                
                row = {
                    'tick': action.get('tick', 0),
                    'timestamp': action.get('timestamp', ''),
                    'agent_name': action.get('agent_name', ''),
                    'from_location': from_loc,
                    'to_location': to_loc,
                    'movement_reason': 'exploration',  # Could be enhanced with personality analysis
                    'energy_before': metadata.get('energy', ''),
                    'time_spent_at_previous': ''  # Could be calculated from previous actions
                }
                
                writer.writerow(row)
        
        return str(filepath)
    
    def _create_social_dataset(self, data: Dict[str, Any], session_dir: Path) -> str:
        """Create dataset for social interaction analysis."""
        filename = "social_analysis.csv"
        filepath = session_dir / filename
        
        # Analyze co-location and interactions
        state_data = data.get('simulation_state', {})
        
        fieldnames = [
            'tick', 'timestamp', 'location', 'agent_count', 'agents_present',
            'social_density', 'interaction_potential'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for tick, tick_data in state_data.items():
                # Group agents by location
                location_groups = {}
                agents = tick_data.get('agents', {})
                
                for agent_id, agent_data in agents.items():
                    location = agent_data.get('location_name', 'unknown')
                    if location not in location_groups:
                        location_groups[location] = []
                    location_groups[location].append(agent_data.get('name', agent_id))
                
                # Create rows for each location with multiple agents
                for location, agent_list in location_groups.items():
                    if len(agent_list) > 1:  # Only locations with social potential
                        row = {
                            'tick': tick,
                            'timestamp': tick_data.get('timestamp', ''),
                            'location': location,
                            'agent_count': len(agent_list),
                            'agents_present': ', '.join(agent_list),
                            'social_density': len(agent_list) / 10.0,  # Normalized by max capacity
                            'interaction_potential': min(len(agent_list) * (len(agent_list) - 1) / 2, 10)
                        }
                        
                        writer.writerow(row)
        
        return str(filepath)
    
    def _create_vitals_dataset(self, data: Dict[str, Any], session_dir: Path) -> str:
        """Create dataset for energy and mood tracking."""
        filename = "vitals_analysis.csv"
        filepath = session_dir / filename
        
        state_data = data.get('simulation_state', {})
        
        fieldnames = [
            'tick', 'timestamp', 'agent_name', 'energy', 'mood', 'status',
            'energy_change', 'mood_change', 'location', 'activity_type'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            previous_state = {}
            
            for tick, tick_data in state_data.items():
                agents = tick_data.get('agents', {})
                
                for agent_id, agent_data in agents.items():
                    current_energy = agent_data.get('energy', 100)
                    current_mood = agent_data.get('mood', 5.0)
                    
                    # Calculate changes from previous tick
                    prev_data = previous_state.get(agent_id, {})
                    energy_change = current_energy - prev_data.get('energy', current_energy)
                    mood_change = current_mood - prev_data.get('mood', current_mood)
                    
                    row = {
                        'tick': tick,
                        'timestamp': tick_data.get('timestamp', ''),
                        'agent_name': agent_data.get('name', agent_id),
                        'energy': current_energy,
                        'mood': current_mood,
                        'status': agent_data.get('status', 'active'),
                        'energy_change': round(energy_change, 2) if prev_data else 0,
                        'mood_change': round(mood_change, 2) if prev_data else 0,
                        'location': agent_data.get('location_name', ''),
                        'activity_type': 'unknown'  # Could be inferred from recent actions
                    }
                    
                    writer.writerow(row)
                
                # Store current state for next iteration
                for agent_id, agent_data in agents.items():
                    previous_state[agent_id] = {
                        'energy': agent_data.get('energy', 100),
                        'mood': agent_data.get('mood', 5.0)
                    }
        
        return str(filepath)
    
    def _create_timeseries_dataset(self, data: Dict[str, Any], session_dir: Path) -> str:
        """Create time series dataset for temporal analysis."""
        filename = "timeseries_analysis.csv"
        filepath = session_dir / filename
        
        actions = data.get('agent_actions', [])
        
        # Aggregate actions by tick for time series analysis
        tick_aggregates = {}
        
        for action in actions:
            tick = action.get('tick', 0)
            if tick not in tick_aggregates:
                tick_aggregates[tick] = {
                    'tick': tick,
                    'timestamp': action.get('timestamp', ''),
                    'total_actions': 0,
                    'movement_actions': 0,
                    'wait_actions': 0,
                    'observe_actions': 0,
                    'interact_actions': 0,
                    'successful_actions': 0,
                    'unique_agents': set(),
                    'unique_locations': set()
                }
            
            agg = tick_aggregates[tick]
            agg['total_actions'] += 1
            agg['unique_agents'].add(action.get('agent_name', ''))
            
            result = action.get('result', '').lower()
            if 'moved' in result:
                agg['movement_actions'] += 1
            elif 'waited' in result:
                agg['wait_actions'] += 1
            elif 'observed' in result:
                agg['observe_actions'] += 1
            elif 'interact' in result:
                agg['interact_actions'] += 1
            
            if action.get('success', True):
                agg['successful_actions'] += 1
            
            location = action.get('metadata', {}).get('location', '')
            if location:
                agg['unique_locations'].add(location)
        
        fieldnames = [
            'tick', 'timestamp', 'total_actions', 'movement_actions', 'wait_actions',
            'observe_actions', 'interact_actions', 'successful_actions',
            'success_rate', 'active_agents', 'active_locations', 'activity_diversity'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for tick in sorted(tick_aggregates.keys()):
                agg = tick_aggregates[tick]
                total = agg['total_actions']
                
                row = {
                    'tick': tick,
                    'timestamp': agg['timestamp'],
                    'total_actions': total,
                    'movement_actions': agg['movement_actions'],
                    'wait_actions': agg['wait_actions'],
                    'observe_actions': agg['observe_actions'],
                    'interact_actions': agg['interact_actions'],
                    'successful_actions': agg['successful_actions'],
                    'success_rate': round(agg['successful_actions'] / total * 100, 2) if total > 0 else 0,
                    'active_agents': len(agg['unique_agents']),
                    'active_locations': len(agg['unique_locations']),
                    'activity_diversity': len([x for x in [agg['movement_actions'], agg['wait_actions'], 
                                                          agg['observe_actions'], agg['interact_actions']] if x > 0])
                }
                
                writer.writerow(row)
        
        return str(filepath)
    
    def _generate_summary_report(self, data: Dict[str, Any], session_dir: Path, session_name: str) -> str:
        """Generate a human-readable summary report."""
        filename = "summary_report.md"
        filepath = session_dir / filename
        
        actions = data.get('agent_actions', [])
        state_data = data.get('simulation_state', {})
        total_ticks = data.get('total_ticks', 0)
        
        # Calculate statistics
        total_actions = len(actions)
        unique_agents = len(set(a['agent_name'] for a in actions))
        successful_actions = len([a for a in actions if a.get('success', True)])
        
        action_types = {}
        for action in actions:
            result = action.get('result', '').lower()
            if 'moved' in result:
                action_types['movement'] = action_types.get('movement', 0) + 1
            elif 'waited' in result:
                action_types['waiting'] = action_types.get('waiting', 0) + 1
            elif 'observed' in result:
                action_types['observation'] = action_types.get('observation', 0) + 1
            else:
                action_types['other'] = action_types.get('other', 0) + 1
        
        # Generate report
        report_content = f"""# Simulation Summary Report
        
**Session:** {session_name}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Simulation Ticks:** {total_ticks}
- **Total Actions Logged:** {total_actions}
- **Active Agents:** {unique_agents}
- **Success Rate:** {(successful_actions / total_actions * 100):.1f}% ({successful_actions}/{total_actions})

## Action Breakdown
"""
        
        for action_type, count in action_types.items():
            percentage = (count / total_actions * 100) if total_actions > 0 else 0
            report_content += f"- **{action_type.title()}:** {count} ({percentage:.1f}%)\n"
        
        report_content += f"""
## Agent Behavior Summary
"""
        
        # Analyze each agent's behavior
        agent_stats = {}
        for action in actions:
            agent_name = action.get('agent_name', 'unknown')
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    'total_actions': 0,
                    'movements': 0,
                    'waits': 0,
                    'observations': 0,
                    'locations_visited': set()
                }
            
            stats = agent_stats[agent_name]
            stats['total_actions'] += 1
            
            result = action.get('result', '').lower()
            if 'moved' in result:
                stats['movements'] += 1
            elif 'waited' in result:
                stats['waits'] += 1
            elif 'observed' in result:
                stats['observations'] += 1
            
            location = action.get('metadata', {}).get('location', '')
            if location:
                stats['locations_visited'].add(location)
        
        for agent_name, stats in agent_stats.items():
            report_content += f"""
### {agent_name}
- **Total Actions:** {stats['total_actions']}
- **Movements:** {stats['movements']} ({(stats['movements']/stats['total_actions']*100):.1f}%)
- **Wait Periods:** {stats['waits']} ({(stats['waits']/stats['total_actions']*100):.1f}%)
- **Observations:** {stats['observations']} ({(stats['observations']/stats['total_actions']*100):.1f}%)
- **Locations Visited:** {len(stats['locations_visited'])} unique locations
"""
        
        report_content += f"""
## Data Files Generated
All data has been exported in multiple formats for analysis:

### CSV Files (for analysis in Excel, Python, R)
- `agent_actions.csv` - Detailed action log
- `simulation_state.csv` - Agent state snapshots
- `movement_analysis.csv` - Movement pattern analysis
- `social_analysis.csv` - Social interaction data
- `vitals_analysis.csv` - Energy and mood tracking
- `timeseries_analysis.csv` - Time series aggregates

### JSON Files (for programmatic access)
- `complete_simulation.json` - Complete simulation data

## Suggested Analysis
1. **Movement Patterns:** Analyze agent movement preferences and location popularity
2. **Social Dynamics:** Study co-location patterns and potential interactions
3. **Temporal Patterns:** Look for activity cycles and peak interaction times
4. **Agent Personalities:** Compare behavior patterns across different agent types
5. **Energy/Mood Correlation:** Analyze how agent state affects behavior choices

---
*Generated by AI Simulacra Agents Data Exporter*
"""
        
        with open(filepath, 'w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        return str(filepath)
    
    def _display_export_summary(self, exported_files: Dict[str, str], session_name: str) -> None:
        """Display beautiful export summary."""
        summary_text = Text()
        summary_text.append("📊 Data Export Complete\n\n", style="bold bright_green")
        summary_text.append(f"Session: {session_name}\n", style="cyan")
        summary_text.append(f"Export Time: {datetime.now().strftime('%H:%M:%S')}\n\n", style="dim")
        
        # Group files by type
        csv_files = [f for k, f in exported_files.items() if 'csv' in k]
        json_files = [f for k, f in exported_files.items() if 'json' in k]
        report_files = [f for k, f in exported_files.items() if 'report' in k]
        
        summary_text.append("📈 CSV Files for Analysis:\n", style="bold yellow")
        for file_path in csv_files:
            filename = Path(file_path).name
            summary_text.append(f"  • {filename}\n", style="green")
        
        summary_text.append("\n🔧 JSON Files for Development:\n", style="bold blue")
        for file_path in json_files:
            filename = Path(file_path).name
            summary_text.append(f"  • {filename}\n", style="blue")
        
        summary_text.append("\n📄 Reports:\n", style="bold magenta")
        for file_path in report_files:
            filename = Path(file_path).name
            summary_text.append(f"  • {filename}\n", style="magenta")
        
        summary_text.append(f"\n📁 All files saved to: {session_name}/", style="dim")
        
        self.console.print(Panel(
            summary_text,
            title="💾 Export Summary",
            border_style="bright_green",
            padding=(1, 2)
        ))
        self.console.print()
