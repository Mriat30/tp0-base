from common.protocol import ServerProtocol
from common.utils import ActionType
from model.bet import Bet
import unittest
from unittest.mock import MagicMock
import datetime

class TestProtocol(unittest.TestCase):
    def test_protocol_read_action_register_single_bet_success(self):
        socket = MagicMock()
        socket.recv.return_value = b'\x01' 
        
        protocol = ServerProtocol(socket)
        
        action = protocol.read_action()
        
        self.assertEqual(action, ActionType.REGISTER_SINGLE_BET)

    def test_protocol_read_action_client_disconnection(self):
        socket = MagicMock()
        socket.recv.return_value = b'' 
        
        protocol = ServerProtocol(socket)
        
        with self.assertRaises(EOFError):
            protocol.read_action()
        
    def test_protocol_read_bet_success(self):
            socket = MagicMock()
            socket.recv.side_effect = [
                b'\x00\x00\x00\x01',
                b'\x05', b'Mateo',
                b'\x05', b'Perez',
                b'\x02\x62\x5a\x00',
                b'\x0a', b'2000-01-01',
                b'\x00\x00\x1d\x96'
            ]

            protocol = ServerProtocol(socket)
            bet = protocol.read_bet()

            self.assertEqual(bet.agency, 1)
            self.assertEqual(bet.first_name, 'Mateo')
            self.assertEqual(bet.last_name, 'Perez')
            self.assertEqual(bet.document, 40000000)
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

    def test_send_bet_registered_writes_successfully(self):
        socket = MagicMock()
        protocol = ServerProtocol(socket)
        
        protocol.send_bet_registered()
        
        socket.sendall.assert_called_once_with(protocol._SEND_BET_REGISTERED_RESPONSE)

    def test_send_bet_registered_client_disconnection(self):
        socket = MagicMock()
        socket.sendall.side_effect = OSError("Socket cerrado por el cliente")
        protocol = ServerProtocol(socket)

        with self.assertRaises(EOFError):
            protocol.send_bet_registered()

    def test_protocol_read_action_register_batch_of_bets_success(self):
        socket = MagicMock()
        socket.recv.return_value = b'\x02' 
        
        protocol = ServerProtocol(socket)
        
        action = protocol.read_action()
        
        self.assertEqual(action, ActionType.REGISTER_BATCH_OF_BETS)

    def test_read_batch_of_bets_with_single_bet_success(self):
        socket = MagicMock()
        socket.recv.side_effect = [
            b'\x00\x00\x00\x01', # Cantidad de apuestas
            b'\x00\x00\x00\x01', # Agencia
            b'\x05', b'Mateo',   # Nombre
            b'\x05', b'Perez',   # Apellido
            b'\x02\x62\x5a\x00', # Documento
            b'\x0a', b'2000-01-01', # Fecha de nacimiento
            b'\x00\x00\x1d\x96'  # Número de apuesta
        ]

        protocol = ServerProtocol(socket)
        bets = protocol.read_batch_of_bets()

        self.assertEqual(len(bets), 1)
        self.assertEqual(bets[0].agency, 1)
        self.assertEqual(bets[0].first_name, 'Mateo')
        self.assertEqual(bets[0].last_name, 'Perez')
        self.assertEqual(bets[0].document, 40000000)
        self.assertEqual(bets[0].birthdate, datetime.date.fromisoformat('2000-01-01'))
        self.assertEqual(bets[0].number, 7574)
    
    def test_read_batch_of_bets_with_multiple_bets_fail(self):
        socket = MagicMock()
        socket.recv.side_effect = [
                b'\x00\x00\x00\x02', # Cantidad = 2
                # --- Apuesta 1 ---
                b'\x00\x00\x00\x01', # Agencia
                b'\x05', b'Mateo',   # Nombre
                b'\x05', b'Perez',   # Apellido
                b'\x02\x62\x5a\x00', # Documento
                b'\x0a', b'2000-01-01', # Fecha
                b'\x00\x00\x1d\x96', # Número
                # --- Apuesta 2 ---
                b'\x00\x00\x00\x01', # Agencia
                b'\x04', b'Juan',    # Nombre
                b'',                 # Apellido con disconexión del cliente
            ]
        protocol = ServerProtocol(socket)
        with self.assertRaises(EOFError):
            protocol.read_batch_of_bets()
    
if __name__ == '__main__':
    unittest.main()