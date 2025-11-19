package com.fittracker.user.service;

import com.fittracker.common.event.UserWeightUpdatedEvent;
import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.user.dto.WeightHistoryDto;
import com.fittracker.user.dto.WeightHistoryRequest;
import com.fittracker.user.entity.User;
import com.fittracker.user.entity.WeightHistory;
import com.fittracker.user.kafka.EventPublisher;
import com.fittracker.user.repository.UserRepository;
import com.fittracker.user.repository.WeightHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class WeightHistoryService {

    private final WeightHistoryRepository weightHistoryRepository;
    private final UserRepository userRepository;
    private final EventPublisher eventPublisher;

    @Transactional
    public WeightHistoryDto logWeight(Long userId, WeightHistoryRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));

        WeightHistory weightHistory = WeightHistory.builder()
                .user(user)
                .weightKg(request.getWeightKg())
                .bodyFatPercentage(request.getBodyFatPercentage())
                .muscleMassKg(request.getMuscleMassKg())
                .notes(request.getNotes())
                .recordedAt(request.getRecordedAt() != null ? request.getRecordedAt() : LocalDateTime.now())
                .build();

        WeightHistory saved = weightHistoryRepository.save(weightHistory);
        log.info("Weight logged for user {}: {} kg", userId, request.getWeightKg());

        // Publish UserWeightUpdatedEvent
        UserWeightUpdatedEvent event = UserWeightUpdatedEvent.create(
                userId,
                request.getWeightKg(),
                saved.getRecordedAt().toLocalDate()
        );
        eventPublisher.publishUserWeightUpdatedEvent(event);

        return toDto(saved);
    }

    @Transactional(readOnly = true)
    public List<WeightHistoryDto> getWeightHistory(Long userId) {
        return weightHistoryRepository.findByUserIdOrderByRecordedAtDesc(userId)
                .stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<WeightHistoryDto> getWeightHistory(Long userId, Pageable pageable) {
        return weightHistoryRepository.findByUserIdOrderByRecordedAtDesc(userId, pageable)
                .map(this::toDto);
    }

    @Transactional(readOnly = true)
    public List<WeightHistoryDto> getWeightHistoryByDateRange(Long userId, LocalDateTime start, LocalDateTime end) {
        return weightHistoryRepository.findByUserIdAndDateRange(userId, start, end)
                .stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    private WeightHistoryDto toDto(WeightHistory entity) {
        return WeightHistoryDto.builder()
                .id(entity.getId())
                .userId(entity.getUser().getId())
                .weightKg(entity.getWeightKg())
                .bodyFatPercentage(entity.getBodyFatPercentage())
                .muscleMassKg(entity.getMuscleMassKg())
                .notes(entity.getNotes())
                .recordedAt(entity.getRecordedAt())
                .build();
    }
}
