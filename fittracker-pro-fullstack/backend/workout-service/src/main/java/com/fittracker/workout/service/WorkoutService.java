package com.fittracker.workout.service;

import com.fittracker.common.event.WorkoutCompletedEvent;
import com.fittracker.common.exception.BadRequestException;
import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.workout.dto.CompleteWorkoutRequest;
import com.fittracker.workout.dto.CreateWorkoutRequest;
import com.fittracker.workout.entity.Exercise;
import com.fittracker.workout.entity.Workout;
import com.fittracker.workout.entity.WorkoutExercise;
import com.fittracker.workout.kafka.EventPublisher;
import com.fittracker.workout.repository.ExerciseRepository;
import com.fittracker.workout.repository.WorkoutRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class WorkoutService {

    private final WorkoutRepository workoutRepository;
    private final ExerciseRepository exerciseRepository;
    private final EventPublisher eventPublisher;

    @Transactional
    public Workout createWorkout(CreateWorkoutRequest request) {
        log.info("Creating workout for user {}: {} on {}",
                request.getUserId(), request.getWorkoutName(), request.getWorkoutDate());

        // Create workout
        Workout workout = Workout.builder()
                .userId(request.getUserId())
                .workoutName(request.getWorkoutName())
                .workoutDate(request.getWorkoutDate())
                .startTime(request.getStartTime())
                .status(Workout.WorkoutStatus.IN_PROGRESS)
                .notes(request.getNotes())
                .build();

        // Add exercises
        for (int i = 0; i < request.getExercises().size(); i++) {
            var exerciseRequest = request.getExercises().get(i);

            Exercise exercise = exerciseRepository.findById(exerciseRequest.getExerciseId())
                    .orElseThrow(() -> new ResourceNotFoundException(
                            "Exercise not found with id: " + exerciseRequest.getExerciseId()));

            WorkoutExercise workoutExercise = WorkoutExercise.builder()
                    .exercise(exercise)
                    .exerciseOrder(i + 1)
                    .plannedSets(exerciseRequest.getPlannedSets())
                    .plannedReps(exerciseRequest.getPlannedReps())
                    .plannedDurationSeconds(exerciseRequest.getPlannedDurationSeconds())
                    .actualSets(exerciseRequest.getActualSets())
                    .actualReps(exerciseRequest.getActualReps())
                    .actualDurationSeconds(exerciseRequest.getActualDurationSeconds())
                    .weightKg(exerciseRequest.getWeightKg())
                    .notes(exerciseRequest.getNotes())
                    .build();

            // Calculate calories burned if duration is provided
            if (workoutExercise.getActualDurationSeconds() != null && exercise.getCaloriesPerMinute() != null) {
                BigDecimal minutes = BigDecimal.valueOf(workoutExercise.getActualDurationSeconds() / 60.0);
                int calories = exercise.getCaloriesPerMinute().multiply(minutes).intValue();
                workoutExercise.setCaloriesBurned(calories);
            }

            workout.addExercise(workoutExercise);
        }

        Workout savedWorkout = workoutRepository.save(workout);
        log.info("Workout created with ID {}", savedWorkout.getId());

        return savedWorkout;
    }

    @Transactional
    public Workout completeWorkout(Long workoutId, CompleteWorkoutRequest request) {
        log.info("Completing workout {}", workoutId);

        Workout workout = workoutRepository.findById(workoutId)
                .orElseThrow(() -> new ResourceNotFoundException("Workout not found with id: " + workoutId));

        if (workout.getStatus() == Workout.WorkoutStatus.COMPLETED) {
            throw new BadRequestException("Workout is already completed");
        }

        workout.setEndTime(request.getEndTime());
        workout.setStatus(Workout.WorkoutStatus.COMPLETED);

        // Calculate total duration
        Duration duration = Duration.between(workout.getStartTime(), workout.getEndTime());
        workout.setTotalDurationMinutes((int) duration.toMinutes());

        // Calculate total calories burned
        int totalCalories = workout.getWorkoutExercises().stream()
                .mapToInt(we -> we.getCaloriesBurned() != null ? we.getCaloriesBurned() : 0)
                .sum();
        workout.setTotalCaloriesBurned(totalCalories);

        Workout completedWorkout = workoutRepository.save(workout);
        log.info("Workout {} completed: {} minutes, {} calories",
                workoutId, completedWorkout.getTotalDurationMinutes(), completedWorkout.getTotalCaloriesBurned());

        // Publish WorkoutCompletedEvent
        String workoutType = determineWorkoutType(completedWorkout);
        WorkoutCompletedEvent event = WorkoutCompletedEvent.create(
                completedWorkout.getId(),
                completedWorkout.getUserId(),
                completedWorkout.getWorkoutDate(),
                completedWorkout.getTotalDurationMinutes(),
                completedWorkout.getTotalCaloriesBurned(),
                workoutType,
                completedWorkout.getWorkoutExercises().size()
        );
        eventPublisher.publishWorkoutCompletedEvent(event);

        return completedWorkout;
    }

    @Transactional(readOnly = true)
    public Workout getWorkoutById(Long workoutId) {
        return workoutRepository.findById(workoutId)
                .orElseThrow(() -> new ResourceNotFoundException("Workout not found with id: " + workoutId));
    }

    @Transactional(readOnly = true)
    public List<Workout> getUserWorkouts(Long userId) {
        return workoutRepository.findByUserIdOrderByWorkoutDateDesc(userId);
    }

    @Transactional(readOnly = true)
    public List<Workout> getWorkoutsForDate(Long userId, LocalDate date) {
        return workoutRepository.findByUserIdAndWorkoutDate(userId, date);
    }

    @Transactional(readOnly = true)
    public List<Workout> getWorkoutsInRange(Long userId, LocalDate startDate, LocalDate endDate) {
        return workoutRepository.findByUserIdAndWorkoutDateBetweenOrderByWorkoutDateDesc(userId, startDate, endDate);
    }

    @Transactional
    public void deleteWorkout(Long workoutId) {
        Workout workout = getWorkoutById(workoutId);
        log.info("Deleting workout {}", workoutId);
        workoutRepository.delete(workout);
    }

    private String determineWorkoutType(Workout workout) {
        // Simple heuristic: get the most common exercise category
        return workout.getWorkoutExercises().stream()
                .map(we -> we.getExercise().getCategory().getName())
                .findFirst()
                .orElse("GENERAL");
    }
}
