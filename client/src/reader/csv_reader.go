package reader

import (
	"fmt"
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
        if err != nil { return nil, fmt.Errorf("error reading CSV: %w", err) }

        doc, err := strconv.ParseUint(record[2], 10, 32)
        if err != nil {
            return nil, fmt.Errorf("invalid DNI %d: %w", i, err)
        }

        num, err := strconv.ParseUint(record[4], 10, 32)
        if err != nil {
            return nil, fmt.Errorf("invalid bet number %d: %w", i, err)
        }

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