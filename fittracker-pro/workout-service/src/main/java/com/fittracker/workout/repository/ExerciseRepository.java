package com.fittracker.workout.repository;

import com.fittracker.workout.entity.Exercise;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface ExerciseRepository extends JpaRepository<Exercise, Long> {

    Page<Exercise> findByNameContainingIgnoreCase(String name, Pageable pageable);

    Page<Exercise> findByCategoryId(Long categoryId, Pageable pageable);

    Page<Exercise> findByDifficultyLevel(Exercise.DifficultyLevel difficultyLevel, Pageable pageable);

    @Query("SELECT e FROM Exercise e WHERE LOWER(e.name) LIKE LOWER(CONCAT('%', :query, '%')) OR LOWER(e.muscleGroups) LIKE LOWER(CONCAT('%', :query, '%'))")
    Page<Exercise> searchExercises(@Param("query") String query, Pageable pageable);
}
