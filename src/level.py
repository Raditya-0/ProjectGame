# level.py
# File untuk menyimpan data tata letak level (Jarak Disesuaikan)

from settings import *

# Format: (x, y, width, height, dimension, type)
# dimension: 'normal', 'gema', atau 'both'
# type: 'platform', 'trap', 'door'

level_1_layout = [
    # Lantai awal
    (0, SCREEN_HEIGHT - 40, 300, 40, 'both', 'platform'),
    
    # Rintangan 1: Jurang yang harus dilewati dengan platform gema (didekatkan)
    (400, SCREEN_HEIGHT - 100, 150, 30, 'gema', 'platform'),
    (600, SCREEN_HEIGHT - 180, 150, 30, 'gema', 'platform'),
    
    # Lantai setelah jurang (didekatkan)
    (800, SCREEN_HEIGHT - 40, 400, 40, 'both', 'platform'),
    
    # Rintangan 2: Jebakan duri yang harus dihindari dengan pindah dimensi
    (950, SCREEN_HEIGHT - 80, 150, 40, 'normal', 'trap'),
    
    # Lantai terakhir
    (1300, SCREEN_HEIGHT - 40, 300, 40, 'both', 'platform'),
    
    # Pintu Keluar
    (1520, SCREEN_HEIGHT - 40 - 100, 60, 100, 'both', 'door')
]

level_2_layout = [
    # Platform lurus panjang tanpa lubang
    (0, SCREEN_HEIGHT - 40, 3000, 40, 'both', 'platform'),

    # --- Rangkaian Jebakan "Hell Level" ---

    # Jebakan 1: Duri muncul di depan saat pemain jalan
    {
        'type': 'trigger_trap',
        'trigger_rect': (300, SCREEN_HEIGHT - 100, 50, 100),
        'trap_rect': (400, SCREEN_HEIGHT - 80, 150, 40),
        'dim': 'normal'
    },

    # Jebakan 2: Duri muncul tepat di bawah pemain (memaksa refleks lompat)
    {
        'type': 'trigger_trap',
        'trigger_rect': (700, SCREEN_HEIGHT - 100, 50, 100),
        'trap_rect': (680, SCREEN_HEIGHT - 80, 100, 40),
        'dim': 'normal'
    },
    
    # Jebakan 3: Duri muncul di depan DAN di belakang (menjebak pemain)
    {
        'type': 'trigger_trap',
        'trigger_rect': (1100, SCREEN_HEIGHT - 100, 20, 100),
        'trap_rect': (1000, SCREEN_HEIGHT - 80, 220, 40),
        'dim': 'normal'
    },
    
    # Jebakan 4: Jebakan di dimensi GEMA untuk variasi
    {
        'type': 'trigger_trap',
        'trigger_rect': (1500, SCREEN_HEIGHT - 100, 50, 100),
        'trap_rect': (1600, SCREEN_HEIGHT - 80, 100, 40),
        'dim': 'gema'
    },

    # Pintu Keluar di ujung
    (2900, SCREEN_HEIGHT - 40 - 100, 60, 100, 'both', 'door')
]
