"""
Citizen NPC Class for Rogue City.

Common townsfolk who provide atmosphere, local information,
and world-building through casual conversation.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_npc import BaseNPC, NPCPersonality, NPCMood
from areas.npc_system import NPCType
from core.alignment_system import Alignment
import random


class CitizenNPC(BaseNPC):
    """
    Citizen NPC - Ordinary townsfolk who provide atmosphere and local flavor.
    
    Citizens are the backbone of society, providing local gossip, directions,
    cultural information, and general world-building through conversations.
    They react to events and create a living, breathing world.
    """
    
    def __init__(self, npc_id: str, name: str, alignment: Alignment = Alignment.NEUTRAL,
                 faction: str = "common_folk", personality: NPCPersonality = NPCPersonality.FRIENDLY,
                 occupation: str = "citizen", description: str = "",
                 local_area: str = "town"):
        """
        Initialize Citizen NPC.
        
        Args:
            npc_id: Unique identifier
            name: Citizen's name
            alignment: Usually neutral, varies by individual
            faction: Usually common_folk
            personality: Varies widely
            occupation: What they do for work
            description: Physical description
            local_area: Where they live/work
        """
        super().__init__(
            npc_id=npc_id,
            name=name,
            npc_type=NPCType.CITIZEN,
            alignment=alignment,
            faction=faction,
            personality=personality,
            description=description,
            base_reaction=0
        )
        
        self.occupation = occupation
        self.local_area = local_area
        self.family_members = []
        self.concerns = []
        self.interests = []
        
        # Citizen-specific capabilities
        self.knows_local_gossip = True
        self.gives_directions = True
        self.shares_opinions = True
        self.reacts_to_events = True
        
        # Services and knowledge based on occupation
        self.services_offered = [
            'local_directions',
            'area_gossip',
            'daily_life_info',
            'cultural_information'
        ]
        
        self.special_knowledge = [
            'local_gossip',
            'area_history',
            'daily_routines',
            'local_customs',
            'neighborhood_info',
            'family_matters'
        ]
        
        # Initialize occupation-specific traits
        self._initialize_occupation_traits()
        
        # Generate personal details
        self._generate_personal_details()
        
        # Citizen-specific responses
        self.citizen_responses = self._initialize_citizen_responses()
    
    def _initialize_occupation_traits(self):
        """Set traits based on occupation."""
        occupation_traits = {
            'farmer': {
                'knowledge': ['crops', 'weather', 'seasons', 'rural_life'],
                'concerns': ['harvest', 'weather', 'crop_prices'],
                'services': ['farming_advice', 'weather_prediction']
            },
            'blacksmith': {
                'knowledge': ['metalwork', 'weapons', 'armor', 'tools'],
                'concerns': ['iron_prices', 'coal_supply', 'apprentices'],
                'services': ['equipment_advice', 'repair_recommendations']
            },
            'baker': {
                'knowledge': ['bread_making', 'grain_prices', 'recipes'],
                'concerns': ['flour_supply', 'competition', 'early_hours'],
                'services': ['cooking_tips', 'meal_recommendations']
            },
            'innkeeper': {
                'knowledge': ['travelers', 'roads', 'accommodations', 'rumors'],
                'concerns': ['guests', 'supplies', 'staff'],
                'services': ['traveler_advice', 'room_recommendations']
            },
            'craftsman': {
                'knowledge': ['crafting', 'materials', 'tools', 'techniques'],
                'concerns': ['material_costs', 'competition', 'customers'],
                'services': ['crafting_advice', 'tool_recommendations']
            },
            'fisher': {
                'knowledge': ['fishing', 'rivers', 'lakes', 'weather'],
                'concerns': ['fish_population', 'water_quality', 'competition'],
                'services': ['fishing_advice', 'water_conditions']
            },
            'shopkeeper': {
                'knowledge': ['commerce', 'customers', 'inventory', 'prices'],
                'concerns': ['sales', 'theft', 'competition'],
                'services': ['shopping_advice', 'price_information']
            },
            'laborer': {
                'knowledge': ['construction', 'manual_work', 'tools'],
                'concerns': ['work_availability', 'wages', 'safety'],
                'services': ['work_opportunities', 'labor_advice']
            }
        }
        
        traits = occupation_traits.get(self.occupation, occupation_traits['citizen'] if 'citizen' in occupation_traits else {})
        
        # Add occupation-specific knowledge
        occupation_knowledge = traits.get('knowledge', [])
        self.special_knowledge.extend(occupation_knowledge)
        
        # Add occupation-specific concerns
        self.concerns.extend(traits.get('concerns', []))
        
        # Add occupation-specific services
        self.services_offered.extend(traits.get('services', []))
    
    def _generate_personal_details(self):
        """Generate random personal details for more interesting conversations."""
        
        # Generate interests
        possible_interests = [
            'music', 'dancing', 'storytelling', 'cooking', 'gardening',
            'history', 'politics', 'sports', 'crafts', 'animals',
            'travel', 'books', 'festivals', 'family', 'religion'
        ]
        self.interests = random.sample(possible_interests, random.randint(2, 4))
        
        # Generate family situation
        family_situations = [
            'single', 'married', 'widowed', 'married_with_children',
            'large_family', 'elderly_parents', 'grown_children'
        ]
        family_situation = random.choice(family_situations)
        
        if family_situation == 'married':
            self.family_members = ['spouse']
        elif family_situation == 'married_with_children':
            self.family_members = ['spouse', 'children']
        elif family_situation == 'large_family':
            self.family_members = ['spouse', 'children', 'extended_family']
        elif family_situation == 'elderly_parents':
            self.family_members = ['elderly_parents']
        elif family_situation == 'grown_children':
            self.family_members = ['adult_children']
        
        # Generate current concerns (in addition to occupation ones)
        general_concerns = [
            'town_safety', 'rising_prices', 'bad_weather', 'local_politics',
            'family_health', 'business_competition', 'monster_threats',
            'tax_increases', 'festival_preparations', 'neighborhood_changes'
        ]
        self.concerns.extend(random.sample(general_concerns, random.randint(1, 3)))
    
    def _initialize_citizen_responses(self) -> Dict[str, List[str]]:
        """Initialize citizen-specific dialogue responses."""
        return {
            'friendly_greeting': [
                "Oh hello there! Nice to meet you!",
                "Good day to you, stranger! Welcome to our town!",
                "Well hello! Are you new around here?",
                "Greetings! Lovely weather we're having, isn't it?"
            ],
            'cautious_greeting': [
                "Oh... hello. I haven't seen you around before.",
                "Good day... you're not from around here, are you?",
                "Hello there. Just passing through, I hope?",
                "Afternoon. What brings you to our little town?"
            ],
            'directions_given': [
                "Oh, I'd be happy to help you find your way!",
                "Sure thing! I know this area like the back of my hand.",
                "Of course! Let me think... ah yes, here's how you get there.",
                "I can point you in the right direction, no problem!"
            ],  
            'gossip_sharing': [
                "Well, since you asked... I probably shouldn't say, but...",
                "Oh, you haven't heard? Everyone's talking about it!",
                "I'm not one to spread rumors, but did you know...",
                "Keep this between us, but I heard that..."
            ],
            'personal_sharing': [
                "My family and I have lived here for generations.",
                "I've been working as a {occupation} for most of my life.",
                "This town has changed so much over the years.",
                "We're simple folk here, but we look out for each other."
            ],
            'concern_expression': [
                "I have to say, I'm worried about {concern}.",
                "These days, {concern} keeps me up at night.",
                "Things used to be different before {concern} became an issue.",
                "I hope something can be done about {concern} soon."
            ],
            'opinion_sharing': [
                "In my opinion, things were better in the old days.",
                "I think what this town needs is more {interest}.",
                "People don't appreciate {interest} like they used to.",
                "Mark my words, {concern} is going to cause real problems."
            ]
        }
    
    def get_personalized_greeting(self, character) -> str:
        """Get greeting that reflects personality and local customs."""
        alignment = character.alignment_manager.get_alignment()
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        # Choose greeting style based on personality and reaction
        if reaction.value >= 1 or self.personality in [NPCPersonality.FRIENDLY, NPCPersonality.CHEERFUL]:
            greeting_type = 'friendly_greeting'
        else:
            greeting_type = 'cautious_greeting'
        
        greetings = self.citizen_responses[greeting_type]
        return random.choice(greetings)
    
    def get_available_services(self) -> List[str]:
        """Get services this citizen can provide."""
        return self.services_offered.copy()
    
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if citizen can provide service to character."""
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        if service == 'local_directions':
            if reaction.value <= -2:
                return False, "I... I don't think I should help you."
            return True, "I'd be happy to help you find your way around!"
        
        elif service == 'area_gossip':
            if reaction.value <= -1:
                return False, "I don't gossip with strangers."
            elif self.personality == NPCPersonality.CAUTIOUS:
                return False, "I prefer not to spread rumors."
            return True, "Oh, I hear all sorts of interesting things around town!"
        
        elif service == 'daily_life_info':
            if reaction.value < 0:
                return False, "That's... personal information."
            return True, "I can tell you about life in our community."
        
        elif service == 'cultural_information':
            return True, "I can share what I know about our local customs."
        
        # Occupation-specific services
        elif service in ['farming_advice', 'weather_prediction', 'equipment_advice', 
                        'cooking_tips', 'traveler_advice', 'fishing_advice']:
            if reaction.value < 0:
                return False, "I don't give advice to people I don't trust."
            return True, f"I can help with {service.replace('_', ' ')}."
        
        return False, f"I don't know anything about {service}."
    
    def give_directions(self, character, destination: str) -> str:
        """Provide directions to a destination."""
        # This would integrate with the actual area/map system
        direction_templates = [
            f"To get to {destination}, head {random.choice(['north', 'south', 'east', 'west'])} from the town square, then {random.choice(['turn left', 'turn right', 'go straight'])} at the {random.choice(['fountain', 'old oak tree', 'stone bridge'])}.",
            f"Oh, {destination}! That's easy. Just follow the {random.choice(['main road', 'cobblestone path', 'dirt trail'])} {random.choice(['past the market', 'beyond the church', 'through the gates'])} and you can't miss it.",
            f"For {destination}, you'll want to {random.choice(['ask the guards', 'follow the signs', 'look for the tall building'])}. It's {random.choice(['not far', 'just around the corner', 'a short walk'])} from here.",
            f"I go to {destination} all the time! {random.choice(['Take the path behind the inn', 'Cross the bridge and turn right', 'Follow the market street'])} and you'll see it."
        ]
        
        intro = random.choice(self.citizen_responses['directions_given'])
        directions = random.choice(direction_templates)
        
        return f"{intro} {directions}"
    
    def share_gossip(self, character) -> str:
        """Share local gossip and rumors."""
        gossip_topics = [
            "the mayor's been acting strange lately",
            "there's been weird noises coming from the old mill at night",
            "young Sarah's been seen talking to that mysterious stranger",
            "the blacksmith raised his prices again",
            "there's talk of bandits on the northern road",
            "the harvest this year might be the worst in decades",
            "strange lights were seen over the forest last week",
            "the merchant's daughter is getting married next month",
            "they say there's gold hidden in the old ruins",
            "the priest has been having trouble sleeping lately"
        ]
        
        intro = random.choice(self.citizen_responses['gossip_sharing'])
        gossip = random.choice(gossip_topics)
        
        return f"{intro} {gossip}."
    
    def share_personal_info(self, character) -> str:
        """Share information about personal life and background."""
        personal_templates = self.citizen_responses['personal_sharing']
        template = random.choice(personal_templates)
        
        # Replace placeholders
        response = template.replace('{occupation}', self.occupation)
        
        # Add family information if relevant
        if self.family_members and random.random() < 0.3:
            family_info = self._get_family_info()
            response += f" {family_info}"
        
        return response
    
    def _get_family_info(self) -> str:
        """Get information about family situation."""
        if 'spouse' in self.family_members and 'children' in self.family_members:
            return "My spouse and I are raising our children here."
        elif 'spouse' in self.family_members:
            return "My spouse and I enjoy the quiet life here."
        elif 'children' in self.family_members:
            return "I'm raising my children to appreciate our community."
        elif 'elderly_parents' in self.family_members:
            return "I take care of my elderly parents."
        elif 'adult_children' in self.family_members:
            return "My grown children have moved away, but they visit sometimes."
        else:
            return "I enjoy the independence of living on my own."
    
    def express_concern(self, character) -> str:
        """Express a current concern or worry."""
        if not self.concerns:
            return "Things are going well for me these days, thankfully."
        
        concern = random.choice(self.concerns)
        template = random.choice(self.citizen_responses['concern_expression'])
        
        return template.replace('{concern}', concern.replace('_', ' '))
    
    def share_opinion(self, character) -> str:
        """Share a personal opinion about local matters."""
        template = random.choice(self.citizen_responses['opinion_sharing'])
        
        # Replace placeholders with interests or concerns
        if '{interest}' in template and self.interests:
            interest = random.choice(self.interests)
            template = template.replace('{interest}', interest)
        
        if '{concern}' in template and self.concerns:
            concern = random.choice(self.concerns)
            template = template.replace('{concern}', concern.replace('_', ' '))
        
        return template
    
    def get_cultural_information(self, character) -> str:
        """Provide information about local culture and customs."""
        cultural_info = [
            "We celebrate the Harvest Festival every autumn with music and dancing.",
            "It's customary here to greet your neighbors every morning.",
            "The weekly market day is when everyone comes together to trade and socialize.",
            "We have a tradition of leaving bread out for travelers on cold nights.",
            "The town bell rings at sunset - that's when most folks head home for dinner.",
            "Young people here learn a trade from their parents or are apprenticed out.",
            "We hold a memorial service every year for those lost in the great fire.",
            "Marriages are celebrated with three days of feasting and festivities.",
            "Children here are taught to respect their elders and help their neighbors.",
            "We believe in hard work, fair dealing, and community support."
        ]
        
        return random.choice(cultural_info)
    
    def get_occupation_advice(self, character, advice_type: str) -> str:
        """Provide occupation-specific advice."""
        advice_db = {
            'farming_advice': [
                "Plant your crops after the last frost, never before.",
                "Good soil is the foundation of a good harvest.",
                "Always save seed from your best plants for next year.",
                "Watch the weather - it can make or break a season."
            ],
            'weather_prediction': [
                "When the cats hide all day, expect rain by evening.",
                "Red sky at morning, sailors take warning. Red sky at night, sailors' delight.",
                "If the smoke from chimneys doesn't rise, storm's on the way.",
                "When birds fly low, expect rain. When they fly high, clear skies ahead."
            ],
            'cooking_tips': [
                "Always knead bread dough until it springs back from your touch.",
                "Add herbs at the end of cooking to preserve their flavor.",
                "A watched pot never boils, but an unwatched one always burns.",
                "The secret to good stew is time and patience."
            ],
            'fishing_advice': [
                "Fish bite best in the early morning and just before sunset.",
                "Still water runs deep - that's where the big fish hide.",
                "Change your bait if you're not catching anything after an hour.",
                "Patience is the fisherman's greatest tool."
            ]
        }
        
        advice_list = advice_db.get(advice_type, ["I wish I could help, but that's not my area of expertise."])
        return random.choice(advice_list)
    
    def react_to_event(self, event_type: str, details: str = "") -> str:
        """React to events happening in the world."""
        reactions = {
            'monster_attack': [
                "I heard about the monster attack! Everyone's staying indoors now.",
                "These creatures are getting bolder. What's the world coming to?",
                "I hope the guards can handle these monster problems."
            ],
            'festival': [
                "Oh, the festival! I've been looking forward to this all year!",
                "The preparations have been keeping everyone busy.",
                "These celebrations bring the whole community together."
            ],
            'crime': [
                "I can't believe such things happen in our peaceful town.",
                "We used to never lock our doors. Times are changing.",
                "I hope they catch whoever's responsible soon."
            ],
            'good_news': [
                "Isn't that wonderful? Finally some good news around here!",
                "That's the best thing I've heard all week!",
                "See? Good things do happen to good people."
            ]
        }
        
        event_reactions = reactions.get(event_type, ["That's... interesting news."])
        reaction = random.choice(event_reactions)
        
        if details:
            reaction += f" {details}"
        
        return reaction