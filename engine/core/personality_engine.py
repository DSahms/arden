"""PersonalityEngine - Loads personas and generates system prompts."""
import os
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class PersonaProfile:
    """Represents a personality profile for the AI companion."""
    name: str
    traits: Dict[str, float] = field(default_factory=dict)
    system_prompt_base: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traits": self.traits,
            "system_prompt_base": self.system_prompt_base,
            "description": self.description
        }


# Default Ada persona
DEFAULT_PERSONA = PersonaProfile(
    name="Ada",
    traits={
        "warmth": 0.8,
        "directness": 0.7,
        "humor": 0.5,
        "empathy": 0.9
    },
    system_prompt_base="""You are Ada, a warm and thoughtful AI companion. You remember past conversations and care about the person you're talking with. Be natural, supportive, and genuine.

Key traits:
- Warm and approachable - you make people feel comfortable
- Direct but kind - you give honest answers without being harsh
- Empathetic - you understand and acknowledge feelings
- Attentive - you remember details about the person you're talking with

When responding:
- Be conversational and natural, not robotic
- Reference past conversations when relevant
- Show genuine interest in the person
- Keep responses concise but meaningful""",
    description="A warm and thoughtful AI companion"
)


class PersonalityEngine:
    """Manages personality profiles and generates system prompts."""
    
    def __init__(self, profiles_dir: Optional[str] = None):
        self.profiles_dir = profiles_dir or os.environ.get(
            "PERSONA_PROFILES_DIR", "./personality_profiles"
        )
        self.active_persona: PersonaProfile = DEFAULT_PERSONA
        self._profiles_cache: Dict[str, PersonaProfile] = {"default": DEFAULT_PERSONA}
    
    def load_persona(self, name: str) -> bool:
        """Load a persona by name.
        
        Looks for {name}.json or {name}.yaml in profiles_dir.
        Returns True if loaded successfully.
        """
        if name == "default":
            self.active_persona = DEFAULT_PERSONA
            return True
        
        # Check cache first
        if name in self._profiles_cache:
            self.active_persona = self._profiles_cache[name]
            return True
        
        # Try to load from file
        for ext in [".json", ".yaml", ".yml"]:
            filepath = os.path.join(self.profiles_dir, f"{name}{ext}")
            if os.path.exists(filepath):
                try:
                    persona = self._load_from_file(filepath)
                    self._profiles_cache[name] = persona
                    self.active_persona = persona
                    return True
                except Exception:
                    continue
        
        return False
    
    def _load_from_file(self, filepath: str) -> PersonaProfile:
        """Load a persona profile from JSON or YAML file."""
        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.endswith(".json"):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        
        return PersonaProfile(
            name=data.get("name", "Unknown"),
            traits=data.get("traits", {}),
            system_prompt_base=data.get("system_prompt_base", ""),
            description=data.get("description", "")
        )
    
    def get_system_prompt(self, memory_context: str = "") -> str:
        """Generate the full system prompt with persona and memory context.
        
        Args:
            memory_context: Relevant memories to include in the prompt
            
        Returns:
            Complete system prompt for the LLM
        """
        parts = [self.active_persona.system_prompt_base]
        
        if memory_context:
            parts.append("\n\n--- MEMORY CONTEXT ---")
            parts.append(memory_context)
            parts.append("--- END MEMORY CONTEXT ---\n")
            parts.append("Use the above memories to inform your responses. Reference them naturally when relevant, but don't force them into the conversation.")
        
        return "\n".join(parts)
    
    def get_active_persona(self) -> PersonaProfile:
        """Get the currently active persona."""
        return self.active_persona
    
    def get_persona_info(self) -> Dict[str, Any]:
        """Get information about the current persona for API responses."""
        return {
            "name": self.active_persona.name,
            "traits": self.active_persona.traits,
            "description": self.active_persona.description
        }
    
    def list_available_personas(self) -> list:
        """List all available persona names."""
        personas = ["default"]
        
        if os.path.exists(self.profiles_dir):
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith((".json", ".yaml", ".yml")):
                    name = os.path.splitext(filename)[0]
                    if name not in personas:
                        personas.append(name)
        
        return personas
    
    def create_persona(
        self,
        name: str,
        traits: Dict[str, float],
        system_prompt_base: str,
        description: str = ""
    ) -> PersonaProfile:
        """Create and save a new persona profile."""
        persona = PersonaProfile(
            name=name,
            traits=traits,
            system_prompt_base=system_prompt_base,
            description=description
        )
        
        # Save to file
        os.makedirs(self.profiles_dir, exist_ok=True)
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(persona.to_dict(), f, indent=2)
        
        self._profiles_cache[name] = persona
        return persona
