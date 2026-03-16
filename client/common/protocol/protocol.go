package protocol

import (
	"encoding/binary"
	"io"
)
const (
	RegisterSingleBet uint8 = 1
)

type Protocol struct {
	rw io.ReadWriter
}

func NewProtocol(rw io.ReadWriter) *Protocol {
	return &Protocol{rw: rw}
}

func (p *Protocol) SendBet(agency int32, firstName, lastName, document, birthdate, number string) error {
	if err := binary.Write(p.rw, binary.BigEndian, RegisterSingleBet); err != nil {
		return err
	}
	if err := binary.Write(p.rw, binary.BigEndian, agency); err != nil {
		return err
	}
	fields := []string{firstName, lastName, document, birthdate, number}
	for _, field := range fields {
		if err := p.writeString(field); err != nil {
			return err
		}
	}
	return nil
}

func (p *Protocol) writeString(s string) error {
	length := uint8(len(s))
	if err := binary.Write(p.rw, binary.BigEndian, length); err != nil {
		return err
	}
	_, err := p.rw.Write([]byte(s))
	return err
}