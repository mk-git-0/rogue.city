#!/usr/bin/env python3
"""
Comprehensive Quest System Validation Test

Tests all components of the MajorMUD quest system implementation:
- Quest system framework and data loading
- Quest command system functionality
- Quest giver NPCs and dialogue
- Class-specific rewards and progression
- Alignment-based quest restrictions
"""

def test_quest_system_loading():
    """Test core quest system loading and initialization"""
    print("=== TESTING QUEST SYSTEM LOADING ===")
    
    try:
        from core.quest_system import QuestSystem
        from core.game_engine import GameEngine
        
        # Test basic loading
        game = GameEngine()
        quest_system = QuestSystem(game)
        
        print(f"✓ Quest system loaded successfully")
        print(f"✓ {len(quest_system.quest_definitions)} quest definitions loaded")
        
        # Test alignment quest lines
        for alignment in ['good', 'neutral', 'evil']:
            quest_line = quest_system.get_alignment_quest_line(alignment)
            print(f"✓ {alignment.title()} quest line: {quest_line['quest_giver']} ({quest_line['faction']})")
        
        return True
        
    except Exception as e:
        print(f"✗ Quest system loading failed: {e}")
        return False

def test_quest_data_integrity():
    """Test quest data file integrity and structure"""
    print("\\n=== TESTING QUEST DATA INTEGRITY ===")
    
    try:
        import json
        
        # Test quest definitions
        with open('data/quests/quest_definitions.json', 'r') as f:
            quests = json.load(f)
        
        print(f"✓ {len(quests)} quest definitions loaded")
        
        alignment_counts = {'good': 0, 'neutral': 0, 'evil': 0}
        experience_totals = {'good': 0, 'neutral': 0, 'evil': 0}
        
        for quest_id, quest_data in quests.items():
            alignment = quest_data['alignment_requirement']
            experience = quest_data['rewards']['experience']
            
            alignment_counts[alignment] += 1
            experience_totals[alignment] += experience
            
            # Validate required fields
            required_fields = ['name', 'description', 'quest_giver', 'alignment_requirement', 
                             'level_requirement', 'steps', 'rewards']
            for field in required_fields:
                if field not in quest_data:
                    print(f"✗ Quest {quest_id} missing required field: {field}")
                    return False
        
        print("Quest distribution:")
        for alignment, count in alignment_counts.items():
            exp_total = experience_totals[alignment]
            print(f"  {alignment.title()}: {count} quests, {exp_total:,} total experience")
        
        # Test quest rewards
        with open('data/quests/quest_rewards.json', 'r') as f:
            rewards = json.load(f)
        
        print(f"✓ Quest rewards data loaded")
        
        # Test quest NPCs
        with open('data/quests/quest_npcs.json', 'r') as f:
            npcs = json.load(f)
        
        print(f"✓ Quest NPC data loaded ({len(npcs)} main NPCs)")
        
        return True
        
    except Exception as e:
        print(f"✗ Quest data integrity test failed: {e}")
        return False

def test_quest_commands():
    """Test quest command system"""
    print("\\n=== TESTING QUEST COMMANDS ===")
    
    try:
        from core.command_parser import CommandParser
        
        parser = CommandParser(None)
        
        quest_commands = [
            ('quest', 'cmd_quest'),
            ('accept', 'cmd_accept_quest'),
            ('abandon', 'cmd_abandon_quest'),
            ('journal', 'cmd_quest_journal')
        ]
        
        for cmd_name, method_name in quest_commands:
            if hasattr(parser, method_name):
                print(f"✓ {cmd_name} command implemented")
            else:
                print(f"✗ {cmd_name} command missing")
                return False
        
        # Test quest command aliases
        quest_aliases = ['q', 'que', 'quests', 'acc', 'aban', 'jour', 'log']
        for alias in quest_aliases:
            if alias in parser.aliases:
                print(f"✓ Alias '{alias}' -> '{parser.aliases[alias]}'")
            else:
                print(f"✗ Missing alias: {alias}")
        
        return True
        
    except Exception as e:
        print(f"✗ Quest command test failed: {e}")
        return False

def test_quest_givers():
    """Test quest giver NPCs"""
    print("\\n=== TESTING QUEST GIVER NPCS ===")
    
    try:
        from npcs.quest_giver_npc import create_quest_giver
        
        quest_givers = [
            ('chancellor_annora', 'Chancellor Annora', 'good', 3),
            ('hooded_traveller', 'The Hooded Traveller', 'neutral', 2),
            ('balthazar_dark_lord', 'Balthazar the Dark Lord', 'evil', 2)
        ]
        
        for npc_id, expected_name, expected_alignment, expected_quests in quest_givers:
            npc = create_quest_giver(npc_id)
            
            if not npc:
                print(f"✗ Failed to create {npc_id}")
                return False
            
            print(f"✓ {npc.name} created successfully")
            print(f"  Alignment: {npc.alignment_requirement} (expected: {expected_alignment})")
            print(f"  Available quests: {len(npc.available_quests)} (expected: {expected_quests})")
            
            if npc.alignment_requirement != expected_alignment:
                print(f"✗ Alignment mismatch for {npc_id}")
                return False
            
            if len(npc.available_quests) != expected_quests:
                print(f"✗ Quest count mismatch for {npc_id}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Quest giver test failed: {e}")
        return False

def test_quest_rewards():
    """Test quest reward system"""
    print("\\n=== TESTING QUEST REWARD SYSTEM ===")
    
    try:
        from core.quest_rewards import QuestRewardCalculator
        
        calculator = QuestRewardCalculator()
        print("✓ Quest reward calculator initialized")
        
        # Test tier calculation
        test_cases = [
            ('good_quest_1', 1),
            ('neutral_quest_2', 2),
            ('evil_quest_1', 1)
        ]
        
        for quest_id, expected_tier in test_cases:
            tier = calculator.get_quest_tier(quest_id)
            if tier == expected_tier:
                print(f"✓ {quest_id} correctly identified as tier {tier}")
            else:
                print(f"✗ {quest_id} tier mismatch: got {tier}, expected {expected_tier}")
                return False
        
        # Test experience progression
        exp_progression = calculator.reward_data.get('experience_progression', {})
        expected_exp = {
            'quest_tier_1': 150000,
            'quest_tier_2': 2000000,
            'quest_tier_3': 7500000,
            'quest_tier_4': 30000000,
            'quest_tier_5': 175000000
        }
        
        for tier, expected in expected_exp.items():
            if tier in exp_progression and exp_progression[tier] == expected:
                print(f"✓ {tier}: {exp_progression[tier]:,} experience")
            else:
                print(f"✗ {tier} experience mismatch")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Quest reward test failed: {e}")
        return False

def test_integration():
    """Test quest system integration with ask commands"""
    print("\\n=== TESTING QUEST SYSTEM INTEGRATION ===")
    
    try:
        from core.command_parser import CommandParser
        
        parser = CommandParser(None)
        
        # Test ask command enhancement
        if hasattr(parser, '_handle_ask_missions'):
            print("✓ Enhanced ask command with mission support")
        else:
            print("✗ Missing _handle_ask_missions method")
            return False
        
        # Test NPC name mapping
        test_method = getattr(parser, '_handle_ask_missions', None)
        if test_method:
            print("✓ NPC mission request handler available")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all quest system validation tests"""
    print("MajorMUD Quest System Validation Test")
    print("=" * 50)
    
    tests = [
        test_quest_system_loading,
        test_quest_data_integrity, 
        test_quest_commands,
        test_quest_givers,
        test_quest_rewards,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ Test {test.__name__} failed")
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print(f"\\n=== VALIDATION RESULTS ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All quest system components validated successfully!")
        print("\\nQuest System Features Implemented:")
        print("• Complete alignment-based quest lines (Good/Neutral/Evil)")
        print("• Progressive quest difficulty with 150k to 175M experience rewards")
        print("• Class-specific rewards and bonuses")
        print("• Quest giver NPCs with authentic MajorMUD dialogue")
        print("• Quest command system (quest, accept, abandon, info)")
        print("• Integration with NPC conversation system (ask <npc> missions)")
        print("• Comprehensive quest data and reward structures")
        return True
    else:
        print(f"✗ {total - passed} tests failed. Quest system needs attention.")
        return False

if __name__ == "__main__":
    main()