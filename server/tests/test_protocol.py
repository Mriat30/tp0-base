from common.protocol import ServerProtocol
from common.utils import OpCode
import unittest
from unittest.mock import MagicMock
import datetime

class TestProtocol(unittest.TestCase):
    def setUp(self):
        self.socket = MagicMock()
        self.protocol = ServerProtocol(self.socket)

    def tearDown(self):
        pass

    def _create_bet(self, agency, first_name, last_name, document, birthdate, number):
        return [
            agency.to_bytes(4, 'big'),
            bytes([len(first_name)]), first_name.encode('utf-8'),
            bytes([len(last_name)]), last_name.encode('utf-8'),
            document.to_bytes(4, 'big'),
            bytes([len(birthdate)]), birthdate.encode('utf-8'),
            number.to_bytes(4, 'big')
        ]

    def test_protocol_read_client_id_success(self):
        self.socket.recv.side_effect = [
            b'\x00\x00\x00\x2a'
        ]

        client_id = self.protocol.read_client_id()

        self.assertEqual(client_id, 42)

    def test_protocol_read_action_register_single_bet_success(self):
        self.socket.recv.return_value = OpCode.REGISTER_SINGLE_BET.value.to_bytes(1, 'big')
        
        action = self.protocol.read_action()
        
        self.assertEqual(action, OpCode.REGISTER_SINGLE_BET)

    def test_protocol_read_action_client_disconnection(self):
        self.socket.recv.return_value = b'' 
        
        with self.assertRaises(EOFError):
            self.protocol.read_action()
        
    def test_protocol_read_bet_success(self):
        self.socket.recv.side_effect = self._create_bet(
            agency=1,
            first_name='Mateo',
            last_name='Perez',
            document=40000000,
            birthdate='2000-01-01',
            number=7574
        )

        bet = self.protocol.read_bet()

        self.assertEqual(bet.agency, 1)
        self.assertEqual(bet.first_name, 'Mateo')
        self.assertEqual(bet.last_name, 'Perez')
        self.assertEqual(bet.document, 40000000)
        self.assertEqual(bet.birthdate, datetime.date.fromisoformat('2000-01-01'))
        self.assertEqual(bet.number, 7574)
            
    def test_read_bet_client_disconnection(self):
        self.socket.recv.return_value = b''

        with self.assertRaises(EOFError):
            self.protocol.read_bet()
            
    def test_read_bet_disconnection_during_name_length(self):
        self.socket.recv.side_effect = [
            b'\x00\x00\x00\x01',
            b''                  
        ]

        with self.assertRaises(EOFError):
            self.protocol.read_bet()

    def test_read_bet_invalid_utf8_in_lastname(self):
        self.socket.recv.side_effect = [
            b'\x00\x00\x00\x01', # Agencia
            b'\x04', b'Juan',    # Nombre OK
            b'\x02', b'\xff\xfe',# Apellido con bytes no UTF-8
        ]

        with self.assertRaises(UnicodeDecodeError):
            self.protocol.read_bet()

    def test_send_bet_registered_writes_successfully(self):
        self.protocol.send_bet_registered()
        
        self.socket.sendall.assert_called_once_with(OpCode.BET_REGISTERED.value.to_bytes(self.protocol._CHAR_SIZE, byteorder='big'))

    def test_send_bet_registered_client_disconnection(self):
        self.socket.sendall.side_effect = OSError("Socket cerrado por el cliente")

        with self.assertRaises(EOFError):
            self.protocol.send_bet_registered()

    def test_protocol_read_action_register_batch_of_bets_success(self):
        self.socket.recv.return_value = OpCode.REGISTER_BATCH_OF_BETS.value.to_bytes(1, 'big')
        
        action = self.protocol.read_action()
        
        self.assertEqual(action, OpCode.REGISTER_BATCH_OF_BETS)

    def test_read_batch_of_bets_with_single_bet_success(self):
        self.socket.recv.side_effect = [
            b'\x00\x00\x00\x01', # Cantidad de apuestas
        ] + self._create_bet(
            agency=1,
            first_name='Mateo',
            last_name='Perez',
            document=40000000,
            birthdate='2000-01-01',
            number=7574
        )

        bets = self.protocol.read_batch_of_bets()

        self.assertEqual(len(bets), 1)
        self.assertEqual(bets[0].agency, 1)
        self.assertEqual(bets[0].first_name, 'Mateo')
        self.assertEqual(bets[0].last_name, 'Perez')
        self.assertEqual(bets[0].document, 40000000)
        self.assertEqual(bets[0].birthdate, datetime.date.fromisoformat('2000-01-01'))
        self.assertEqual(bets[0].number, 7574)
    
    def test_read_batch_of_bets_with_multiple_bets_fail(self):
        self.socket.recv.side_effect = [
            b'\x00\x00\x00\x02', # Cantidad = 2
            # --- Apuesta 1 ---
        ] + self._create_bet(
            agency=1,
            first_name='Mateo',
            last_name='Perez',
            document=40000000,
            birthdate='2000-01-01',
            number=7574
        ) + [
            # --- Apuesta 2 ---
            b'\x00\x00\x00\x01', # Agencia
            b'\x04', b'Juan',    # Nombre
            b'',                 # Apellido con disconexión del cliente
        ]

        with self.assertRaises(EOFError):
            self.protocol.read_batch_of_bets()
    
if __name__ == '__main__':
    unittest.main()