package com.example.demo;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.time.Duration;

@SpringBootApplication
public class DemoObservabilityApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoObservabilityApplication.class, args);
    }

    @Bean
    Counter businessEventsCounter(MeterRegistry registry) {
        return Counter.builder("app_business_events_total")
                .description("Example custom counter for business events")
                .register(registry);
    }

    @Bean
    Timer businessOperationTimer(MeterRegistry registry) {
        return Timer.builder("app_business_operation_seconds")
                .description("Example custom timer for a simulated business operation")
                .publishPercentileHistogram()
                .serviceLevelObjectives(
                        Duration.ofMillis(10),
                        Duration.ofMillis(50),
                        Duration.ofMillis(100),
                        Duration.ofMillis(250),
                        Duration.ofMillis(500))
                .register(registry);
    }
}
