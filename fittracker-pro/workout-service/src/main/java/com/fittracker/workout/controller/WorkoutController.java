package com.fittracker.workout.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.workout.dto.CompleteWorkoutRequest;
import com.fittracker.workout.dto.CreateWorkoutRequest;
import com.fittracker.workout.entity.Exercise;
import com.fittracker.workout.entity.Workout;
import com.fittracker.workout.service.ExerciseService;
import com.fittracker.workout.service.WorkoutService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/workouts")
@RequiredArgsConstructor
public class WorkoutController {

    private final ExerciseService exerciseService;
    private final WorkoutService workoutService;

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

    // Workout session endpoints

    @PostMapping
    public ResponseEntity<ApiResponse<Workout>> createWorkout(@Valid @RequestBody CreateWorkoutRequest request) {
        log.info("Create workout request for user {}: {}", request.getUserId(), request.getWorkoutName());
        Workout workout = workoutService.createWorkout(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Workout created successfully", workout));
    }

    @PostMapping("/{workoutId}/complete")
    public ResponseEntity<ApiResponse<Workout>> completeWorkout(
            @PathVariable Long workoutId,
            @Valid @RequestBody CompleteWorkoutRequest request) {
        log.info("Complete workout request for workout {}", workoutId);
        Workout workout = workoutService.completeWorkout(workoutId, request);
        return ResponseEntity.ok(ApiResponse.success("Workout completed successfully", workout));
    }

    @GetMapping("/{workoutId}")
    public ResponseEntity<ApiResponse<Workout>> getWorkout(@PathVariable Long workoutId) {
        log.info("Get workout by id: {}", workoutId);
        Workout workout = workoutService.getWorkoutById(workoutId);
        return ResponseEntity.ok(ApiResponse.success(workout));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<Workout>>> getUserWorkouts(@PathVariable Long userId) {
        log.info("Get all workouts for user: {}", userId);
        List<Workout> workouts = workoutService.getUserWorkouts(userId);
        return ResponseEntity.ok(ApiResponse.success(workouts));
    }

    @GetMapping("/user/{userId}/date/{date}")
    public ResponseEntity<ApiResponse<List<Workout>>> getWorkoutsForDate(
            @PathVariable Long userId,
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        log.info("Get workouts for user {} on date: {}", userId, date);
        List<Workout> workouts = workoutService.getWorkoutsForDate(userId, date);
        return ResponseEntity.ok(ApiResponse.success(workouts));
    }

    @GetMapping("/user/{userId}/range")
    public ResponseEntity<ApiResponse<List<Workout>>> getWorkoutsInRange(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        log.info("Get workouts for user {} from {} to {}", userId, startDate, endDate);
        List<Workout> workouts = workoutService.getWorkoutsInRange(userId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(workouts));
    }

    @DeleteMapping("/{workoutId}")
    public ResponseEntity<ApiResponse<Void>> deleteWorkout(@PathVariable Long workoutId) {
        log.info("Delete workout: {}", workoutId);
        workoutService.deleteWorkout(workoutId);
        return ResponseEntity.ok(ApiResponse.success("Workout deleted successfully", null));
    }
}
