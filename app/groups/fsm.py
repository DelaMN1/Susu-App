class GroupStateMachine:
    """
    Finite State Machine to manage Susu group states and transitions
    
    States:
    - forming: Group is being formed, accepting new members
    - collecting: Group is active and collecting contributions
    - disbursing: Group is disbursing funds to the current recipient
    - complete: Group has completed all cycles
    """
    
    # Define valid states
    STATES = {
        'forming',
        'collecting',
        'disbursing',
        'complete'
    }
    
    # Define valid transitions
    TRANSITIONS = {
        'forming': {'collecting'},  # forming -> collecting
        'collecting': {'disbursing'},  # collecting -> disbursing
        'disbursing': {'collecting', 'complete'},  # disbursing -> collecting or complete
        'complete': set()  # complete is a terminal state
    }
    
    @classmethod
    def validate_transition(cls, current_state, next_state):
        """
        Validate if a transition from current_state to next_state is allowed
        
        Args:
            current_state (str): The current state of the group
            next_state (str): The desired next state
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        if current_state not in cls.STATES or next_state not in cls.STATES:
            return False
        
        return next_state in cls.TRANSITIONS.get(current_state, set())
    
    @classmethod
    def get_next_states(cls, current_state):
        """
        Get all possible next states from the current state
        
        Args:
            current_state (str): The current state of the group
            
        Returns:
            set: Set of possible next states
        """
        return cls.TRANSITIONS.get(current_state, set())
    
    @classmethod
    def can_join(cls, state):
        """
        Check if users can join a group in the given state
        
        Args:
            state (str): The current state of the group
            
        Returns:
            bool: True if users can join, False otherwise
        """
        return state == 'forming'
    
    @classmethod
    def can_start(cls, state, member_count, required_count):
        """
        Check if a group can start collecting contributions
        
        Args:
            state (str): The current state of the group
            member_count (int): Current number of members
            required_count (int): Required number of members
            
        Returns:
            bool: True if group can start, False otherwise
        """
        return state == 'forming' and member_count >= required_count
    
    @classmethod
    def can_disburse(cls, state, all_paid):
        """
        Check if a group can disburse funds to the current recipient
        
        Args:
            state (str): The current state of the group
            all_paid (bool): Whether all members have paid for the current cycle
            
        Returns:
            bool: True if group can disburse, False otherwise
        """
        return state == 'collecting' and all_paid
    
    @classmethod
    def is_complete(cls, state, current_cycle, total_cycles):
        """
        Check if a group has completed all cycles
        
        Args:
            state (str): The current state of the group
            current_cycle (int): Current cycle number
            total_cycles (int): Total number of cycles
            
        Returns:
            bool: True if group is complete, False otherwise
        """
        return state == 'disbursing' and current_cycle >= total_cycles