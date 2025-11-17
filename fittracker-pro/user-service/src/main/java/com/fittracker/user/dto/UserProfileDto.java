package com.fittracker.user.dto;

import com.fittracker.user.entity.UserProfile;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserProfileDto {

    private Long id;
    private Long userId;
    private LocalDate dateOfBirth;
    private UserProfile.Gender gender;
    private BigDecimal heightCm;
    private BigDecimal currentWeightKg;
    private BigDecimal targetWeightKg;
    private UserProfile.ActivityLevel activityLevel;
    private UserProfile.FitnessGoal fitnessGoal;
    private Integer age; // calculated field
}
