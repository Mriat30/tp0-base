package protocol

import (
	"bytes"
	"encoding/binary"
	"testing"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
)

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

	checkUint8(t, r, 1)
	checkUint32(t, r, 5)
	checkString(t, r, "Juan")
	checkString(t, r, "Perez")
	checkUint32(t, r, 123)
	checkString(t, r, "2000-01-01")
	checkUint32(t, r, 7574)
}

func TestProtocol_ReadBetRegistered_Success(t *testing.T) {
	buf := bytes.NewBuffer([]byte{0})
	proto := NewProtocol(buf)

	err := proto.ReadBetRegistered()
	if err != nil {
		t.Errorf("got error %v, want nil", err)
	}
}
