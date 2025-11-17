package com.fittracker.nutrition.repository;

import com.fittracker.nutrition.entity.FoodItem;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface FoodItemRepository extends JpaRepository<FoodItem, Long> {

    Page<FoodItem> findByNameContainingIgnoreCase(String name, Pageable pageable);

    Page<FoodItem> findByCategory(FoodItem.FoodCategory category, Pageable pageable);

    Optional<FoodItem> findByBarcode(String barcode);

    @Query("SELECT f FROM FoodItem f WHERE LOWER(f.name) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(f.brand) LIKE LOWER(CONCAT('%', :query, '%'))")
    Page<FoodItem> searchFoods(@Param("query") String query, Pageable pageable);
}
