package reader

import (
	"encoding/csv"
	"io"
	"strconv"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/src/model"
)

type CSVBetReader struct {
	csvReader *csv.Reader
	agencyID  uint32
}

func NewCSVBetReader(r io.Reader, agencyIDStr string) *CSVBetReader {
	id, _ := strconv.Atoi(agencyIDStr)
	return &CSVBetReader{
		csvReader: csv.NewReader(r),
		agencyID:  uint32(id),
	}
}

func (c *CSVBetReader) NextBatch(size int) ([]model.Bet, error) {
	var batch []model.Bet

	for i := 0; i < size; i++ {
		record, err := c.csvReader.Read()
		if err == io.EOF {
			if len(batch) > 0 { return batch, nil }
			return nil, io.EOF
		}
		if err != nil { return nil, err }

		doc, _ := strconv.Atoi(record[2])
		num, _ := strconv.Atoi(record[4])

		batch = append(batch, model.Bet{
			Agency:    c.agencyID,
			FirstName: record[0],
			LastName:  record[1],
			Document:  uint32(doc),
			Birthdate: record[3],
			Number:    uint32(num),
		})
	}

	return batch, nil
}