FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY ../go.mod ./
RUN go mod tidy

COPY . .
RUN go build -o service-b main.go

FROM alpine:3.19

WORKDIR /app
COPY --from=builder /app/service-b ./service-b

EXPOSE 8081

CMD ["./service-b"]
