package com.fittracker.nutrition.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MealItemRequest {

    @NotNull(message = "Food item ID is required")
    private Long foodItemId;

    @NotNull(message = "Servings is required")
    @DecimalMin(value = "0.1", message = "Servings must be at least 0.1")
    private BigDecimal servings;
}
