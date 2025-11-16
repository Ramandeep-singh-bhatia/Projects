package com.interviewtracker.controller;

import com.interviewtracker.service.BackupService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/backup")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class BackupController {

    private final BackupService backupService;

    // Create manual backup
    @PostMapping("/create")
    public ResponseEntity<Map<String, String>> createBackup() {
        try {
            String backupPath = backupService.createBackup();
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                    "message", "Backup created successfully",
                    "backupPath", backupPath
            ));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                    "error", "Failed to create backup: " + e.getMessage()
            ));
        }
    }

    // List all backups
    @GetMapping("/list")
    public ResponseEntity<List<Map<String, Object>>> listBackups() {
        List<Map<String, Object>> backups = backupService.listBackups();
        return ResponseEntity.ok(backups);
    }

    // Download backup file
    @GetMapping("/{fileName}/download")
    public ResponseEntity<Resource> downloadBackup(@PathVariable String fileName) {
        try {
            List<Map<String, Object>> backups = backupService.listBackups();
            Map<String, Object> backup = backups.stream()
                    .filter(b -> b.get("fileName").equals(fileName))
                    .findFirst()
                    .orElseThrow(() -> new RuntimeException("Backup not found"));

            String filePath = (String) backup.get("filePath");
            Resource resource = new FileSystemResource(filePath);

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileName + "\"")
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    // Delete backup
    @DeleteMapping("/{fileName}")
    public ResponseEntity<Map<String, String>> deleteBackup(@PathVariable String fileName) {
        try {
            backupService.deleteBackup(fileName);
            return ResponseEntity.ok(Map.of("message", "Backup deleted successfully"));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                    "error", "Failed to delete backup: " + e.getMessage()
            ));
        }
    }

    // Verify backup
    @PostMapping("/{fileName}/verify")
    public ResponseEntity<Map<String, Object>> verifyBackup(@PathVariable String fileName) {
        boolean valid = backupService.verifyBackup(fileName);
        return ResponseEntity.ok(Map.of(
                "fileName", fileName,
                "valid", valid,
                "message", valid ? "Backup is valid" : "Backup is corrupted or invalid"
        ));
    }

    // Get backup statistics
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getBackupStats() {
        Map<String, Object> stats = backupService.getBackupStats();
        return ResponseEntity.ok(stats);
    }
}
