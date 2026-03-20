package protocol

import (
    "bytes"
    "encoding/binary"
    "fmt"
    "io"
    "github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
)

type OpCode uint8
type ClientIDType uint32
type DocumentType uint32
type BetNumberType uint32

const (
	DefaultMaxBatchSize int = 8192 // Default max batch size is 8KB
)

const (
	OpCodeClientID OpCode = 1
	OpCodeRegisterSingleBet OpCode = 2
	OpCodeRegisterBatchBets OpCode = 3
	OpCodeBetRegistered OpCode = 4
)

type Option func(*Protocol)

type Protocol struct {
    rw io.ReadWriter
    maxBatchSize int
}

func WithMaxBatchSize(maxBatchSize int) func(*Protocol) {
    return func(p *Protocol) {
        p.maxBatchSize = maxBatchSize
    }
}

func NewProtocol(rw io.ReadWriter, opts ...Option) *Protocol {
    p := &Protocol{
        rw:           rw,
        maxBatchSize: DefaultMaxBatchSize,
    }

    for _, opt := range opts {
        opt(p)
    }

    return p
}

func (p *Protocol) SendBet(bet model.Bet) error {
	binary.Write(p.rw, binary.BigEndian, OpCodeRegisterSingleBet)
	p.writeBet(p.rw, bet)
	return nil
}

func (p *Protocol) SendBatchOfBets(bets []model.Bet) error {
    buf := new(bytes.Buffer)

	binary.Write(buf, binary.BigEndian, OpCodeRegisterBatchBets)
	binary.Write(buf, binary.BigEndian, uint32(len(bets)))
	for _, bet := range bets {
		p.writeBet(buf, bet)
	}

	if buf.Len() > p.maxBatchSize {
		return fmt.Errorf("batch too large: %d bytes (max %d)", buf.Len(), p.maxBatchSize)
	}

	_, err := p.rw.Write(buf.Bytes())
	return err
}

func (p *Protocol) writeBet(w io.Writer, bet model.Bet) {
	binary.Write(w, binary.BigEndian, ClientIDType(bet.Agency))
	p.writeString(w, bet.FirstName)
	p.writeString(w, bet.LastName)
	binary.Write(w, binary.BigEndian, DocumentType(bet.Document))
	p.writeString(w, bet.Birthdate)
	binary.Write(w, binary.BigEndian, BetNumberType(bet.Number))
}

func (p *Protocol) ReadBetRegistered() error {
	var ack OpCode
	err := binary.Read(p.rw, binary.BigEndian, &ack)
	if err != nil {
		return err
	}
	if ack != OpCodeBetRegistered {
		return fmt.Errorf("error: bet not registered")
	}
	return nil
}

func (p *Protocol) writeString(w io.Writer, s string) {
	binary.Write(w, binary.BigEndian, uint8(len(s)))
	w.Write([]byte(s))
}