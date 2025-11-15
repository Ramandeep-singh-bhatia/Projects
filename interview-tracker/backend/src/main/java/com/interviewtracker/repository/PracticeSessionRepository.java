package com.interviewtracker.repository;

import com.interviewtracker.model.PracticeSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface PracticeSessionRepository extends JpaRepository<PracticeSession, Long> {

    List<PracticeSession> findByTopicIdOrderBySessionDateDesc(Long topicId);

    @Query("SELECT ps FROM PracticeSession ps WHERE ps.sessionDate >= :startDate ORDER BY ps.sessionDate DESC")
    List<PracticeSession> findSessionsAfter(@Param("startDate") LocalDateTime startDate);

    @Query("SELECT ps FROM PracticeSession ps WHERE ps.topic.id = :topicId AND ps.sessionDate >= :startDate")
    List<PracticeSession> findByTopicIdAndSessionDateAfter(@Param("topicId") Long topicId,
                                                            @Param("startDate") LocalDateTime startDate);

    @Query("SELECT COUNT(DISTINCT ps.sessionDate) FROM PracticeSession ps WHERE ps.sessionDate >= :startDate")
    Long countDistinctDaysStudied(@Param("startDate") LocalDateTime startDate);

    @Query("SELECT ps FROM PracticeSession ps ORDER BY ps.sessionDate DESC LIMIT :limit")
    List<PracticeSession> findRecentSessions(@Param("limit") int limit);
}
