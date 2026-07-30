package httpapi

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync/atomic"
	"time"

	"notes/go-backend-service/internal/order"
)

const maxRequestBody = 1 << 20

type API struct {
	orders        *order.Service
	requestNumber atomic.Uint64
}

func New(orders *order.Service) *API {
	return &API{orders: orders}
}

func (a *API) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", a.health)
	mux.HandleFunc("POST /orders", a.createOrder)
	mux.HandleFunc("GET /orders/{id}", a.findOrder)
	return a.withRequestContext(mux)
}

func (a *API) withRequestContext(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := strings.TrimSpace(r.Header.Get("X-Request-ID"))
		if requestID == "" {
			requestID = fmt.Sprintf("req-%d", a.requestNumber.Add(1))
		}
		w.Header().Set("X-Request-ID", requestID)

		ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
		defer cancel()
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func (a *API) health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

type createOrderRequest struct {
	CustomerID  string `json:"customer_id"`
	AmountCents int64  `json:"amount_cents"`
}

func (a *API) createOrder(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, maxRequestBody)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()

	var input createOrderRequest
	if err := decoder.Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", "request body must be valid JSON")
		return
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		writeError(w, http.StatusBadRequest, "invalid_json", "request body must contain one JSON object")
		return
	}

	value, created, err := a.orders.Create(
		r.Context(),
		r.Header.Get("Idempotency-Key"),
		input.CustomerID,
		input.AmountCents,
	)
	if err != nil {
		a.writeServiceError(w, err)
		return
	}
	status := http.StatusOK
	if created {
		status = http.StatusCreated
	}
	writeJSON(w, status, value)
}

func (a *API) findOrder(w http.ResponseWriter, r *http.Request) {
	value, err := a.orders.FindByID(r.Context(), r.PathValue("id"))
	if err != nil {
		a.writeServiceError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, value)
}

func (a *API) writeServiceError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, order.ErrInvalid):
		writeError(w, http.StatusBadRequest, "invalid_order", err.Error())
	case errors.Is(err, order.ErrNotFound):
		writeError(w, http.StatusNotFound, "order_not_found", "order not found")
	case errors.Is(err, order.ErrConflict):
		writeError(w, http.StatusConflict, "idempotency_conflict", "idempotency key was already used for different input")
	case errors.Is(err, context.Canceled), errors.Is(err, context.DeadlineExceeded):
		writeError(w, http.StatusGatewayTimeout, "request_timeout", "request was canceled or timed out")
	default:
		writeError(w, http.StatusInternalServerError, "internal_error", "internal server error")
	}
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	writeJSON(w, status, map[string]string{"code": code, "message": message})
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}
