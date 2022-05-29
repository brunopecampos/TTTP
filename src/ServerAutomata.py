InitialState = '0'

TransitionMachine = {
    InitialState: [],
    'NOT_LOGGED': [InitialState, 'LOGGED'],
    'LOGGED': ['NOT_LOGGED', 'PLAYING'],
    'PLAYING': ['LOGGED'],
}

CommandList = {
    'HELO': {
        'next_state': 'NOT_LOGGED',
        'args': 0,
    },
    'PING': {
        'next_state': '',
        'args': 0,
    },
    'PINL': {
        'next_state': '',
        'args': 0,
    },
    'NUSR': {
        'next_state': '',
        'args': 2,
    },
    'LOGN': {
        'next_state': 'LOGGED',
        'args': 2,
    },
    'LOUT': {
        'next_state': 'NOT_LOGGED',
        'args': 0,
    },
    'USRL': {
        'next_state': '',
        'args': 0,
    },
    'UHOF': {
        'next_state': '',
        'args': 0,
    },
    'GTIP': {
        'next_state': '',
        'args': 1,
    },
    'MSTR': {
        'next_state': 'PLAYING',
        'args': 2,
    },
    'MEND': {
        'next_state': 'LOGG',
        'args': 1,
    },
    'GBYE': {
        'next_state': '',
        'args': 0,
    }
}
