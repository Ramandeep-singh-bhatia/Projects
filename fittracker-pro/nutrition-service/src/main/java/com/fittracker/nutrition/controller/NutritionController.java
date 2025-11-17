package com.fittracker.nutrition.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.nutrition.entity.FoodItem;
import com.fittracker.nutrition.service.FoodItemService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/nutrition")
@RequiredArgsConstructor
public class NutritionController {

    private final FoodItemService foodItemService;

    @GetMapping("/foods/search")
    public ResponseEntity<ApiResponse<Page<FoodItem>>> searchFoods(
            @RequestParam String query,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Search foods request - query: {}, page: {}, size: {}", query, page, size);
        Page<FoodItem> foods = foodItemService.searchFoods(query, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(foods));
    }

    @GetMapping("/foods/{id}")
    public ResponseEntity<ApiResponse<FoodItem>> getFoodById(@PathVariable Long id) {
        log.info("Get food by id: {}", id);
        FoodItem food = foodItemService.getFoodItemById(id);
        return ResponseEntity.ok(ApiResponse.success(food));
    }

    @GetMapping("/foods/category/{category}")
    public ResponseEntity<ApiResponse<Page<FoodItem>>> getFoodsByCategory(
            @PathVariable FoodItem.FoodCategory category,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Get foods by category: {}", category);
        Page<FoodItem> foods = foodItemService.getFoodsByCategory(category, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(foods));
    }
}
