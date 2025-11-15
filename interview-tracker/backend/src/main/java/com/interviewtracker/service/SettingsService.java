package com.interviewtracker.service;

import com.interviewtracker.model.Settings;
import com.interviewtracker.repository.SettingsRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SettingsService {

    @Autowired
    private SettingsRepository settingsRepository;

    public Settings getSettings() {
        return settingsRepository.findById(1L)
                .orElseGet(() -> {
                    // Create default settings if none exist
                    Settings defaultSettings = new Settings();
                    return settingsRepository.save(defaultSettings);
                });
    }

    @Transactional
    public Settings updateSettings(Settings settings) {
        Settings existingSettings = getSettings();

        existingSettings.setDailyStudyHours(settings.getDailyStudyHours());
        existingSettings.setWeeklyDsaGoal(settings.getWeeklyDsaGoal());
        existingSettings.setWeeklyHldGoal(settings.getWeeklyHldGoal());
        existingSettings.setWeeklyLldGoal(settings.getWeeklyLldGoal());
        existingSettings.setWeeklyBehavioralGoal(settings.getWeeklyBehavioralGoal());
        existingSettings.setWeekStartDay(settings.getWeekStartDay());
        existingSettings.setTheme(settings.getTheme());

        return settingsRepository.save(existingSettings);
    }
}
