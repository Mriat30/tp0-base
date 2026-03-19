package model

type BetProvider interface {
	NextBatch(size int) ([]Bet, error)
}

type Bet struct {
	Agency    uint32
	FirstName string
	LastName  string
	Document  uint32
	Birthdate string
	Number    uint32
}
