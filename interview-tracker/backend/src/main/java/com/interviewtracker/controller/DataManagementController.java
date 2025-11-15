package com.interviewtracker.controller;

import com.interviewtracker.service.DataManagementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@RestController
@RequestMapping("/api/data")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class DataManagementController {

    @Autowired
    private DataManagementService dataManagementService;

    @GetMapping("/export")
    public ResponseEntity<String> exportData() {
        String jsonData = dataManagementService.exportDataToJson();

        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        String filename = "interview-tracker-export-" + timestamp + ".json";

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .contentType(MediaType.APPLICATION_JSON)
                .body(jsonData);
    }

    @PostMapping("/import")
    public ResponseEntity<Map<String, String>> importData(
            @RequestParam("file") MultipartFile file,
            @RequestParam(defaultValue = "false") boolean merge) {

        try {
            String jsonContent = new String(file.getBytes());
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
            mapper.registerModule(new com.fasterxml.jackson.datatype.jsr310.JavaTimeModule());

            @SuppressWarnings("unchecked")
            Map<String, Object> data = mapper.readValue(jsonContent, Map.class);

            dataManagementService.importData(data, merge);

            return ResponseEntity.ok(Map.of("message", "Data imported successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to import data: " + e.getMessage()));
        }
    }

    @DeleteMapping("/reset")
    public ResponseEntity<Map<String, String>> resetAllData() {
        dataManagementService.resetAllData(true);
        return ResponseEntity.ok(Map.of("message", "All data has been reset successfully"));
    }

    @PostMapping("/backup")
    public ResponseEntity<Map<String, String>> createBackup() {
        dataManagementService.createBackup();
        return ResponseEntity.ok(Map.of("message", "Backup created successfully"));
    }

    @GetMapping("/storage-info")
    public ResponseEntity<Map<String, Object>> getStorageInfo() {
        Map<String, Object> info = dataManagementService.getStorageInfo();
        return ResponseEntity.ok(info);
    }
}
