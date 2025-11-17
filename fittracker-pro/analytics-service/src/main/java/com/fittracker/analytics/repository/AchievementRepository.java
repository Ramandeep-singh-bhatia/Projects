package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.Achievement;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface AchievementRepository extends JpaRepository<Achievement, Long> {

    Page<Achievement> findByUserIdOrderByAchievementDateDesc(Long userId, Pageable pageable);

    List<Achievement> findByUserIdAndAchievementType(Long userId, Achievement.AchievementType achievementType);

    @Query("SELECT a FROM Achievement a WHERE a.userId = :userId " +
           "AND a.achievementDate BETWEEN :startDate AND :endDate " +
           "ORDER BY a.achievementDate DESC")
    List<Achievement> findAchievementsInPeriod(@Param("userId") Long userId,
                                               @Param("startDate") LocalDate startDate,
                                               @Param("endDate") LocalDate endDate);

    @Query("SELECT COUNT(a) FROM Achievement a WHERE a.userId = :userId " +
           "AND a.achievementDate BETWEEN :startDate AND :endDate")
    Long countAchievementsInPeriod(@Param("userId") Long userId,
                                   @Param("startDate") LocalDate startDate,
                                   @Param("endDate") LocalDate endDate);

    List<Achievement> findTop10ByUserIdOrderByAchievementDateDesc(Long userId);
}
