"""
Quest Giver NPC Class for Rogue City.

NPCs that provide missions, tasks, and adventure hooks based on
character alignment, reputation, and capabilities.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_npc import BaseNPC, NPCPersonality, NPCMood
from areas.npc_system import NPCType
from core.alignment_system import Alignment
import time


class QuestGiverNPC(BaseNPC):
    """
    Quest Giver NPC - Provides missions and tasks to adventurers.
    
    Quest givers offer different types of missions based on character
    alignment, reputation, and past performance. They track quest
    completion and adjust future offerings accordingly.
    """
    
    def __init__(self, npc_id: str, name: str, alignment: Alignment = Alignment.NEUTRAL,
                 faction: str = "quest_givers", personality: NPCPersonality = NPCPersonality.FRIENDLY,
                 quest_type_focus: str = "general", description: str = "",
                 authority_level: int = 1):
        """
        Initialize Quest Giver NPC.
        
        Args:
            npc_id: Unique identifier
            name: Quest giver's name
            alignment: Alignment affects types of quests offered
            faction: Faction membership
            personality: Personality type
            quest_type_focus: Primary quest category (general, combat, social, etc.)
            description: Physical description
            authority_level: Level of quests they can authorize (1-5)
        """
        super().__init__(
            npc_id=npc_id,
            name=name,
            npc_type=NPCType.CITIZEN,  # Using citizen as base, could add QUEST_GIVER type
            alignment=alignment,
            faction=faction,
            personality=personality,
            description=description,
            base_reaction=0
        )
        
        self.quest_type_focus = quest_type_focus
        self.authority_level = authority_level
        
        # Quest management
        self.available_quests = []
        self.completed_quests = {}  # character_name -> [quest_ids]
        self.active_quests = {}     # character_name -> [quest_ids]
        self.quest_cooldowns = {}   # quest_id -> cooldown_end_time
        self.failed_quests = {}     # character_name -> [quest_ids]
        
        # Quest giver capabilities
        self.max_concurrent_quests = 3
        self.gives_rewards = True
        self.tracks_reputation = True
        
        # Services and knowledge
        self.services_offered = [
            'available_quests',
            'quest_progress',
            'quest_rewards',
            'adventure_advice',
            'area_dangers'
        ]
        
        self.special_knowledge = [
            'local_problems',
            'adventure_opportunities',
            'dangerous_areas',
            'treasure_locations',
            'monster_threats',
            'political_situations'
        ]
        
        # Initialize quest types based on focus and alignment
        self._initialize_quest_templates()
        
        # Quest giver specific responses
        self.quest_responses = self._initialize_quest_responses()
    
    def _initialize_quest_templates(self):
        """Initialize quest templates based on focus and alignment."""
        base_quests = {
            'general': [
                {
                    'id': 'delivery_package',
                    'name': 'Package Delivery',
                    'description': 'Deliver a package to another location',
                    'alignment_req': None,
                    'level_req': 1,
                    'reward_gold': 25,
                    'reputation_reward': 5
                },
                {
                    'id': 'gather_herbs',
                    'name': 'Herb Gathering',
                    'description': 'Collect medicinal herbs from the forest',
                    'alignment_req': None,
                    'level_req': 1,
                    'reward_gold': 30,
                    'reputation_reward': 3
                }
            ],
            'combat': [
                {
                    'id': 'clear_monsters',
                    'name': 'Monster Clearing',
                    'description': 'Clear dangerous creatures from an area',
                    'alignment_req': None,
                    'level_req': 3,
                    'reward_gold': 100,
                    'reputation_reward': 10
                },
                {
                    'id': 'bandit_leader',
                    'name': 'Bandit Leader',
                    'description': 'Eliminate the bandit leader terrorizing travelers',
                    'alignment_req': Alignment.GOOD,
                    'level_req': 5,
                    'reward_gold': 200,
                    'reputation_reward': 15
                }
            ],
            'social': [
                {
                    'id': 'negotiate_peace',
                    'name': 'Peace Negotiations',
                    'description': 'Negotiate peace between feuding factions',
                    'alignment_req': Alignment.NEUTRAL,
                    'level_req': 4,
                    'reward_gold': 150,
                    'reputation_reward': 20
                },
                {
                    'id': 'gather_information',
                    'name': 'Information Gathering',
                    'description': 'Gather intelligence on suspicious activities',
                    'alignment_req': None,
                    'level_req': 2,
                    'reward_gold': 75,
                    'reputation_reward': 8
                }
            ]
        }
        
        # Add alignment-specific quests
        if self.alignment == Alignment.GOOD:
            base_quests[self.quest_type_focus].extend([
                {
                    'id': 'rescue_mission',
                    'name': 'Rescue Mission',
                    'description': 'Rescue kidnapped civilians from bandits',
                    'alignment_req': Alignment.GOOD,
                    'level_req': 4,
                    'reward_gold': 175,
                    'reputation_reward': 25
                },
                {
                    'id': 'charity_work',
                    'name': 'Charity Work',
                    'description': 'Help distribute food to the needy',
                    'alignment_req': Alignment.GOOD,
                    'level_req': 1,
                    'reward_gold': 20,
                    'reputation_reward': 15
                }
            ])
        elif self.alignment == Alignment.EVIL:
            base_quests[self.quest_type_focus].extend([
                {
                    'id': 'sabotage_mission',
                    'name': 'Sabotage',
                    'description': 'Sabotage a rival organization\'s operations',
                    'alignment_req': Alignment.EVIL,
                    'level_req': 3,
                    'reward_gold': 125,
                    'reputation_reward': 10
                },
                {
                    'id': 'intimidation_job',
                    'name': 'Intimidation',
                    'description': 'Convince someone to pay their debts',
                    'alignment_req': Alignment.EVIL,
                    'level_req': 2,
                    'reward_gold': 60,
                    'reputation_reward': 5
                }
            ])
        
        self.available_quests = base_quests.get(self.quest_type_focus, base_quests['general'])
    
    def _initialize_quest_responses(self) -> Dict[str, List[str]]:
        """Initialize quest giver specific dialogue responses."""
        return {
            'quest_available': [
                "I have a task that might interest someone of your capabilities.",
                "There's work to be done, if you're willing and able.",
                "I could use someone with your skills for an important matter."
            ],
            'no_quests': [
                "I don't have any tasks suitable for you right now.",
                "Check back later - new opportunities arise constantly.",
                "Nothing at the moment, but that could change soon."
            ],
            'quest_accepted': [
                "Excellent! I knew I could count on you.",
                "Wonderful! Here are the details you'll need.",
                "Perfect! Time is of the essence, so don't delay."
            ],
            'quest_declined': [
                "I understand. Perhaps another time.",
                "No worries - not every task is for everyone.",
                "Fair enough. The offer stands if you change your mind."
            ],
            'quest_completed': [
                "Outstanding work! You've exceeded my expectations.",
                "Perfectly done! I'm impressed by your efficiency.",
                "Excellent! Your reputation for getting things done is well-earned."
            ],
            'quest_failed': [
                "That's... disappointing. I had hoped for better.",
                "Well, perhaps it was too ambitious. Better luck next time.",
                "These things happen. Not everyone is cut out for every task."
            ],
            'reputation_check': [
                "I need to be sure I can trust you with this responsibility.",
                "Your reputation precedes you, but I must verify.",
                "This task requires someone of proven reliability."
            ]
        }
    
    def get_available_services(self) -> List[str]:
        """Get services this quest giver can provide."""
        return self.services_offered.copy()
    
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if quest giver can provide service to character."""
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        if service == 'available_quests':
            if reaction.value <= -2:
                return False, "I don't trust you with important tasks."
            return True, "I have several opportunities available."
        
        elif service == 'quest_progress':
            if character.name not in self.active_quests:
                return False, "You don't have any active quests with me."
            return True, "Let me check on your current assignments."
        
        elif service == 'quest_rewards':
            completed = self.completed_quests.get(character.name, [])
            if not completed:
                return False, "You haven't completed any quests for me yet."
            return True, "Your completed work deserves recognition."
        
        elif service == 'adventure_advice':
            if reaction.value < 0:
                return False, "I don't give advice to untrustworthy individuals."
            return True, "I can share some wisdom about adventuring."
        
        elif service == 'area_dangers':
            return True, "I can warn you about local dangers."
        
        return False, f"I don't provide {service}."
    
    def get_suitable_quests(self, character) -> List[Dict[str, Any]]:
        """Get quests suitable for the character."""
        suitable_quests = []
        
        character_level = getattr(character, 'level', 1)
        character_alignment = character.alignment_manager.get_alignment()
        
        # Check reputation
        reputation = 0
        if hasattr(character, 'reputation_manager'):
            reputation = character.reputation_manager.get_reputation(self.faction)
        
        for quest in self.available_quests:
            # Check if quest is on cooldown
            if quest['id'] in self.quest_cooldowns:
                if time.time() < self.quest_cooldowns[quest['id']]:
                    continue
            
            # Check level requirement
            if character_level < quest['level_req']:
                continue
            
            # Check alignment requirement
            if quest['alignment_req'] and quest['alignment_req'] != character_alignment:
                continue
            
            # Check if already completed (for non-repeatable quests)
            completed = self.completed_quests.get(character.name, [])
            if quest['id'] in completed and not quest.get('repeatable', False):
                continue
            
            # Check if already active
            active = self.active_quests.get(character.name, [])
            if quest['id'] in active:
                continue
            
            # Check reputation requirement
            rep_req = quest.get('reputation_req', -50)
            if reputation < rep_req:
                continue
            
            suitable_quests.append(quest)
        
        return suitable_quests
    
    def offer_quest(self, character, quest_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Offer a specific quest to character."""
        suitable_quests = self.get_suitable_quests(character)
        quest = next((q for q in suitable_quests if q['id'] == quest_id), None)
        
        if not quest:
            return False, "That quest is not available to you right now.", None
        
        # Check concurrent quest limit
        active_count = len(self.active_quests.get(character.name, []))
        if active_count >= self.max_concurrent_quests:
            return False, f"You already have {self.max_concurrent_quests} active quests. Complete some first.", None
        
        import random
        offer_response = random.choice(self.quest_responses['quest_available'])
        
        quest_details = {
            'id': quest['id'],
            'name': quest['name'],
            'description': quest['description'],
            'reward_gold': quest['reward_gold'],
            'giver': self.name,
            'giver_id': self.npc_id
        }
        
        return True, f"{offer_response}\n\nQuest: {quest['name']}\n{quest['description']}\nReward: {quest['reward_gold']} gold", quest_details
    
    def accept_quest(self, character, quest_id: str) -> str:
        """Process quest acceptance."""
        if character.name not in self.active_quests:
            self.active_quests[character.name] = []
        
        self.active_quests[character.name].append(quest_id)
        self.update_conversation_memory(character.name, f'accepted_{quest_id}')
        
        import random
        return random.choice(self.quest_responses['quest_accepted'])
    
    def complete_quest(self, character, quest_id: str) -> Tuple[bool, str, int]:
        """Process quest completion and give rewards."""
        # Verify quest was active
        active_quests = self.active_quests.get(character.name, [])
        if quest_id not in active_quests:
            return False, "You don't have that quest active.", 0
        
        # Find quest details
        quest = next((q for q in self.available_quests if q['id'] == quest_id), None)
        if not quest:
            return False, "Unknown quest.", 0
        
        # Remove from active, add to completed
        active_quests.remove(quest_id)
        
        if character.name not in self.completed_quests:
            self.completed_quests[character.name] = []
        self.completed_quests[character.name].append(quest_id)
        
        # Give rewards
        gold_reward = quest['reward_gold']
        reputation_reward = quest.get('reputation_reward', 0)
        
        # Apply currency reward
        if hasattr(character, 'currency') and character.currency:
            character.currency.add_gold(gold_reward)
        
        # Apply reputation reward
        if hasattr(character, 'reputation_manager') and reputation_reward > 0:
            character.reputation_manager.modify_reputation(
                self.faction, reputation_reward, f"Completed quest: {quest['name']}"
            )
        
        # Update mood and memory
        self.change_mood(NPCMood.GRATEFUL, 0.8)
        self.update_conversation_memory(character.name, f'completed_{quest_id}')
        
        # Set cooldown for repeatable quests
        if quest.get('repeatable', False):
            cooldown_hours = quest.get('cooldown_hours', 24)
            self.quest_cooldowns[quest_id] = time.time() + (cooldown_hours * 3600)
        
        import random
        response = random.choice(self.quest_responses['quest_completed'])
        
        return True, f"{response}\n\nYou received {gold_reward} gold and {reputation_reward} reputation!", gold_reward
    
    def fail_quest(self, character, quest_id: str, reason: str = "") -> str:
        """Process quest failure."""
        # Remove from active quests
        active_quests = self.active_quests.get(character.name, [])
        if quest_id in active_quests:
            active_quests.remove(quest_id)
        
        # Add to failed quests
        if character.name not in self.failed_quests:
            self.failed_quests[character.name] = []
        self.failed_quests[character.name].append(quest_id)
        
        # Reputation penalty
        if hasattr(character, 'reputation_manager'):
            character.reputation_manager.modify_reputation(
                self.faction, -5, f"Failed quest: {quest_id}"
            )
        
        # Update mood and memory
        self.change_mood(NPCMood.ANNOYED, 0.6)
        self.update_conversation_memory(character.name, f'failed_{quest_id}')
        
        import random
        response = random.choice(self.quest_responses['quest_failed'])
        
        if reason:
            response += f" Reason: {reason}"
        
        return response
    
    def get_quest_progress(self, character) -> List[str]:
        """Get information about character's quest progress."""
        progress_info = []
        
        active_quests = self.active_quests.get(character.name, [])
        for quest_id in active_quests:
            quest = next((q for q in self.available_quests if q['id'] == quest_id), None)
            if quest:
                progress_info.append(f"Active: {quest['name']} - {quest['description']}")
        
        completed_count = len(self.completed_quests.get(character.name, []))
        if completed_count > 0:
            progress_info.append(f"Completed {completed_count} quests for me.")
        
        failed_count = len(self.failed_quests.get(character.name, []))
        if failed_count > 0:
            progress_info.append(f"Failed {failed_count} quests.")
        
        return progress_info if progress_info else ["No quest history with me."]
    
    def get_adventure_advice(self, character) -> str:
        """Provide adventure advice based on character and experience."""
        advice_options = [
            "Always carry extra healing potions - you never know when you'll need them.",
            "Don't venture into dangerous areas alone. Find trustworthy companions.",
            "Reputation matters. Treat people well and doors will open for you.",
            "Save some money for equipment repairs. Battle damage adds up quickly.",
            "Learn about local customs before traveling to new areas.",
            "Information is often more valuable than gold. Listen to rumors carefully.",
            "Trust your instincts. If something feels wrong, it probably is.",
            "Prepare for the unexpected. Quests rarely go exactly as planned."
        ]
        
        import random
        return random.choice(advice_options)
    
    def get_area_dangers(self, character) -> List[str]:
        """Provide information about local dangers."""
        dangers = [
            "The old cemetery is haunted - avoid it after dark.",
            "Bandits have been seen on the eastern road lately.",
            "Strange lights in the northern forest worry the locals.",
            "The abandoned mine has cave-ins and possibly worse.",
            "Wild animals are more aggressive than usual this season.",
            "Some travelers report seeing unusual creatures near the river.",
            "The ruins to the south are said to be cursed.",
            "Thieves target wealthy-looking adventurers in the market district."
        ]
        
        import random
        return random.sample(dangers, min(3, len(dangers)))