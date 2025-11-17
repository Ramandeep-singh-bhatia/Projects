package com.fittracker.nutrition.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.nutrition.entity.FoodItem;
import com.fittracker.nutrition.service.FoodItemService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/nutrition/foods")
@RequiredArgsConstructor
public class FoodItemController {

    private final FoodItemService foodItemService;

    @GetMapping("/search")
    public ResponseEntity<ApiResponse<Page<FoodItem>>> searchFoods(
            @RequestParam String query,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<FoodItem> foods = foodItemService.searchFoods(query, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(foods));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<FoodItem>> getFoodById(@PathVariable Long id) {
        FoodItem food = foodItemService.getFoodItemById(id);
        return ResponseEntity.ok(ApiResponse.success(food));
    }
}
