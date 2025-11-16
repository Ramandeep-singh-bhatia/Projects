package com.interviewtracker.repository;

import com.interviewtracker.model.CalibrationCheck;
import com.interviewtracker.model.Topic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CalibrationCheckRepository extends JpaRepository<CalibrationCheck, Long> {

    List<CalibrationCheck> findByTopicOrderByCheckDateDesc(Topic topic);

    List<CalibrationCheck> findTop10ByOrderByCheckDateDesc();
}
