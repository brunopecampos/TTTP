INITIAL_STATE = 0b00001
ADDRESSING    = 0b00010
NOT_LOGGED    = 0b00100
LOGGED        = 0b01000
PLAYING       = 0b10000
NONE          = 0b00000
ANY           = 0b11111
SAME          = 0b11110

AUTOMATA = {
    'HELO': {
        'incoming_states': INITIAL_STATE,
        'next_state': ADDRESSING,
        'args': 0,
    },
    'PING': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': SAME,
        'args': 0,
    },
    'PINL': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': SAME,
        'args': 0,
    },
    'NUSR': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': SAME,
        'args': 2,
    },
    'LOGN': {
        'incoming_states': NOT_LOGGED,
        'next_state': LOGGED,
        'args': 2,
    },
    'LOUT': {
        'incoming_states': LOGGED | PLAYING,
        'next_state': NOT_LOGGED,
        'args': 0,
    },
    'USRL': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': SAME,
        'args': 0,
    },
    'UHOF': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': SAME,
        'args': 0,
    },
    'GADR': {
        'incoming_states': NOT_LOGGED | LOGGED,
        'next_state': SAME,
        'args': 1,
    },
    'SADR': {
        'incoming_states': ADDRESSING,
        'next_state': NOT_LOGGED,
        'args': 1,
    },
    'MSTR': {
        'incoming_states': LOGGED,
        'next_state': PLAYING,
        'args': 1,
    },
    'MEND': {
        'incoming_states': PLAYING,
        'next_state': LOGGED,
        'args': 2,
    },
    'GBYE': {
        'incoming_states': LOGGED | NOT_LOGGED | ADDRESSING,
        'next_state': NONE,
        'args': 0,
    }
}
