package com.fittracker.workout.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI workoutServiceOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("FitTracker Pro - Workout Service API")
                        .description("Workout tracking and exercise library service")
                        .version("v1.0.0")
                        .contact(new Contact()
                                .name("FitTracker Pro Team")
                                .email("support@fittracker.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")));
    }
}
