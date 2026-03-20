package protocol

import (
	"bytes"
	"encoding/binary"
	"testing"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
)

func checkOpCode(t *testing.T, r *bytes.Reader, want OpCode) {
	var got OpCode
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkClientID(t *testing.T, r *bytes.Reader, want ClientIDType) {
	var got ClientIDType
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkDocument(t *testing.T, r *bytes.Reader, want DocumentType) {
	var got DocumentType
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkBetNumber(t *testing.T, r *bytes.Reader, want BetNumberType) {
	var got BetNumberType
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkUint8(t *testing.T, r *bytes.Reader, want uint8) {
	var got uint8
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkUint32(t *testing.T, r *bytes.Reader, want uint32) {
	var got uint32
	binary.Read(r, binary.BigEndian, &got)
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func checkString(t *testing.T, r *bytes.Reader, want string) {
	var length uint8
	binary.Read(r, binary.BigEndian, &length)
	data := make([]byte, length)
	r.Read(data)
	if string(data) != want {
		t.Errorf("got %s, want %s", string(data), want)
	}
}

func checkBet(t *testing.T, r *bytes.Reader, bet model.Bet) {
	checkString(t, r, bet.FirstName)
	checkString(t, r, bet.LastName)
	checkDocument(t, r, DocumentType(bet.Document))
	checkString(t, r, bet.Birthdate)
	checkBetNumber(t, r, BetNumberType(bet.Number))
}

func TestProtocol_SendClientId(t *testing.T) {
	buf := new(bytes.Buffer)
	proto := NewProtocol(buf)
	clientID := ClientIDType(12345)

	proto.SendClientId(clientID)
	r := bytes.NewReader(buf.Bytes())

	checkOpCode(t, r, OpCodeClientID)
	checkClientID(t, r, clientID)
}

func TestProtocol_SendBet(t *testing.T) {
	buf := new(bytes.Buffer)
	proto := NewProtocol(buf)
	bet := model.Bet{
		Agency:    5,
		FirstName: "Juan",
		LastName:  "Perez",
		Document:  123,
		Birthdate: "2000-01-01",
		Number:    7574,
	}

	proto.SendBet(bet)
	r := bytes.NewReader(buf.Bytes())

	checkOpCode(t, r, OpCodeRegisterSingleBet)
	checkBet(t, r, bet)
}

func TestProtocol_ReadBetRegistered_Success(t *testing.T) {
	buf := bytes.NewBuffer([]byte{byte(OpCodeBetRegistered)})
	proto := NewProtocol(buf)

	err := proto.ReadBetRegistered()
	if err != nil {
		t.Errorf("got error %v, want nil", err)
	}
}

func TestProtocol_ReadBetRegistered_Fail(t *testing.T) {
	buf := bytes.NewBuffer([]byte{byte(OpCode(99))})
	proto := NewProtocol(buf)

	err := proto.ReadBetRegistered()
	if err == nil {
		t.Error("got nil, want error")
	}
}

func TestProtocol_SendBatchOfBets_Success(t *testing.T) {
	buf := new(bytes.Buffer)
	proto := NewProtocol(buf)
	bets := []model.Bet{
		{
			Agency:    5,
			FirstName: "Juan",
			LastName:  "Perez",
			Document:  123,
			Birthdate: "2000-01-01",
			Number:    7574,
		},
		{
			Agency:    10,
			FirstName: "Maria",
			LastName:  "Gomez",
			Document:  456,
			Birthdate: "1995-05-05",
			Number:    1234,
		},
	}

	proto.SendBatchOfBets(bets)
	r := bytes.NewReader(buf.Bytes())
	checkOpCode(t, r, OpCodeRegisterBatchBets)
	checkUint32(t, r, 2)

	for _, bet := range bets {
		checkBet(t, r, bet)
	}
}

func TestProtocol_SendBatchOfBets_WithLimit(t *testing.T) {
	buf := new(bytes.Buffer)
    lowLimit := 50
    proto := NewProtocol(buf, WithMaxBatchSize(lowLimit))

    batch := []model.Bet{
        {
            Agency:    1,
            FirstName: "Santiago Lionel",
            LastName:  "Lorca",
            Document:  30904465,
            Birthdate: "1999-03-17",
            Number:    7574,
        },
        {
            Agency:    1,
            FirstName: "Mateo",
            LastName:  "Perez",
            Document:  40000000,
            Birthdate: "2000-01-01",
            Number:    1234,
        },
    }

    err := proto.SendBatchOfBets(batch)

    if err == nil {
        t.Fatal("got nil, want error")
    }
}