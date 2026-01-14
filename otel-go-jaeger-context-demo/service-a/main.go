package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	shutdown := initTracer(ctx)
	defer func() {
		if err := shutdown(context.Background()); err != nil {
			log.Printf("error shutting down tracer provider: %v", err)
		}
	}()

	mux := http.NewServeMux()
	mux.Handle("/hello", otelhttp.NewHandler(http.HandlerFunc(helloHandler), "hello-handler"))

	server := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}

	go func() {
		log.Println("Service A starting on :8080")
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	<-ctx.Done()
	log.Println("Service A shutting down HTTP server...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("server shutdown failed: %v", err)
	}
}

func initTracer(ctx context.Context) func(context.Context) error {
	res, err := resource.New(
		ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String("service-a"),
			attribute.String("service.environment", "dev"),
		),
	)
	if err != nil {
		log.Fatalf("failed to create resource: %v", err)
	}

	exporter, err := otlptracehttp.New(ctx,
		otlptracehttp.WithEndpoint("otel-collector:4318"),
		otlptracehttp.WithInsecure(),
		otlptracehttp.WithURLPath("/v1/traces"),
	)
	if err != nil {
		log.Fatalf("failed to create OTLP trace exporter: %v", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(
		propagation.NewCompositeTextMapPropagator(
			propagation.TraceContext{},
			propagation.Baggage{},
		),
	)

	return tp.Shutdown
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	tracer := otel.Tracer("service-a-tracer")

	// Simulate some work in service A
	_, span := tracer.Start(ctx, "service-a-work")
	delay := time.Duration(rand.Intn(200)+50) * time.Millisecond
	time.Sleep(delay)
	span.SetAttributes(attribute.String("service-a.work", "simulated"))
	span.End()

	// Now call Service B, propagating the context
	client := http.Client{
		Transport: otelhttp.NewTransport(http.DefaultTransport),
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "http://service-b:8081/work", nil)
	if err != nil {
		http.Error(w, "failed to create request to service B", http.StatusInternalServerError)
		return
	}

	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, fmt.Sprintf("error calling service B: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("Service A /hello response\n"))
	_, _ = w.Write([]byte("Service B replied: " + string(body) + "\n"))
}
