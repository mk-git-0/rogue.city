"""
Guard NPC Class for Rogue City.

Law enforcement NPCs with authority, investigation capabilities,
and alignment-sensitive interactions.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_npc import BaseNPC, NPCPersonality, NPCMood
from areas.npc_system import NPCType
from core.alignment_system import Alignment


class GuardNPC(BaseNPC):
    """
    Guard NPC - Law enforcement with investigation and authority powers.
    
    Guards are alignment-sensitive NPCs who maintain order and investigate
    crimes. They offer bounties, arrest criminals, and provide security
    information to trustworthy characters.
    """
    
    def __init__(self, npc_id: str, name: str, alignment: Alignment = Alignment.GOOD,
                 faction: str = "town_guards", personality: NPCPersonality = NPCPersonality.STERN,
                 rank: str = "Guard", description: str = ""):
        """
        Initialize Guard NPC.
        
        Args:
            npc_id: Unique identifier
            name: Guard's name
            alignment: Usually Good, but can vary
            faction: Guard faction (usually town_guards)
            personality: Personality type (usually stern, gruff, or noble)
            rank: Military/guard rank
            description: Physical description
        """
        super().__init__(
            npc_id=npc_id,
            name=name,
            npc_type=NPCType.GUARD,
            alignment=alignment,
            faction=faction,
            personality=personality,
            description=description,
            base_reaction=1  # Guards start slightly positive to lawful characters
        )
        
        self.rank = rank
        self.patrol_area = ""
        self.authority_level = self._get_authority_level(rank)
        
        # Guard-specific capabilities
        self.can_arrest = True
        self.can_investigate = True
        self.has_bounty_access = True
        self.knows_local_laws = True
        
        # Services and knowledge
        self.services_offered = [
            'report_crime',
            'ask_directions', 
            'bounty_information',
            'law_enforcement',
            'area_security'
        ]
        
        self.special_knowledge = [
            'local_laws',
            'recent_crimes',
            'wanted_criminals',
            'patrol_routes',
            'security_concerns',
            'suspicious_activity'
        ]
        
        # Quest hooks for guard-related missions
        self.quest_hooks = [
            'investigate_theft',
            'capture_criminal',
            'patrol_assistance',
            'evidence_gathering',
            'witness_protection'
        ]
        
        # Guard-specific dialogue responses
        self.guard_responses = self._initialize_guard_responses()
    
    def _get_authority_level(self, rank: str) -> int:
        """Get numerical authority level based on rank."""
        rank_levels = {
            'Recruit': 1,
            'Guard': 2,
            'Corporal': 3,
            'Sergeant': 4,
            'Lieutenant': 5,
            'Captain': 6,
            'Commander': 7,
            'Chief': 8
        }
        return rank_levels.get(rank, 2)
    
    def _initialize_guard_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize guard-specific dialogue responses by alignment."""
        return {
            'good_character': {
                'greeting': [
                    f"{self.rank} {self.name} at your service, citizen.",
                    "Greetings, law-abiding citizen. How may I assist you?",
                    "Good to see honest folk. What brings you to speak with me?"
                ],
                'report_crime': [
                    "I appreciate citizens who report suspicious activity.",
                    "Thank you for bringing this to my attention. I'll investigate immediately.",
                    "Your civic duty is commendable. Tell me everything you saw."
                ],
                'bounty_inquiry': [
                    "There are indeed criminals at large. Are you licensed for bounty work?",
                    "I have information on wanted individuals, but only for qualified hunters.",
                    "Bounty work is dangerous. Ensure you're properly prepared."
                ]
            },
            'neutral_character': {
                'greeting': [
                    "State your business with the guard.",
                    "I am {self.rank} {self.name}. What do you need?",
                    "Citizen. How can the guard assist you today?"
                ],
                'report_crime': [
                    "I'll make note of your report. Provide all relevant details.",
                    "Your information will be investigated. Thank you for reporting it.",
                    "We take all reports seriously. What exactly did you witness?"
                ],
                'bounty_inquiry': [
                    "Bounty information is available to those who prove their competence.",
                    "Are you seeking mercenary work? Prove your abilities first.",
                    "Criminal apprehension is serious business. Show me your credentials."
                ]
            },
            'evil_character': {
                'greeting': [
                    "You. I'll be watching you closely.",
                    "State your business quickly. I have my eye on you.",
                    "What do you want? Make it fast."
                ],
                'report_crime': [
                    "How do I know you're not the one I should be investigating?",
                    "I'll look into it... and I'll be looking into you as well.",
                    "Criminals reporting crimes. How... convenient."
                ],
                'bounty_inquiry': [
                    "Bounty work? I'd rather see you behind bars than chasing others.",
                    "You asking about bounties makes me suspicious of your motives.",
                    "I don't trust you with that kind of responsibility."
                ]
            }
        }
    
    def get_alignment_specific_response(self, character, context: str) -> str:
        """Get response appropriate to character's alignment."""
        import random
        
        alignment = character.alignment_manager.get_alignment()
        
        if alignment == Alignment.GOOD:
            alignment_key = 'good_character'
        elif alignment == Alignment.EVIL:
            alignment_key = 'evil_character'
        else:
            alignment_key = 'neutral_character'
        
        responses = self.guard_responses.get(alignment_key, {}).get(context, [])
        if responses:
            response = random.choice(responses)
            # Replace placeholder names
            return response.replace('{self.rank}', self.rank).replace('{self.name}', self.name)
        
        return f"{self.rank} {self.name} nods at you."
    
    def get_available_services(self) -> List[str]:
        """Get services this guard can provide."""
        return self.services_offered.copy()
    
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if guard can provide service to character."""
        alignment = character.alignment_manager.get_alignment()
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        # Service availability based on alignment and reputation
        if service == 'report_crime':
            return True, "I'll take your report."
        
        elif service == 'ask_directions':
            return True, "I can point you in the right direction."
        
        elif service == 'bounty_information':
            if alignment == Alignment.EVIL and reaction.value < 0:
                return False, "I don't trust you with bounty information."
            elif reaction.value < -1:
                return False, "Prove your trustworthiness first."
            else:
                return True, "I have information on wanted criminals."
        
        elif service == 'law_enforcement':
            if self.authority_level < 3:
                return False, "That's above my authority level."
            elif alignment == Alignment.EVIL:
                return False, "I can't trust you with law enforcement matters."
            else:
                return True, "I can assist with official matters."
        
        elif service == 'area_security':
            if reaction.value < 0:
                return False, "That information is not for you."
            else:
                return True, "I can share security information."
        
        return False, f"I don't provide {service}."
    
    def investigate_character(self, character) -> Dict[str, Any]:
        """Investigate a character's background and activities."""
        investigation_results = {
            'alignment_assessment': character.alignment_manager.get_alignment().name,
            'reputation_standing': {},
            'criminal_record': [],
            'trustworthiness': 'unknown'
        }
        
        # Check reputation with law enforcement factions
        for faction in ['town_guards', 'paladins', 'priests']:
            if hasattr(character, 'reputation_manager'):
                rep = character.reputation_manager.get_reputation(faction)
                investigation_results['reputation_standing'][faction] = rep
        
        # Assess overall trustworthiness
        alignment = character.alignment_manager.get_alignment()
        if alignment == Alignment.GOOD:
            investigation_results['trustworthiness'] = 'high'
        elif alignment == Alignment.EVIL:
            investigation_results['trustworthiness'] = 'low' 
        else:
            investigation_results['trustworthiness'] = 'moderate'
        
        return investigation_results
    
    def offer_bounty_mission(self, character) -> Optional[Dict[str, Any]]:
        """Offer a bounty mission if character is qualified."""
        if not self.can_provide_service('bounty_information', character)[0]:
            return None
        
        # Generate bounty mission based on character level and reputation
        bounty_missions = [
            {
                'target': 'Pickpocket Gang',
                'reward': 50,
                'difficulty': 'easy',
                'description': 'A group of pickpockets has been targeting merchants in the market square.'
            },
            {
                'target': 'Highway Bandit',
                'reward': 100,
                'difficulty': 'medium', 
                'description': 'A bandit has been robbing travelers on the main road.'
            },
            {
                'target': 'Corrupt Official',
                'reward': 200,
                'difficulty': 'hard',
                'description': 'Evidence suggests a city official is taking bribes.'
            }
        ]
        
        import random
        return random.choice(bounty_missions)
    
    def process_crime_report(self, character, crime_details: str) -> str:
        """Process a crime report from a character."""
        alignment = character.alignment_manager.get_alignment()
        
        # Increase reputation for reporting crimes (good citizenship)
        if hasattr(character, 'reputation_manager'):
            character.reputation_manager.modify_reputation(
                self.faction, 
                2 if alignment == Alignment.GOOD else 1,
                f"Reported crime: {crime_details[:50]}..."
            )
        
        # Update mood to grateful
        self.change_mood(NPCMood.GRATEFUL, 0.7)
        
        responses = [
            f"Thank you for this report. I'll investigate {crime_details} immediately.",
            f"Your civic duty is noted. We'll look into {crime_details}.",
            f"I appreciate citizens who report {crime_details}. The investigation begins now."
        ]
        
        import random
        return random.choice(responses)
    
    def get_law_information(self, character) -> List[str]:
        """Provide information about local laws."""
        if not self.knows_local_laws:
            return ["I don't have access to legal information."]
        
        laws = [
            "Theft and burglary are punishable by fines and imprisonment.",
            "Murder carries the death penalty or life imprisonment.",
            "Disturbing the peace results in fines and temporary detention.",
            "Practicing necromancy is strictly forbidden within city limits.",
            "Weapons must be peace-bonded in certain areas of the city.",
            "Merchants must have proper licenses to trade.",
            "Public intoxication may result in overnight detention."
        ]
        
        return laws
    
    def arrest_character(self, character, crime: str) -> str:
        """Attempt to arrest a character for a crime."""
        if not self.can_arrest:
            return f"{self.rank} {self.name} calls for backup to handle the arrest."
        
        alignment = character.alignment_manager.get_alignment()
        
        # Resistance based on alignment and reputation
        if alignment == Alignment.EVIL:
            return f"You're under arrest for {crime}! Don't even think about resisting!"
        elif alignment == Alignment.GOOD:
            return f"I'm sorry, but I must arrest you for {crime}. Please come peacefully."
        else:
            return f"You're under arrest for {crime}. Comply and this will go easier."
    
    def get_patrol_information(self, character) -> str:
        """Provide patrol route information to trusted characters."""
        can_share, message = self.can_provide_service('area_security', character)
        if not can_share:
            return message
        
        patrol_info = [
            "We patrol the market square every two hours during daylight.",
            "Night patrols focus on the tavern district and main roads.",
            "The warehouse district has increased patrols due to recent thefts.",
            "Guard posts are stationed at all city gates.",
            "Emergency signals are horn blasts - three short, one long."
        ]
        
        import random
        return random.choice(patrol_info)