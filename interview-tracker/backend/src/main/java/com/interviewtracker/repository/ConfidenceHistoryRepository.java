package com.interviewtracker.repository;

import com.interviewtracker.model.ConfidenceHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ConfidenceHistoryRepository extends JpaRepository<ConfidenceHistory, Long> {

    List<ConfidenceHistory> findByTopicIdOrderByChangeDateDesc(Long topicId);

    List<ConfidenceHistory> findByChangeDateAfterOrderByChangeDateDesc(LocalDateTime date);

    Long countByTopicIdAndChangeReason(Long topicId, com.interviewtracker.model.ChangeReason changeReason);
}
