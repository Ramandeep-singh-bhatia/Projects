package com.interviewtracker.repository;

import com.interviewtracker.model.Topic;
import com.interviewtracker.model.TopicCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TopicRepository extends JpaRepository<Topic, Long> {

    @Query("SELECT t FROM Topic t WHERE TYPE(t) = :type")
    List<Topic> findByType(@Param("type") Class<? extends Topic> type);

    @Query("SELECT t FROM Topic t WHERE t.lastStudiedDate >= :startDate")
    List<Topic> findTopicsStudiedAfter(@Param("startDate") LocalDateTime startDate);

    @Query("SELECT t FROM Topic t WHERE TYPE(t) = :type AND t.lastStudiedDate >= :startDate")
    List<Topic> findByTypeAndLastStudiedAfter(@Param("type") Class<? extends Topic> type,
                                               @Param("startDate") LocalDateTime startDate);

    @Query("SELECT t FROM Topic t WHERE t.confidence <= :maxConfidence")
    List<Topic> findByConfidenceLessThanEqual(@Param("maxConfidence") Integer maxConfidence);
}
