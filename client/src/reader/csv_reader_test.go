package reader

import (
	"strings"
	"testing"
)

func TestCSVBetReader_NextBatch(t *testing.T) {
	data := "Juan,Perez,123,2000-01-01,7574\nMaria,Gomez,456,1995-05-05,1234"
	r := strings.NewReader(data)
	reader := NewCSVBetReader(r, "5")

	batch, err := reader.NextBatch(1)
	
	if err != nil {
		t.Fatalf("Error reading batch: %v", err)
	}
	if len(batch) != 1 {
		t.Errorf("Expected 1 bet, got %d", len(batch))
	}
	if batch[0].FirstName != "Juan" || batch[0].Agency != 5 {
		t.Errorf("Incorrect bet data: %+v", batch[0])
	}

	batch2, err := reader.NextBatch(10)
	if len(batch2) != 1 {
		t.Errorf("Expected 1 remaining bet, got %d", len(batch2))
	}
	if batch2[0].FirstName != "Maria" {
		t.Errorf("Incorrect second bet: %s", batch2[0].FirstName)
	}
}

func TestCSVBetReader_InvalidData(t *testing.T) {
    data := "Juan,Perez,ESTO_NO_ES_UN_DNI,2000-01-01,7574"
    r := strings.NewReader(data)
    reader := NewCSVBetReader(r, "5")

    _, err := reader.NextBatch(1)

    if err == nil {
        t.Fatal("Expected an error for invalid DNI, but none was obtained")
    }

    if !strings.Contains(err.Error(), "invalid syntax") {
        t.Errorf("The error should mention a syntax problem, but was: %v", err)
    }
}