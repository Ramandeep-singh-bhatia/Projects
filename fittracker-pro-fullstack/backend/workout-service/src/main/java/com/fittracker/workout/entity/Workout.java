package com.fittracker.workout.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "workouts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Workout {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "template_id")
    private WorkoutTemplate template;

    @Column(name = "workout_name", nullable = false)
    private String workoutName;

    @Column(name = "workout_date", nullable = false)
    private LocalDate workoutDate;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "total_duration_minutes")
    private Integer totalDurationMinutes;

    @Column(name = "total_calories_burned")
    private Integer totalCaloriesBurned;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    @Builder.Default
    private WorkoutStatus status = WorkoutStatus.IN_PROGRESS;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @OneToMany(mappedBy = "workout", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<WorkoutExercise> workoutExercises = new ArrayList<>();

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public enum WorkoutStatus {
        PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    }

    public void addExercise(WorkoutExercise exercise) {
        workoutExercises.add(exercise);
        exercise.setWorkout(this);
    }
}
