package protocol

import (
	"bytes"
	"testing"
)

func TestProtocol_SendBet(t *testing.T) {
	buf := new(bytes.Buffer)
	proto := NewProtocol(buf)
	agency := int32(5)
	firstName := "Juan"

	err := proto.SendBet(agency, firstName, "Perez", "123", "2000-01-01", "7574")
	if err != nil {
		t.Fatalf("Error enviando apuesta: %v", err)
	}

	result := buf.Bytes()
	if result[0] != 1 {
		t.Errorf("Action esperado 1, obtenido %v", result[0])
	}
	if result[4] != 5 {
		t.Errorf("Agency byte final esperado 5, obtenido %v", result[4])
	}

	if result[5] != 4 {
		t.Errorf("Largo de nombre esperado 4, obtenido %v", result[5])
	}
	name := string(result[6:10])
	if name != "Juan" {
		t.Errorf("Nombre esperado 'Juan', obtenido '%v'", name)
	}
}