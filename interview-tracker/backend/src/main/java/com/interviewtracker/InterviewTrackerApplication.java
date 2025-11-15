package com.interviewtracker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class InterviewTrackerApplication {

    public static void main(String[] args) {
        SpringApplication.run(InterviewTrackerApplication.class, args);
        System.out.println("\n======================================");
        System.out.println("Interview Tracker Backend Started!");
        System.out.println("API available at: http://localhost:8080");
        System.out.println("H2 Console at: http://localhost:8080/h2-console");
        System.out.println("======================================\n");
    }
}
