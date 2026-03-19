package common

import (
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/protocol"
)

type Bookmaker struct {
	id    string
	proto *protocol.Protocol
	bet   model.Bet
}

func NewBookmaker(proto *protocol.Protocol, bet model.Bet, clientID string) *Bookmaker {
	return &Bookmaker{
		proto: proto,
		bet:   bet,
		id:    clientID,
	}
}

func (b *Bookmaker) Register() error {
	err := b.proto.SendBet(b.bet)
	if err != nil {
		log.Errorf("action: send_message | result: fail | client_id: %v | error: %v", b.id, err)
		return err
	}
	log.Infof("action: apuesta_enviada | result: success | dni: %v", b.bet.Document)
	err = b.proto.ReadBetRegistered()
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", b.id, err)
		return err
	}
	log.Infof("action: apuesta_almacenada | result: success | dni: %v", b.bet.Document)

	return nil
}