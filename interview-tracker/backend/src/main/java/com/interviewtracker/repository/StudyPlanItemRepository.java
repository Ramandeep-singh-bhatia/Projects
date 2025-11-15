package com.interviewtracker.repository;

import com.interviewtracker.model.StudyPlanItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface StudyPlanItemRepository extends JpaRepository<StudyPlanItem, Long> {

    List<StudyPlanItem> findByStudyPlanIdOrderByScheduledDateAscDisplayOrderAsc(Long studyPlanId);

    @Query("SELECT s FROM StudyPlanItem s WHERE s.studyPlan.id = :planId AND s.scheduledDate = :date ORDER BY s.displayOrder")
    List<StudyPlanItem> findByStudyPlanIdAndScheduledDate(@Param("planId") Long planId, @Param("date") LocalDate date);

    @Query("SELECT s FROM StudyPlanItem s WHERE s.studyPlan.id = :planId AND s.completed = false ORDER BY s.scheduledDate, s.displayOrder")
    List<StudyPlanItem> findIncompleteByStudyPlanId(@Param("planId") Long planId);
}
