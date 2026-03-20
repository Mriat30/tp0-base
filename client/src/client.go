package src
import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
	"context"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/domain"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/protocol"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	BatchMaxAmount int
	BetProvider model.BetProvider
}

type Client struct {
	config            ClientConfig
	conn              net.Conn
	should_be_running bool
}

func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

func (c *Client) StartClientLoop() {
	ctx, cancel := context.WithCancel(context.Background())
	c.handleSigterm(cancel)
    err := c.createClientSocket()
    if err != nil {
        log.Errorf("action: connect | result: fail | error: %v", err)
        return
    }

	defer c.conn.Close()
    proto := protocol.NewProtocol(c.conn)
    bookMaker := domain.NewBookmaker(proto, c.config.BetProvider, c.config.ID)
    err = bookMaker.RegisterAll(ctx, c.config.BatchMaxAmount, c.config.LoopPeriod)
    if err != nil {
        log.Errorf("action: register_all | result: fail | client_id: %v | error: %v", c.config.ID, err)
    } else {
        log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
    }
}

func (c *Client) handleSigterm(cancel context.CancelFunc) {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM)
	go func() {
		<-sigs
		log.Infof("action: graceful_shutdown | result: in_progress")
		cancel()
		c.conn.Close()
	}()
}