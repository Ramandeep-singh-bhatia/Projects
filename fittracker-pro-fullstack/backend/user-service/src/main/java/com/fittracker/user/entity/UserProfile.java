package com.fittracker.user.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_profiles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private Gender gender;

    @Column(name = "height_cm", precision = 5, scale = 2)
    private BigDecimal heightCm;

    @Column(name = "current_weight_kg", precision = 5, scale = 2)
    private BigDecimal currentWeightKg;

    @Column(name = "target_weight_kg", precision = 5, scale = 2)
    private BigDecimal targetWeightKg;

    @Enumerated(EnumType.STRING)
    @Column(name = "activity_level", length = 20)
    private ActivityLevel activityLevel;

    @Enumerated(EnumType.STRING)
    @Column(name = "fitness_goal", length = 50)
    private FitnessGoal fitnessGoal;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public enum Gender {
        MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY
    }

    public enum ActivityLevel {
        SEDENTARY,
        LIGHTLY_ACTIVE,
        MODERATELY_ACTIVE,
        VERY_ACTIVE,
        EXTREMELY_ACTIVE
    }

    public enum FitnessGoal {
        LOSE_WEIGHT,
        MAINTAIN_WEIGHT,
        GAIN_WEIGHT,
        BUILD_MUSCLE,
        IMPROVE_ENDURANCE,
        GENERAL_FITNESS
    }
}
