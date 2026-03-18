package protocol

import (
    "encoding/binary"
    "fmt"
    "io"
    "github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
)

const (
    RegisterSingleBet uint8 = 1
    RegisterBatchBets uint8 = 2
)

type Protocol struct {
    rw io.ReadWriter
}

func NewProtocol(rw io.ReadWriter) *Protocol {
    return &Protocol{rw: rw}
}

func (p *Protocol) SendBet(bet model.Bet) error {
    binary.Write(p.rw, binary.BigEndian, RegisterSingleBet)
    p.writeBet(bet)
    return nil
}

func (p *Protocol) SendBatchOfBets(bets []model.Bet) error {
    binary.Write(p.rw, binary.BigEndian, RegisterBatchBets)
    binary.Write(p.rw, binary.BigEndian, uint32(len(bets)))
    for _, bet := range bets {
        p.writeBet(bet)
    }
    return nil
}

func (p *Protocol) writeBet(bet model.Bet) {
    binary.Write(p.rw, binary.BigEndian, bet.Agency)
    p.writeString(bet.FirstName)
    p.writeString(bet.LastName)
    binary.Write(p.rw, binary.BigEndian, bet.Document)
    p.writeString(bet.Birthdate)
    binary.Write(p.rw, binary.BigEndian, bet.Number)
}

func (p *Protocol) ReadBetRegistered() error {
	var ack uint8
	err := binary.Read(p.rw, binary.BigEndian, &ack)
	if err != nil {
		return err
	}
	if ack != 0 {
		return fmt.Errorf("error: bet not registered")
	}
	return nil
}

func (p *Protocol) writeString(s string) {
    binary.Write(p.rw, binary.BigEndian, uint8(len(s)))
    p.rw.Write([]byte(s))
}