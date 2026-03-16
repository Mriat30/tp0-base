package protocol

import (
    "encoding/binary"
    "io"
    "github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
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

func (p *Protocol) SendBet(bet model.Bet) error {
    binary.Write(p.rw, binary.BigEndian, uint8(1))
    binary.Write(p.rw, binary.BigEndian, bet.Agency)
    p.writeString(bet.FirstName)
    p.writeString(bet.LastName)
    binary.Write(p.rw, binary.BigEndian, bet.Document)
    p.writeString(bet.Birthdate)
    binary.Write(p.rw, binary.BigEndian, bet.Number)
    return nil
}

func (p *Protocol) writeString(s string) {
    binary.Write(p.rw, binary.BigEndian, uint8(len(s)))
    p.rw.Write([]byte(s))
}