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
	// 先检查请求是否已经取消，避免在明显超时后继续生成业务 ID。
	if err := ctx.Err(); err != nil {
		return Order{}, false, err
	}

	// 规范化后再校验并落库，确保空格差异不会产生两条看似相同的业务请求。
	idempotencyKey = strings.TrimSpace(idempotencyKey)
	customerID = strings.TrimSpace(customerID)
	if idempotencyKey == "" || customerID == "" || amountCents <= 0 {
		return Order{}, false, fmt.Errorf("%w: idempotency key, customer and positive amount are required", ErrInvalid)
	}

	value := Order{
		// ID 在 Service 层生成只是教学实现；生产环境通常由数据库/雪花号服务保证全局约束。
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
