package com.fittracker.workout.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.workout.entity.Exercise;
import com.fittracker.workout.service.ExerciseService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/workouts")
@RequiredArgsConstructor
public class WorkoutController {

    private final ExerciseService exerciseService;

    @GetMapping("/exercises/search")
    public ResponseEntity<ApiResponse<Page<Exercise>>> searchExercises(
            @RequestParam String query,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Search exercises request - query: {}", query);
        Page<Exercise> exercises = exerciseService.searchExercises(query, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(exercises));
    }

    @GetMapping("/exercises/{id}")
    public ResponseEntity<ApiResponse<Exercise>> getExerciseById(@PathVariable Long id) {
        log.info("Get exercise by id: {}", id);
        Exercise exercise = exerciseService.getExerciseById(id);
        return ResponseEntity.ok(ApiResponse.success(exercise));
    }

    @GetMapping("/exercises/category/{categoryId}")
    public ResponseEntity<ApiResponse<Page<Exercise>>> getExercisesByCategory(
            @PathVariable Long categoryId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Get exercises by category: {}", categoryId);
        Page<Exercise> exercises = exerciseService.getExercisesByCategory(categoryId, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(exercises));
    }

    @GetMapping("/exercises/difficulty/{difficulty}")
    public ResponseEntity<ApiResponse<Page<Exercise>>> getExercisesByDifficulty(
            @PathVariable Exercise.DifficultyLevel difficulty,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Get exercises by difficulty: {}", difficulty);
        Page<Exercise> exercises = exerciseService.getExercisesByDifficulty(difficulty, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(exercises));
    }
}
