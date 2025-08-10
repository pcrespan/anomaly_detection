# Build
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY . .

RUN if [ ! -f go.mod ]; then \
      echo "module api-gateway" > go.mod; \
    fi

RUN go mod tidy

RUN go build -o main .

# Runtime
FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
