package httpapi_test

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"notes/go-backend-service/internal/httpapi"
	"notes/go-backend-service/internal/order"
)

func newHandler() http.Handler {
	repository := order.NewMemoryRepository()
	service := order.NewService(repository)
	return httpapi.New(service).Handler()
}

func TestCreateOrderIsIdempotent(t *testing.T) {
	handler := newHandler()
	first := createOrder(t, handler, "same-key", 1999)
	second := createOrder(t, handler, "same-key", 1999)

	if first.Code != http.StatusCreated {
		t.Fatalf("first status = %d, want %d", first.Code, http.StatusCreated)
	}
	if second.Code != http.StatusOK {
		t.Fatalf("second status = %d, want %d", second.Code, http.StatusOK)
	}

	var firstOrder, secondOrder order.Order
	if err := json.Unmarshal(first.Body.Bytes(), &firstOrder); err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(second.Body.Bytes(), &secondOrder); err != nil {
		t.Fatal(err)
	}
	if firstOrder.ID != secondOrder.ID {
		t.Fatalf("ids differ: %q != %q", firstOrder.ID, secondOrder.ID)
	}
}

func TestCreateOrderRejectsInvalidAmount(t *testing.T) {
	response := createOrder(t, newHandler(), "key", 0)
	if response.Code != http.StatusBadRequest {
		t.Fatalf("status = %d, want %d", response.Code, http.StatusBadRequest)
	}
}

func TestCreateOrderRejectsReusedKeyWithDifferentInput(t *testing.T) {
	handler := newHandler()
	first := createOrder(t, handler, "same-key", 1999)
	second := createOrder(t, handler, "same-key", 2999)
	if first.Code != http.StatusCreated {
		t.Fatalf("first status = %d, want %d", first.Code, http.StatusCreated)
	}
	if second.Code != http.StatusConflict {
		t.Fatalf("second status = %d, want %d", second.Code, http.StatusConflict)
	}
}

func TestFindMissingOrder(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, "/orders/missing", nil)
	response := httptest.NewRecorder()
	newHandler().ServeHTTP(response, request)
	if response.Code != http.StatusNotFound {
		t.Fatalf("status = %d, want %d", response.Code, http.StatusNotFound)
	}
}

func createOrder(t *testing.T, handler http.Handler, key string, amount int64) *httptest.ResponseRecorder {
	t.Helper()
	body := strings.NewReader(`{"customer_id":"customer-1","amount_cents":` + jsonNumber(amount) + `}`)
	request := httptest.NewRequest(http.MethodPost, "/orders", body)
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Idempotency-Key", key)
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, request)
	return response
}

func jsonNumber(value int64) string {
	return fmt.Sprintf("%d", value)
}
