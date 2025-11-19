package com.fittracker.nutrition.dto;

import com.fittracker.nutrition.entity.Meal;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateMealRequest {

    @NotNull(message = "User ID is required")
    private Long userId;

    @NotNull(message = "Meal type is required")
    private Meal.MealType mealType;

    @NotNull(message = "Meal date is required")
    private LocalDate mealDate;

    private LocalTime mealTime;

    @NotEmpty(message = "At least one meal item is required")
    @Valid
    private List<MealItemRequest> items;

    @Size(max = 500, message = "Notes must not exceed 500 characters")
    private String notes;
}
