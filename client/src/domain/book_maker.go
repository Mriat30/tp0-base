package domain

import (
	"io"
	"time"
	"context"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/protocol"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Bookmaker struct {
	id       protocol.ClientIDType
	proto    *protocol.Protocol
	provider model.BetProvider
}

func NewBookmaker(proto *protocol.Protocol, provider model.BetProvider, clientID protocol.ClientIDType) *Bookmaker {
	return &Bookmaker{
		proto:    proto,
		provider: provider,
		id:       clientID,
	}
}

func (b *Bookmaker) RegisterAll(ctx context.Context, batchSize int, loopPeriod time.Duration) error {
	err := b.proto.SendClientId(b.id)
	if err != nil {
		log.Errorf("action: handshake | result: fail | client_id: %v | error: %v", b.id, err)
		return err
	}
	log.Infof("action: handshake | result: success | client_id: %v", b.id)

	for {
		select {
        case <-ctx.Done():
            log.Infof("action: graceful_shutdown | result: success")
            return nil
        default:
        }
		batch, err := b.provider.NextBatch(batchSize)
		if err == io.EOF {
			log.Infof("action: procesamiento_finalizado | result: success | client_id: %v", b.id)
			return nil
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
		time.Sleep(loopPeriod)
	}
	return nil
}