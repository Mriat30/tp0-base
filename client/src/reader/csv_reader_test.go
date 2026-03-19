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
		t.Fatalf("No se esperaba error, se obtuvo: %v", err)
	}
	if len(batch) != 1 {
		t.Errorf("Se esperaba 1 apuesta, se obtuvieron %d", len(batch))
	}
	if batch[0].FirstName != "Juan" || batch[0].Agency != 5 {
		t.Errorf("Datos de la apuesta incorrectos: %+v", batch[0])
	}

	batch2, err := reader.NextBatch(10)
	if len(batch2) != 1 {
		t.Errorf("Se esperaba 1 apuesta restante, se obtuvieron %d", len(batch2))
	}
	if batch2[0].FirstName != "Maria" {
		t.Errorf("Segunda apuesta incorrecta: %s", batch2[0].FirstName)
	}
}