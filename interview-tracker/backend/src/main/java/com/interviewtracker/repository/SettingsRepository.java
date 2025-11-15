package com.interviewtracker.repository;

import com.interviewtracker.model.Settings;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SettingsRepository extends JpaRepository<Settings, Long> {
    // Singleton pattern - only one Settings record with ID = 1
}
