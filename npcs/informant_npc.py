"""
Informant NPC Class for Rogue City.

Secretive NPCs who trade in information, rumors, and hidden knowledge
for gold and favors. They operate in shadows and serve various masters.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_npc import BaseNPC, NPCPersonality, NPCMood
from areas.npc_system import NPCType
from core.alignment_system import Alignment
import random
import time


class InformantNPC(BaseNPC):
    """
    Informant NPC - Information broker dealing in secrets and rumors.
    
    Informants are shadowy figures who trade in knowledge, rumors, and secrets.
    They have connections throughout society and sell information to the highest
    bidder, while maintaining their own network of contacts and sources.
    """
    
    def __init__(self, npc_id: str, name: str, alignment: Alignment = Alignment.NEUTRAL,
                 faction: str = "informants", personality: NPCPersonality = NPCPersonality.MYSTERIOUS,
                 specialization: str = "general", description: str = "",
                 trustworthiness: float = 0.7):
        """
        Initialize Informant NPC.
        
        Args:
            npc_id: Unique identifier
            name: Informant's name (often an alias)
            alignment: Usually neutral, but varies
            faction: Informants faction or independent
            personality: Usually mysterious, cautious, or greedy
            specialization: Type of information they focus on
            description: Physical description
            trustworthiness: How reliable their information is (0.0-1.0)
        """
        super().__init__(
            npc_id=npc_id,
            name=name,
            npc_type=NPCType.CITIZEN,  # Blend in as citizens
            alignment=alignment,
            faction=faction,
            personality=personality,
            description=description,
            base_reaction=-1  # Naturally cautious of strangers
        )
        
        self.specialization = specialization
        self.trustworthiness = trustworthiness
        self.real_name = ""  # Hidden true identity
        self.cover_identity = ""  # Public persona
        self.network_size = 0  # Number of contacts
        
        # Informant-specific capabilities
        self.sells_information = True
        self.buys_information = True
        self.has_connections = True
        self.operates_secretly = True
        
        # Information inventory
        self.information_catalog = {}  # category -> {info_id: details}
        self.exclusive_information = {}  # High-value, unique info
        self.rumor_mill = []  # Current circulating rumors
        self.client_list = {}  # character_name -> relationship_level
        
        # Pricing and business
        self.base_prices = {}  # information_type -> base_price
        self.loyalty_discounts = {}  # client_name -> discount_rate
        self.information_cooldowns = {}  # info_id -> cooldown_end_time
        
        # Services and knowledge
        self.services_offered = [
            'buy_information',
            'sell_rumors',
            'investigate_person',
            'track_movements',
            'find_connections',
            'verify_information'
        ]
        
        self.special_knowledge = [
            'underworld_contacts',
            'noble_secrets',
            'merchant_deals',
            'criminal_activities',
            'political_intrigue',
            'hidden_locations'
        ]
        
        # Initialize specialization-specific traits
        self._initialize_specialization()
        
        # Generate information catalog
        self._generate_information_catalog()
        
        # Informant-specific responses
        self.informant_responses = self._initialize_informant_responses()
    
    def _initialize_specialization(self):
        """Set traits based on informant specialization."""
        specializations = {
            'criminal': {
                'knowledge': ['criminal_activities', 'underworld_contacts', 'illegal_trades', 'hideouts'],
                'connections': ['thieves', 'smugglers', 'fences', 'assassins'],
                'base_prices': {'criminal_info': 50, 'wanted_info': 75, 'hideout_locations': 100}
            },
            'political': {
                'knowledge': ['political_intrigue', 'noble_secrets', 'government_corruption', 'alliances'],
                'connections': ['nobles', 'officials', 'diplomats', 'spies'],
                'base_prices': {'political_info': 100, 'noble_secrets': 150, 'corruption_evidence': 200}
            },
            'commercial': {
                'knowledge': ['merchant_deals', 'trade_routes', 'market_manipulation', 'business_secrets'],
                'connections': ['merchants', 'traders', 'caravan_masters', 'guild_members'],
                'base_prices': {'trade_info': 25, 'business_secrets': 75, 'market_tips': 40}
            },
            'military': {
                'knowledge': ['troop_movements', 'fortifications', 'weapon_shipments', 'battle_plans'],
                'connections': ['soldiers', 'officers', 'mercenaries', 'weapon_dealers'],
                'base_prices': {'military_info': 80, 'troop_movements': 120, 'fortification_plans': 150}
            },
            'magical': {
                'knowledge': ['magical_research', 'artifact_locations', 'spell_components', 'wizard_activities'],
                'connections': ['mages', 'scholars', 'artifact_hunters', 'cultists'],
                'base_prices': {'magical_info': 90, 'artifact_locations': 200, 'spell_research': 60}
            },
            'general': {
                'knowledge': ['general_rumors', 'local_gossip', 'traveler_news', 'miscellaneous_secrets'],
                'connections': ['various', 'widespread', 'diverse'],
                'base_prices': {'general_info': 20, 'local_rumors': 15, 'travel_news': 30}
            }
        }
        
        spec_data = specializations.get(self.specialization, specializations['general'])
        
        # Add specialization knowledge
        self.special_knowledge.extend(spec_data['knowledge'])
        
        # Set base prices
        self.base_prices = spec_data['base_prices']
        
        # Set network size based on connections
        self.network_size = len(spec_data['connections']) * random.randint(2, 5)
    
    def _generate_information_catalog(self):
        """Generate available information based on specialization."""
        base_info = {
            'general': {
                'local_crime': {
                    'description': 'Recent criminal activities in the area',
                    'reliability': 0.8,
                    'price_category': 'general_info',
                    'content': 'There have been several break-ins at merchant shops lately. The pattern suggests organized activity rather than random crime.'
                },
                'traveler_warnings': {
                    'description': 'Dangers on local travel routes',
                    'reliability': 0.9,
                    'price_category': 'travel_news',
                    'content': 'Bandits have been spotted on the northern road. They seem to be targeting lone travelers and small groups.'
                },
                'local_gossip': {
                    'description': 'Current rumors and social news',
                    'reliability': 0.6,
                    'price_category': 'local_rumors',
                    'content': "The mayor's been meeting with strangers after dark. Could be nothing, but the timing is suspicious."
                }
            },
            'criminal': {
                'fence_locations': {
                    'description': 'Where stolen goods are sold',
                    'reliability': 0.9,
                    'price_category': 'criminal_info',
                    'content': 'There are three main fences in the city. The most reliable operates out of the old warehouse district.'
                },
                'gang_territories': {
                    'description': 'Criminal organization boundaries',
                    'reliability': 0.8,
                    'price_category': 'criminal_info',
                    'content': 'The Shadowblades control the docks, while the Red Knives run the market district. Neutral ground is shrinking.'
                }
            },
            'political': {
                'succession_rumors': {
                    'description': 'Rumors about noble succession',
                    'reliability': 0.7,
                    'price_category': 'political_info',
                    'content': 'Duke Aldwin has no clear heir. Several cousins are positioning themselves for a claim, which could mean civil conflict.'
                },
                'tax_changes': {
                    'description': 'Upcoming changes to taxation',
                    'reliability': 0.8,
                    'price_category': 'political_info',
                    'content': 'New taxes on luxury goods are being discussed. Implementation expected within the month.'
                }
            }
        }
        
        # Add appropriate information to catalog
        self.information_catalog = base_info.get(self.specialization, base_info['general'])
        
        # Add some general info regardless of specialization
        if self.specialization != 'general':
            general_items = random.sample(list(base_info['general'].items()), 2)
            for info_id, info_data in general_items:
                self.information_catalog[info_id] = info_data
    
    def _initialize_informant_responses(self) -> Dict[str, List[str]]:
        """Initialize informant-specific dialogue responses."""
        return {
            'cautious_greeting': [
                "You're not from around here, are you?",
                "What brings a stranger to speak with me?",
                "Careful who you talk to in this part of town.",
                "I don't know you. That could be good or bad."
            ],
            'trusted_greeting': [
                "Ah, my valued contact returns.",
                "I was wondering when you'd show up again.",
                "Good to see a reliable client.",
                "I may have something that interests you."
            ],
            'information_pitch': [
                "Information is the most valuable currency in this world.",
                "Knowledge is power, and power has its price.",
                "I deal in facts, rumors, and everything in between.",
                "What you don't know can hurt you. What I know can help."
            ],
            'price_negotiation': [
                "Quality information doesn't come cheap.",
                "You get what you pay for in this business.",
                "My sources risk their necks for this knowledge.",
                "Good intel is worth its weight in gold."
            ],
            'transaction_complete': [
                "Pleasure doing business. Remember, you didn't hear this from me.",
                "Use this knowledge wisely. Information shared loses its value.",
                "I trust you'll handle this information... discreetly.",
                "That's all I can tell you about that matter."
            ],
            'insufficient_payment': [
                "Your coin purse seems a bit light for that kind of information.",
                "I'm afraid that grade of intel requires a more substantial investment.",
                "Come back when you can afford premium information.",
                "I don't deal in pocket change for high-grade secrets."
            ],
            'trust_building': [
                "Trust is earned in drops and lost in buckets.",
                "Prove your discretion, and better information becomes available.",
                "Reliable clients get access to my exclusive network.",
                "Demonstrate your value, and I'll demonstrate mine."
            ],
            'warning': [
                "Some knowledge comes with danger attached.",
                "Be careful who you share this information with.",
                "This kind of information has gotten people killed.",
                "What I'm about to tell you... forget where you heard it."
            ]
        }
    
    def get_client_relationship_level(self, character) -> str:
        """Determine relationship level with character."""
        if character.name not in self.client_list:
            return 'unknown'
        
        relationship_score = self.client_list[character.name]
        
        if relationship_score >= 100:
            return 'trusted_partner'
        elif relationship_score >= 50:
            return 'valued_client'
        elif relationship_score >= 20:
            return 'regular_customer'
        elif relationship_score >= 0:
            return 'known_contact'
        else:
            return 'suspicious'
    
    def get_personalized_greeting(self, character) -> str:
        """Get greeting based on relationship and personality."""
        relationship = self.get_client_relationship_level(character)
        
        if relationship in ['trusted_partner', 'valued_client']:
            greeting_type = 'trusted_greeting'
        else:
            greeting_type = 'cautious_greeting'
        
        greetings = self.informant_responses[greeting_type]
        return random.choice(greetings)
    
    def get_available_services(self) -> List[str]:
        """Get services this informant can provide."""
        return self.services_offered.copy()
    
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if informant can provide service to character."""
        relationship = self.get_client_relationship_level(character)
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        if service == 'buy_information':
            if reaction.value <= -3:
                return False, "I don't do business with people I can't trust."
            return True, "I have various types of information available."
        
        elif service == 'sell_rumors':
            if reaction.value <= -2:
                return False, "I'm not interested in information from unreliable sources."
            return True, "I might be interested in what you know. Depends on the quality."
        
        elif service == 'investigate_person':
            if relationship == 'unknown':
                return False, "That kind of service is for established clients only."
            elif reaction.value <= -1:
                return False, "I need to trust someone before I'll investigate for them."
            return True, "I can look into people's backgrounds and activities."
        
        elif service == 'track_movements':
            if relationship not in ['valued_client', 'trusted_partner']:
                return False, "Surveillance work is for my premium clients only."
            return True, "My network can keep tabs on individuals for you."
        
        elif service == 'find_connections':
            if relationship == 'unknown':
                return False, "Connection services require an established relationship."
            return True, "I can help you find the right people for various needs."
        
        elif service == 'verify_information':
            return True, "I can check the reliability of information for a fee."
        
        return False, f"I don't provide {service}."
    
    def sell_information(self, character, info_type: str) -> Tuple[bool, str, int, str]:
        """Sell information to character."""
        if info_type not in self.information_catalog:
            return False, "I don't have information on that topic.", 0, ""
        
        info_data = self.information_catalog[info_type]
        base_price = self.base_prices.get(info_data['price_category'], 50)
        
        # Apply modifiers
        price_modifier = self._calculate_price_modifier(character)
        final_price = int(base_price * price_modifier)
        
        # Check cooldown
        if info_type in self.information_cooldowns:
            if time.time() < self.information_cooldowns[info_type]:
                return False, "I've already sold that information recently. Come back later.", 0, ""
        
        # Check payment
        if hasattr(character, 'currency') and character.currency:
            if character.currency.get_total_copper() >= final_price * 100:
                # Process payment
                character.currency.subtract_gold(final_price)
                
                # Provide information
                content = info_data['content']
                reliability = info_data['reliability']
                
                # Modify content based on reliability and trustworthiness
                if reliability < self.trustworthiness:
                    content = self._add_uncertainty_to_info(content)
                
                # Update relationship
                self._update_client_relationship(character, 5)
                
                # Set cooldown
                self.information_cooldowns[info_type] = time.time() + (24 * 3600)  # 24 hour cooldown
                
                # Add warning if dangerous
                warning = ""
                if 'criminal' in info_type or 'secret' in info_type:
                    warning = " " + random.choice(self.informant_responses['warning'])
                
                transaction_msg = random.choice(self.informant_responses['transaction_complete'])
                
                return True, f"{content}{warning}\n\n{transaction_msg}", final_price, content
            else:
                insufficient_msg = random.choice(self.informant_responses['insufficient_payment'])
                return False, insufficient_msg, final_price, ""
        else:
            return False, "I need to see your coin first.", final_price, ""
    
    def buy_information(self, character, information: str, asking_price: int) -> Tuple[bool, str, int]:
        """Buy information from character."""
        # Assess information value
        info_value = self._assess_information_value(information)
        
        # Calculate offer based on relationship and info value
        relationship_bonus = self._get_relationship_bonus(character)
        offer = int(info_value * (0.5 + relationship_bonus))  # Base 50% of value
        
        if offer >= asking_price:
            # Accept the information
            if hasattr(character, 'currency') and character.currency:
                character.currency.add_gold(offer)
            
            # Add to rumor mill or catalog
            self._integrate_new_information(information, character.name)
            
            # Update relationship
            self._update_client_relationship(character, 3)
            
            return True, f"That's useful information. I'll pay {offer} gold for it.", offer
        else:
            return False, f"I can only offer {offer} gold for that information.", offer
    
    def investigate_person(self, character, target_name: str) -> Tuple[bool, str, int]:
        """Investigate a person's background and activities."""
        base_cost = 75
        price_modifier = self._calculate_price_modifier(character)
        final_cost = int(base_cost * price_modifier)
        
        if hasattr(character, 'currency') and character.currency:
            if character.currency.get_total_copper() >= final_cost * 100:
                character.currency.subtract_gold(final_cost)
                
                # Generate investigation results
                investigation_results = self._generate_investigation_results(target_name)
                
                self._update_client_relationship(character, 8)
                
                return True, investigation_results, final_cost
            else:
                return False, f"Investigation services cost {final_cost} gold.", final_cost
        else:
            return False, f"I need {final_cost} gold up front for investigation work.", final_cost
    
    def _calculate_price_modifier(self, character) -> float:
        """Calculate price modifier based on relationship and reputation."""
        base_modifier = 1.0
        
        # Relationship discount
        relationship = self.get_client_relationship_level(character)
        relationship_discounts = {
            'trusted_partner': 0.7,  # 30% discount
            'valued_client': 0.8,    # 20% discount
            'regular_customer': 0.9, # 10% discount
            'known_contact': 1.0,    # No discount
            'unknown': 1.2,          # 20% markup
            'suspicious': 1.5        # 50% markup
        }
        base_modifier *= relationship_discounts.get(relationship, 1.0)
        
        # Reputation modifier
        if hasattr(character, 'reputation_manager'):
            faction_rep = character.reputation_manager.get_reputation(self.faction)
            if faction_rep > 20:
                base_modifier *= 0.9
            elif faction_rep < -20:
                base_modifier *= 1.3
        
        return base_modifier
    
    def _get_relationship_bonus(self, character) -> float:
        """Get relationship bonus for buying information."""
        relationship = self.get_client_relationship_level(character)
        bonuses = {
            'trusted_partner': 0.3,
            'valued_client': 0.2,
            'regular_customer': 0.1,
            'known_contact': 0.05,
            'unknown': 0.0,
            'suspicious': -0.1
        }
        return bonuses.get(relationship, 0.0)
    
    def _assess_information_value(self, information: str) -> int:
        """Assess the value of information being sold."""
        # Simple assessment based on keywords and length
        value_keywords = {
            'secret': 20, 'murder': 30, 'treasure': 25, 'conspiracy': 35,
            'corruption': 25, 'criminal': 15, 'noble': 20, 'magic': 18,
            'war': 40, 'invasion': 45, 'assassination': 50, 'artifact': 30
        }
        
        base_value = 10  # Minimum value
        info_lower = information.lower()
        
        for keyword, value in value_keywords.items():
            if keyword in info_lower:
                base_value += value
        
        # Length bonus (more detailed = more valuable)
        length_bonus = min(20, len(information) // 10)
        
        return base_value + length_bonus
    
    def _integrate_new_information(self, information: str, source: str):
        """Integrate new information into catalog or rumor mill."""
        # Add to rumor mill for now
        self.rumor_mill.append({
            'content': information,
            'source': source,
            'timestamp': time.time(),
            'reliability': 0.6  # Unknown reliability
        })
        
        # Keep rumor mill manageable
        if len(self.rumor_mill) > 20:
            self.rumor_mill.pop(0)
    
    def _update_client_relationship(self, character, points: int):
        """Update relationship score with client."""
        if character.name not in self.client_list:
            self.client_list[character.name] = 0
        
        self.client_list[character.name] += points
        
        # Cap at reasonable values
        self.client_list[character.name] = max(-50, min(150, self.client_list[character.name]))
    
    def _add_uncertainty_to_info(self, content: str) -> str:
        """Add uncertainty markers to unreliable information."""
        uncertainty_phrases = [
            "I heard that ", "Word is ", "Supposedly ", "They say ",
            "I'm told ", "Rumor has it ", "According to my sources "
        ]
        prefix = random.choice(uncertainty_phrases)
        return prefix.lower() + content
    
    def _generate_investigation_results(self, target_name: str) -> str:
        """Generate investigation results for a target."""
        # This would ideally integrate with actual character data
        investigation_templates = [
            f"{target_name} has been seen frequenting the tavern district late at night.",
            f"Financial records suggest {target_name} has come into money recently.",
            f"{target_name} has connections to several merchant families.",
            f"There are rumors that {target_name} owes money to some unsavory characters.",
            f"{target_name} was seen meeting with strangers outside the city gates.",
            f"My sources indicate {target_name} has been asking questions about ancient artifacts.",
            f"{target_name} appears to be living beyond their apparent means.",
            f"There's talk that {target_name} has been spreading rumors about certain nobles."
        ]
        
        results = random.sample(investigation_templates, random.randint(2, 4))
        return f"Here's what I found about {target_name}:\n" + "\n".join(f"• {result}" for result in results)
    
    def get_rumor_mill_info(self, character) -> List[str]:
        """Get current rumors circulating."""
        if not self.rumor_mill:
            return ["Nothing interesting circulating right now."]
        
        # Return recent rumors
        recent_rumors = [rumor['content'] for rumor in self.rumor_mill[-5:]]
        return recent_rumors
    
    def offer_exclusive_information(self, character) -> Optional[Dict[str, Any]]:
        """Offer exclusive, high-value information to trusted clients."""
        relationship = self.get_client_relationship_level(character)
        
        if relationship not in ['valued_client', 'trusted_partner']:
            return None
        
        # Generate exclusive information offer
        exclusive_offers = [
            {
                'title': 'Noble Succession Crisis',
                'price': 200,
                'description': 'Inside information about an impending succession dispute that could affect trade and politics.',
                'danger_level': 'high'
            },
            {
                'title': 'Ancient Artifact Location',
                'price': 300,
                'description': 'Precise location of a powerful magical artifact, recently discovered.',
                'danger_level': 'extreme'
            },
            {
                'title': 'Criminal Organization Plans',
                'price': 150,
                'description': 'Detailed information about an upcoming major criminal operation.',
                'danger_level': 'moderate'
            }
        ]
        
        return random.choice(exclusive_offers)