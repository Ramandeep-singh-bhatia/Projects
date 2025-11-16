package com.interviewtracker.repository;

import com.interviewtracker.model.StudyPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StudyPlanRepository extends JpaRepository<StudyPlan, Long> {

    List<StudyPlan> findByActiveTrueOrderByCreatedDateDesc();

    Optional<StudyPlan> findFirstByActiveTrueOrderByCreatedDateDesc();

    List<StudyPlan> findAllByOrderByCreatedDateDesc();
}
