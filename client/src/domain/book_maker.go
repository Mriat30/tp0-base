package domain

import (
	"io"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/protocol"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Bookmaker struct {
	id       string
	proto    *protocol.Protocol
	provider model.BetProvider
}

func NewBookmaker(proto *protocol.Protocol, provider model.BetProvider, clientID string) *Bookmaker {
	return &Bookmaker{
		proto:    proto,
		provider: provider,
		id:       clientID,
	}
}

func (b *Bookmaker) RegisterAll(batchSize int) error {
	for {
		batch, err := b.provider.NextBatch(batchSize)
		if err == io.EOF {
			log.Infof("action: procesamiento_finalizado | result: success | client_id: %v", b.id)
			break
		}
		if err != nil {
			log.Errorf("action: leer_batch | result: fail | client_id: %v | error: %v", b.id, err)
			return err
		}
		err = b.proto.SendBatchOfBets(batch)
		if err != nil {
			log.Errorf("action: enviar_batch | result: fail | client_id: %v | error: %v", b.id, err)
			return err
		}
		err = b.proto.ReadBetRegistered()
		if err != nil {
			log.Errorf("action: confirmar_batch | result: fail | client_id: %v | error: %v", b.id, err)
			return err
		}
		log.Infof("action: batch_procesado | result: success | client_id: %v | cantidad: %d", b.id, len(batch))
	}
	return nil
}