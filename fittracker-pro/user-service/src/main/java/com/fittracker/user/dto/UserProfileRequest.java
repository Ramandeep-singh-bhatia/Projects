package com.fittracker.user.dto;

import com.fittracker.user.entity.UserProfile;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Past;
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
public class UserProfileRequest {

    @Past(message = "Date of birth must be in the past")
    private LocalDate dateOfBirth;

    private UserProfile.Gender gender;

    @DecimalMin(value = "0.0", inclusive = false, message = "Height must be greater than 0")
    private BigDecimal heightCm;

    @DecimalMin(value = "0.0", inclusive = false, message = "Weight must be greater than 0")
    private BigDecimal currentWeightKg;

    @DecimalMin(value = "0.0", inclusive = false, message = "Target weight must be greater than 0")
    private BigDecimal targetWeightKg;

    private UserProfile.ActivityLevel activityLevel;

    private UserProfile.FitnessGoal fitnessGoal;
}
