"""
Data model for Portuguese verb conjugations.
"""

VERBS = {
    "falar": {
        "presente": ["falo", "fala", "falamos", "falam"],
        "preterito_perfeito": ["falei", "falou", "falamos", "falaram"],
        "preterito_imperfeito": ["falava", "falava", "falávamos", "falavam"],
        "subjuntivo_presente": ["fale", "fale", "falemos", "falem"],
        "subjuntivo_preterito": ["falasse", "falasse", "falássemos", "falassem"],
        "subjuntivo_futuro": ["falar", "falar", "falarmos", "falarem"]
    },
    "cantar": {
        "presente": ["canto", "canta", "cantamos", "cantam"],
        "preterito_perfeito": ["cantei", "cantou", "cantamos", "cantaram"],
        "preterito_imperfeito": ["cantava", "cantava", "cantávamos", "cantavam"],
        "subjuntivo_presente": ["cante", "cante", "cantemos", "cantem"],
        "subjuntivo_preterito": ["cantasse", "cantasse", "cantássemos", "cantassem"],
        "subjuntivo_futuro": ["cantar", "cantar", "cantarmos", "cantarem"]
    },
    "comprar": {
        "presente": ["compro", "compra", "compramos", "compram"],
        "preterito_perfeito": ["comprei", "comprou", "compramos", "compraram"],
        "preterito_imperfeito": ["comprava", "comprava", "comprávamos", "compravam"],
        "subjuntivo_presente": ["compre", "compre", "compremos", "comprem"],
        "subjuntivo_preterito": ["comprasse", "comprasse", "comprássemos", "comprassem"],
        "subjuntivo_futuro": ["comprar", "comprar", "comprarmos", "comprarem"]
    },
    "andar": {
        "presente": ["ando", "anda", "andamos", "andam"],
        "preterito_perfeito": ["andei", "andou", "andamos", "andaram"],
        "preterito_imperfeito": ["andava", "andava", "andávamos", "andavam"],
        "subjuntivo_presente": ["ande", "ande", "andemos", "andem"],
        "subjuntivo_preterito": ["andasse", "andasse", "andássemos", "andassem"],
        "subjuntivo_futuro": ["andar", "andar", "andarmos", "andarem"]
    },
    "comer": {
        "presente": ["como", "come", "comemos", "comem"],
        "preterito_perfeito": ["comi", "comeu", "comemos", "comeram"],
        "preterito_imperfeito": ["comia", "comia", "comíamos", "comiam"],
        "subjuntivo_presente": ["coma", "coma", "comamos", "comam"],
        "subjuntivo_preterito": ["comesse", "comesse", "comêssemos", "comessem"],
        "subjuntivo_futuro": ["comer", "comer", "comermos", "comerem"]
    },
    "beber": {
        "presente": ["bebo", "bebe", "bebemos", "bebem"],
        "preterito_perfeito": ["bebi", "bebeu", "bebemos", "beberam"],
        "preterito_imperfeito": ["bebia", "bebia", "bebíamos", "bebiam"],
        "subjuntivo_presente": ["beba", "beba", "bebamos", "bebam"],
        "subjuntivo_preterito": ["bebesse", "bebesse", "bebêssemos", "bebessem"],
        "subjuntivo_futuro": ["beber", "beber", "bebermos", "beberem"]
    }
}

# Dictionary mapping tense keys to display names
TENSE_NAMES = {
    "presente": "Presente",
    "preterito_perfeito": "Pretérito Perfeito",
    "preterito_imperfeito": "Pretérito Imperfeito",
    "subjuntivo_presente": "Subjuntivo Presente",
    "subjuntivo_preterito": "Subjuntivo Pretérito",
    "subjuntivo_futuro": "Subjuntivo Futuro"
}

# List of pronouns in order
PRONOUNS = ["eu", "ele/ela/você", "nós", "eles/elas/vocês"]