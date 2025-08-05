"""
Enhanced Merchant NPC Class for Rogue City.

Extends the existing merchant system with conversation capabilities,
reputation-based pricing, and information trading.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_npc import BaseNPC, NPCPersonality, NPCMood
from areas.npc_system import NPCType
from core.alignment_system import Alignment


class MerchantNPC(BaseNPC):
    """
    Enhanced Merchant NPC with conversation, reputation pricing, and information trading.
    
    Merchants are profit-focused NPCs who trade goods, information, and services.
    They adjust prices based on reputation and offer exclusive deals to valued customers.
    """
    
    def __init__(self, npc_id: str, name: str, alignment: Alignment = Alignment.NEUTRAL,
                 faction: str = "merchants", personality: NPCPersonality = NPCPersonality.GREEDY,
                 merchant_type: str = "general", description: str = ""):
        """
        Initialize Enhanced Merchant NPC.
        
        Args:
            npc_id: Unique identifier
            name: Merchant's name
            alignment: Usually Neutral, focused on profit
            faction: Merchant faction (usually merchants)
            personality: Personality type (usually greedy or friendly)
            merchant_type: Type of merchant (general, weapons, magic, etc.)
            description: Physical description
        """
        super().__init__(
            npc_id=npc_id,
            name=name,
            npc_type=NPCType.MERCHANT,
            alignment=alignment,
            faction=faction,
            personality=personality,
            description=description,
            base_reaction=0  # Merchants are neutral to everyone initially
        )
        
        self.merchant_type = merchant_type
        self.haggling_skill = 0.7  # How good they are at negotiations
        self.information_stock = {}  # Information they're willing to sell
        self.exclusive_customers = []  # VIP customer list
        self.price_memory = {}  # Remember negotiated prices
        
        # Merchant-specific capabilities
        self.buys_items = True
        self.sells_items = True
        self.repairs_equipment = merchant_type in ['general', 'weapons', 'armor']
        self.identifies_items = merchant_type in ['general', 'magic', 'artifacts']
        self.provides_information = True
        
        # Services and knowledge
        self.services_offered = [
            'buy_items',
            'sell_items',
            'price_check',
            'trade_information',
            'market_gossip'
        ]
        
        if self.repairs_equipment:
            self.services_offered.append('repair_equipment')
        
        if self.identifies_items:
            self.services_offered.append('identify_items')
        
        self.special_knowledge = [
            'trade_routes',
            'item_values',  
            'market_trends',
            'distant_lands',
            'rare_goods',
            'other_merchants'
        ]
        
        # Quest hooks for merchant-related missions
        self.quest_hooks = [
            'delivery_request',
            'rare_item_search',
            'trade_route_security',
            'business_partnership',
            'merchant_rescue'
        ]
        
        # Merchant-specific dialogue responses
        self.merchant_responses = self._initialize_merchant_responses()
        
        # Initialize information stock
        self._initialize_information_stock()
    
    def _initialize_merchant_responses(self) -> Dict[str, List[str]]:
        """Initialize merchant-specific dialogue responses."""
        return {
            'greeting_new_customer': [
                "Welcome to my establishment! First time customer?",
                "Ah, a new face! Welcome, welcome! What brings you to my shop?",
                "Greetings, traveler! I have the finest goods at fair prices!"
            ],
            'greeting_regular_customer': [
                "Ah, my valued customer returns! What can I do for you today?",
                "Welcome back! I've been expecting you!",
                "Always a pleasure to see you! Got anything interesting to trade?"
            ],
            'greeting_vip_customer': [
                "My most esteemed patron! Right this way!",
                "Welcome back! I've set aside some special items just for you!",
                "Ah, my friend! Come, let me show you the premium collection!"
            ],
            'no_money': [
                "I'm afraid your purse seems a bit light for my wares.",
                "Come back when you have proper coin, my friend.",
                "I run a business, not a charity. Gold first, goods second."
            ],
            'successful_trade': [
                "Pleasure doing business with you!",
                "Excellent! I do love a satisfied customer!",
                "May this purchase serve you well in your adventures!"
            ],
            'haggling_success': [
                "You drive a hard bargain! Very well, I accept.",
                "Alright, alright! You've worn me down. Deal!",
                "I can see you know the value of things. Agreed!"
            ],
            'haggling_failure': [
                "I'm afraid that's as low as I can go.",
                "My prices are already fair. I cannot budge further.",
                "You ask too much! My family would starve at those prices!"
            ],
            'information_request': [
                "Information has its price, just like everything else.",
                "Ah, seeking knowledge? That's a valuable commodity.",
                "I might know something... for the right price, of course."
            ]
        }
    
    def _initialize_information_stock(self):
        """Initialize the merchant's stock of information for sale."""
        self.information_stock = {
            'trade_routes': {
                'price': 10,
                'info': "The northern trade route is safer but longer. Southern route has bandits but better profits."
            },
            'rare_items': {
                'price': 25,
                'info': "I heard tell of a magical sword in the ruins to the east. Dangerous place though."
            },
            'market_trends': {
                'price': 5,
                'info': "Weapon prices are rising due to increased monster activity. Good time to sell!"
            },
            'other_merchants': {
                'price': 15,
                'info': "Old Henrik in the next town has the best armor. Tell him I sent you for a discount."
            },
            'distant_lands': {
                'price': 20,
                'info': "The capital is in turmoil. Political instability makes for... interesting opportunities."
            }
        }
    
    def get_customer_type(self, character) -> str:
        """Determine what type of customer this character is."""
        if character.name in self.exclusive_customers:
            return 'vip_customer'
        elif self.has_discussed_topic(character.name, 'trade') or \
             self.has_discussed_topic(character.name, 'purchase'):
            return 'regular_customer'
        else:
            return 'new_customer'
    
    def get_greeting(self, character) -> str:
        """Get greeting appropriate to customer relationship."""
        import random
        
        customer_type = self.get_customer_type(character)
        greeting_key = f'greeting_{customer_type}'
        
        greetings = self.merchant_responses.get(greeting_key, self.merchant_responses['greeting_new_customer'])
        return random.choice(greetings)
    
    def get_available_services(self) -> List[str]:
        """Get services this merchant can provide."""
        return self.services_offered.copy()
    
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if merchant can provide service to character."""
        reaction = self.get_enhanced_reaction(character.alignment_manager)
        
        if service == 'buy_items':
            if reaction.value <= -3:
                return False, "I don't do business with your kind."
            return True, "I'll buy your goods at fair prices."
        
        elif service == 'sell_items':
            if reaction.value <= -3:
                return False, "My shop is closed to you."
            return True, "Browse my wares! Everything has a price."
        
        elif service == 'price_check':
            return True, "I can appraise the value of your items."
        
        elif service == 'trade_information':
            if reaction.value < -1:
                return False, "Information is for trusted customers only."
            return True, "I have information... for the right price."
        
        elif service == 'repair_equipment':
            if not self.repairs_equipment:
                return False, "I don't offer repair services."
            elif reaction.value <= -2:
                return False, "I won't work on equipment for someone like you."
            return True, "I can repair your equipment for a fee."
        
        elif service == 'identify_items':
            if not self.identifies_items:
                return False, "I don't provide identification services."
            elif reaction.value <= -1:
                return False, "Item identification requires trust."
            return True, "I can identify mysterious items for you."
        
        return False, f"I don't provide {service}."
    
    def calculate_price_modifier(self, character) -> float:
        """Calculate price modifier based on reputation and relationship."""
        base_modifier = 1.0
        
        # Reputation modifier
        if hasattr(character, 'reputation_manager'):
            rep_modifier = character.reputation_manager.get_price_modifier(self.faction)
            base_modifier *= rep_modifier
        
        # Customer relationship modifier
        customer_type = self.get_customer_type(character)
        if customer_type == 'vip_customer':
            base_modifier *= 0.85  # 15% discount for VIP
        elif customer_type == 'regular_customer':
            base_modifier *= 0.95  # 5% discount for regulars
        
        # Mood modifier
        mood_modifiers = {
            NPCMood.HAPPY: 0.9,
            NPCMood.GRATEFUL: 0.85,
            NPCMood.CONTENT: 1.0,
            NPCMood.ANNOYED: 1.1,
            NPCMood.ANGRY: 1.3,
            NPCMood.SUSPICIOUS: 1.2
        }
        base_modifier *= mood_modifiers.get(self.current_mood, 1.0)
        
        return base_modifier
    
    def attempt_haggling(self, character, item_name: str, offered_price: int, actual_price: int) -> Tuple[bool, str, int]:
        """Process haggling attempt from character."""
        # Calculate haggling success based on character stats and merchant skill
        character_charisma = getattr(character, 'charisma', 10)
        character_bonus = (character_charisma - 10) // 2
        
        # Merchant's resistance to haggling
        merchant_resistance = int(self.haggling_skill * 10)
        
        # Roll for haggling success (simplified)
        import random
        haggle_roll = random.randint(1, 20) + character_bonus
        success_threshold = 10 + merchant_resistance
        
        if haggle_roll >= success_threshold:
            # Successful haggling
            discount_percent = min(0.3, (haggle_roll - success_threshold) * 0.05)  # Up to 30% discount
            final_price = int(actual_price * (1.0 - discount_percent))
            final_price = max(final_price, offered_price)  # Don't go below offered price
            
            response = random.choice(self.merchant_responses['haggling_success'])
            self.change_mood(NPCMood.HAPPY, 0.3)  # Enjoys good negotiations
            
            return True, response, final_price
        else:
            # Failed haggling
            response = random.choice(self.merchant_responses['haggling_failure'])
            self.change_mood(NPCMood.ANNOYED, 0.2)
            
            return False, response, actual_price
    
    def sell_information(self, character, info_type: str) -> Tuple[bool, str, int]:
        """Sell information to character."""
        if info_type not in self.information_stock:
            return False, "I don't have information about that.", 0
        
        info_data = self.information_stock[info_type]
        price = info_data['price']
        
        # Apply price modifier
        price_modifier = self.calculate_price_modifier(character)
        final_price = int(price * price_modifier)
        
        # Check if character can afford it
        if hasattr(character, 'currency') and character.currency:
            if character.currency.get_total_copper() >= final_price * 100:  # Convert to copper
                # Process payment
                character.currency.subtract_gold(final_price)
                
                # Provide information
                info = info_data['info']
                
                # Increase reputation for information trading
                if hasattr(character, 'reputation_manager'):
                    character.reputation_manager.modify_reputation(
                        self.faction, 1, f"Purchased information: {info_type}"
                    )
                
                self.change_mood(NPCMood.HAPPY, 0.5)
                self.update_conversation_memory(character.name, f"bought_{info_type}")
                
                return True, f"Here's what I know: {info}", final_price
            else:
                return False, "You don't have enough gold for that information.", final_price
        else:
            return False, "I need to see your coin first.", final_price
    
    def offer_special_deal(self, character) -> Optional[Dict[str, Any]]:
        """Offer special deal to valued customers."""
        customer_type = self.get_customer_type(character)
        
        if customer_type != 'vip_customer':
            return None
        
        # Generate special offers for VIP customers
        special_deals = [
            {
                'type': 'bulk_discount',
                'description': 'Buy 3 items, get 20% off the total',
                'requirements': 'Purchase 3 or more items in one transaction'
            },
            {
                'type': 'exclusive_item',
                'description': 'Access to rare items not available to other customers',
                'requirements': 'VIP status maintained'
            },
            {
                'type': 'information_package',
                'description': 'Bundle of all available information at 50% off',
                'requirements': 'Purchase all information types'
            }
        ]
        
        import random
        return random.choice(special_deals)
    
    def process_successful_trade(self, character, trade_value: int):
        """Process effects of successful trade."""
        # Update customer relationship
        total_trades = self.conversation_memory.get(character.name, []).count('trade') + 1
        
        if total_trades >= 10 and character.name not in self.exclusive_customers:
            self.exclusive_customers.append(character.name)
            self.change_mood(NPCMood.GRATEFUL, 1.0)
        
        # Increase reputation
        if hasattr(character, 'reputation_manager'):
            rep_gain = max(1, trade_value // 100)  # 1 rep per 100 gold value
            character.reputation_manager.modify_reputation(
                self.faction, rep_gain, f"Trade transaction: {trade_value} gold value"
            )
        
        self.update_conversation_memory(character.name, 'trade')
        
        return random.choice(self.merchant_responses['successful_trade'])
    
    def get_market_gossip(self, character) -> str:
        """Provide market gossip and rumors."""
        gossip_options = [
            "I heard the dwarven smiths are running low on good iron ore.",
            "Word is there's a new dungeon discovered north of the city.",
            "The mage tower is buying up rare spell components at premium prices.",
            "Bandits have been hitting caravans on the eastern trade route.",
            "Some noble is offering big money for information about ancient artifacts.",
            "The harvest was poor this year - food prices will rise soon.",
            "I've got a cousin who swears he saw a dragon flying over the mountains.",
            "The thieves guild is recruiting, or so I hear through... unofficial channels."
        ]
        
        import random
        return random.choice(gossip_options)
    
    def assess_item_value(self, character, item_description: str) -> str:
        """Provide assessment of item value."""
        # This would integrate with the actual item system
        assessments = [
            f"That {item_description} looks to be worth about 50-75 gold pieces.",
            f"I'd say {item_description} is worth maybe 100-150 gold, depending on condition.",
            f"That's a fine {item_description}! Worth at least 200 gold to the right buyer.",
            f"Hmm, {item_description} is common goods. Maybe 20-30 gold.",
            f"Interesting {item_description}. Could be valuable to collectors - 300+ gold."
        ]
        
        import random
        return random.choice(assessments)