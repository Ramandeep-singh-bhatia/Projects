package com.fittracker.user.repository;

import com.fittracker.user.entity.WeightHistory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface WeightHistoryRepository extends JpaRepository<WeightHistory, Long> {

    List<WeightHistory> findByUserIdOrderByRecordedAtDesc(Long userId);

    Page<WeightHistory> findByUserIdOrderByRecordedAtDesc(Long userId, Pageable pageable);

    @Query("SELECT w FROM WeightHistory w WHERE w.user.id = :userId AND w.recordedAt BETWEEN :startDate AND :endDate ORDER BY w.recordedAt DESC")
    List<WeightHistory> findByUserIdAndDateRange(
            @Param("userId") Long userId,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate
    );

    @Query("SELECT w FROM WeightHistory w WHERE w.user.id = :userId ORDER BY w.recordedAt DESC LIMIT 1")
    WeightHistory findLatestByUserId(@Param("userId") Long userId);
}
