package com.fittracker.nutrition.service;

import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.nutrition.entity.FoodItem;
import com.fittracker.nutrition.repository.FoodItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class FoodItemService {

    private final FoodItemRepository foodItemRepository;

    @Transactional(readOnly = true)
    @Cacheable(value = "foodItems", key = "#id")
    public FoodItem getFoodItemById(Long id) {
        return foodItemRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Food item not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Page<FoodItem> searchFoods(String query, Pageable pageable) {
        log.info("Searching foods with query: {}", query);
        return foodItemRepository.searchFoods(query, pageable);
    }

    @Transactional(readOnly = true)
    public Page<FoodItem> getFoodsByCategory(FoodItem.FoodCategory category, Pageable pageable) {
        return foodItemRepository.findByCategory(category, pageable);
    }
}
