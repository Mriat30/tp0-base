from common.protocol import ServerProtocol
from common.utils import ActionType
from model.bet import Bet
import unittest
from unittest.mock import MagicMock
import datetime

class TestProtocol(unittest.TestCase):
    def test_protocol_read_action_success(self):
        socket = MagicMock()
        socket.recv.return_value = b'\x01' 
        
        protocol = ServerProtocol(socket)
        
        action = protocol.read_action()
        
        self.assertEqual(action, ActionType.REGISTER_SINGLE_BET)

    def test_protocol_read_action_throws_error_if_bytes_is_empty(self):
        socket = MagicMock()
        socket.recv.return_value = b'' 
        
        protocol = ServerProtocol(socket)
        
        with self.assertRaises(ValueError):
            protocol.read_action()
        
    def test_protocol_read_bet_success(self):
            socket = MagicMock()
            
            socket.recv.side_effect = [
                b'\x00\x00\x00\x01', # Agencia (numero 1, como es int se representa con 4 bytes big endian)
                b'\x05', b'Mateo',    # Nombre (longitud 5, 'Mateo')
                b'\x05', b'Perez',    # Apellido (longitud 5, 'Perez')
                b'\x08', b'40000000', # Documento (longitud 8, '40000000')
                b'\x0a', b'2000-01-01',# Fecha (longitud 10, '2000-01-01')
                b'\x04', b'7574'      # Numero (longitud 4, '7574')
            ]

            protocol = ServerProtocol(socket)
            bet = protocol.read_bet()

            self.assertEqual(bet.agency, 1)
            self.assertEqual(bet.first_name, 'Mateo')
            self.assertEqual(bet.last_name, 'Perez')
            self.assertEqual(bet.document, '40000000')
            self.assertEqual(bet.birthdate, datetime.date.fromisoformat('2000-01-01'))
            self.assertEqual(bet.number, 7574)

    def test_read_bet_client_disconnection(self):
        socket = MagicMock()
        socket.recv.return_value = b''
        protocol = ServerProtocol(socket)

        with self.assertRaises(EOFError):
            protocol.read_bet()
            
    def test_read_bet_disconnection_during_name_length(self):
        socket = MagicMock()
        socket.recv.side_effect = [
            b'\x00\x00\x00\x01',
            b''                  
        ]
        protocol = ServerProtocol(socket)

        with self.assertRaises(EOFError):
            protocol.read_bet()

    def test_read_bet_invalid_utf8_in_lastname(self):
        socket = MagicMock()
        socket.recv.side_effect = [
            b'\x00\x00\x00\x01', # Agencia
            b'\x04', b'Juan',    # Nombre OK
            b'\x02', b'\xff\xfe',# Apellido con bytes no UTF-8
        ]
        protocol = ServerProtocol(socket)

        with self.assertRaises(UnicodeDecodeError):
            protocol.read_bet()

    def test_send_bet_registered_writes_success_byte(self):
        socket = MagicMock()
        protocol = ServerProtocol(socket)
        
        protocol.send_bet_registered()
        
        socket.sendall.assert_called_once_with(b'\x00')

    def test_send_bet_registered_client_disconnection(self):
        socket = MagicMock()
        socket.sendall.side_effect = OSError("Socket cerrado por el cliente")
        protocol = ServerProtocol(socket)

        with self.assertRaises(EOFError):
            protocol.send_bet_registered()

if __name__ == '__main__':
    unittest.main()