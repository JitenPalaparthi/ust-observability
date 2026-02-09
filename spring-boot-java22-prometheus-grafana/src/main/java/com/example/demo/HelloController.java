package com.example.demo;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

@RestController
@Validated
public class HelloController {

    private final Counter businessEvents;
    private final Timer businessTimer;

    public HelloController(Counter businessEventsCounter, Timer businessOperationTimer) {
        this.businessEvents = businessEventsCounter;
        this.businessTimer = businessOperationTimer;
    }

    @GetMapping("/api/hello")
    public ResponseEntity<Map<String, Object>> hello(
            @RequestParam(defaultValue = "JP") String name,
            @RequestParam(defaultValue = "10") @Min(0) @Max(1000) int workMs
    ) {
        // Simulate some work so you get non-trivial latency/throughput graphs
        businessEvents.increment();
        businessTimer.record(() -> sleepRandom(workMs));

        return ResponseEntity.ok(Map.of(
                "message", "Hello " + name + "!",
                "workMsRequested", workMs
        ));
    }

    private void sleepRandom(int baseMs) {
        int jitter = ThreadLocalRandom.current().nextInt(0, Math.max(1, baseMs / 2 + 1));
        int total = baseMs + jitter;
        try {
            TimeUnit.MILLISECONDS.sleep(total);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
