package order

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"sync/atomic"
	"time"
)

var (
	ErrConflict = errors.New("idempotency key conflicts with an existing request")
	ErrInvalid  = errors.New("invalid order")
	ErrNotFound = errors.New("order not found")
)

type Order struct {
	ID          string    `json:"id"`
	CustomerID  string    `json:"customer_id"`
	AmountCents int64     `json:"amount_cents"`
	CreatedAt   time.Time `json:"created_at"`
}

type Repository interface {
	Save(ctx context.Context, idempotencyKey string, value Order) (saved Order, created bool, err error)
	FindByID(ctx context.Context, id string) (Order, error)
}

type Service struct {
	repository Repository
	now        func() time.Time
	nextID     atomic.Uint64
}

func NewService(repository Repository) *Service {
	return &Service{repository: repository, now: time.Now}
}

func (s *Service) Create(ctx context.Context, idempotencyKey, customerID string, amountCents int64) (Order, bool, error) {
	if err := ctx.Err(); err != nil {
		return Order{}, false, err
	}

	idempotencyKey = strings.TrimSpace(idempotencyKey)
	customerID = strings.TrimSpace(customerID)
	if idempotencyKey == "" || customerID == "" || amountCents <= 0 {
		return Order{}, false, fmt.Errorf("%w: idempotency key, customer and positive amount are required", ErrInvalid)
	}

	value := Order{
		ID:          fmt.Sprintf("ord-%d", s.nextID.Add(1)),
		CustomerID:  customerID,
		AmountCents: amountCents,
		CreatedAt:   s.now().UTC(),
	}
	return s.repository.Save(ctx, idempotencyKey, value)
}

func (s *Service) FindByID(ctx context.Context, id string) (Order, error) {
	if strings.TrimSpace(id) == "" {
		return Order{}, fmt.Errorf("%w: id is required", ErrInvalid)
	}
	return s.repository.FindByID(ctx, id)
}
