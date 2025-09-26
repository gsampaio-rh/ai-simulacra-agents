# World Configuration

Learn how to design and configure the simulation world where your AI agents live, explore, and interact. The world system provides rich environments that influence agent behavior and enable realistic simulations.

## 🌍 World System Overview

The simulation world consists of **places** where agents can be located and **objects** they can interact with. The world configuration defines the physical and social environment that shapes agent behavior.

### Core Components

**Places**:
- Physical locations where agents can be present
- Have properties like capacity, description, and connections
- Support agent movement and spatial reasoning

**Objects**:
- Interactive items within places
- Enable rich environmental interactions
- Can have state and support multiple interaction types

**Connections**:
- Define how places link together
- Control agent movement possibilities
- Create the spatial topology of your world

## 📁 Configuration Files

### `config/world.json`

The main world configuration file defines all places and objects:

```json
{
  "places": [
    {
      "id": "cafe",
      "name": "Community Cafe",
      "description": "A cozy neighborhood cafe with comfortable seating, local art on the walls, and the aroma of fresh coffee.",
      "capacity": 20,
      "connections": ["street", "apartment_1"],
      "properties": {
        "atmosphere": "social",
        "noise_level": "moderate",
        "lighting": "warm"
      }
    }
  ],
  "objects": [
    {
      "id": "espresso_machine",
      "name": "Professional Espresso Machine",
      "description": "A gleaming espresso machine that produces perfect coffee",
      "location": "cafe",
      "interactions": ["make_coffee", "clean", "examine"],
      "properties": {
        "state": "ready",
        "uses_remaining": 50
      }
    }
  ]
}
```

### `config/agents.json`

Defines which agents exist and their home locations:

```json
{
  "agents": [
    {
      "id": "isabella",
      "name": "Isabella Rodriguez",
      "bio": "Isabella is a warm and community-minded cafe owner who loves hosting events and bringing people together.",
      "personality": "warm, community-minded, creative, empathetic, organized",
      "home_location": "apartment_1",
      "relationships": {
        "john": "friend",
        "maria": "friend"
      }
    }
  ]
}
```

## 🏠 Designing Places

### Place Schema

```json
{
  "id": "unique_identifier",           // Required: Unique place ID
  "name": "Display Name",              // Required: Human-readable name
  "description": "Rich description",   // Required: What agents observe
  "capacity": 10,                      // Optional: Max agents (default: unlimited)
  "connections": ["place1", "place2"], // Optional: Connected places
  "properties": {                      // Optional: Custom properties
    "atmosphere": "quiet",
    "accessibility": "wheelchair_accessible"
  }
}
```

### Place Types and Examples

**Residential Spaces**:
```json
{
  "id": "apartment_1",
  "name": "Isabella's Apartment",
  "description": "A cozy apartment above the cafe, filled with warm lighting, colorful artwork, and the lingering aroma of something delicious cooking in the kitchen.",
  "capacity": 4,
  "connections": ["cafe", "street"],
  "properties": {
    "privacy_level": "private",
    "comfort_level": "high",
    "creativity_boost": true
  }
}
```

**Social Spaces**:
```json
{
  "id": "community_garden",
  "name": "Community Garden",
  "description": "A peaceful community garden with raised beds full of vegetables and flowers, benches for resting, and the gentle sound of a small fountain.",
  "capacity": 15,
  "connections": ["street", "park"],
  "properties": {
    "atmosphere": "peaceful",
    "activity_type": "gardening",
    "social_interaction": "moderate"
  }
}
```

**Work Spaces**:
```json
{
  "id": "design_studio",
  "name": "John's Design Studio",
  "description": "A minimalist workspace with dual monitors, design sketches pinned to the walls, and large windows providing excellent natural light.",
  "capacity": 3,
  "connections": ["apartment_2"],
  "properties": {
    "productivity_boost": true,
    "creativity_support": true,
    "noise_level": "quiet"
  }
}
```

**Public Spaces**:
```json
{
  "id": "town_square",
  "name": "Main Town Square",
  "description": "A bustling public square with a central fountain, surrounded by shops and cafes. People gather here to meet, relax, and enjoy street performances.",
  "capacity": 50,
  "connections": ["street", "market", "cafe", "library"],
  "properties": {
    "social_energy": "high",
    "event_space": true,
    "foot_traffic": "heavy"
  }
}
```

### Connection Patterns

**Linear Layout** (Street-based):
```
apartment_1 ←→ street ←→ cafe ←→ market
```

**Hub and Spoke** (Central square):
```
    library
      ↑
cafe ←→ town_square ←→ park
      ↓
   market
```

**Grid Layout** (Urban planning):
```
residential_north ←→ commercial_north ←→ park_north
      ↑                    ↑                 ↑
residential_center ←→ town_square ←→ commercial_center
      ↑                    ↑                 ↑
residential_south ←→ commercial_south ←→ park_south
```

## 🎯 Interactive Objects

### Object Schema

```json
{
  "id": "unique_identifier",           // Required: Unique object ID
  "name": "Display Name",              // Required: Human-readable name
  "description": "What agents see",    // Required: Observable description
  "location": "place_id",              // Required: Where object exists
  "interactions": ["action1", "action2"], // Optional: Possible interactions
  "properties": {                      // Optional: Object state and metadata
    "state": "ready",
    "durability": 100
  }
}
```

### Object Categories

**Functional Objects**:
```json
{
  "id": "coffee_machine",
  "name": "Espresso Machine",
  "description": "A professional-grade espresso machine with steam wand and multiple brew settings",
  "location": "cafe",
  "interactions": ["make_coffee", "clean", "maintain", "examine"],
  "properties": {
    "state": "ready",
    "coffee_beans": 80,
    "water_level": 90,
    "last_cleaned": "2025-09-26T08:00:00"
  }
}
```

**Comfort Objects**:
```json
{
  "id": "reading_chair",
  "name": "Comfortable Reading Chair",
  "description": "A plush armchair with perfect reading light and a small side table for coffee",
  "location": "library",
  "interactions": ["sit", "read", "relax", "observe"],
  "properties": {
    "comfort_level": "high",
    "occupancy": "available",
    "preferred_activity": "reading"
  }
}
```

**Creative Objects**:
```json
{
  "id": "art_easel",
  "name": "Artist's Easel",
  "description": "A wooden easel set up with a blank canvas, surrounded by paints and brushes",
  "location": "art_studio",
  "interactions": ["paint", "sketch", "clean_brushes", "examine"],
  "properties": {
    "canvas_state": "blank",
    "paint_supplies": "full",
    "current_project": null
  }
}
```

**Social Objects**:
```json
{
  "id": "community_board",
  "name": "Community Message Board",
  "description": "A cork board filled with local announcements, event flyers, and personal messages",
  "location": "cafe",
  "interactions": ["read_messages", "post_message", "take_flyer"],
  "properties": {
    "message_count": 12,
    "recent_posts": ["yoga_class", "book_club", "garden_party"],
    "last_updated": "2025-09-26T10:30:00"
  }
}
```

## 🎨 Advanced World Design

### Dynamic Properties

Objects and places can have properties that change over time or based on agent interactions:

```json
{
  "id": "garden_bed",
  "name": "Vegetable Garden Bed",
  "description": "A raised bed with tomatoes, herbs, and flowers in various stages of growth",
  "location": "community_garden",
  "interactions": ["water", "weed", "harvest", "plant", "examine"],
  "properties": {
    "growth_stage": "flowering",
    "water_level": "adequate",
    "last_tended": "2025-09-26T07:00:00",
    "seasonal_state": "summer",
    "yield_potential": "high"
  }
}
```

### Atmospheric Properties

Places can have properties that influence agent mood and behavior:

```json
{
  "id": "meditation_room",
  "name": "Quiet Meditation Space",
  "description": "A serene room with soft lighting, comfortable cushions, and the gentle sound of a small water feature",
  "capacity": 6,
  "connections": ["wellness_center"],
  "properties": {
    "stress_reduction": 0.8,
    "focus_enhancement": 0.7,
    "noise_level": "silent",
    "lighting": "soft",
    "temperature": "comfortable",
    "meditation_aids": ["cushions", "blankets", "singing_bowl"]
  }
}
```

### Seasonal and Time-Based Changes

Configure properties that change based on time or conditions:

```json
{
  "id": "outdoor_market",
  "name": "Farmers Market",
  "description": "A bustling outdoor market with fresh produce, handmade crafts, and local delicacies",
  "capacity": 30,
  "connections": ["town_square", "parking"],
  "properties": {
    "operating_hours": {
      "saturday": "08:00-14:00",
      "sunday": "09:00-13:00"
    },
    "weather_dependent": true,
    "seasonal_vendors": {
      "spring": ["flower_vendor", "plant_starts"],
      "summer": ["fruit_vendor", "vegetable_vendor"],
      "fall": ["pumpkin_vendor", "apple_vendor"],
      "winter": ["craft_vendor", "hot_drinks"]
    }
  }
}
```

## 🔗 World Topology

### Connection Design Principles

**Realistic Movement Patterns**:
- Agents should be able to move between logically connected spaces
- Consider physical proximity and transportation methods
- Include both direct and indirect paths for variety

**Social Flow**:
- Create natural gathering points (cafes, squares, parks)
- Balance private spaces (homes) with public spaces
- Enable chance encounters and planned meetings

**Activity Zones**:
- Group related places (residential areas, commercial districts)
- Provide diverse environments for different agent personalities
- Support various activities (work, socializing, recreation)

### Example: Small Town Layout

```json
{
  "places": [
    {
      "id": "main_street",
      "name": "Main Street",
      "description": "A quiet residential street lined with trees and small apartment buildings",
      "connections": ["apartment_1", "apartment_2", "apartment_3", "cafe", "town_square"]
    },
    {
      "id": "town_square",
      "name": "Central Town Square",
      "description": "The heart of the community with a fountain, benches, and regular events",
      "connections": ["main_street", "cafe", "library", "market", "community_garden"]
    },
    {
      "id": "cafe",
      "name": "Community Cafe",
      "description": "A cozy neighborhood cafe where locals gather for coffee and conversation",
      "connections": ["main_street", "town_square", "apartment_1"]
    },
    {
      "id": "community_garden",
      "name": "Community Garden",
      "description": "A shared gardening space where neighbors grow vegetables and flowers together",
      "connections": ["town_square", "park"]
    },
    {
      "id": "library",
      "name": "Public Library",
      "description": "A quiet library with reading areas, community meeting rooms, and local history archives",
      "connections": ["town_square"]
    }
  ]
}
```

## 🎭 Agent Behavior Influence

### How World Design Affects Agents

**Personality Expression**:
- Introverted agents prefer quiet spaces (library, home)
- Social agents gravitate toward gathering places (cafe, square)
- Creative agents seek inspiring environments (art studio, garden)

**Goal Achievement**:
- Agents plan activities based on available locations
- Object interactions support various agent objectives
- Place properties influence mood and energy

**Social Interactions**:
- Gathering places enable chance encounters
- Shared objects create interaction opportunities
- Place capacity affects social dynamics

### Design for Agent Stories

**Example: Isabella's Daily Flow**:
```
Home (apartment_1) → Cafe (work) → Town Square (social) → 
Community Garden (peaceful) → Cafe (evening social)
```

**Supporting Configuration**:
- Apartment connected to cafe (convenient commute)
- Cafe connected to town square (social opportunities)
- Garden provides peaceful alternative
- Multiple paths enable variety and choice

## 🛠️ Configuration Best Practices

### Start Simple

**Basic World**:
1. 5-7 places maximum
2. Clear connection patterns
3. Mix of private and public spaces
4. Few essential objects

### Add Complexity Gradually

**Enhanced World**:
1. Specialized spaces for different activities
2. Rich object interactions
3. Dynamic properties
4. Seasonal or time-based changes

### Test with Agents

**Validation**:
1. Run simulations to observe agent movement patterns
2. Check if all places are reachable and used
3. Verify that agent personalities are expressed appropriately
4. Adjust connections and properties based on behavior

### Performance Considerations

**Efficient Design**:
- Limit place count for faster pathfinding
- Avoid overly complex connection graphs
- Use meaningful object interactions
- Balance detail with simulation performance

## 📊 World Analysis

### Monitor World Usage

**CLI Commands**:
```bash
python main.py status                    # See current agent locations
python main.py export                    # Export movement data
python main.py agent isabella --memories # Check location memories
```

**Analysis Questions**:
- Which places do agents visit most frequently?
- Are there isolated or unused locations?
- Do agent movement patterns match their personalities?
- Are social interactions happening in appropriate spaces?

### Iteration and Improvement

**Common Adjustments**:
1. **Add missing connections** - If agents seem "stuck" in areas
2. **Adjust capacities** - If spaces feel too crowded or empty
3. **Enhance descriptions** - If agent observations lack detail
4. **Add interactive objects** - If spaces feel static
5. **Create activity zones** - If agent behavior lacks variety

## 🎯 Example Configurations

### Cozy Neighborhood

Perfect for community-focused simulations:

```json
{
  "places": [
    {
      "id": "residential_street",
      "name": "Maple Street",
      "description": "A tree-lined residential street with charming houses and gardens",
      "connections": ["home_1", "home_2", "home_3", "neighborhood_cafe"]
    },
    {
      "id": "neighborhood_cafe",
      "name": "The Corner Cafe",
      "description": "A beloved local cafe with regulars who know each other by name",
      "capacity": 12,
      "connections": ["residential_street", "small_park"]
    },
    {
      "id": "small_park",
      "name": "Pocket Park",
      "description": "A small neighborhood park with benches, a playground, and old oak trees",
      "connections": ["neighborhood_cafe", "residential_street"]
    }
  ]
}
```

### Urban Campus

Ideal for studying work-life balance:

```json
{
  "places": [
    {
      "id": "co_working_space",
      "name": "Creative Co-working Hub",
      "description": "An open workspace with shared desks, meeting rooms, and a coffee bar",
      "capacity": 25,
      "connections": ["lobby", "rooftop_terrace"]
    },
    {
      "id": "rooftop_terrace",
      "name": "Rooftop Garden Terrace",
      "description": "A peaceful outdoor space with plants, seating areas, and city views",
      "connections": ["co_working_space"]
    },
    {
      "id": "campus_cafe",
      "name": "Campus Cafe",
      "description": "A busy cafe popular with students and workers",
      "capacity": 30,
      "connections": ["lobby", "library", "study_rooms"]
    }
  ]
}
```

### Rural Retreat

Great for wellness and nature-focused scenarios:

```json
{
  "places": [
    {
      "id": "retreat_center",
      "name": "Wellness Retreat Center",
      "description": "A peaceful center with meditation rooms, yoga studios, and healing spaces",
      "connections": ["walking_trails", "organic_garden", "dining_hall"]
    },
    {
      "id": "walking_trails",
      "name": "Forest Walking Trails",
      "description": "Winding trails through old-growth forest with benches and meditation spots",
      "connections": ["retreat_center", "meditation_grove"]
    },
    {
      "id": "organic_garden",
      "name": "Organic Teaching Garden",
      "description": "A beautiful garden where guests learn about sustainable growing practices",
      "connections": ["retreat_center", "greenhouse"]
    }
  ]
}
```

---

The world configuration is the foundation that enables rich, believable agent behavior. By thoughtfully designing places and objects, you create environments where agent personalities can shine and authentic interactions can emerge.

**Next**: Try [Agent Configuration](agent-configuration.md) to create agents that match your world, or see [Examples](../examples/) for complete world setups.
