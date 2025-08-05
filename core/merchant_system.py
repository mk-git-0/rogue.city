"""
Merchant System for Rogue City
Handles NPC merchants, trading, and shop interactions.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import os
import random
from core.currency_system import Currency, CurrencySystem
from core.alignment_system import Alignment


class MerchantType(Enum):
    """Types of merchants with different specializations"""
    GENERAL_STORE = "general_store"      # Buys anything, sells basics
    WEAPON_SPECIALIST = "weapon_shop"    # Weapon focused
    ARMOR_SPECIALIST = "armor_shop"      # Armor focused
    MAGIC_SHOP = "magic_shop"           # Magical items and scrolls
    BLACK_MARKET = "black_market"       # Illegal goods, no questions
    TRAVELING_MERCHANT = "traveling"     # Random goods, appears randomly
    BLACKSMITH = "blacksmith"           # Repairs and crafts
    ALCHEMIST = "alchemist"             # Potions and reagents


class MerchantReaction(Enum):
    """NPC merchant reaction levels"""
    HOSTILE = "hostile"          # Won't trade
    UNFRIENDLY = "unfriendly"    # Bad prices, limited selection
    NEUTRAL = "neutral"          # Normal prices
    FRIENDLY = "friendly"        # Good prices, full selection
    HELPFUL = "helpful"          # Best prices, special items


class Merchant:
    """Represents an NPC merchant"""
    
    def __init__(self, merchant_id: str, name: str, merchant_type: MerchantType,
                 area_id: str, room_id: str, alignment: Alignment = Alignment.NEUTRAL):
        self.merchant_id = merchant_id
        self.name = name
        self.merchant_type = merchant_type
        self.area_id = area_id
        self.room_id = room_id
        self.alignment = alignment
        
        # Inventory: Dict[item_id, quantity]
        self.inventory: Dict[str, int] = {}
        
        # What categories this merchant will buy
        self.buy_categories: List[str] = []
        
        # Base markup/markdown percentages
        self.sell_markup = 1.2      # Player pays 120% of base value
        self.buy_markdown = 0.6     # Merchant pays 60% of base value
        
        # Merchant's wealth for buying from players
        self.wealth = Currency(gold=1000)  # Starting wealth
        
        # Dialogue and descriptions
        self.greeting = f"Welcome to my shop!"
        self.description = f"{name} runs a {merchant_type.value.replace('_', ' ')}."
        
        # Hidden merchant (requires skill to find)
        self.is_hidden = False
        self.discovery_skill = None  # 'search', 'listen', etc.
        self.discovery_difficulty = 10
        
        # Trading restrictions
        self.reputation_requirements: Dict[str, int] = {}  # faction: min_reputation
        self.class_restrictions: List[str] = []  # Classes that can't trade
        
        self._initialize_merchant_type()
    
    def _initialize_merchant_type(self):
        """Set up merchant properties based on type"""
        if self.merchant_type == MerchantType.GENERAL_STORE:
            self.buy_categories = ["weapon", "armor", "consumable", "accessory"]
            self.sell_markup = 1.2
            self.buy_markdown = 0.4
            self.greeting = "Welcome! I buy and sell all kinds of goods."
            
        elif self.merchant_type == MerchantType.WEAPON_SPECIALIST:
            self.buy_categories = ["weapon"]
            self.sell_markup = 1.1
            self.buy_markdown = 0.7
            self.greeting = "Looking for fine weapons? You've come to the right place!"
            
        elif self.merchant_type == MerchantType.ARMOR_SPECIALIST:
            self.buy_categories = ["armor"]
            self.sell_markup = 1.1
            self.buy_markdown = 0.7
            self.greeting = "Quality armor and protection, guaranteed!"
            
        elif self.merchant_type == MerchantType.MAGIC_SHOP:
            self.buy_categories = ["consumable"]  # Potions and scrolls
            self.sell_markup = 1.15
            self.buy_markdown = 0.65
            self.greeting = "Magical items and mystical knowledge await!"
            self.class_restrictions = ["barbarian"]  # Barbarians can't use magic shops
            
        elif self.merchant_type == MerchantType.BLACK_MARKET:
            self.buy_categories = ["weapon", "armor", "consumable", "accessory"]
            self.sell_markup = 0.8  # Discount for illegal goods
            self.buy_markdown = 0.8  # Pays well, no questions asked
            self.greeting = "You didn't see me, and I didn't see you..."
            self.is_hidden = True
            self.discovery_skill = "search"
            self.discovery_difficulty = 15
            self.reputation_requirements = {"town_guard": -10}  # Must be disliked by guards
            
        elif self.merchant_type == MerchantType.TRAVELING_MERCHANT:
            self.buy_categories = ["weapon", "armor", "consumable"]
            self.sell_markup = 1.3  # Higher prices for convenience
            self.buy_markdown = 0.5
            self.greeting = "Greetings, traveler! Care to see my wares?"
            
        elif self.merchant_type == MerchantType.BLACKSMITH:
            self.buy_categories = ["weapon", "armor"]
            self.sell_markup = 1.1
            self.buy_markdown = 0.8  # Pays well for metal items
            self.greeting = "Need repairs or quality metalwork?"
            
        elif self.merchant_type == MerchantType.ALCHEMIST:
            self.buy_categories = ["consumable"]
            self.sell_markup = 1.15
            self.buy_markdown = 0.75
            self.greeting = "Potions, elixirs, and alchemical supplies!"
    
    def can_trade_with(self, character) -> Tuple[bool, str]:
        """Check if merchant will trade with character"""
        # Check class restrictions
        if (self.class_restrictions and 
            character.character_class.lower() in [c.lower() for c in self.class_restrictions]):
            return False, f"{self.name} refuses to trade with your kind."
        
        # Check reputation requirements
        for faction, min_rep in self.reputation_requirements.items():
            char_rep = character.get_reputation(faction)
            if char_rep < min_rep:
                return False, f"{self.name} doesn't trust you enough to trade."
        
        # Check alignment compatibility (some merchants are picky)
        reaction = self.get_reaction_level(character)
        if reaction == MerchantReaction.HOSTILE:
            return False, f"{self.name} refuses to deal with you!"
        
        return True, ""
    
    def get_reaction_level(self, character) -> MerchantReaction:
        """Determine merchant's reaction to character"""
        # Base reaction from alignment compatibility
        char_alignment = character.get_alignment()
        alignment_modifier = character.get_npc_reaction_modifier(self.alignment)
        
        # Factor in reputation with relevant factions
        reputation_modifier = 0
        if self.merchant_type == MerchantType.BLACK_MARKET:
            # Black market likes criminals
            reputation_modifier = -character.get_reputation("town_guard") // 10
        else:
            # Most merchants like law-abiding citizens
            reputation_modifier = character.get_reputation("town_guard") // 10
        
        # Calculate total reaction
        total_modifier = alignment_modifier + reputation_modifier
        
        if total_modifier <= -10:
            return MerchantReaction.HOSTILE
        elif total_modifier <= -5:
            return MerchantReaction.UNFRIENDLY
        elif total_modifier <= 5:
            return MerchantReaction.NEUTRAL
        elif total_modifier <= 10:
            return MerchantReaction.FRIENDLY
        else:
            return MerchantReaction.HELPFUL
    
    def has_item(self, item_id: str) -> bool:
        """Check if merchant has item in stock"""
        return item_id in self.inventory and self.inventory[item_id] > 0
    
    def add_inventory(self, item_id: str, quantity: int = 1):
        """Add items to merchant's inventory"""
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity
    
    def remove_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Remove items from merchant's inventory"""
        if not self.has_item(item_id):
            return False
        
        if self.inventory[item_id] < quantity:
            return False
        
        self.inventory[item_id] -= quantity
        if self.inventory[item_id] <= 0:
            del self.inventory[item_id]
        
        return True
    
    def will_buy_item_type(self, item_type: str) -> bool:
        """Check if merchant will buy this type of item"""
        return item_type.lower() in [cat.lower() for cat in self.buy_categories]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize merchant for saving"""
        return {
            'merchant_id': self.merchant_id,
            'name': self.name,
            'merchant_type': self.merchant_type.value,
            'area_id': self.area_id,
            'room_id': self.room_id,
            'alignment': self.alignment.value,
            'inventory': self.inventory.copy(),
            'buy_categories': self.buy_categories.copy(),
            'sell_markup': self.sell_markup,
            'buy_markdown': self.buy_markdown,
            'wealth': {
                'gold': self.wealth.gold,
                'silver': self.wealth.silver,
                'copper': self.wealth.copper
            },
            'greeting': self.greeting,
            'description': self.description,
            'is_hidden': self.is_hidden,
            'discovery_skill': self.discovery_skill,
            'discovery_difficulty': self.discovery_difficulty,
            'reputation_requirements': self.reputation_requirements.copy(),
            'class_restrictions': self.class_restrictions.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Merchant':
        """Create merchant from saved data"""
        merchant_type = MerchantType(data['merchant_type'])
        alignment = getattr(Alignment, data['alignment'])
        
        merchant = cls(
            data['merchant_id'],
            data['name'],
            merchant_type,
            data['area_id'],
            data['room_id'],
            alignment
        )
        
        # Restore saved properties
        merchant.inventory = data.get('inventory', {})
        merchant.buy_categories = data.get('buy_categories', [])
        merchant.sell_markup = data.get('sell_markup', 1.2)
        merchant.buy_markdown = data.get('buy_markdown', 0.6)
        
        # Restore wealth
        wealth_data = data.get('wealth', {'gold': 1000, 'silver': 0, 'copper': 0})
        merchant.wealth = Currency(
            wealth_data.get('gold', 1000),
            wealth_data.get('silver', 0),
            wealth_data.get('copper', 0)
        )
        
        merchant.greeting = data.get('greeting', 'Welcome!')
        merchant.description = data.get('description', '')
        merchant.is_hidden = data.get('is_hidden', False)
        merchant.discovery_skill = data.get('discovery_skill')
        merchant.discovery_difficulty = data.get('discovery_difficulty', 10)
        merchant.reputation_requirements = data.get('reputation_requirements', {})
        merchant.class_restrictions = data.get('class_restrictions', [])
        
        return merchant


class MerchantSystem:
    """Manages all merchants and trading operations"""
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.currency_system = CurrencySystem()
        
        # All merchants in the game: Dict[merchant_id, Merchant]
        self.merchants: Dict[str, Merchant] = {}
        
        # Discovered merchants per character: Dict[character_name, List[merchant_id]]
        self.discovered_merchants: Dict[str, List[str]] = {}
        
        # Load merchant data
        self._load_merchant_data()
    
    def _load_merchant_data(self):
        """Load merchant definitions from data files"""
        merchants_file = "data/merchants/merchant_definitions.json"
        if os.path.exists(merchants_file):
            try:
                with open(merchants_file, 'r') as f:
                    merchants_data = json.load(f)
                
                for merchant_data in merchants_data.get('merchants', []):
                    merchant = Merchant.from_dict(merchant_data)
                    self.merchants[merchant.merchant_id] = merchant
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading merchant data: {e}")
        
        # Create default merchants if file doesn't exist
        if not self.merchants:
            self._create_default_merchants()
    
    def _create_default_merchants(self):
        """Create default merchants for initial gameplay"""
        # Tutorial area merchant
        grex = Merchant(
            "grex_trader", "Grex the Trader", MerchantType.GENERAL_STORE,
            "tutorial_cave", "cave_exit", Alignment.NEUTRAL
        )
        grex.greeting = "Ah, a new adventurer! Let me help you get properly equipped."
        grex.add_inventory("minor_health_potion", 5)
        grex.add_inventory("rations", 3)
        grex.add_inventory("training_sword", 1)
        grex.add_inventory("leather_scraps", 2)
        self.merchants["grex_trader"] = grex
        
        # Forest wandering merchant
        peddler = Merchant(
            "forest_peddler", "Wandering Peddler", MerchantType.TRAVELING_MERCHANT,
            "forest", "clearing", Alignment.NEUTRAL
        )
        peddler.add_inventory("rations", 2)
        peddler.add_inventory("minor_health_potion", 3)
        peddler.add_inventory("rope", 1)
        self.merchants["forest_peddler"] = peddler
    
    def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        """Get merchant by ID"""
        return self.merchants.get(merchant_id)
    
    def get_merchants_in_area(self, area_id: str, room_id: str) -> List[Merchant]:
        """Get all merchants in a specific location"""
        merchants = []
        for merchant in self.merchants.values():
            if merchant.area_id == area_id and merchant.room_id == room_id:
                merchants.append(merchant)
        return merchants
    
    def discover_merchant(self, character_name: str, merchant_id: str):
        """Mark a hidden merchant as discovered by character"""
        if character_name not in self.discovered_merchants:
            self.discovered_merchants[character_name] = []
        
        if merchant_id not in self.discovered_merchants[character_name]:
            self.discovered_merchants[character_name].append(merchant_id)
    
    def is_merchant_discovered(self, character_name: str, merchant_id: str) -> bool:
        """Check if character has discovered a hidden merchant"""
        if character_name not in self.discovered_merchants:
            return False
        return merchant_id in self.discovered_merchants[character_name]
    
    def calculate_buy_price(self, item, merchant: Merchant, character) -> Currency:
        """Calculate price player pays to buy item from merchant"""
        if not item:
            return Currency(0)
        
        base_price = Currency(gold=item.value)
        
        # Apply merchant markup
        markup_multiplier = merchant.sell_markup
        
        # Apply reaction modifier
        reaction = merchant.get_reaction_level(character)
        reaction_modifiers = {
            MerchantReaction.HOSTILE: 2.0,
            MerchantReaction.UNFRIENDLY: 1.5,
            MerchantReaction.NEUTRAL: 1.0,
            MerchantReaction.FRIENDLY: 0.9,
            MerchantReaction.HELPFUL: 0.8
        }
        
        reaction_multiplier = reaction_modifiers[reaction]
        
        # Calculate final price
        total_multiplier = markup_multiplier * reaction_multiplier
        final_copper = int(base_price.total_copper() * total_multiplier)
        
        return Currency.from_copper(max(1, final_copper))
    
    def calculate_sell_price(self, item, merchant: Merchant, character) -> Currency:
        """Calculate price merchant pays to buy item from player"""
        if not item:
            return Currency(0)
        
        # Check if merchant will buy this item type
        if not merchant.will_buy_item_type(item.item_type.value):
            return Currency(0)
        
        base_price = Currency(gold=item.value)
        
        # Apply merchant markdown
        markdown_multiplier = merchant.buy_markdown
        
        # Apply reaction modifier
        reaction = merchant.get_reaction_level(character)
        reaction_modifiers = {
            MerchantReaction.HOSTILE: 0.1,
            MerchantReaction.UNFRIENDLY: 0.5,
            MerchantReaction.NEUTRAL: 1.0,
            MerchantReaction.FRIENDLY: 1.1,
            MerchantReaction.HELPFUL: 1.2
        }
        
        reaction_multiplier = reaction_modifiers[reaction]
        
        # Calculate final price
        total_multiplier = markdown_multiplier * reaction_multiplier
        final_copper = int(base_price.total_copper() * total_multiplier)
        
        return Currency.from_copper(max(1, final_copper))
    
    def attempt_purchase(self, character, merchant: Merchant, item_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """Attempt to purchase item from merchant"""
        # Check if merchant exists and will trade
        can_trade, reason = merchant.can_trade_with(character)
        if not can_trade:
            return False, reason
        
        # Check if item is in stock
        if not merchant.has_item(item_id) or merchant.inventory[item_id] < quantity:
            return False, f"{merchant.name} doesn't have enough {item_id} in stock."
        
        # Get item for price calculation
        from core.item_factory import ItemFactory
        item_factory = ItemFactory()
        item = item_factory.create_item(item_id)
        if not item:
            return False, f"Unknown item: {item_id}"
        
        # Calculate total price
        unit_price = self.calculate_buy_price(item, merchant, character)
        total_price = Currency.from_copper(unit_price.total_copper() * quantity)
        
        # Check if character can afford it
        if not character.currency.can_afford(total_price):
            return False, f"You need {total_price} but only have {character.currency}."
        
        # Check inventory space
        if not character.inventory_system.can_add_item(item, quantity):
            return False, "You don't have enough inventory space."
        
        # Process the transaction
        if character.currency.subtract(total_price):
            merchant.remove_inventory(item_id, quantity)
            merchant.wealth.add(total_price)
            
            # Add items to character inventory
            for _ in range(quantity):
                new_item = item_factory.create_item(item_id)
                character.inventory_system.add_item(new_item)
            
            return True, f"You purchase {quantity}x {item.name} for {total_price}."
        
        return False, "Transaction failed."
    
    def attempt_sale(self, character, merchant: Merchant, item_id: str, quantity: int = 1) -> Tuple[bool, str]:
        """Attempt to sell item to merchant"""
        # Check if merchant exists and will trade
        can_trade, reason = merchant.can_trade_with(character)
        if not can_trade:
            return False, reason
        
        # Check if character has the item
        if not character.inventory_system.has_item(item_id, quantity):
            return False, f"You don't have {quantity}x {item_id}."
        
        # Get item for price calculation
        item = character.inventory_system.get_item(item_id)
        if not item:
            return False, f"Item not found in inventory: {item_id}"
        
        # Calculate sell price
        unit_price = self.calculate_sell_price(item, merchant, character)
        if unit_price.total_copper() == 0:
            return False, f"{merchant.name} doesn't buy {item.item_type.value}s."
        
        total_price = Currency.from_copper(unit_price.total_copper() * quantity)
        
        # Check if merchant can afford it
        if not merchant.wealth.can_afford(total_price):
            return False, f"{merchant.name} doesn't have enough money to buy that."
        
        # Process the transaction
        if merchant.wealth.subtract(total_price):
            # Remove items from character inventory
            for _ in range(quantity):
                character.inventory_system.remove_item(item_id, 1)
            
            # Add items to merchant inventory
            merchant.add_inventory(item_id, quantity)
            
            # Pay character
            character.currency.add(total_price)
            
            return True, f"You sell {quantity}x {item.name} for {total_price}."
        
        return False, "Transaction failed."
    
    def get_merchant_inventory_display(self, merchant: Merchant, character) -> str:
        """Get formatted display of merchant's inventory"""
        lines = []
        lines.append(f"=== {merchant.name.upper()}'S SHOP ===")
        lines.append(f'"{merchant.greeting}"')
        lines.append("")
        
        if not merchant.inventory:
            lines.append("Nothing for sale right now.")
            return "\n".join(lines)
        
        lines.append("FOR SALE:")
        
        from core.item_factory import ItemFactory
        item_factory = ItemFactory()
        
        counter = 1
        for item_id, quantity in merchant.inventory.items():
            if quantity > 0:
                item = item_factory.create_item(item_id)
                if item:
                    price = self.calculate_buy_price(item, merchant, character)
                    qty_text = f" ({quantity} available)" if quantity > 1 else ""
                    lines.append(f"  {counter}. {item.name}{qty_text} - {price}")
                    counter += 1
        
        lines.append("")
        lines.append(f"{merchant.name.upper()} WILL BUY:")
        buy_types = [cat.replace('_', ' ').title() for cat in merchant.buy_categories]
        lines.append(f"  - {', '.join(buy_types)}")
        
        reaction = merchant.get_reaction_level(character)
        if reaction == MerchantReaction.FRIENDLY:
            lines.append("(This merchant likes you - better prices!)")
        elif reaction == MerchantReaction.HELPFUL:
            lines.append("(This merchant trusts you - best prices!)")
        elif reaction == MerchantReaction.UNFRIENDLY:
            lines.append("(This merchant is wary of you - higher prices)")
        
        lines.append("")
        lines.append(f"Your money: {character.currency}")
        lines.append("")
        lines.append("Commands: buy <item>, sell <item>, list, appraise <item>, quit")
        
        return "\n".join(lines)
    
    def save_merchants(self, filename: str):
        """Save all merchant data to file"""
        merchant_data = {
            'merchants': [merchant.to_dict() for merchant in self.merchants.values()],
            'discovered_merchants': self.discovered_merchants
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(merchant_data, f, indent=2)
    
    def load_merchants(self, filename: str):
        """Load merchant data from file"""
        if not os.path.exists(filename):
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.merchants = {}
            for merchant_data in data.get('merchants', []):
                merchant = Merchant.from_dict(merchant_data)
                self.merchants[merchant.merchant_id] = merchant
            
            self.discovered_merchants = data.get('discovered_merchants', {})
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading merchant save data: {e}")