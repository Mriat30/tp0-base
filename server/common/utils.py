from enum import Enum

class OpCode(Enum):
    CLIENT_ID = 0x01
    REGISTER_SINGLE_BET = 0x02
    REGISTER_BATCH_OF_BETS = 0x03
    BET_REGISTERED = 0x04
    WINNERS = 0x05
    WAITING_FOR_WINNERS = 0x06

    @classmethod
    def from_bytes(cls, raw_bytes):
        """
        Convierte un byte de red en un miembro del Enum.
        Lanza ValueError si el byte no corresponde a ninguna acción.
        """
        if not raw_bytes:
            raise ValueError("No se recibieron bytes")
        
        value = int.from_bytes(raw_bytes, byteorder='big')

        return cls(value)