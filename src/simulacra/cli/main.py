"""Main CLI interface for simulacra agents."""

import asyncio
import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..simulation.simulation_controller import SimulationController

# Setup rich console
console = Console()

# Global simulation controller
sim_controller: Optional[SimulationController] = None


def setup_logging():
    """Setup logging for CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.group()
@click.pass_context
def cli(ctx):
    """AI Simulacra Agents - Watch agents live their lives."""
    ctx.ensure_object(dict)
    setup_logging()


@cli.command()
def start():
    """Start the simulation."""
    console.print("[bold green]Starting simulation...[/bold green]")
    
    async def _start():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.start_simulation()
        
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Simulation interrupted by user[/yellow]")
        finally:
            await sim_controller.cleanup()
    
    try:
        asyncio.run(_start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")


@cli.command()
def step():
    """Advance simulation by one tick."""
    console.print("[bold blue]Stepping simulation...[/bold blue]")
    
    async def _step():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.step_simulation()
        
        # Show status after step
        status = sim_controller.get_simulation_status()
        _display_status(status)
        
        await sim_controller.cleanup()
    
    asyncio.run(_step())


@cli.command()
def status():
    """Show current simulation status."""
    async def _status():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        status = sim_controller.get_simulation_status()
        _display_status(status)
        
        await sim_controller.cleanup()
    
    asyncio.run(_status())


@cli.command()
@click.argument('agent_id')
def agent(agent_id: str):
    """Show details for a specific agent."""
    async def _agent():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        details = sim_controller.get_agent_details(agent_id, log_beautifully=True)
        if not details:
            console.print(f"[red]Agent '{agent_id}' not found[/red]")
            return
        
        await sim_controller.cleanup()
    
    asyncio.run(_agent())


@cli.command()
def export():
    """Export simulation data for analysis."""
    async def _export():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        console.print("[blue]Exporting simulation data...[/blue]")
        exported_files = sim_controller.export_simulation_data()
        
        if not exported_files:
            console.print("[yellow]No simulation data to export[/yellow]")
        else:
            console.print("[green]✅ Data exported successfully![/green]")
        
        await sim_controller.cleanup()
    
    asyncio.run(_export())


@cli.command()
def interactive():
    """Start interactive simulation mode."""
    console.print("[bold green]Starting interactive simulation mode...[/bold green]")
    console.print("Commands: start, pause, step, status, agent <id>, quit")
    
    async def _interactive():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        try:
            while True:
                try:
                    command = await asyncio.to_thread(input, "\n> ")
                    command = command.strip().lower()
                    
                    if command == "quit" or command == "exit":
                        break
                    elif command == "start":
                        console.print("[green]Starting simulation...[/green]")
                        await sim_controller.start_simulation()
                    elif command == "pause":
                        console.print("[yellow]Pausing simulation...[/yellow]")
                        await sim_controller.pause_simulation()
                    elif command == "step":
                        console.print("[blue]Stepping simulation...[/blue]")
                        await sim_controller.step_simulation()
                    elif command == "status":
                        status = sim_controller.get_simulation_status()
                        _display_status(status)
                    elif command.startswith("agent "):
                        agent_id = command.split(" ", 1)[1]
                        details = sim_controller.get_agent_details(agent_id)
                        if details:
                            _display_agent_details(details)
                        else:
                            console.print(f"[red]Agent '{agent_id}' not found[/red]")
                    else:
                        console.print("[red]Unknown command. Available: start, pause, step, status, agent <id>, quit[/red]")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
        
        finally:
            await sim_controller.cleanup()
    
    try:
        asyncio.run(_interactive())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")


def _display_status(status: dict):
    """Display simulation status."""
    # Title
    title = f"Simulation Status: {status['status'].upper()}"
    console.print(Panel(title, style="bold blue"))
    
    # Time information
    time_info = status.get('time', {})
    tick = time_info.get('current_tick', 0)
    elapsed = time_info.get('elapsed_minutes', 0)
    console.print(f"⏰ Tick: {tick} ({elapsed} minutes elapsed)")
    
    # World summary
    world_info = status.get('world', {})
    console.print(f"🌍 World: {world_info.get('total_places', 0)} places, {world_info.get('total_agents', 0)} agents")
    
    # Agent locations table
    agents_info = status.get('agents', {})
    if agents_info:
        table = Table(title="Agent Locations")
        table.add_column("Agent", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Energy", style="yellow")
        table.add_column("Status", style="magenta")
        
        for agent_id, agent_data in agents_info.items():
            table.add_row(
                agent_data.get('name', agent_id),
                agent_data.get('location_name', 'unknown'),
                f"{agent_data.get('energy', 0):.1f}",
                agent_data.get('status', 'unknown')
            )
        
        console.print(table)
    
    # Place occupancy
    place_occupancy = world_info.get('place_occupancy', {})
    if place_occupancy:
        console.print("\n📍 Place Occupancy:")
        for place_id, place_data in place_occupancy.items():
            agent_count = place_data.get('agent_count', 0)
            place_name = place_data.get('name', place_id)
            if agent_count > 0:
                agents = ", ".join(place_data.get('agents', []))
                console.print(f"  • {place_name}: {agent_count} agents ({agents})")


def _display_agent_details(details: dict):
    """Display detailed agent information."""
    name = details.get('name', 'Unknown')
    
    # Create panel with agent info
    info_text = Text()
    info_text.append(f"ID: {details.get('id', 'unknown')}\n", style="dim")
    info_text.append(f"Bio: {details.get('bio', 'No bio available')}\n")
    info_text.append(f"Personality: {details.get('personality', 'No personality defined')}\n")
    info_text.append(f"Home: {details.get('home_location', 'unknown')}\n")
    
    console.print(Panel(info_text, title=f"Agent: {name}", style="cyan"))
    
    # Current state
    state = details.get('state', {})
    location_name = details.get('current_location_name', 'unknown')
    
    state_text = Text()
    state_text.append(f"Location: {location_name}\n", style="green")
    state_text.append(f"Status: {state.get('status', 'unknown')}\n", style="yellow")
    state_text.append(f"Energy: {state.get('energy', 0):.1f}/100\n", style="red" if state.get('energy', 0) < 50 else "green")
    state_text.append(f"Mood: {state.get('mood', 0):.1f}/10\n", style="blue")
    
    current_task = state.get('current_task')
    if current_task:
        state_text.append(f"Current Task: {current_task}\n", style="magenta")
    
    console.print(Panel(state_text, title="Current State", style="green"))
    
    # Available actions
    actions = details.get('available_actions', [])
    if actions:
        console.print("\n🎯 Available Actions:")
        for action in actions[:10]:  # Show first 10 actions
            console.print(f"  • {action}")


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
