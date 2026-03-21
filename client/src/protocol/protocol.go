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
	OpCodeWinnerAnnouncement OpCode = 5
	OpCodeWaitingForWinners OpCode = 6
	OpCodeAckWinners OpCode = 7
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

func (p *Protocol) SendClientId(clientId ClientIDType) error {
	if err := binary.Write(p.rw, binary.BigEndian, OpCodeClientID); err != nil {
		return err
	}
	if err := binary.Write(p.rw, binary.BigEndian, clientId); err != nil {
		return err
	}
	return nil
}

func (p *Protocol) SendAckWinners() error {
	return binary.Write(p.rw, binary.BigEndian, OpCodeAckWinners)
}

func (p *Protocol) SendWaitingForWinners() error {
	return binary.Write(p.rw, binary.BigEndian, OpCodeWaitingForWinners)
}

func (p *Protocol) ReadWinners() ([]model.Winner, error) {
	var opCode OpCode
	err := binary.Read(p.rw, binary.BigEndian, &opCode)
	if err != nil {
		return nil, err
	}
	if opCode != OpCodeWinnerAnnouncement {
		return nil, fmt.Errorf("error: expected OpCodeWinnerAnnouncement, got %d", opCode)
	}
	
	var length uint32
	err = binary.Read(p.rw, binary.BigEndian, &length)
	if err != nil {
		return nil, err
	}
	
	winnersBytes := make([]byte, length)
	_, err = io.ReadFull(p.rw, winnersBytes)
	if err != nil {
		return nil, err
	}
	
	winnersStr := string(winnersBytes)
	if winnersStr == "" {
		return []model.Winner{}, nil
	}
	
	var winners []model.Winner
	for _, doc := range bytes.Split(winnersBytes, []byte(",")) {
		if len(doc) > 0 {
			winners = append(winners, model.Winner{Document: string(doc)})
		}
	}
	
	return winners, nil
}

func (p *Protocol) SendBet(bet model.Bet) error {
	if err := binary.Write(p.rw, binary.BigEndian, OpCodeRegisterSingleBet); err != nil {
		return err
	}
	return p.writeBet(p.rw, bet)
}

func (p *Protocol) SendBatchOfBets(bets []model.Bet) error {
    buf := new(bytes.Buffer)

	if err := binary.Write(buf, binary.BigEndian, OpCodeRegisterBatchBets); err != nil {
		return err
	}
	if err := binary.Write(buf, binary.BigEndian, uint32(len(bets))); err != nil {
		return err
	}
	for _, bet := range bets {
		if err := p.writeBet(buf, bet); err != nil {
			return err
		}
	}

	if buf.Len() > p.maxBatchSize {
		return fmt.Errorf("batch too large: %d bytes (max %d)", buf.Len(), p.maxBatchSize)
	}

	return writeAll(p.rw, buf.Bytes())
}

func (p *Protocol) writeBet(w io.Writer, bet model.Bet) error {
	if err := p.writeString(w, bet.FirstName); err != nil {
		return err
	}
	if err := p.writeString(w, bet.LastName); err != nil {
		return err
	}
	if err := binary.Write(w, binary.BigEndian, DocumentType(bet.Document)); err != nil {
		return err
	}
	if err := p.writeString(w, bet.Birthdate); err != nil {
		return err
	}
	if err := binary.Write(w, binary.BigEndian, BetNumberType(bet.Number)); err != nil {
		return err
	}
	return nil
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

func (p *Protocol) writeString(w io.Writer, s string) error {
	if err := binary.Write(w, binary.BigEndian, uint8(len(s))); err != nil {
		return err
	}
	return writeAll(w, []byte(s))
}

func writeAll(w io.Writer, data []byte) error {
	written := 0
	for written < len(data) {
		n, err := w.Write(data[written:])
		if err != nil {
			return err
		}
		if n == 0 {
			return io.ErrShortWrite
		}
		written += n
	}
	return nil
}