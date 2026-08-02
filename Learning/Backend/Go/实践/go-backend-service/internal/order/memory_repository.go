package order

import (
	"context"
	"sync"
)

type MemoryRepository struct {
	mu            sync.RWMutex
	byID          map[string]Order
	byIdempotency map[string]string
}

func NewMemoryRepository() *MemoryRepository {
	return &MemoryRepository{
		byID:          make(map[string]Order),
		byIdempotency: make(map[string]string),
	}
}

func (r *MemoryRepository) Save(ctx context.Context, idempotencyKey string, value Order) (Order, bool, error) {
	if err := ctx.Err(); err != nil {
		return Order{}, false, err
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	if existingID, ok := r.byIdempotency[idempotencyKey]; ok {
		// 在同一把锁内比较原始请求，保证重复请求不会竞态地生成第二个订单。
		existing := r.byID[existingID]
		if existing.CustomerID != value.CustomerID || existing.AmountCents != value.AmountCents {
			return Order{}, false, ErrConflict
		}
		return existing, false, nil
	}
	r.byID[value.ID] = value
	r.byIdempotency[idempotencyKey] = value.ID
	return value, true, nil
}

func (r *MemoryRepository) FindByID(ctx context.Context, id string) (Order, error) {
	if err := ctx.Err(); err != nil {
		return Order{}, err
	}

	r.mu.RLock()
	defer r.mu.RUnlock()
	// 读路径只持有读锁；Repository 替换成数据库后仍需保留同样的并发语义。
	value, ok := r.byID[id]
	if !ok {
		return Order{}, ErrNotFound
	}
	return value, nil
}
