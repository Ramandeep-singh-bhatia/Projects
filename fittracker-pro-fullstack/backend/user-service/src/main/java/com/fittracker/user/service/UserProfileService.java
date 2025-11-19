package com.fittracker.user.service;

import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.user.dto.UserProfileDto;
import com.fittracker.user.dto.UserProfileRequest;
import com.fittracker.user.entity.User;
import com.fittracker.user.entity.UserProfile;
import com.fittracker.user.repository.UserProfileRepository;
import com.fittracker.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.Period;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserProfileService {

    private final UserProfileRepository profileRepository;
    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public UserProfileDto getProfile(Long userId) {
        UserProfile profile = profileRepository.findByUserId(userId)
                .orElseThrow(() -> new ResourceNotFoundException("Profile not found for user: " + userId));

        return toDto(profile);
    }

    @Transactional
    public UserProfileDto createOrUpdateProfile(Long userId, UserProfileRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));

        UserProfile profile = profileRepository.findByUserId(userId)
                .orElse(UserProfile.builder().user(user).build());

        updateProfileFromRequest(profile, request);
        UserProfile savedProfile = profileRepository.save(profile);

        log.info("Profile saved for user: {}", userId);
        return toDto(savedProfile);
    }

    private void updateProfileFromRequest(UserProfile profile, UserProfileRequest request) {
        if (request.getDateOfBirth() != null) {
            profile.setDateOfBirth(request.getDateOfBirth());
        }
        if (request.getGender() != null) {
            profile.setGender(request.getGender());
        }
        if (request.getHeightCm() != null) {
            profile.setHeightCm(request.getHeightCm());
        }
        if (request.getCurrentWeightKg() != null) {
            profile.setCurrentWeightKg(request.getCurrentWeightKg());
        }
        if (request.getTargetWeightKg() != null) {
            profile.setTargetWeightKg(request.getTargetWeightKg());
        }
        if (request.getActivityLevel() != null) {
            profile.setActivityLevel(request.getActivityLevel());
        }
        if (request.getFitnessGoal() != null) {
            profile.setFitnessGoal(request.getFitnessGoal());
        }
    }

    private UserProfileDto toDto(UserProfile profile) {
        Integer age = null;
        if (profile.getDateOfBirth() != null) {
            age = Period.between(profile.getDateOfBirth(), LocalDate.now()).getYears();
        }

        return UserProfileDto.builder()
                .id(profile.getId())
                .userId(profile.getUser().getId())
                .dateOfBirth(profile.getDateOfBirth())
                .gender(profile.getGender())
                .heightCm(profile.getHeightCm())
                .currentWeightKg(profile.getCurrentWeightKg())
                .targetWeightKg(profile.getTargetWeightKg())
                .activityLevel(profile.getActivityLevel())
                .fitnessGoal(profile.getFitnessGoal())
                .age(age)
                .build();
    }
}
