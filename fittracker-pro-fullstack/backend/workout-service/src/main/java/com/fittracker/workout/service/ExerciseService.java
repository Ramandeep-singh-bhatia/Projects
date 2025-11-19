package com.fittracker.workout.service;

import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.workout.entity.Exercise;
import com.fittracker.workout.repository.ExerciseRepository;
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
public class ExerciseService {

    private final ExerciseRepository exerciseRepository;

    @Transactional(readOnly = true)
    @Cacheable(value = "exercises", key = "#id")
    public Exercise getExerciseById(Long id) {
        return exerciseRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Exercise not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Page<Exercise> searchExercises(String query, Pageable pageable) {
        log.info("Searching exercises with query: {}", query);
        return exerciseRepository.searchExercises(query, pageable);
    }

    @Transactional(readOnly = true)
    public Page<Exercise> getExercisesByCategory(Long categoryId, Pageable pageable) {
        return exerciseRepository.findByCategoryId(categoryId, pageable);
    }

    @Transactional(readOnly = true)
    public Page<Exercise> getExercisesByDifficulty(Exercise.DifficultyLevel difficulty, Pageable pageable) {
        return exerciseRepository.findByDifficultyLevel(difficulty, pageable);
    }
}
