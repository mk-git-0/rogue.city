"""
Timer System for Rogue City
Manages queue-based action timing for combat and other timed events.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from heapq import heappush, heappop


@dataclass
class TimedAction:
    """Represents a scheduled action with timing information."""
    execute_time: float
    actor_id: str
    action_type: str
    action_data: Dict[str, Any]
    callback: Optional[Callable] = None
    
    def __lt__(self, other):
        """Comparison for heap ordering (earlier times have priority)."""
        return self.execute_time < other.execute_time


class TimerSystem:
    """
    Manages timed actions using a priority queue.
    Supports scheduling actions with delays and processing ready actions.
    """
    
    def __init__(self):
        """Initialize the timer system."""
        self.action_queue: List[TimedAction] = []
        self.actor_timers: Dict[str, float] = {}
        self.paused = False
        self.start_time = time.time()
        
    def get_current_time(self) -> float:
        """Get the current game time in seconds."""
        return time.time() - self.start_time
        
    def pause(self) -> None:
        """Pause the timer system."""
        self.paused = True
        
    def resume(self) -> None:
        """Resume the timer system."""
        self.paused = False
        
    def is_paused(self) -> bool:
        """Check if the timer system is paused."""
        return self.paused
        
    def schedule_action(self, 
                       actor_id: str, 
                       action_type: str, 
                       delay: float, 
                       action_data: Optional[Dict[str, Any]] = None,
                       callback: Optional[Callable] = None) -> None:
        """
        Schedule an action to execute after a delay.
        
        Args:
            actor_id: Unique identifier for the actor performing the action
            action_type: Type of action (e.g., 'attack', 'cast_spell', 'move')
            delay: Delay in seconds before the action should execute
            action_data: Additional data for the action
            callback: Optional callback function to execute with the action
        """
        if action_data is None:
            action_data = {}
            
        execute_time = self.get_current_time() + delay
        
        action = TimedAction(
            execute_time=execute_time,
            actor_id=actor_id,
            action_type=action_type,
            action_data=action_data,
            callback=callback
        )
        
        heappush(self.action_queue, action)
        self.actor_timers[actor_id] = execute_time
        
    def schedule_recurring_action(self, 
                                 actor_id: str, 
                                 action_type: str, 
                                 interval: float,
                                 action_data: Optional[Dict[str, Any]] = None,
                                 callback: Optional[Callable] = None) -> None:
        """
        Schedule a recurring action that repeats at regular intervals.
        
        Args:
            actor_id: Unique identifier for the actor
            action_type: Type of action
            interval: Time in seconds between repetitions
            action_data: Additional data for the action
            callback: Optional callback function
        """
        def recurring_callback(*args, **kwargs):
            # Execute the original callback if provided
            if callback:
                callback(*args, **kwargs)
            
            # Reschedule the action
            self.schedule_action(actor_id, action_type, interval, action_data, recurring_callback)
        
        self.schedule_action(actor_id, action_type, interval, action_data, recurring_callback)
        
    def cancel_actor_actions(self, actor_id: str) -> int:
        """
        Cancel all pending actions for a specific actor.
        
        Args:
            actor_id: Actor whose actions should be cancelled
            
        Returns:
            Number of actions cancelled
        """
        original_count = len(self.action_queue)
        self.action_queue = [action for action in self.action_queue 
                           if action.actor_id != actor_id]
        
        # Remove from actor timers
        self.actor_timers.pop(actor_id, None)
        
        cancelled_count = original_count - len(self.action_queue)
        
        # Rebuild the heap if we removed items
        if cancelled_count > 0:
            import heapq
            heapq.heapify(self.action_queue)
            
        return cancelled_count
        
    def get_actor_next_action_time(self, actor_id: str) -> Optional[float]:
        """
        Get the time when the actor's next action will execute.
        
        Args:
            actor_id: Actor to check
            
        Returns:
            Time in seconds when next action executes, or None if no actions
        """
        return self.actor_timers.get(actor_id)
        
    def get_actor_action_delay(self, actor_id: str) -> Optional[float]:
        """
        Get how long until the actor's next action executes.
        
        Args:
            actor_id: Actor to check
            
        Returns:
            Seconds until next action, or None if no actions
        """
        next_time = self.get_actor_next_action_time(actor_id)
        if next_time is None:
            return None
            
        current_time = self.get_current_time()
        delay = next_time - current_time
        return max(0, delay)
        
    def is_actor_ready(self, actor_id: str) -> bool:
        """
        Check if an actor has any actions ready to execute.
        
        Args:
            actor_id: Actor to check
            
        Returns:
            True if actor has actions ready to execute
        """
        delay = self.get_actor_action_delay(actor_id)
        return delay is not None and delay <= 0.01  # Small tolerance for timing
        
    def get_ready_actions(self) -> List[TimedAction]:
        """
        Get all actions that are ready to execute now.
        
        Returns:
            List of actions ready for execution
        """
        if self.paused:
            return []
            
        ready_actions = []
        current_time = self.get_current_time()
        
        # Pop all ready actions from the heap
        while self.action_queue and self.action_queue[0].execute_time <= current_time:
            action = heappop(self.action_queue)
            ready_actions.append(action)
            
            # Remove from actor timers since this action is being executed
            if action.actor_id in self.actor_timers:
                if self.actor_timers[action.actor_id] == action.execute_time:
                    del self.actor_timers[action.actor_id]
                    
        return ready_actions
        
    def process_ready_actions(self) -> List[TimedAction]:
        """
        Process all actions that are ready to execute.
        
        Returns:
            List of actions that were processed
        """
        ready_actions = self.get_ready_actions()
        
        for action in ready_actions:
            if action.callback:
                try:
                    action.callback(action)
                except Exception as e:
                    print(f"Error executing callback for {action.actor_id}: {e}")
                    
        return ready_actions
        
    def get_next_action_time(self) -> Optional[float]:
        """
        Get the time when the next action will be ready.
        
        Returns:
            Time in seconds, or None if no actions queued
        """
        if not self.action_queue:
            return None
        return self.action_queue[0].execute_time
        
    def get_time_until_next_action(self) -> Optional[float]:
        """
        Get how long until the next action is ready.
        
        Returns:
            Seconds until next action, or None if no actions
        """
        next_time = self.get_next_action_time()
        if next_time is None:
            return None
            
        current_time = self.get_current_time()
        return max(0, next_time - current_time)
        
    def get_queue_size(self) -> int:
        """Get the number of actions in the queue."""
        return len(self.action_queue)
        
    def clear_all_actions(self) -> None:
        """Clear all pending actions."""
        self.action_queue.clear()
        self.actor_timers.clear()
        
    def get_actor_count(self) -> int:
        """Get the number of actors with pending actions."""
        return len(self.actor_timers)
        
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the timer system."""
        current_time = self.get_current_time()
        
        return {
            'current_time': current_time,
            'paused': self.paused,
            'queue_size': len(self.action_queue),
            'actor_count': len(self.actor_timers),
            'next_action_time': self.get_next_action_time(),
            'time_until_next': self.get_time_until_next_action(),
            'actors_with_timers': list(self.actor_timers.keys())
        }


# Quick test function for validation
def _test_timer_system():
    """Test the timer system functionality."""
    timer = TimerSystem()
    
    # Test scheduling actions
    timer.schedule_action('player', 'attack', 1.0, {'target': 'goblin'})
    timer.schedule_action('goblin', 'attack', 0.5, {'target': 'player'})
    
    assert timer.get_queue_size() == 2, "Should have 2 actions queued"
    assert timer.get_actor_count() == 2, "Should have 2 actors with timers"
    
    # Test getting ready actions (none should be ready immediately)
    ready = timer.get_ready_actions()
    assert len(ready) == 0, "No actions should be ready immediately"
    
    # Test actor readiness
    assert not timer.is_actor_ready('player'), "Player should not be ready immediately"
    assert not timer.is_actor_ready('goblin'), "Goblin should not be ready immediately"
    
    # Test cancelling actions
    cancelled = timer.cancel_actor_actions('player')
    assert cancelled == 1, "Should have cancelled 1 action"
    assert timer.get_queue_size() == 1, "Should have 1 action remaining"
    
    # Test clearing all actions
    timer.clear_all_actions()
    assert timer.get_queue_size() == 0, "Queue should be empty"
    assert timer.get_actor_count() == 0, "No actors should have timers"
    
    print("All timer system tests passed!")


if __name__ == "__main__":
    _test_timer_system()