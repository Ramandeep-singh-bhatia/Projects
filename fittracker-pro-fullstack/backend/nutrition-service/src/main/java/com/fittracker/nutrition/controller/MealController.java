package com.fittracker.nutrition.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.nutrition.dto.CreateMealRequest;
import com.fittracker.nutrition.entity.Meal;
import com.fittracker.nutrition.service.MealService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/nutrition/meals")
@RequiredArgsConstructor
public class MealController {

    private final MealService mealService;

    @PostMapping
    public ResponseEntity<ApiResponse<Meal>> createMeal(@Valid @RequestBody CreateMealRequest request) {
        log.info("Create meal request for user {}: {}", request.getUserId(), request.getMealType());
        Meal meal = mealService.createMeal(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Meal created successfully", meal));
    }

    @GetMapping("/{mealId}")
    public ResponseEntity<ApiResponse<Meal>> getMeal(@PathVariable Long mealId) {
        log.info("Get meal by id: {}", mealId);
        Meal meal = mealService.getMealById(mealId);
        return ResponseEntity.ok(ApiResponse.success(meal));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<Meal>>> getUserMeals(@PathVariable Long userId) {
        log.info("Get all meals for user: {}", userId);
        List<Meal> meals = mealService.getUserMeals(userId);
        return ResponseEntity.ok(ApiResponse.success(meals));
    }

    @GetMapping("/user/{userId}/date/{date}")
    public ResponseEntity<ApiResponse<List<Meal>>> getMealsForDate(
            @PathVariable Long userId,
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        log.info("Get meals for user {} on date: {}", userId, date);
        List<Meal> meals = mealService.getMealsForDate(userId, date);
        return ResponseEntity.ok(ApiResponse.success(meals));
    }

    @GetMapping("/user/{userId}/range")
    public ResponseEntity<ApiResponse<List<Meal>>> getMealsInRange(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        log.info("Get meals for user {} from {} to {}", userId, startDate, endDate);
        List<Meal> meals = mealService.getMealsInRange(userId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(meals));
    }

    @GetMapping("/user/{userId}/recent")
    public ResponseEntity<ApiResponse<List<Meal>>> getRecentMeals(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "7") int days) {
        log.info("Get recent meals for user {} (last {} days)", userId, days);
        List<Meal> meals = mealService.getRecentMeals(userId, days);
        return ResponseEntity.ok(ApiResponse.success(meals));
    }

    @GetMapping("/user/{userId}/calories/{date}")
    public ResponseEntity<ApiResponse<Double>> getTotalCaloriesForDate(
            @PathVariable Long userId,
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        log.info("Get total calories for user {} on {}", userId, date);
        Double totalCalories = mealService.getTotalCaloriesForDate(userId, date);
        return ResponseEntity.ok(ApiResponse.success(totalCalories));
    }

    @DeleteMapping("/{mealId}")
    public ResponseEntity<ApiResponse<Void>> deleteMeal(@PathVariable Long mealId) {
        log.info("Delete meal: {}", mealId);
        mealService.deleteMeal(mealId);
        return ResponseEntity.ok(ApiResponse.success("Meal deleted successfully", null));
    }
}
