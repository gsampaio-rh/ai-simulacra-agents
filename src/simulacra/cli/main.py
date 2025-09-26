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
@click.option('--memories', '-m', default=10, help='Number of recent memories to show')
@click.option('--query', '-q', default=None, help='Query memories using semantic search')
@click.option('--reflections', '-r', is_flag=True, help='Show agent reflections')
def agent(agent_id: str, memories: int, query: str, reflections: bool):
    """Show details for a specific agent including memories."""
    async def _agent():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        details = sim_controller.get_agent_details(agent_id, log_beautifully=False)
        if not details:
            console.print(f"[red]Agent '{agent_id}' not found[/red]")
            return
        
        # Get planning information
        agent = await sim_controller.storage.get_agent(agent_id)
        if agent:
            try:
                current_plan = await sim_controller.planning_engine.get_current_daily_plan(agent_id)
                current_task = await sim_controller.planning_engine.get_current_task(agent_id)
                
                details["planning"] = {
                    "has_plan": current_plan is not None,
                    "current_goal": current_plan.goals[0] if current_plan and current_plan.goals else None,
                    "current_task": current_task.description if current_task else None,
                    "current_task_location": current_task.location if current_task else None,
                    "plan_blocks_count": len(current_plan.hourly_blocks) if current_plan else 0
                }
            except Exception as e:
                details["planning"] = {"error": str(e)}
        
        # Display agent details with planning information
        _display_agent_details(details)
        
        # Show recent memories
        try:
            if query:
                console.print(f"\n[bold cyan]Memories for '{query}' (agent: {agent_id}):[/bold cyan]")
                results = await sim_controller.memory_manager.retrieve_relevant_memories(
                    agent_id, query, memories
                )
                
                if not results:
                    console.print(f"[yellow]No relevant memories found for query: '{query}'[/yellow]")
                else:
                    for i, result in enumerate(results, 1):
                        memory = result.memory
                        score_text = Text()
                        score_text.append(f"{i}. ", style="bold")
                        score_text.append(f"{memory.content}", style="white")
                        score_text.append(f"\n   Score: {result.score:.3f} ", style="dim")
                        score_text.append(f"(semantic: {result.semantic_score:.3f}, ", style="dim green")
                        score_text.append(f"recency: {result.recency_score:.3f}, ", style="dim yellow")
                        score_text.append(f"importance: {result.importance_score:.3f})", style="dim red")
                        
                        timestamp = memory.timestamp.strftime("%H:%M")
                        score_text.append(f" [{timestamp}]", style="dim blue")
                        
                        console.print(score_text)
            else:
                recent_memories = await sim_controller.memory_manager.get_recent_memories(agent_id, memories)
                if recent_memories:
                    console.print(f"\n[bold cyan]Recent memories for {agent_id}:[/bold cyan]")
                    for i, memory in enumerate(recent_memories, 1):
                        memory_text = Text()
                        memory_text.append(f"{i}. ", style="bold")
                        memory_text.append(f"{memory.content}", style="white")
                        memory_text.append(f" (importance: {memory.importance_score:.1f}, ", style="dim")
                        memory_text.append(f"{memory.memory_type.value})", style="dim")
                        
                        timestamp = memory.timestamp.strftime("%H:%M")
                        memory_text.append(f" [{timestamp}]", style="dim blue")
                        
                        console.print(memory_text)
                else:
                    console.print(f"[yellow]No memories found for agent '{agent_id}'[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error retrieving memories: {e}[/red]")
        
        # Show reflections if requested
        if reflections:
            try:
                console.print(f"\n[bold cyan]Recent reflections for {agent_id}:[/bold cyan]")
                agent_reflections = await sim_controller.reflection_engine.get_agent_reflections(agent_id, 5)
                
                if agent_reflections:
                    for i, reflection in enumerate(agent_reflections, 1):
                        reflection_text = Text()
                        reflection_text.append(f"{i}. ", style="bold")
                        reflection_text.append(f"{reflection.content}", style="italic bright_cyan")
                        reflection_text.append(f" (importance: {reflection.importance_score:.1f})", style="dim")
                        
                        timestamp = reflection.timestamp.strftime("%H:%M")
                        reflection_text.append(f" [{timestamp}]", style="dim blue")
                        
                        console.print(reflection_text)
                        
                        # Show supporting memories count
                        if reflection.supporting_memories:
                            console.print(f"   [dim]Based on {len(reflection.supporting_memories)} memories[/dim]")
                else:
                    console.print(f"[yellow]No reflections found for agent '{agent_id}'[/yellow]")
                    console.print(f"[dim]Importance accumulator: {details['state'].get('importance_accumulator', 0):.1f} / {sim_controller.settings.reflection_threshold}[/dim]")
            
            except Exception as e:
                console.print(f"[red]Error retrieving reflections: {e}[/red]")
        
        await sim_controller.cleanup()
    
    asyncio.run(_agent())


@cli.command()
@click.argument('agent_id')
def reflect(agent_id: str):
    """Manually trigger reflection for a specific agent."""
    async def _reflect():
        global sim_controller
        sim_controller = SimulationController()
        await sim_controller.initialize()
        
        # Find the agent
        if agent_id not in sim_controller.agents:
            console.print(f"[red]Agent '{agent_id}' not found[/red]")
            available_agents = list(sim_controller.agents.keys())
            if available_agents:
                console.print(f"Available agents: {', '.join(available_agents)}")
            return
        
        agent = sim_controller.agents[agent_id]
        
        console.print(f"[blue]Triggering reflection for {agent.name}...[/blue]")
        console.print(f"Current importance accumulator: {agent.state.importance_accumulator:.1f}")
        
        try:
            # Force reflection regardless of threshold
            reflections = await sim_controller.reflection_engine.trigger_reflection(agent)
            
            if reflections:
                console.print(f"[green]✅ Generated {len(reflections)} reflections for {agent.name}![/green]")
                console.print("\n[bold cyan]Generated Reflections:[/bold cyan]")
                for i, reflection in enumerate(reflections, 1):
                    console.print(f"{i}. [italic]{reflection.content}[/italic]")
            else:
                console.print(f"[yellow]No reflections generated for {agent.name}[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error generating reflections: {e}[/red]")
        
        await sim_controller.cleanup()
    
    asyncio.run(_reflect())


@cli.command()
@click.argument('agent_id')
@click.option('--generate', '-g', is_flag=True, help='Generate a new daily plan')
def plan(agent_id: str, generate: bool):
    """Show or generate agent's daily plan."""
    async def _plan():
        global sim_controller
        
        try:
            if not sim_controller:
                sim_controller = SimulationController()
                await sim_controller.initialize()
            
            # Get agent details
            agent = await sim_controller.storage.get_agent(agent_id)
            
            if not agent:
                console.print(f"[red]Error: Agent '{agent_id}' not found[/red]")
                return
            
            if generate:
                # Generate new plan
                console.print(f"[yellow]Generating new daily plan for {agent.name}...[/yellow]")
                daily_plan = await sim_controller.planning_engine.generate_daily_plan(agent)
                
                if daily_plan:
                    console.print(f"[green]✓ Generated daily plan for {agent.name}[/green]")
                else:
                    console.print(f"[red]✗ Failed to generate plan for {agent.name}[/red]")
                    return
            
            # Get current plan
            current_plan = await sim_controller.planning_engine.get_current_daily_plan(agent_id)
            
            if not current_plan:
                console.print(f"[yellow]No daily plan found for {agent.name}[/yellow]")
                console.print("Use --generate to create a new plan")
                return
            
            # Display the plan beautifully
            await _display_agent_plan(agent, current_plan, sim_controller.planning_engine)
            
        except Exception as e:
            console.print(f"[red]Error showing plan for {agent_id}: {e}[/red]")
        finally:
            if sim_controller:
                await sim_controller.cleanup()
    
    asyncio.run(_plan())


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
                            # Also show recent memories in interactive mode
                            try:
                                memories = await sim_controller.memory_manager.get_recent_memories(agent_id, 5)
                                if memories:
                                    console.print(f"\n[bold cyan]Recent memories for {agent_id}:[/bold cyan]")
                                    for i, memory in enumerate(memories, 1):
                                        console.print(f"  {i}. {memory.content} (importance: {memory.importance_score:.1f})")
                                else:
                                    console.print(f"[yellow]No memories found for '{agent_id}'[/yellow]")
                            except Exception as e:
                                console.print(f"[red]Error retrieving memories: {e}[/red]")
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


async def _display_agent_plan(agent, current_plan, planning_engine):
    """Display agent's daily plan beautifully."""
    from datetime import datetime, time
    
    # Plan header
    plan_text = Text()
    plan_text.append(f"📅 Daily Plan for {current_plan.date}\n\n", style="bold bright_yellow")
    
    # Goals
    if current_plan.goals:
        plan_text.append("🎯 Goals for Today:\n", style="bold bright_white")
        for i, goal in enumerate(current_plan.goals, 1):
            plan_text.append(f"  {i}. {goal}\n", style="bright_yellow")
        plan_text.append("\n")
    
    # Time blocks
    plan_text.append("📋 Schedule:\n", style="bold bright_white")
    current_time = datetime.now().time()
    
    for block in current_plan.hourly_blocks:
        # Time format
        end_time = block.end_time
        time_str = f"{block.start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        
        # Status indicator
        if block.start_time <= current_time <= end_time:
            status_icon = "🔥"  # Currently active
            status_style = "bold bright_red"
        elif current_time > end_time:
            status_icon = "✅"  # Completed
            status_style = "green"
        else:
            status_icon = "⏰"  # Upcoming
            status_style = "blue"
        
        plan_text.append(f"  {status_icon} ", style=status_style)
        plan_text.append(f"{time_str} - ", style="dim")
        plan_text.append(f"{block.activity}", style="bright_white")
        
        if block.location:
            plan_text.append(f" (at {block.location})", style="cyan")
        
        plan_text.append("\n")
        
        # Show tasks if any
        if block.tasks:
            for task in block.tasks:
                task_icon = "📌" if task.status == "pending" else "✓"
                plan_text.append(f"    {task_icon} {task.description}\n", style="dim")
    
    # Current task
    current_task = await planning_engine.get_current_task(agent.id)
    if current_task:
        plan_text.append(f"\n🎯 Current Task: {current_task.description}", style="bold bright_green")
        if current_task.location:
            plan_text.append(f" (at {current_task.location})", style="cyan")
        plan_text.append("\n")
    
    console.print(Panel(
        plan_text,
        title=f"🗓️ {agent.name}'s Daily Plan",
        border_style="bright_yellow",
        padding=(1, 2),
        width=100
    ))


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
    
    # Show importance accumulator and reflection progress
    importance_acc = state.get('importance_accumulator', 0)
    threshold = 15.0  # Should match settings.reflection_threshold
    state_text.append(f"Reflection Progress: {importance_acc:.1f}/{threshold} ", style="cyan")
    if importance_acc >= threshold:
        state_text.append("(Ready to reflect!)\n", style="bright_cyan bold")
    else:
        progress_percent = (importance_acc / threshold) * 100
        state_text.append(f"({progress_percent:.0f}%)\n", style="dim")
    
    current_task = state.get('current_task')
    if current_task:
        state_text.append(f"Current Task: {current_task}\n", style="magenta")
    
    console.print(Panel(state_text, title="Current State", style="green"))
    
    # Planning information
    planning = details.get('planning', {})
    if planning and not planning.get('error'):
        plan_text = Text()
        
        if planning.get('has_plan'):
            plan_text.append("📋 HAS DAILY PLAN\n", style="bold bright_yellow")
            
            if planning.get('current_goal'):
                plan_text.append(f"🎯 Goal: {planning['current_goal']}\n", style="bright_yellow")
            
            if planning.get('current_task'):
                plan_text.append(f"📌 Current Task: {planning['current_task']}", style="bright_green")
                if planning.get('current_task_location'):
                    plan_text.append(f" (at {planning['current_task_location']})", style="cyan")
                plan_text.append("\n")
            else:
                # Show next scheduled activity if no current task
                plan_text.append("📌 No active task right now\n", style="dim")
            
            blocks_count = planning.get('plan_blocks_count', 0)
            if blocks_count > 0:
                plan_text.append(f"⏰ Plan has {blocks_count} time blocks\n", style="dim")
        else:
            plan_text.append("📋 No daily plan", style="dim yellow")
        
        console.print(Panel(plan_text, title="📅 Daily Planning", style="bright_yellow"))
    
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
