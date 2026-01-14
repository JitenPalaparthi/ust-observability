
package main

import (
	"context"
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
	"go.opentelemetry.io/otel/trace"
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
	mux.Handle("/work", otelhttp.NewHandler(http.HandlerFunc(workHandler), "work-handler"))

	server := &http.Server{
		Addr:    ":8081",
		Handler: mux,
	}

	go func() {
		log.Println("Service B starting on :8081")
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	<-ctx.Done()
	log.Println("Service B shutting down HTTP server...")

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
			semconv.ServiceNameKey.String("service-b"),
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

func workHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	span := trace.SpanFromContext(ctx)

	// Simulate some processing
	delay := time.Duration(rand.Intn(300)+100) * time.Millisecond
	time.Sleep(delay)

	span.SetAttributes(
		attribute.String("service-b.work", "processing"),
		attribute.String("service-b.details", "did some work"),
	)

	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("Service B completed work"))
}
