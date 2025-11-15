package com.interviewtracker.controller;

import com.interviewtracker.model.Settings;
import com.interviewtracker.service.SettingsService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class SettingsController {

    @Autowired
    private SettingsService settingsService;

    @GetMapping
    public ResponseEntity<Settings> getSettings() {
        Settings settings = settingsService.getSettings();
        return ResponseEntity.ok(settings);
    }

    @PutMapping
    public ResponseEntity<Settings> updateSettings(@Valid @RequestBody Settings settings) {
        Settings updatedSettings = settingsService.updateSettings(settings);
        return ResponseEntity.ok(updatedSettings);
    }
}
