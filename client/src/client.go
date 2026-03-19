package src
import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

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
	Bet           model.Bet
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
	c.should_be_running = true
	c.handleSigterm()

	for msgID := 1; msgID <= c.config.LoopAmount && c.should_be_running; msgID++ {
		err := c.createClientSocket()
		if err != nil {
			time.Sleep(c.config.LoopPeriod)
			continue
		}

		proto := protocol.NewProtocol(c.conn)
		book_maker := domain.NewBookmaker(proto, c.config.Bet, c.config.ID)

		_ = book_maker.Register()

		c.conn.Close()
		time.Sleep(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) handleSigterm() {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM)
	go func() {
		<-sigs
		log.Infof("action: graceful_shutdown | result: in_progress")
		c.should_be_running = false
	}()
}