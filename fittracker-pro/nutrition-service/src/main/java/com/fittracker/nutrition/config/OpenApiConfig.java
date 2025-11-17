package com.fittracker.nutrition.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI nutritionServiceOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("FitTracker Pro - Nutrition Service API")
                        .description("Nutrition tracking and meal management service with food database")
                        .version("v1.0.0")
                        .contact(new Contact()
                                .name("FitTracker Pro Team")
                                .email("support@fittracker.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")));
    }
}
