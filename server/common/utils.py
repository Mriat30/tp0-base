from enum import Enum

class ActionType(Enum):
    REGISTER_SINGLE_BET = 0x01
    
    @classmethod
    def from_bytes(cls, raw_bytes):
        """
        Convierte un byte de red en un miembro del Enum.
        Lanza ValueError si el byte no corresponde a ninguna acción.
        """
        if not raw_bytes:
            return None
        
        value = int.from_bytes(raw_bytes, byteorder='big')

        return cls(value)